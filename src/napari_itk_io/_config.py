from configparser import ConfigParser
from pathlib import Path

_ini = Path('~/.itk-io.ini').expanduser().absolute()
_settings = ConfigParser()

if _ini.exists():
    _settings.read(_ini)
else:
    default = dict(
        copy_metadata='y',
        flip_on_load='',
        flip_on_save='',
    )
    print(f'Writing configuration file at: {_ini}')
    _settings['DEFAULT'] = default
    _settings['CURRENT'] = dict()
    with open(_ini, 'w') as cf:
        _settings.write(cf)
