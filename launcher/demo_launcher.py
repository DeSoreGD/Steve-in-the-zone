"""Steve in the Zone: direct process supervisor and small desktop front end.

Consumes a prepared profile/Java argument file. Does not read launcher accounts,
invent public login credentials, download Minecraft, or modify an owner's world.
Authentication/profile installation are separate providers still to be integrated.
"""
from __future__ import annotations
import argparse
import ctypes
import json
import msvcrt
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

TITLE = "Steve in the Zone"
DEFAULT_SETTINGS = {"memoryMb": 2048, "maxFps": 60, "soundVolume": 0.7, "gameMode": "survival", "language": "ru"}


def validate_settings(values: dict) -> dict:
    result = {**DEFAULT_SETTINGS, **values}
    if result["memoryMb"] not in (2048, 4096, 6144) or result["maxFps"] not in (0, 30, 60, 90, 120, 144, 240):
        raise ValueError("Некорректные настройки памяти или частоты обновления.")
    volume = result["soundVolume"]
    if not isinstance(volume, (int, float)) or not 0 <= volume <= 1:
        raise ValueError("Некорректная громкость.")
    if result["gameMode"] not in ("creative", "survival"):
        raise ValueError("Некорректный режим игры.")
    if result["language"] not in ("ru", "en"):
        raise ValueError("Некорректный язык приложения.")
    return {key: result[key] for key in DEFAULT_SETTINGS}


def load_config(path: Path) -> dict:
    path = path.resolve()
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    config['installationRoot'] = str(path.parent)
    def relative(value):
        candidate = Path(value)
        return str((candidate if candidate.is_absolute() else path.parent/candidate).resolve())
    settings_path = path.resolve().with_name("launcher-settings.json")
    values = config.get("settings", {})
    if settings_path.exists():
        values = {**values, **json.loads(settings_path.read_text(encoding="utf-8"))}
    config["settings"] = validate_settings(values)
    config["settingsPath"] = str(settings_path)
    for key in ("java", "minecraftArgsFile", "profile"):
        config[key] = str(Path(relative(config[key])).resolve(strict=True))
    for key in ('startupStatusFile','bridgeDirectory'):
        if config.get(key):config[key]=relative(config[key])
    profile = Path(config["profile"])
    if not profile.is_dir():
        raise ValueError("Отдельный профиль отсутствует.")
    if not (profile / "saves/Stalker mirror/level.dat").is_file() and not config.get("createWorldIfMissing"):
        raise ValueError("В отдельном профиле отсутствует демо-мир.")
    if not (profile / "mods/sitz.jar").is_file():
        raise ValueError("В профиле отсутствует мод.")
    native = config["native"]
    native["executable"] = str(Path(relative(native["executable"])).resolve(strict=True))
    native["directory"] = str(Path(relative(native["directory"])).resolve(strict=True))
    if not isinstance(native["arguments"], list) or not all(isinstance(v, str) for v in native["arguments"]):
        raise ValueError("Некорректная конфигурация запуска.")
    # An argument file must explicitly target this disposable/separate profile.
    args = Path(config["minecraftArgsFile"]).read_text(encoding="utf-8-sig")
    if config.get('schema') == 2:
        values=[json.loads(line).replace('@ROOT@',str(path.parent)) for line in args.splitlines() if line.strip()]
        resolved=profile/'prepared-java-resolved.args'
        resolved.write_text('\n'.join(map(java_quote,values)),encoding='utf-8')
        config['minecraftArgsFile']=str(resolved)
        args=resolved.read_text(encoding='utf-8')
    decoded=[json.loads(line) for line in args.splitlines() if line.strip()]
    try:target=Path(decoded[decoded.index('--gameDir')+1]).resolve()
    except (ValueError,IndexError):target=None
    if target != profile:
        raise ValueError("Файл запуска не относится к отдельному демо-профилю.")
    from preflight import validate_prepared
    validate_prepared(config)
    return config


def java_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def require_hidden_test(arguments: list[str], environment: dict) -> None:
    """The engine hides only when all three guards match, including its splash."""
    identity=environment.get('STALKERCRAFT_COMBAT_TEST_ID','')
    if environment.get('STALKERCRAFT_TEST_BACKGROUND')!='1' or len(identity)!=32 or any(c not in '0123456789abcdef' for c in identity) or '-stalkercraft-combatcheck' not in arguments:
        raise ValueError('Hidden test launch refused: missing native background guards.')


