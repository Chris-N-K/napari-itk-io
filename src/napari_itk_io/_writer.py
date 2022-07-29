"""
This module provides itk-based file writing functionality in a writer plugin for napari.

"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Any, Sequence, Tuple, Union
from pathlib import Path

import itk
import numpy as np

from ._utils import image_from_layer
from ._widgets import CopyMetaDialog
from ._config import _settings

__all__ = ['write_nifti']

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_nifti(path: str, data: List[FullLayerData]):
    """Writes image or labels layer(s) to file."""
    save_paths = []
    path = Path(path)
    for (data, meta, layer_type) in data:
        save_path = ''.join([path.parent, path.stem, meta['name'], *path.suffixes])

        if _settings.get('CURRENT', 'flip_on_save'):
            data = np.flip(data, axis=int(_settings.get('CURRENT', 'flip_on_save')))
        if _settings.get('CURRENT', 'copy_metadata') == 'y' and 'itk_metadata' not in meta['metadata']:
            dialog = CopyMetaDialog(meta['name'])
            if dialog.exec():
                ref_layer = dialog.viewer.layers[dialog.combobox.currentText()]
                meta['itk_metadata'] = ref_layer.metadata['itk_metadata']
                meta['scale'] = ref_layer.scale
                meta['translate'] = ref_layer.translate

        img = image_from_layer(data, meta, layer_type)
        itk.imwrite(img, save_path)
        save_paths.append(path)

    return save_paths
