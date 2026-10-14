"""Prepare a separate local single-player installation from owned game components.

No launcher account files, tokens, existing worlds, or native saves are imported.
Missing Minecraft components come from pinned official manifests, never a launcher.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import urllib.request
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor

MC_VERSION='1.20.1'
FABRIC_VERSION='0.19.5'


def find_java(minecraft_source):
    source=Path(minecraft_source)
    candidates=[]
    for folder in (source/'runtime',source/'jre',source.parent/'.tlauncher/legacy/Minecraft/jre',
                   Path.home()/'AppData/Roaming/.tlauncher/legacy/Minecraft/jre'):
        if folder.is_dir():candidates.extend(folder.glob('**/bin/javaw.exe'))
    for candidate in candidates:
        try:validate_java(candidate);return candidate
        except (OSError,ValueError,subprocess.SubprocessError):pass
    raise ValueError('Java 17 or newer was not found automatically. Select javaw.exe.')


def validate_java(java):
    executable=Path(java)
    # SoC and the bundled Minecraft natives are x64; 32-bit Java cannot load them.
    import struct
    with executable.open('rb') as stream:
        if stream.read(2)!=b'MZ':raise ValueError('Select a Windows x64 Java executable.')
        stream.seek(0x3c);offset=struct.unpack('<I',stream.read(4))[0];stream.seek(offset)
        if stream.read(4)!=b'PE\0\0' or struct.unpack('<H',stream.read(2))[0]!=0x8664:
            raise ValueError('Minecraft requires x64 Java 17 or newer for this installation.')
    console=Path(java).with_name('java.exe')
    result=subprocess.run([str(console),'-version'],capture_output=True,text=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
    match=re.search(r'version "(\d+)',result.stderr+result.stdout)
    if result.returncode or not match or int(match[1])<17:raise ValueError('Minecraft 1.20.1 requires Java 17 or newer.')


def fetch(url):
    with urllib.request.urlopen(url,timeout=30) as response:return response.read()


def digest(path,algorithm='sha1'):
    h=hashlib.new(algorithm)
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def obtain(target,url,sha1=None,source=None):
    target.parent.mkdir(parents=True,exist_ok=True)
    if source and source.is_file() and (not sha1 or digest(source)==sha1):
        shutil.copyfile(source,target)
    else:target.write_bytes(fetch(url))
    if sha1 and digest(target)!=sha1:raise ValueError('Component checksum mismatch: '+target.name)


def allowed(library):
    result='rules' not in library
    for rule in library.get('rules',[]):
        system=rule.get('os',{})
        if system.get('name','windows')!='windows':continue
        if system.get('arch','x86_64') not in ('x86_64','amd64'):continue
        if rule.get('features'):continue
        result=rule['action']=='allow'
    return result


def maven_path(name):
    group,artifact,version,*classifier=name.split(':')
    suffix='-'+classifier[0] if classifier else ''
    return f'{group.replace(".","/")}/{artifact}/{version}/{artifact}-{version}{suffix}.jar'


def prepare(destination,game_source,minecraft_source,java,payload,username='Steve',language='ru',notify=lambda _:None):
    destination=Path(destination).absolute();game_source=Path(game_source).resolve(strict=True)
    minecraft_source=Path(minecraft_source).resolve(strict=True)
    java=(Path(java) if java else find_java(minecraft_source)).resolve(strict=True)
    validate_java(java)
    payload=Path(payload).resolve(strict=True)
    if not re.fullmatch(r'[A-Za-z0-9_]{3,16}',username):raise ValueError('Use a nickname with 3–16 letters, numbers, or underscores.')
    if language not in ('ru','en'):raise ValueError('Unknown application language.')
    if destination.exists() or destination.parent.resolve()!=destination.parent:
        raise ValueError('Choose a new folder, outside linked directories.')
    for source in (game_source,minecraft_source,java.parent.parent,payload):
        if destination.is_relative_to(source) or source.is_relative_to(destination):
            raise ValueError('The demo must have a separate installation folder.')
    archives=list(game_source.glob('gamedata.db*'))
    if len(archives)<10:raise ValueError('Select the Shadow of Chernobyl 1.0006 game folder.')
    manifest=json.loads((payload/'payload.json').read_text(encoding='utf-8'))
    actual={str(file.relative_to(payload)).replace('\\','/') for file in payload.rglob('*') if file.is_file() and file.name!='payload.json'}
    if actual!=set(manifest['files']):
        raise ValueError('Installation payload has missing or unexpected files. Extract a fresh package.')
    for relative,expected in manifest['files'].items():
        file=payload/relative
        if not file.resolve().is_relative_to(payload) or digest(file,'sha256')!=expected:
            raise ValueError('Demo payload is damaged: '+relative)
    destination.parent.mkdir(parents=True,exist_ok=True)
    required=sum(file.stat().st_size for file in archives)+3*1024**3
    if shutil.disk_usage(destination.parent).free<required:raise ValueError('Not enough free disk space for the separate demo.')
    stage=destination.with_name(destination.name+'.preparing')
    if stage.exists():raise ValueError('An unfinished installation exists. Choose another folder or retain it for inspection.')
    stage.mkdir()
    try:
        notify('Копирую компоненты «Сталкера»…')
        game=stage/'soc';game.mkdir()
        for archive in archives:shutil.copyfile(archive,game/archive.name)
        shutil.copytree(payload/'gamedata',game/'gamedata')
        shutil.copytree(payload/'bin',game/'bin_steve')
        shutil.copyfile(payload/'fsgame_demo.ltx',game/'fsgame_demo.ltx')
        native_profile=game/'_appdata_steve';native_profile.mkdir()
        (native_profile/'savedgames').mkdir()
        shutil.copyfile(payload/'user_ogsr.ltx',native_profile/'user_ogsr.ltx')
        notify('Подготавливаю Java и Minecraft…')
        shutil.copytree(java.parent.parent,stage/'java',ignore=shutil.ignore_patterns('*.log','*.jfr'))
        cache=stage/'components';cache.mkdir();profile=stage/'minecraft';(profile/'mods').mkdir(parents=True)
        versions=json.loads(fetch('https://launchermeta.mojang.com/mc/game/version_manifest_v2.json'))
        version=next(item for item in versions['versions'] if item['id']==MC_VERSION)
        raw=fetch(version['url'])
        if hashlib.sha1(raw).hexdigest()!=version['sha1']:raise ValueError('Minecraft version metadata checksum mismatch.')
        base=json.loads(raw)
        # The Fabric metadata fixes the loader version; no installer JAR is run.
        fabric=json.loads(fetch(f'https://meta.fabricmc.net/v2/versions/loader/{MC_VERSION}/{FABRIC_VERSION}/profile/json'))
        if fabric.get('inheritsFrom')!=MC_VERSION:raise ValueError('Unexpected Fabric profile.')
        libraries=[]
        native_dir=cache/'natives';native_dir.mkdir()
        for library in [*base['libraries'],*fabric['libraries']]:
            if not allowed(library):continue
            artifact=library.get('downloads',{}).get('artifact',{})
            relative=artifact.get('path') or maven_path(library['name'])
            target=cache/'libraries'/relative
            if not target.resolve().is_relative_to(cache):raise ValueError('Invalid library path.')
            url=artifact.get('url') or library.get('url','https://libraries.minecraft.net/').rstrip('/')+'/'+relative
            obtain(target,url,artifact.get('sha1'),minecraft_source/'libraries'/relative)
            libraries.append(target)
            if target.name.endswith('-natives-windows.jar'):
                with zipfile.ZipFile(target) as archive:
                    for name in archive.namelist():
                        if name.lower().endswith('.dll'):
                            # Modern LWJGL stores DLLs in windows/x64 subfolders.
                            # Extract only the basename from the x64 classifier JAR.
                            (native_dir/Path(name.replace('\\','/')).name).write_bytes(archive.read(name))
        client=base['downloads']['client'];client_source=minecraft_source/'versions/1.20.1/1.20.1.jar'
        if not client_source.exists():
            # A merged Fabric profile still uses the original Minecraft client JAR.
            for candidate in (minecraft_source/'versions').glob('*/*.jar'):
                if digest(candidate)==client['sha1']:client_source=candidate;break
        client_target=cache/'client.jar';obtain(client_target,client['url'],client['sha1'],client_source);libraries.append(client_target)
        # These four native fallback textures belong to the user's Minecraft.
        # They are generated locally, outside the redistributable payload.
        from legacy_assets import create_legacy_textures
        create_legacy_textures(client_target,game)
        notify('Проверяю ресурсы Minecraft…')
        index=base['assetIndex'];index_target=cache/'assets/indexes'/(index['id']+'.json')
        obtain(index_target,index['url'],index['sha1'],minecraft_source/'assets/indexes'/(index['id']+'.json'))
        objects=json.loads(index_target.read_text(encoding='utf-8'))['objects']
        def asset(value):
            relative='assets/objects/'+value[:2]+'/'+value
            obtain(cache/relative,'https://resources.download.minecraft.net/'+value[:2]+'/'+value,value,minecraft_source/relative)
        with ThreadPoolExecutor(max_workers=8) as downloads:
            for _ in downloads.map(asset,{entry['hash'] for entry in objects.values()}):pass
        shutil.copyfile(payload/'sitz.jar',profile/'mods/sitz.jar')
        shutil.copyfile(payload/'fabric-api.jar',profile/'mods/fabric-api.jar')
        (stage/'bridge').mkdir()
        game_language='en_us'
        options=minecraft_source/'options.txt'
        if options.exists():
            for line in options.read_text(encoding='utf-8',errors='replace').splitlines():
                if line.startswith('lang:') and re.fullmatch('[a-z_]+',line[5:]):game_language=line[5:]
        (profile/'options.txt').write_text(f'lang:{game_language}\nonboardAccessibility:false\npauseOnLostFocus:false\nrenderDistance:8\nsimulationDistance:8\n',encoding='utf-8')
        identity=bytearray(hashlib.md5(('OfflinePlayer:'+username).encode()).digest());identity[6]=(identity[6]&15)|48;identity[8]=(identity[8]&63)|128
        def portable(path):return '@ROOT@/'+str(path.relative_to(stage)).replace('\\','/')
        args=['-Xms256M','-Dstalkercraft.bridgeDirectory=@ROOT@/bridge','-Djava.library.path='+portable(native_dir),'-cp',';'.join(map(portable,libraries)),fabric['mainClass'],
              '--username',username,'--uuid',str(uuid.UUID(bytes=bytes(identity))),'--version','Steve in the Zone','--gameDir','@ROOT@/minecraft',
              '--assetsDir','@ROOT@/components/assets','--assetIndex',index['id'],'--accessToken','0','--userType','legacy','--versionType','release','--width','1280','--height','720']
        (stage/'prepared-java.args').write_text('\n'.join(json.dumps(arg,ensure_ascii=False) for arg in args),encoding='utf-8')
        config={'schema':2,'java':'java/bin/'+java.name,'profile':'minecraft','minecraftArgsFile':'prepared-java.args',
                'startupStatusFile':'bridge/demo-launch-status.ltx','bridgeDirectory':'bridge','createWorldIfMissing':True,'createNativeIfMissing':True,
                'existingMappingName':'Local\\StalkerCraft_v6','settings':{'language':language},
                'native':{'executable':'soc/bin_steve/xrEngine.exe','directory':'soc','arguments':['-nointro','-fsltx','fsgame_demo.ltx','-stalkercraft','-start','server(all/single/alife/new)','client(localhost)']}}
        (stage/'demo-launch.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
        # A private candidate application is copied; installed game data stays external to its bundle.
        shutil.copytree(payload/'app',stage/'app')
        if (payload/'notices').is_dir():shutil.copytree(payload/'notices',stage/'notices')
        (stage/'installation.json').write_text(json.dumps({'schema':1,'provider':'local-singleplayer','minecraft':MC_VERSION,'fabric':FABRIC_VERSION,'payload':manifest['files']},indent=2),encoding='utf-8')
        stage.rename(destination)
        notify('Установка завершена.')
        return destination/'demo-launch.json'
    except Exception:
        # Keep failed preparation inspectable. Never remove source games or saves.
        (stage/'FAILED.txt').write_text('Preparation did not complete. Source games and worlds were not modified.\n',encoding='utf-8')
        raise
