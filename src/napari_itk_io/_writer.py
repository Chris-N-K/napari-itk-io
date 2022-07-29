"""
This module is an example of a barebones writer plugin for napari.

It implements the Writer specification.
see: https://napari.org/plugins/stable/guides.html#writers

Replace code below according to your needs.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Any, Sequence, Tuple, Union
from pathlib import Path

import itk
import numpy as np

from ._utils import image_from_layer
from ._widgets import CopyMetaDialog
from ._config import _settings

__all__ = ['write_image', 'write_labels', 'write_multiple']

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_image(path: str, data: Any, meta: dict, **kwargs):
    if _settings.get('CURRENT', 'flip_on_save'):
        data = np.flip(data, axis=_settings.get('Current', 'flip_on_save'))
    if _settings.get('CURRENT', 'copy_metadata') and 'itk_metadata' not in meta['metadata']:
        dialog = CopyMetaDialog(meta['name'])
        if dialog.exec():
            ref_layer = dialog.viewer.layers[dialog.combobox.currentText()]
            meta['itk_metadata'] = ref_layer.metadata['itk_metadata']
            meta['scale'] = ref_layer.scale
            meta['translate'] = ref_layer.translate
    if 'ltype' in kwargs:
        ltype = kwargs['ltype']
    else:
        ltype = 'image'
    img = image_from_layer(data, meta, ltype)
    itk.imwrite(img, path)
    return path


def write_labels(path: str, data: Any, meta: dict):
    write_image(path, data, meta, ltype='labels')
    return path



def write_multiple(path: str, data: List[FullLayerData]):
    """Writes multiple layers of different types."""
    path = Path(path)
    spaths = []
    if path.exists():
        raise FileExistsError
    else:
        for (ldata, lmeta, ltype) in data:
            suffixes = path.suffixes
            if suffixes:
                save_path = ''.join([str(path), lmeta['name'], *suffixes])
            else:
                save_path = ''.join([str(path), lmeta['name'], _settings.get('CURRENT', 'save_format')])
            saved = write_image(save_path, ldata, lmeta, ltype=ltype)
            spaths.append(saved)
    return spaths
