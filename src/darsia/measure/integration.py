"""
Module collecting tools for geometric integration,
taking into account width, height and depth of pixels.

"""

from typing import Optional, Union

import numpy as np

import darsia

# TODO 3d?


class Geometry:
    """
    Class containing information of the geometry.

    Also allows for geometrical integration.

    Example:

    dimensions = {"width": 1., "height": 2., "depth": 0.1}
    shape = (20,10)
    geometry = darsia.Geometry(shape, **dimensions)

    """

    def __init__(self, shape: tuple[int], **kwargs) -> None:

        # Determine number of voxels in each dimension
        Ny, Nx = shape[:2]
        Nz = 1 if len(shape) < 3 else shape[2]

        # Cache
        self.Nx = Nx
        self.Ny = Ny
        self.Nz = Nz

        # Define width, height and depth of each voxel
        self.voxel_width = kwargs.get("voxel_width", None)
        if self.voxel_width is None:
            self.voxel_width = kwargs.get("width") / Nx

        self.voxel_height = kwargs.get("voxel_height", None)
        if self.voxel_height is None:
            self.voxel_height = kwargs.get("height") / Ny

        self.voxel_depth = kwargs.get("voxel_depth", None)
        if self.voxel_depth is None:
            self.voxel_depth = kwargs.get("depth") / Nz

        # Determine effective pixel and voxel measures
        self.voxel_area = np.multiply(self.voxel_width, self.voxel_height)
        self.voxel_volume = (
            self.voxel_area
            if self.voxel_depth is None
            else np.multiply(self.voxel_area, self.voxel_depth)
        )

    def integrate(
        self, data: Union[darsia.Image, np.ndarray], mask: Optional[np.ndarray] = None
    ) -> float:
        """
        Integrate data over the entire geometry.
        """

        # Check compatibility of data formats
        if isinstance(self.voxel_area, np.ndarray):
            assert data.shape[:2] == self.voxel_area.shape[:2]
            # TODO apply cv2.resize with the inter_area option
            return np.sum(np.multiply(self.voxel_volume, data))
        else:
            # TODO 3d
            Ny_data, Nx_data = data.shape[:2]
            rescaled_voxel_volume = (
                self.voxel_volume * self.Nx / Nx_data * self.Ny / Ny_data
            )
            return rescaled_voxel_volume * np.sum(data)


class PorousGeometry(Geometry):
    """
    Class containing information of a porous geometry.

    Also allows for geometrical integration over pore space.

    Example:

    asset = {"porosity": 0.2, "width": 1., "height": 2., "depth": 0.1}
    shape = (20,10)
    geometry = darsia.PorousGeometry(shape, **asset)

    """

    def __init__(self, shape: np.ndarray, **kwargs) -> None:

        super().__init__(shape, **kwargs)
        self.porosity = kwargs.get("porosity")

        # Determine effective pixel and voxel measures
        self.voxel_area = np.multiply(self.voxel_area, self.porosity)
        self.voxel_volume = np.multiply(self.voxel_volume, self.porosity)


def integrate(
    data: Union[darsia.Image, np.ndarray],
    geometry: Optional[Geometry] = None,
    mask: Optional[np.ndarray] = None,
) -> float:
    """
    Integrate data over the entire geometry.
    """

    # TODO extend to darsia.Image
    if isinstance(data, np.ndarray):
        assert geometry is not None

    # Check compatibility of data formats
    if isinstance(geometry.voxel_area, np.ndarray):
        assert data.shape[:2] == geometry.voxel_area.shape[:2]

    # Perform weighted sum
    return geometry.integrate(data)
