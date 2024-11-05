import hashlib
from enum import Enum

import numpy as np
import yaml


class CoordinateMode(Enum):
    cxywh = 1  # center xy, width, height (Default for YOLO dataset)
    xyxy = 2  # top left, bottom right
    xywh = 3  # top left, width, height
    default = cxywh

    @classmethod
    def all_option(cls):
        return [mode.name for mode in list(CoordinateMode)]


def generate_md5_file(filename: str) -> str:
    """Generate md5 hash of the file.

    Args:
        filename(str, path): path to the file

    Returns:
        md5hash(str): string of the md5 hash
    """

    with open(filename, "rb") as f:
        md5hash = hashlib.md5(f.read())

    return md5hash.hexdigest()


def load_yaml_file(file: str) -> dict:
    """Load yaml file for config.

    Args:
        file (str): file path to yaml file

    Returns:
        dict: dict of loaded config
    """
    with open(file, "r") as file:
        return yaml.safe_load(file)


def cxywh2xyxy(x, one_dim=False):
    """
    Convert bounding box coordinates from (x, y, width, height) format to (x1, y1, x2, y2) format where (x1, y1) is the
    top-left corner and (x2, y2) is the bottom-right corner.

    Args:
        x (np.ndarray): The input bounding box coordinates in (x, y, width, height) format.
        one_dim (bool): If true, return bounding box in one dimension

    Returns:
        y (np.ndarray): The bounding box coordinates in [[x1, y1], [x2, y2]] format. (x1, y1, x2, y2) if one_dim = True.
    """
    if not isinstance(x, np.ndarray):
        x = np.array(x, dtype=int)
    if x.ndim != 1:
        x = x.flatten()

    assert x.shape[-1] == 4, f"input shape last dimension expected 4 but input shape is {x.shape}"
    y = np.empty(4)
    dw = x[2] / 2  # half-width
    dh = x[3] / 2  # half-height
    y[0] = x[0] - dw  # top left x
    y[1] = x[1] - dh  # top left y
    y[2] = x[0] + dw  # bottom right x
    y[3] = x[1] + dh  # bottom right y
    return y if one_dim else y.reshape(2, 2)


def xywh2xyxy(x, one_dim=False):
    """
    Convert bounding box coordinates from (x1, y1, width, height) format to (x1, y1, x2, y2) format where (x1, y1) is the
    top-left corner and (x2, y2) is the bottom-right corner.

    Args:
        x (np.ndarray): The input bounding box coordinates in (x, y, width, height) format.
        one_dim (bool): If true, return bounding box in one dimension

    Returns:
        y (np.ndarray): The bounding box coordinates in [[x1, y1], [x2, y2]] format. (x1, y1, x2, y2) if one_dim = True.
    """
    if not isinstance(x, np.ndarray):
        x = np.array(x, dtype=int)
    if x.ndim != 1:
        x = x.flatten()

    assert x.shape[-1] == 4, f"input shape last dimension expected 4 but input shape is {x.shape}"
    y = np.empty(4)
    y[0] = x[0]  # top left x
    y[1] = x[1]  # top left y
    y[2] = x[0] + x[2]  # bottom right x
    y[3] = x[1] + x[3]  # bottom right y
    return y if one_dim else y.reshape(2, 2)
