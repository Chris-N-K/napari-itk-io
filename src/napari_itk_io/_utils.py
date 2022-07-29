import napari
import itk
import numpy as np

__all__ = ["image_layer_from_image", "image_from_layer"]


def image_layer_from_image(image):
    """Convert an itk.Image to a napari.layers.Image."""
    rgb = False
    if isinstance(image, itk.Image):
        PixelType = itk.template(image)[1][0]
        if PixelType is itk.RGBPixel[itk.UC] or PixelType is itk.RGBAPixel[itk.UC]:
            rgb = True

    metadata = dict(image)
    scale = image["spacing"]
    translate = image["origin"]
    # Todo: convert the rotation matrix to angles, in degrees
    #rotate = image['direction']
    # https://github.com/InsightSoftwareConsortium/itk-napari-conversion/issues/7

    data = itk.array_view_from_image(image)
    image_layer = napari.layers.Image(
        data, rgb=rgb, metadata={'itk_metadata': metadata}, scale=scale, translate=translate,
    )
    return image_layer


def image_from_layer(data, meta, ltype):
    """Convert a napari.layers.Image to an itk.Image."""
    if ltype == 'labels':
        data = data.astype(np.int16)
        image = itk.image_view_from_array(data)
    elif meta['rgb'] and data.shape[-1] in (3, 4):
        if data.shape[-1] == 3:
            PixelType = itk.RGBPixel[itk.UC]
        else:
            PixelType = itk.RGBAPixel[itk.UC]
        image = itk.image_view_from_array(data, PixelType)
    else:
        image = itk.image_view_from_array(data)

    if meta['metadata'] is not None:
        try:
            for k, v in meta['metadata']['itk_metadata'].items():
                image[k] = v
        except KeyError:
            pass

    if meta['scale'] is not None:
        image["spacing"] = np.abs(np.asarray(meta['scale']).astype(np.float64))

    if meta['translate'] is not None:
        image["origin"] = np.asarray(meta['translate']).astype(np.float64)

    return image
