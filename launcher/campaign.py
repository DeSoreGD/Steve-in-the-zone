"""Restore an explicitly committed native/Minecraft pair in the owned demo profile."""
from pathlib import Path
import json
import re
import shutil
import time
import stat

IDENTITY=re.compile(r'[0-9]+_[0-9]+\Z')
RESERVE_BYTES=256*1024*1024

def safe_tree(path):
    """Reject symlinks and Windows junctions before copying or pruning a save."""
    path=Path(path)
    for item in (path,*path.rglob('*')):
        value=item.lstat()
        if item.is_symlink() or getattr(value,'st_file_attributes',0)&0x400:
            raise ValueError('Linked file in campaign storage.')
        if not (stat.S_ISDIR(value.st_mode) or stat.S_ISREG(value.st_mode)):
            raise ValueError('Special file in campaign storage.')

def tree_bytes(path):
    safe_tree(path)
    return sum(item.stat().st_size for item in Path(path).rglob('*') if item.is_file())

def require_space(target,amount):
    target=Path(target)
    while not target.exists():target=target.parent
    if shutil.disk_usage(target).free < amount+RESERVE_BYTES:
        raise OSError('Not enough free space for a complete paired save; existing saves retained.')

def manifest_at(campaign):
    manifest=json.loads((campaign/'latest.json').read_text(encoding='utf-8'))
    checkpoint=manifest.get('checkpoint','');stage=manifest.get('stage','')
    if manifest.get('schema')!=1 or not IDENTITY.fullmatch(checkpoint) or stage not in ('source','destination'):
        raise ValueError('Invalid campaign checkpoint manifest.')
    if manifest.get('native_save')!=f'sc_{checkpoint}_{stage}':
        raise ValueError('Native checkpoint identity does not match.')
    return manifest

def complete_pair(pair,checkpoint,stage):
    files=(pair/'native.sav',pair/'native.ready',pair/'minecraft.ready',pair/'minecraft/level.dat')
    if not all(item.is_file() for item in files):return False
    lines=(pair/'native.ready').read_text(encoding='utf-8').splitlines()
    return bool(lines) and lines[0]==f'sc_{checkpoint}_{stage}'

def remove_owned_tree(path,parent):
    # One native filesystem operation; never follow junctions out of the profile.
    path=Path(path);parent=Path(parent).resolve()
    if path.resolve().parent!=parent or path.resolve()==parent:
        raise ValueError('Campaign cleanup target escaped its parent.')
    safe_tree(path)
    shutil.rmtree(path)

def prune_campaign(profile,campaign,keep=3):
    """Call with both games stopped. Preserve latest plus two recovery pairs.

    Incomplete/unknown directories are retained for diagnosis, never guessed away.
    """
    if keep<2:raise ValueError('At least two recovery checkpoints required.')
    profile=Path(profile).resolve();campaign=Path(campaign).resolve()
    if not (campaign/'latest.json').exists():return []
    manifest=manifest_at(campaign);latest=manifest['checkpoint'];stage=manifest['stage']
    checkpoints=campaign/'checkpoints'
    if checkpoints.resolve().parent!=campaign:raise ValueError('Linked campaign checkpoint root.')
    safe_tree(checkpoints)
    if not complete_pair(checkpoints/latest/stage,latest,stage):
        raise ValueError('Incomplete latest pair; cleanup refused.')
    completed=[]
    for item in checkpoints.iterdir():
        if not item.is_dir() or not IDENTITY.fullmatch(item.name):continue
        pairs=[item/s for s in ('source','destination') if complete_pair(item/s,item.name,s)]
        if any((item/s).exists() and not complete_pair(item/s,item.name,s) for s in ('source','destination')):
            continue  # A source may be valid while its failed destination needs diagnosis.
        if pairs:completed.append((max((pair/'native.ready').stat().st_mtime_ns for pair in pairs),item))
    completed.sort(key=lambda value:value[0],reverse=True)
    retain={latest}
    for _,item in completed:
        if len(retain)>=keep:break
        retain.add(item.name)
    # Manual/quicksave slots are user-owned checkpoints, not rotating archives.
    slots=campaign/'slots'
    if slots.exists():
        safe_tree(slots)
        for slot in slots.glob('*.json'):
            if not re.fullmatch(r'(?:[0-9a-f]{2}){1,220}\.json',slot.name):raise ValueError('Invalid paired save slot.')
            selected=json.loads(slot.read_text(encoding='utf-8'))
            checkpoint=selected.get('checkpoint','');selected_stage=selected.get('stage','')
            if selected.get('schema')!=1 or not IDENTITY.fullmatch(checkpoint) or selected_stage not in ('source','destination') or selected.get('native_save')!=f'sc_{checkpoint}_{selected_stage}' or not complete_pair(checkpoints/checkpoint/selected_stage,checkpoint,selected_stage):
                raise ValueError('Incomplete named paired save; cleanup refused.')
            retain.add(checkpoint)
    removed=[]
    for _,item in completed:
        if item.name not in retain:
            remove_owned_tree(item,checkpoints);removed.append(item.name)
    saves=profile/'saves'
    backups=sorted((item for item in saves.glob('.before-restore-*')
                    if item.is_dir() and re.fullmatch(r'\.before-restore-[0-9]+',item.name)),
                   key=lambda item:int(item.name.rsplit('-',1)[1]),reverse=True)
    for item in backups[2:]:
        remove_owned_tree(item,saves);removed.append(item.name)
    return removed

