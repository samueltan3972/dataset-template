# Data Science Project Template (Dataset)

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Template repository for dataset. Focus on dataset only, like parent dataset without model training 'yet'.

## Sample Data
![Sample Data 1](assets/img/sample-data-1.jpg "Sample Data 1")

---

## Getting Started

### Prerequisite

* [Git](https://git-scm.com/downloads)
* [DVC](https://dvc.org/doc/install)

Below is for contributor:

* [Git LFS](https://git-lfs.com/)
* [Make for Ubuntu](https://www.geeksforgeeks.org/how-to-install-make-on-ubuntu/)
* [Make for Windows](https://stackoverflow.com/questions/32127524/how-to-install-and-use-make-in-windows)

### Usage
```bash
# To get all combined data
dvc get <repo-link> data/4-combined

# To get all processed data group by data source
dvc get <repo-link> data/3-processed

# To get processed data group of specific data source
dvc get <repo-link> data/3-processed/<option>
```

Currently, the available of option are:

* None

---

## Contribution Guidelines

All contribution to the dataset must follow the following rules:

* We do not care how the raw data looks like, but the processed data must follow the rules
* All the processed dataset must put under data/3-processed differentiate by the data source
* All the processed image must be rename using `generate_md5_file` from `src.utils`
    * The function can be imported with `from src.utils import generate_md5_file` after running `pip install -e .`
* All the processed data will be group in [data/3-processed](data/3-processed) folder, which can be obtain by `dvc pull`
* The processed data will follow the following structure:

```
└── data-source             <- The folder name represent the data source, change the folder name accordingly
    ├── images              <- Image folder
    └── processed_data.csv  <- Store all the attributes in csv file
```
* All the processed data will be combined in [data/4-combined](data/4-combined) folder.

#### Reference

* Refer to the [reference_pipeline.sh](notebooks/reference_pipeline.sh) or [reference_pipeline.ipynb](notebooks/reference_pipeline.ipynb) for Recommended Data Processing Pipeline.
* Refer to `processed_data_header` section in [config file](config/config.yaml) for allowed header in the processed dataset.
* Refer to [src](src/) for provided script and code for data processing.

### Installation
```bash
make create_environment
make install

# if the above is not working, then run the following command one by one
pipenv shell
python3 -m pip install -r requirements.txt
pre-commit install
git lfs install
dvc pull
```

---

### Scripts📜

#### 1. yolo_to_csv.py 💻

Extract metadata from YOLO format dataset into csv. The output of coordinate is xyxy where it is top left, and bottom right.

```sh
python src/yolo_to_csv.py -i <input_folder> -o [output.csv] -m [coordinate_mode: cxywh, xyxy, xywh] -c [config_file]

python3 src/yolo_to_csv.py -i data/1-raw/2024-04-24/ -o data/2-interim/2024-04-24/interim_data.csv -m xywh -c config/config.yaml
```

| Arguments         | Details               | Default           |
|-----------        |----------             |---------          |
| input_folder      | path of dataset       |                   |
| output_file       | path of output csv    |                   |
| coordinate_mode   | input coordinate mode | cxywh             |
| config_file       | path of config file   |                   |

### 2. annotate_image.py ✅

Application for annotate the image, based on the csv file generated from `yolo_to_csv.py`

```sh
python3 src/annotate_image.py [input_csv] -c [config_file]

python3 src/annotate_image.py data/2-interim/data-source/interim_data.csv -c config/config.yaml
```

Available Shortcut:

| Shortcut              | Action                |
|-----------            |----------             |
| Ctrl+Right, PageDown  | Next Image            |
| Ctrl+Left, PageUp     | Previous Image        |
| Ctrl+S, Enter         | Save Annotation       |
| Ctrl+Del              | Delete image          |
| Ctrl+F                | Go to row n           |
| Ctrl+R, Home          | Go to first unlabel   |
| Ctrl+W                | Quit                  |


### 3. interim_to_processed.py 💱

It provides a reference pipeline from interim to processed data.

* Rename image with new unique filename using md5
* Remove all attributes not in processed_data_header in config.yaml
* Move old image to new path
* Save the .csv

```sh
python3 src/interim_to_processed.py [csv_file] -o [output_folder] -c [config_file]

python3 src/interim_to_processed.py data/2-interim/data-source/interim_data.csv -o data/3-processed/data-source/images -c config/config.yaml
```

### 4. combine_csv.py 🔁

Combine CSV files and filter license plate if needed.

```sh
python3 src/combine_csv.py [list-csv-files or folder-that-contain-csv-files] -o [output_csv]

python3 src/combine_csv.py data/3-processed/ -o data/4-combined/processed_data.csv
```

### 5. copy_images.sh 📝

Copy all images in the directory (including all sub-folder) to destination

```sh
python3 src/copy_images.py [source] [dest]

bash src/copy_images.sh data/3-processed/ data/4-combined/images
```

---

### Project Organization

```
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── config               <- Folder for storing config file.
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for
│                         src and configuration for tools like black
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── src   <- Source code for use in this project.
```

--------

## Atribution

* Photo by Esther Simmendinger: https://www.pexels.com/photo/stunning-hill-of-seven-colors-in-humahuaca-argentina-29088845/
