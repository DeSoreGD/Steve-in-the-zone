"""Check prepared dependencies before starting either game; never log session arguments."""
from pathlib import Path
import json
import zipfile

def validate_prepared(config):
    source=Path(config['minecraftArgsFile']).read_text(encoding='utf-8-sig').splitlines()
    args=[json.loads(line) for line in source if line.strip()]
    def option(name):
        try:return args[args.index(name)+1]
        except (ValueError,IndexError):raise ValueError('Incomplete Minecraft configuration: '+name)
    classpath=option('-cp').split(';')
    if not classpath or any(not Path(item).is_file() for item in classpath):
        raise ValueError('Minecraft libraries are missing. Prepare or repair this demo profile.')
    assets=Path(option('--assetsDir'))
    if not (assets/'indexes'/(option('--assetIndex')+'.json')).is_file() or not (assets/'objects').is_dir():
        raise ValueError('Minecraft assets are missing. Complete the component download first.')
    native_dirs=[value.split('=',1)[1] for value in args if value.startswith('-Djava.library.path=')]
    if not native_dirs or not (Path(native_dirs[0])/'glfw.dll').is_file():
        raise ValueError('Minecraft Windows native libraries are missing.')
    profile=Path(config['profile'])
    if not (profile/'mods/fabric-api.jar').is_file():raise ValueError('Fabric API is missing in this demo profile.')
    game=Path(config['native']['directory'])
    for item in config['native']['arguments']:
        if any(flag in item for flag in ('-stalkercraft-combatcheck','-stalkercraft-meshcheck','-stalkercraft-levelcheck')) and not config.get('testProfile'):
            raise ValueError('Test-only game flags are present in the playable profile.')
    if config.get('testProfile'):return
    arguments=config['native']['arguments']
    if '-fsltx' not in arguments:raise ValueError('S.T.A.L.K.E.R. filesystem configuration is missing.')
    fs=game/arguments[arguments.index('-fsltx')+1]
    if not fs.is_file():raise ValueError('S.T.A.L.K.E.R. filesystem configuration is missing.')
    if not list(game.glob('gamedata.db*')):raise ValueError('S.T.A.L.K.E.R. game archives are missing.')
    for file in ('mc_lab.sav',):
        if not (game/'_appdata_steve/savedgames'/file).is_file() and not config.get('createNativeIfMissing'):
            raise ValueError('The Cordon demo scene is missing. Prepare the native scene first.')
    for file in ('OpenAL32.dll','dbghelp.dll'):
        if not (Path(config['native']['executable']).parent/file).is_file():
            raise ValueError('S.T.A.L.K.E.R. runtime components are missing: '+file)
    if config.get('schema')==2 and not (Path(config['native']['executable']).parent/'vcomp140.dll').is_file():
        raise ValueError('OpenMP runtime is missing. Extract a fresh complete installation package.')