def close_native(process: subprocess.Popen) -> bool:
    """Request a normal close only on windows belonging to our own child PID."""
    if process.poll() is not None:
        return True
    user = ctypes.windll.user32
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user.GetWindowThreadProcessId.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong))
    user.PostMessageW.argtypes = (ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p)
    user.EnumWindows.argtypes = (callback_type, ctypes.c_void_p)
    def visit(window, _):
        pid = ctypes.c_ulong()
        user.GetWindowThreadProcessId(window, ctypes.byref(pid))
        if pid.value == process.pid:
            user.PostMessageW(window, 0x0010, None, None)  # WM_CLOSE
        return True
    user.EnumWindows(callback_type(visit), None)
    try:
        process.wait(timeout=40)
        return True
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait(timeout=8)
        return False


def supervise(config: dict, cancel: threading.Event, notify, attach_test_host: int = 0) -> int:
    from new_campaign import session_lock
    from reset_world import reset_demo
    with session_lock(Path(config['profile'])) as lock:
        while True:
            restart={}
            result=_supervise_once(config,cancel,notify,attach_test_host,lock,restart)
            if not restart or cancel.is_set():return result
            if attach_test_host:raise ValueError('Нельзя перезапустить чужую тестовую сессию.')
            notify('Начинаю новую кампанию. Сохраняю предыдущие миры в резервную копию…')
            backup=reset_demo(config,_session_lock=lock)
            notify('Предыдущая кампания сохранена в резервную копию. Запускаю новую игру…')
            if cancel.is_set():return result


