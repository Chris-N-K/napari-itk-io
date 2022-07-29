try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._config import _settings, _ini
from ._reader import napari_get_reader
from ._writer import *
from ._widgets import *
from ._utils import *

__config__ = _ini
