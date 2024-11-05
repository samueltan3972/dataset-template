import argparse
import sys
from pathlib import Path

import colorama
import pandas as pd
from colorama import Fore

colorama.init()


def filter_lp(data: pd.DataFrame) -> pd.DataFrame:
    # REGEX Filters
    regex_filters = ["^[A-Z]+[0-9]+[A-Z]*$", "^CANNOT$"]
    final_regex = f"({'|'.join([f'({regex})' for regex in regex_filters])})"

    temp_df = data[data["lp"] == "CANNOT"]
    df = data[data["lp"] != "CANNOT"]

    df = df.drop_duplicates(subset=["lp"])
    df = pd.concat([df, temp_df])

    return df[df["lp"].str.match(final_regex)]


def combine_csv(csv_files: list[str], output_file: str, filter: bool = False):
    """Combine all csv files input one csv file."""

    if not isinstance(output_file, Path):
        output_file = Path(output_file)

    # Initialize the full DataFrame
    df_full = pd.DataFrame()

    # Combine csv files
    for csv_file in csv_files:
        try:
            data = pd.read_csv(csv_file)
            print(f"Original {csv_file}: {data.shape}")
        except FileNotFoundError:
            print(f"File {csv_file} NOT FOUND")
            sys.exit(1)

        if filter:
            data = filter_lp(data)  # fmt: skip

        df_full = pd.concat([df_full, data])

    print(f"New: {df_full.shape}")
    print(f"File saved as {output_file}")
    df_full.to_csv(output_file, index=False)


if __name__ == "__main__":
    # fmt: off
    parser = argparse.ArgumentParser(
        description="Combine CSV files and filter license plate if needed."
    )

    parser.add_argument("csv_files", nargs="+", help="List of input folder or CSV files to combine")
    parser.add_argument("-o", "--output_file", type=str, help="Output file path", required=True)
    parser.add_argument("--filter_lp", action='store_true', help="Whether to filter license plate")
    # fmt: on

    # Parse the arguments
    args = parser.parse_args()

    # Check provided arguments are csv file
    if not args.output_file.endswith(".csv"):
        parser.error(Fore.RED + "Output file must end with .csv")

    csv_list = []

    for input in args.csv_files:
        if not input.endswith(".csv"):
            csv_list.extend(list(Path(input).glob("**/*.csv")))
        else:
            csv_list.append(input)

    combine_csv(csv_list, args.output_file, args.filter_lp)
