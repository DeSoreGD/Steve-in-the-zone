"""Idle-only paired reset by rename, with recoverable backups and a crash journal."""
from pathlib import Path
import ctypes
import json
import msvcrt
import os
import time


def locations(config):
    from campaign import native_saves
    root=Path(config['installationRoot']).resolve()
    profile=Path(config['profile']).resolve()
    targets=[profile/'saves/Stalker mirror',profile/'campaign',native_saves(config['native'])]
    for target in targets:
        if not target.is_relative_to(root) or target.resolve()!=target:
            raise ValueError('Reset requires an owned, unlinked demo installation.')
        if target.exists():
            for child in target.rglob('*'):
                if child.is_symlink() or child.resolve()!=child:
                    raise ValueError('Linked files cannot be reset automatically.')
    return root,profile,targets


def journal_write(path,data):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data,indent=2),encoding='utf-8')
    temporary.replace(path)


def recover_reset(config):
    root=Path(config['installationRoot']).resolve()
    journal=root/'reset-journal.json'
    if not journal.exists():return
    root,profile,targets=locations(config)
    data=json.loads(journal.read_text(encoding='utf-8'))
    identity=data.get('identity','')
    if not identity.isdigit():raise ValueError('Invalid reset journal.')
    backup=root/'backups'/('reset-'+identity)
    if backup.resolve()!=backup:raise ValueError('Linked reset backup.')
    if data.get('phase')=='committed':journal.unlink();return
    for index,target in reversed(list(enumerate(targets))):
        saved=backup/str(index)
        if saved.exists():
            if target.exists():
                # Keep any interrupted new world too; never delete either copy.
                target.rename(backup/('interrupted-'+str(index)))
            target.parent.mkdir(parents=True,exist_ok=True)
            saved.rename(target)
    journal.unlink()


def reset_demo(config,*,_session_lock=None):
    if not config.get('createNativeIfMissing'):
        raise ValueError('This profile has not been prepared for a fresh native scene.')
    root,profile,targets=locations(config)
    lock=_session_lock if _session_lock is not None else (profile/'demo-session.lock').open('a+b')
    try:
        if _session_lock is None:
            lock.seek(0)
            if os.fstat(lock.fileno()).st_size==0:lock.write(b'0');lock.flush()
            lock.seek(0)
            try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
            except OSError:raise ValueError('Close the demo before resetting its world.')
        elif Path(lock.name).resolve()!=profile/'demo-session.lock':
            raise ValueError('Session lock belongs to another profile.')
        kernel=ctypes.windll.kernel32
        kernel.OpenFileMappingW.argtypes=(ctypes.c_ulong,ctypes.c_bool,ctypes.c_wchar_p)
        kernel.OpenFileMappingW.restype=ctypes.c_void_p
        kernel.CloseHandle.argtypes=(ctypes.c_void_p,)
        handle=kernel.OpenFileMappingW(4,False,config.get('existingMappingName','Local\\StalkerCraft_v6'))
        if handle:
            kernel.CloseHandle(handle)
            raise ValueError('Close S.T.A.L.K.E.R. before resetting the demo.')
        recover_reset(config)
        identity=str(time.time_ns());backup=root/'backups'/('reset-'+identity)
        if (root/'backups').exists() and (root/'backups').resolve()!=root/'backups':
            raise ValueError('Linked backup directory.')
        backup.mkdir(parents=True)
        journal=root/'reset-journal.json'
        journal_write(journal,{'schema':1,'identity':identity,'phase':'moving'})
        try:
            for index,target in enumerate(targets):
                if target.exists():target.rename(backup/str(index))
            from create_world import create_demo_world
            create_demo_world(targets[0],config.get('settings',{}).get('gameMode','survival'))
            targets[1].mkdir();targets[2].mkdir(parents=True)
            journal_write(journal,{'schema':1,'identity':identity,'phase':'committed'})
            journal.unlink()
        except Exception:
            recover_reset(config)
            raise
        (backup/'README.txt').write_text('Paired reset backup: 0 = Minecraft world, 1 = campaign checkpoints, 2 = native saves.\n',encoding='utf-8')
        return backup
    finally:
        if _session_lock is None:lock.close()
