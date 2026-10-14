"""Accept a live native New Game request; own the profile across both sessions."""
from contextlib import contextmanager
from pathlib import Path
import msvcrt,os,re

DIFFICULTIES={'gd_novice','gd_stalker','gd_veteran','gd_master'}


@contextmanager
def session_lock(profile):
    with (Path(profile)/'demo-session.lock').open('a+b') as handle:
        if os.fstat(handle.fileno()).st_size==0:handle.write(b'0');handle.flush()
        handle.seek(0)
        try:msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:raise ValueError('Этот профиль уже запущен. Закрой предыдущую сессию.')
        yield handle


def _fields(path,limit=1024):
    if path.resolve()!=path or path.is_symlink() or path.stat().st_size>limit:
        raise ValueError('Некорректный запрос новой игры.')
    fields={}
    for line in path.read_text(encoding='ascii').splitlines():
        key,sep,value=line.partition('=')
        if not sep or key in fields:raise ValueError('Некорректный запрос новой игры.')
        fields[key]=value
    return fields


def consume(config):
    profile=Path(config['profile'])
    bridge=Path(config.get('bridgeDirectory',str(profile.parent/'bridge')))
    path=bridge/'new-campaign.request'
    if not path.exists():return None
    if not config.get('createNativeIfMissing'):
        raise ValueError('Этот профиль не подготовлен для новой кампании.')
    request=_fields(path)
    identity=_fields(bridge/'native-identity.ltx')
    if (set(request)!={'protocol','session','generation','difficulty'} or request['protocol']!='1'
        or request['difficulty'] not in DIFFICULTIES or identity.get('protocol')!='1'
        or any(not re.fullmatch('[0-9]+',request[key]) or request[key]!=identity.get(key)
               for key in ['session','generation'])):
        raise ValueError('Запрос новой игры относится к другой сессии или повреждён.')
    path.unlink()
    return request['difficulty']


def consume_finished(config):
    """Only a current native after-credits event ends the owned two-game session."""
    profile=Path(config['profile'])
    bridge=Path(config.get('bridgeDirectory',str(profile.parent/'bridge')))
    path=bridge/'campaign-finished.request'
    if not path.exists():return False
    request=_fields(path)
    identity=_fields(bridge/'native-identity.ltx')
    if (set(request)!={'protocol','session','generation','action'} or request['protocol']!='1'
        or request['action']!='credits_finished' or identity.get('protocol')!='1'
        or any(not re.fullmatch('[0-9]+',request[key]) or request[key]!=identity.get(key)
               for key in ['session','generation'])):
        raise ValueError('Сообщение завершения кампании относится к другой сессии или повреждено.')
    path.unlink()
    return True