def _supervise_once(config,cancel,notify,attach_test_host=0,_session_lock=None,restart=None):
    profile = Path(config["profile"])
    startup_path=Path(config["startupStatusFile"]) if config.get("startupStatusFile") else None
    original_notify=notify
    last_startup_phase=None
    def startup(phase):
        nonlocal last_startup_phase
        if startup_path is None:return
        if phase==last_startup_phase:return
        startup_path.parent.mkdir(parents=True,exist_ok=True)
        temporary=startup_path.with_suffix(".tmp")
        temporary.write_text("protocol=1\nphase="+phase+"\nupdated_ms="+str(int(time.time()*1000))+"\n",encoding="ascii")
        # Native Lua may briefly hold the status file without FILE_SHARE_DELETE.
        # A cosmetic progress update must not tear down the running campaign.
        for attempt in range(3):
            try:
                temporary.replace(startup_path)
                last_startup_phase=phase
                return
            except PermissionError:
                if attempt<2:time.sleep(.01)
    def notify(message):
        phases={"Создаю чистый демо-мир…":"world","Запускаю «Сталкер»…":"native","Загружаю Minecraft в фоне…":"minecraft", "Готово — играй в окне «Сталкера».":"ready", "Ожидаю подключения к «Сталкеру»…":"connecting", "Сохраняю мир и закрываю демо…":"saving"}
        if message in phases:startup(phases[message])
        original_notify(message)
    native = minecraft = None
    stdout = stderr = None
    ready = False
    waiting = False
    finished = False
    session_owned=_session_lock is not None
    lock = _session_lock if _session_lock is not None else (profile / "demo-session.lock").open("a+b")
    try:
        if _session_lock is None:
            lock.seek(0)
            if os.fstat(lock.fileno()).st_size==0:
                lock.write(b"0"); lock.flush()
            lock.seek(0)
            try:
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                session_owned=True
            except OSError:
                raise ValueError("Это демо уже запущено. Закрой предыдущую сессию.")
        if attach_test_host and not (config.get("testProfile") is True and profile.name.isalnum()
                                     and len(profile.name) == 32 and profile.parent.name == "combat-smoke"):
            raise ValueError("Подключение к внешнему PID разрешено только изолированному тесту.")
        for name in ("demo-stop.request", "demo-status.txt"):
            (profile / name).unlink(missing_ok=True)
        bridge=Path(config.get('bridgeDirectory',str(profile.parent/'bridge')))
        for name in ('new-campaign.request','new-campaign.pending','campaign-finished.request'):
            (bridge/name).unlink(missing_ok=True)
        mapping = config.get("existingMappingName")
        if mapping:
            kernel = ctypes.windll.kernel32
            kernel.OpenFileMappingW.argtypes = (ctypes.c_ulong, ctypes.c_bool, ctypes.c_wchar_p)
            kernel.OpenFileMappingW.restype = ctypes.c_void_p
            kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
            handle = kernel.OpenFileMappingW(4, False, mapping)
            if handle:
                kernel.CloseHandle(handle)
                raise ValueError("Уже открыт «Сталкер» с мостом Minecraft. Закрой его перед новым запуском.")
        from reset_world import recover_reset
        recover_reset(config)
        if not (profile / "saves/Stalker mirror/level.dat").exists():
            notify("Создаю чистый демо-мир…")
            from create_world import create_demo_world
            create_demo_world(profile / "saves/Stalker mirror",config['settings']['gameMode'])
        campaign=profile/'campaign'
        campaign.mkdir(exist_ok=True)
        from campaign import restore_latest,prune_campaign
        if not attach_test_host:prune_campaign(profile,campaign)
        resume=restore_latest(profile,config['native'],campaign) if not attach_test_host else None
        if attach_test_host:
            host_pid = attach_test_host  # Never terminate a process we did not create.
        else:
            notify("Запускаю «Сталкер»…")
            settings = config["native"]
            native_arguments=list(settings['arguments'])
            if resume:
                start=native_arguments.index('-start')+1
                native_arguments[start]=f'server({resume}/single/alife/load)'
            native_environment=dict(os.environ,STALKERCRAFT_CAMPAIGN_DIR=str(campaign))
            native_environment['SITZ_MAX_FPS']=str(config['settings']['maxFps'])
            # Foreground owners keep their settings. Only explicitly isolated
            # probes use the native hidden/no-input mode, including their splash.
            if config.get('testProfile') is True:
                native_environment['STALKERCRAFT_TEST_BACKGROUND']='1'
                require_hidden_test(native_arguments,native_environment)
                if config.get('testNativeSoundCallbacks') is not True:
                    native_arguments.append('-nosound')
            else:
                native_environment.pop('STALKERCRAFT_TEST_BACKGROUND',None)
            native_environment['STALKERCRAFT_BRIDGE_DIR']=config.get('bridgeDirectory',str(profile.parent/'bridge'))
            native_environment['STALKERCRAFT_NEW_GAME_SUPPORTED']='1' if config.get('createNativeIfMissing') else '0'
            native_environment['STALKERCRAFT_CORDON_ORIGIN']=' '.join(map(str,config.get('cordonOrigin',[-247.387,-19.222,-126.259])))
            if not resume and config.get('createNativeIfMissing'):
                from campaign import native_saves
                if not (native_saves(settings)/'mc_lab.sav').exists():
                    native_arguments[native_arguments.index('-start')+1]='server(all/single/alife/new)'
                    native_environment['STALKERCRAFT_FRESH_SCENE']='1'
            native = subprocess.Popen([settings["executable"], *native_arguments],env=native_environment,
                                      cwd=settings["directory"], creationflags=subprocess.CREATE_NO_WINDOW)
            host_pid = native.pid
        notify("Загружаю Minecraft в фоне…")
        settings = config["settings"]
        flags = ["-Dstalkercraft.demoLaunch=true", "-Dstalkercraft.startHidden=true",
                 "-Dstalkercraft.demoHostPid=" + str(host_pid), "-Xmx" + str(settings["memoryMb"]) + "M",
                 "-Dstalkercraft.demoMaxFps=" + str(settings["maxFps"]),
                 "-Dstalkercraft.demoGameMode=" + settings["gameMode"],
                 "-Dstalkercraft.demoSoundVolume=" + str(0 if config.get('testProfile') is True else settings["soundVolume"])]
        flags.append('-Dstalkercraft.campaignDirectory='+str(campaign))
        arguments = profile / "demo-java.args"
        base = Path(config["minecraftArgsFile"]).read_text(encoding="utf-8-sig").splitlines()
        base = [line for line in base if not line.startswith('"-Xmx')]
        arguments.write_text("\n".join([*map(java_quote, flags), *base]), encoding="utf-8")
        stdout = (profile / "demo-minecraft.log").open("w", encoding="utf-8")
        stderr = (profile / "demo-minecraft-error.log").open("w", encoding="utf-8")
        minecraft = subprocess.Popen([config["java"], "@" + str(arguments)], cwd=profile,
                                     stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        (profile / "demo-processes.json").write_text(json.dumps({"minecraft": minecraft.pid,
            "native": native.pid if native is not None else None}), encoding="utf-8")
        began = time.monotonic()
        while minecraft.poll() is None:
            status_path = profile / "demo-status.txt"
            status = status_path.read_text(encoding="utf-8").strip() if status_path.exists() else ""
            if status.startswith("error:"):
                raise RuntimeError("Не удалось подключить демо: " + status[6:])
            if status.startswith("ready:") and not ready:
                if status != "ready:hidden=true":
                    raise RuntimeError("Minecraft не подтвердил скрытый рендер.")
                ready = True
                notify("Готово — играй в окне «Сталкера».")
            elif status == "waiting-for-bridge" and ready and not waiting:
                waiting = True
                notify("Ожидаю подключения к «Сталкеру»…")
            elif status.startswith("ready:") and waiting:
                waiting = False
                notify("Готово — играй в окне «Сталкера».")
            elif status.startswith('loading:'):
                startup('saving' if status in ('loading:1','loading:3') else 'level')
                waiting=True
            if cancel.is_set() or (native is not None and native.poll() is not None):
                break
            if ready and native is not None:
                from new_campaign import consume,consume_finished
                if consume_finished(config):
                    finished=True
                    break
                difficulty=consume(config)
                if difficulty:
                    if restart is None:raise RuntimeError('Новая игра требует совместного запуска.')
                    restart['difficulty']=difficulty
                    notify('Закрываю текущую кампанию перед новой игрой…')
                    break
            if not ready and time.monotonic() - began > 210:
                raise RuntimeError("Подключение заняло слишком долго. Подробности в журнале демо.")
            time.sleep(0.2)
        if minecraft.poll() is not None and minecraft.returncode != 0:
            raise RuntimeError("Minecraft завершился с ошибкой. Подробности в журнале демо.")
        if not ready and not cancel.is_set():
            raise RuntimeError("Minecraft завершился до подключения демо.")
        return 0
    finally:
        # Native teardown requests a paired checkpoint while Minecraft is alive.
        native_closed=True; minecraft_closed=True
        if native is not None:native_closed=close_native(native)
        if minecraft is not None and minecraft.poll() is None:
            notify("Сохраняю мир и закрываю демо…")
            (profile / "demo-stop.request").write_text("stop\n", encoding="utf-8")
            try:
                minecraft.wait(timeout=35)
            except subprocess.TimeoutExpired:
                notify("Minecraft не ответил на выход; закрываю только процесс этой сессии.")
                minecraft.terminate(); minecraft.wait(timeout=8)
                minecraft_closed=False
        startup("completed" if finished and native_closed and minecraft_closed else "closed")
        if finished and native_closed and minecraft_closed:
            original_notify("Кампания завершена.")
        if stdout is not None:
            stdout.close(); stderr.close()
        try:
            if not native_closed or not minecraft_closed:
                raise RuntimeError('Демо не завершило штатное сохранение. Сохранил журналы и последнюю целую пару мира.')
            if session_owned and not attach_test_host:
                # Keep the session lock until cleanup finishes; a second launcher
                # must never prune snapshots while the first game is running.
                from campaign import prune_campaign
                prune_campaign(profile,profile/'campaign')
        finally:
            if _session_lock is None:lock.close()


def desktop(config: dict) -> int:
    from desktop_ui import desktop as front_end
    return front_end(config, supervise, validate_settings)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--no-ui", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument('--reset',action='store_true')
    parser.add_argument('--report',type=Path)
    parser.add_argument("--test-attach-host", type=int, default=0)
    options = parser.parse_args()
    try:
        config = load_config(options.config)
        if options.check:
            if options.report:options.report.write_text(json.dumps({'success':True,'schema':config.get('schema',1)}),encoding='utf-8')
            if sys.stdout is not None:print("Prepared profile validated.")
            return 0
        if options.reset:
            from reset_world import reset_demo
            backup=reset_demo(config)
            if options.report:options.report.write_text(json.dumps({'success':True,'backup':str(backup)}),encoding='utf-8')
            return 0
        if options.no_ui:
            return supervise(config, threading.Event(), print, options.test_attach_host)
        if options.test_attach_host:
            raise ValueError("Тестовое подключение требует --no-ui.")
        return desktop(config)
    except Exception as error:
        if options.report:options.report.write_text(json.dumps({'success':False,'error':str(error)}),encoding='utf-8')
        # Never dump argument files/session credentials or full process commands.
        if sys.stdout is not None:
            print(str(error))
        if not options.no_ui:
            from tkinter import messagebox
            messagebox.showerror(TITLE, str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
