###############################
# Reference pipeline - CLI way
###############################

# Step 1: Convert yolo (txt) dataset to csv
python3 src/yolo_to_csv.py -i data/1-raw/ -o data/2-interim/interim_data.csv -m xywh -c config/config.yaml

# Step 2: Annotate or verify the image
python3 src/annotate_image.py data/2-interim/interim_data.csv -c config/config.yaml

# Step 3: Process from interim (verified) data to processed data
# It make sure the processed_data follow the required format and rename the image with md5
python3 src/interim_to_processed.py data/2-interim/interim_data.csv -o data/3-processed/images -c config/config.yaml

# Step 4: Combine all processed data
python3 src/combine_csv.py data/3-processed/ -o data/4-combined/processed_data.csv
bash src/copy_images.sh data/3-processed/ data/4-combined/images
