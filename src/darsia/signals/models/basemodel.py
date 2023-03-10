"""
Module containing abstract Model.
Models convert signals to data.

"""
import abc

import numpy as np


class Model:
    @abc.abstractmethod
    def __call__(self, img: np.ndarray) -> np.ndarray:
        """
        Translation of signal to data.
        """
        pass

    @abc.abstractmethod
    def calibrate(self) -> None:
        """
        Calibration routine of model.
        """
        pass
