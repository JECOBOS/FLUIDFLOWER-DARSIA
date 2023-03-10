"""
Module containing objects to align images with a baseline image,
when restricted to a significant ROI. By this correction for drift
is taking care of.
"""

import copy
import json
from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np

import darsia


class DriftCorrection:
    """
    Class for drift correction of images wrt. a baseline image.
    """

    def __init__(
        self,
        base: Union[str, Path, np.ndarray, darsia.Image],
        config: Optional[dict] = None,
        roi: Optional[Union[np.ndarray, tuple, list]] = None,
    ) -> None:
        """
        Constructor for DriftCorrection.

        Args:
            base (str, Path, or array): path to baseline array, or array.
            config (dict, str, Path): config file for initialization of
                images.
            roi (2-tuple of slices or array): region of interest defining
                the considered area for detecting features and aligning
                images. Either as tuple of ranges, or array of points.
                Can also be provided in config; roi in config is
                prioritized.
        """

        # Read baseline image
        if isinstance(base, str) or isinstance(base, Path):
            base_BGR = cv2.imread(str(Path(base)), cv2.IMREAD_UNCHANGED)
            self.base = cv2.cvtColor(base_BGR, cv2.COLOR_BGR2RGB)
        elif isinstance(base, np.ndarray):
            self.base = np.copy(base)
        elif isinstance(base, darsia.Image):
            self.base = np.copy(base.img)
        else:
            raise ValueError("Data type for baseline image not supported.")

        # Cache config
        if config is not None:
            self.config = copy.deepcopy(config)
        else:
            self.config = {}

        # Cache ROI
        self.roi = None
        if "roi" in self.config:
            self.roi = darsia.bounding_box(np.array(self.config["roi"]))
        elif isinstance(roi, np.ndarray):
            self.roi = darsia.bounding_box(roi)
            self.config["roi"] = roi.tolist()
        elif isinstance(roi, list):
            # If a list is added as the roi, it is assumed that it comes from
            # the color correction roi and some padding might be needed in
            # order to apply the drift correction. Here 5% of the picture is
            # added as padding to the roi.
            self.roi = darsia.bounding_box(
                np.array(roi),
                padding=round(0.05 * self.base.shape[0]),
                max_size=[self.base.shape[0], self.base.shape[1]],
            )
            self.config["roi"] = darsia.bounding_box_inverse(self.roi).tolist()
        elif isinstance(roi, tuple):
            self.roi = roi
            self.config["roi"] = darsia.bounding_box_inverse(roi).tolist()

        # Define a translation estimator
        self.translation_estimator = darsia.TranslationEstimator()

    def __call__(self, img: np.ndarray, roi: Optional[tuple] = None) -> np.ndarray:
        """
        Main routine for aligning image with baseline image.

        Args:
            img (np.ndarray): input image, to be aligned.
            roi (2-tuple of slices, optional): ROI to be applied to img; if None
                the cached roi is used.

        Returns:
            np.ndarray: aligned image array.
        """
        # Define roi for source image. Let input argument be dominating over self.roi.
        roi_src = self.roi if roi is None else roi
        # Match image with baseline image
        return self.translation_estimator.match_roi(
            img_src=img, img_dst=self.base, roi_src=roi_src, roi_dst=self.roi
        )

    def write_config_to_file(self, path: Union[Path, str]) -> None:
        """
        Writes the config dictionary to a json-file.

        Arguments:
            path (Path): path to the json file
        """

        with open(Path(path), "w") as outfile:
            json.dump(self.config, outfile, indent=4)
