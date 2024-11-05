#!/bin/bash

RED='\033[0;31m'
NC='\033[0m' # No Color
YELLOW='\033[1;33m'

# Function to display usage
usage() {
    echo "Usage: $0 <input_directory> <output_directory>"
    echo "Example: $0 /home/user/documents /data"
    exit 1
}

# Check if input directory is provided
if [ $# -ne 1 ]; then
    usage
fi

if [ $# -ne 2 ]; then
    usage
fi

# Check if input directory exists
if [ ! -d "$1" ]; then
    echo "Error: Directory '$1' does not exist"
    exit 1
fi

# Convert arguement to absolute path
input_dir=$(realpath "$1")
output_dir=$(realpath "$2")

# Check if output directory exists, if not create it
if [ ! -d "$output_dir" ]; then
    echo "Creating output directory..."
    sudo mkdir -p $output_dir
    sudo chmod 777 $output_dir
fi

# Initialize counter for copied files
count=0
echo "Searching for Image files in: $input_dir"

while read -r file; do
    # Get the filename without the path
    filename=$(basename "$file")

    # Check if file already exists in destination
    if [ -f "$output_dir/$filename" ]; then
        echo -e "${YELLOW}Warning: $filename already exists in $input_dir, skip the file${NC}"
        continue
    fi

    # Copy the file
    if cp "$file" "$output_dir/$filename"; then
        echo "Copied: $file -> $output_dir/$filename"
        ((count++))
    else
        echo -e "${RED}Error copying $file${NC}"
    fi
done < <(find "$input_dir" -type f -iregex '.*\.\(jpg\|jpeg\|png\)$')

echo "Operation complete. $count Image files copied to $output_dir directory."
