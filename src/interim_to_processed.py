import argparse
import os
import shutil
from pathlib import Path

import colorama
import pandas as pd
from colorama import Fore

from src.utils import generate_md5_file, load_yaml_file

colorama.init()


def interim_to_processed(csv_file: str, output_folder: str, config_file: str = "config.yaml"):
    """It provides a reference pipeline from interim to processed data.

    Rename image with new unique filename using md5
    Remove all attributes not in processed_data_header in config.yaml
    Move old image to new path
    Save the .csv

    Args:
        csv_file (str): Interim csv file.
        output_folder (str): Output folder path.
        config_file (str, optional): Path to config file. Defaults to "config.yaml".
    """
    if not isinstance(output_folder, Path):
        output_folder = Path(output_folder)

    config = load_yaml_file(config_file)
    df = pd.read_csv(csv_file)

    old_image_path_col_name = config["yolo_to_csv_header"][0]
    old_image_name_col_name = config["yolo_to_csv_header"][1]

    # Rename image with new unique filename using md5
    for _, row in df.iterrows():
        full_old_image_path = Path(row[old_image_path_col_name]) / row[old_image_name_col_name]

        if full_old_image_path.exists():
            new_image_name = generate_md5_file(full_old_image_path) + full_old_image_path.suffix
            new_image_file = output_folder / new_image_name

            # Copy the image into new directory
            os.makedirs(os.path.dirname(new_image_file), exist_ok=True)
            shutil.copy(full_old_image_path, new_image_file)

            df.loc[df["old_image_name"] == row[old_image_name_col_name], ["new_image_name"]] = new_image_name

    # Remove all attributes not in processed_data_header in config
    df = df.filter(config["processed_data_header"])
    df.to_csv(output_folder / "processed_data.csv", index=False)

    print(Fore.GREEN + "Completed")
    print(Fore.BLUE + "Remember to update 3-processed/README.md and combine all the processed data")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process interim data to processed data. It provides a reference.")

    # Add arguments
    parser.add_argument("csv_file", type=str, help="Interim csv file")
    parser.add_argument("-o", "--output_folder", type=str, help="Output folder", required=True)
    parser.add_argument("-c", "--config", type=str, help="Config file path", default="config.yml")

    args = parser.parse_args()

    # Check that output file ends with .csv
    if not args.csv_file.endswith(".csv"):
        parser.error(Fore.RED + "Input file must end with .csv")

    interim_to_processed(args.csv_file, args.output_folder, args.config)