def native_saves(settings):
    game=Path(settings['directory']).resolve()
    args=settings['arguments']
    if '-fsltx' not in args:raise ValueError('Native filesystem configuration missing.')
    config=(game/args[args.index('-fsltx')+1]).resolve()
    aliases={}
    for line in config.read_text(encoding='utf-8-sig').splitlines():
        if '=' not in line:continue
        key,value=line.split('=',1);parts=[part.strip() for part in value.split('|')]
        if len(parts)>=3:aliases[key.strip()]=parts[2:]
    def resolve(key,seen=()):
        if key=='$fs_root$':return game
        if key in seen or key not in aliases:raise ValueError('Invalid native save alias.')
        parts=aliases[key];base=resolve(parts[0],(*seen,key)) if parts[0].startswith('$') else Path(parts[0])
        for part in parts[1:]:base=base/part.replace('\\','/').rstrip('/')
        return base.resolve()
    return resolve('$game_saves$')

def restore_latest(profile,settings,campaign):
    profile=Path(profile).resolve();campaign=Path(campaign).resolve()
    latest=campaign/'latest.json'
    if not latest.exists():return None
    manifest=manifest_at(campaign)
    checkpoint=manifest.get('checkpoint','');stage=manifest.get('stage','')
    if manifest.get('schema')!=1 or not IDENTITY.fullmatch(checkpoint) or stage not in ('source','destination'):
        raise ValueError('Invalid campaign checkpoint manifest.')
    expected=f'sc_{checkpoint}_{stage}'
    if manifest.get('native_save')!=expected:raise ValueError('Native checkpoint identity does not match.')
    pair=campaign/'checkpoints'/checkpoint/stage
    if pair.resolve()!=pair:raise ValueError('Symlink in campaign checkpoint path.')
    world_source=pair/'minecraft'
    if not all(path.is_file() for path in (pair/'native.sav',pair/'native.ready',pair/'minecraft.ready',world_source/'level.dat')):
        raise ValueError('Incomplete paired checkpoint; refusing to load half of the campaign.')
    if (pair/'native.ready').read_text(encoding='utf-8').splitlines()[0]!=expected:
        raise ValueError('Native checkpoint marker does not match.')
    saves=profile/'saves';saves.mkdir(exist_ok=True)
    world=saves/'Stalker mirror';staging=saves/f'.restore-{checkpoint}-{stage}'
    if world.is_symlink() or staging.exists():raise ValueError('World restore path is busy or linked.')
    for path in world_source.rglob('*'):
        if path.is_symlink():raise ValueError('Linked file in paired Minecraft checkpoint.')
    safe_tree(pair)
    native_dir=native_saves(settings)
    world_size=tree_bytes(world_source);native_size=(pair/'native.sav').stat().st_size
    # The two games may live on different drives. Check each before any copy.
    require_space(saves,world_size+native_size)
    require_space(native_dir,native_size)
    try:
        shutil.copytree(world_source,staging)
        native_dir.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(pair/'native.sav',native_dir/f'{expected}.sav')
    except Exception:
        if staging.exists() and staging.resolve().parent == saves.resolve():
            shutil.rmtree(staging)
        raise
    backup=saves/f'.before-restore-{time.time_ns()}'
    # Keep a recoverable prior working save. All mutations stay in this profile.
    if world.exists():world.rename(backup)
    try:staging.rename(world)
    except OSError:
        if backup.exists():backup.rename(world)
        raise
    return expected
