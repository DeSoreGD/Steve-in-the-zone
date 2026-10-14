"""Update project files in an existing installation; keep worlds and preferences.

Only installer-created installations are accepted. Every replacement has a local
backup and a write-ahead journal. Failed/interrupted updates restore that backup.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import hashlib
import json
import msvcrt
import os
import shutil
import uuid


def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inside(root, relative):
    part=PurePosixPath(relative)
    if part.is_absolute() or '..' in part.parts or '\\' in relative or ':' in relative:
        raise ValueError('Invalid update file path.')
    target=root.joinpath(*part.parts)
    if not target.resolve().is_relative_to(root):
        raise ValueError('Linked update files outside the installation are not supported.')
    return target


def _destination(relative):
    part=PurePosixPath(relative)
    if part.parts[0]=='bin':return 'soc/bin_steve/'+str(part.relative_to('bin'))
    if part.parts[0]=='gamedata':return 'soc/'+relative
    if part.parts[0] in ('app','notices'):return relative
    if relative in ('sitz.jar','fabric-api.jar'):return 'minecraft/mods/'+relative
    if relative in ('fsgame_demo.ltx','user_ogsr.ltx'):return None
    raise ValueError('Unknown component in update: '+relative)


def _write(path, value):
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2),encoding='utf-8')
    os.replace(temp,path)


def _restore(root, journal):
    if journal.get('schema')!=1 or not journal.get('backup','').startswith('update-backups/'):
        raise ValueError('Unrecognized update recovery receipt.')
    backup=_inside(root,journal['backup'])
    # Validate the entire receipt before touching any installed component.
    checked=[]
    for entry in journal['files']:
        target=_inside(root,entry['path'])
        if entry['path']!='installation.json' and entry['path']!='minecraft/mods/stalkercraft.jar':
            if not entry['path'].startswith(('app/','notices/','soc/bin_steve/','soc/gamedata/','minecraft/mods/')):
                raise ValueError('Update recovery contains an unexpected file.')
        previous=_inside(backup,entry['path'])
        if entry['existed'] and (not previous.is_file() or _hash(previous)!=entry['sha256']):
            raise ValueError('Update backup is incomplete. Keep the backup for recovery.')
        checked.append((entry,target,previous))
    for entry,target,previous in checked:
        if entry['existed']:
            target.parent.mkdir(parents=True,exist_ok=True)
            temp=target.with_name(target.name+'.restore-'+uuid.uuid4().hex)
            shutil.copy2(previous,temp);os.replace(temp,target)
        elif target.exists():target.unlink()


def update_installation(destination,payload,notify=lambda _:None):
    root=Path(destination).absolute()
    if root.resolve()!=root or not root.is_dir():raise ValueError('Choose an existing installation outside linked directories.')
    installed=_inside(root,'installation.json')
    old=json.loads(installed.read_text(encoding='utf-8'))
    if old.get('schema')!=1 or old.get('provider')!='local-singleplayer' or old.get('minecraft')!='1.20.1':
        raise ValueError('Select a Steve in the Zone installation created by Setup.')
    config=json.loads(_inside(root,'demo-launch.json').read_text(encoding='utf-8-sig'))
    if config.get('schema')!=2 or config.get('profile')!='minecraft' or config.get('native',{}).get('executable')!='soc/bin_steve/xrEngine.exe':
        raise ValueError('This installation uses a custom layout. Automatic update is not supported.')
    payload=Path(payload).resolve(strict=True)
    manifest=json.loads((payload/'payload.json').read_text(encoding='utf-8'))
    actual={p.relative_to(payload).as_posix() for p in payload.rglob('*') if p.is_file() and p.name!='payload.json'}
    if actual!=set(manifest['files']):raise ValueError('Update package has missing or unexpected files. Extract the entire archive.')
    replacements={}
    for relative,expected in manifest['files'].items():
        source=_inside(payload,relative)
        if _hash(source)!=expected:raise ValueError('Update package is damaged: '+relative)
        mapped=_destination(relative)
        if mapped:replacements[mapped]=source
    for required in ('minecraft/mods/sitz.jar','minecraft/mods/fabric-api.jar','soc/bin_steve/xrEngine.exe','app/SteveInTheZone.exe'):
        if required not in replacements:raise ValueError('Update package lacks a required component.')
    lockpath=_inside(root,'minecraft/demo-session.lock')
    with lockpath.open('a+b') as lock:
        lock.seek(0)
        if lockpath.stat().st_size==0:lock.write(b'0');lock.flush()
        lock.seek(0)
        try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:raise ValueError('Close the game and its launcher before updating.')
        journalpath=_inside(root,'.update-in-progress.json')
        try:
            if journalpath.exists():
                notify('Восстанавливаю предыдущую версию после прерванного обновления…')
                _restore(root,json.loads(journalpath.read_text(encoding='utf-8')))
                journalpath.unlink()
                old=json.loads(installed.read_text(encoding='utf-8'))
            legacy=_inside(root,'minecraft/mods/stalkercraft.jar')
            if legacy.exists():
                if old.get('payload',{}).get('stalkercraft.jar')!=_hash(legacy):
                    raise ValueError('Unrecognized older mod file. Keep it and remove the duplicate before updating.')
                replacements['minecraft/mods/stalkercraft.jar']=None
            # World's files are never in this list. Keep the installation path,
            # profile identity, Java/assets, options, native config and account data.
            backup=_inside(root,'update-backups/'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex)
            backup.mkdir(parents=True)
            entries=[]
            for relative in [*replacements,'installation.json']:
                target=_inside(root,relative)
                existed=target.is_file()
                if target.exists() and not existed:raise ValueError('A component file is replaced by a directory: '+relative)
                if existed:
                    previous=_inside(backup,relative);previous.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,previous)
                entries.append({'path':relative,'existed':existed,'sha256':_hash(target) if existed else None})
            journal={'schema':1,'backup':backup.relative_to(root).as_posix(),'files':entries}
            _write(journalpath,journal)
            try:
                notify('Обновляю файлы игры. Сохранения и настройки сохраняются…')
                for relative,source in replacements.items():
                    target=_inside(root,relative);target.parent.mkdir(parents=True,exist_ok=True)
                    if source is None:target.unlink();continue
                    temp=target.with_name(target.name+'.update-'+uuid.uuid4().hex)
                    try:shutil.copy2(source,temp);os.replace(temp,target)
                    finally:temp.unlink(missing_ok=True)
                _write(installed,{**old,'payload':manifest['files'],'version':manifest.get('version'),'lastUpdateBackup':str(backup)})
                journalpath.unlink()
            except Exception:
                _restore(root,journal);journalpath.unlink();raise
            notify('Обновление завершено. Прогресс и настройки сохранены.')
            return root/'demo-launch.json'
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
