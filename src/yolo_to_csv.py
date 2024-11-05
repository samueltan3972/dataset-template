import argparse
import os
from pathlib import Path

import colorama
import pandas as pd
import yaml
from colorama import Fore

from src.utils import CoordinateMode, cxywh2xyxy, xywh2xyxy

colorama.init()


def get_csv_header(config_file: str) -> list:
    with open(config_file, "r") as file:
        return yaml.safe_load(file)["yolo_to_csv_header"]


def yolo_to_csv(
    input_folder: str,
    output_file: str,
    mode: CoordinateMode = CoordinateMode.cxywh,
    csv_header: list = None,
):
    """
    Extract metadata from YOLO format dataset into csv.
    The output of coordinate is xyxy where it is top left, and bottom right.

    Args:
        input_folder(str): path to input folder
        output_file(str): path to output file, must be .csv file
        mode(CoordinateMode): mode of input dataset label coordinate, default to cxywh
        csv_header(list): list of header for output csv
    """
    if not isinstance(input_folder, Path):
        input_folder = Path(input_folder)

    data = []

    # Traverse the folder structure
    for file in input_folder.glob("**/*.txt"):
        # Read the file contents
        with open(file, "r") as f:
            content = f.read().strip().split("\t")

        # Process coordinate according to its input
        if mode is not CoordinateMode.xyxy:
            coordinate = content[1:5]

            if mode is CoordinateMode.cxywh:
                coordinate = cxywh2xyxy(coordinate, True)
            elif mode is CoordinateMode.xywh:
                coordinate = xywh2xyxy(coordinate, True)

            content[1:5] = coordinate.astype(int).tolist()

        content.insert(0, file.parent.resolve())
        data.append(content)

    # Save to csv
    try:
        df = pd.DataFrame(data, columns=csv_header)
    except ValueError:
        raise ValueError(f"Invalid csv header in config, csv_header={csv_header}")

    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract metadata from yolo dataset to csv.")

    # Add arguments
    parser.add_argument("-i ", "--input_folder", type=str, help="Input folder path", required=True)
    parser.add_argument("-o", "--output_file", type=str, help="Output file name (csv)", required=True)
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        help=f"Input label coordinate mode. (default: %(default)s)",
        choices=CoordinateMode.all_option(),
        default=CoordinateMode.default.name,
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Config file path",
        default="config.yml",
    )

    args = parser.parse_args()

    # Check that output file ends with .csv
    if not args.output_file.endswith(".csv"):
        parser.error(Fore.RED + "Output file must end with .csv")

    # Check if the input folder exists
    if not os.path.exists(args.input_folder):
        parser.error(Fore.RED + f"Folder {args.input_folder} NOT FOUND")

    try:
        yolo_to_csv(
            args.input_folder,
            args.output_file,
            mode=CoordinateMode[args.mode],
            csv_header=get_csv_header(args.config),
        )
    except:
        import traceback

        parser.error(Fore.RED + traceback.format_exc())
