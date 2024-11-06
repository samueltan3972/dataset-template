import argparse
import os
from pathlib import Path
from tkinter import BooleanVar, StringVar, Tk, messagebox, simpledialog
from tkinter.ttk import Button, Entry, Label

import colorama
import numpy as np
import pandas as pd
import yaml
from colorama import Fore
from PIL import Image, ImageDraw, ImageTk
from ttkwidgets.autocomplete import AutocompleteCombobox

colorama.init()


class ImageAnnotatorApp:
    def __init__(self, csv_file, config_file: str = "config.yml"):
        self.csv_file = csv_file
        self.data = pd.read_csv(csv_file)

        if "processed" not in self.data.columns:
            self.data["processed"] = False

        self.index = -1

        # Load Config
        self.config = {}

        if config_file is not None:
            with open(config_file, "r") as file:
                self.config = yaml.safe_load(file)

        # Initialize UI component
        self.root = Tk()
        self.root.title("Image Annotator")
        self.image_label = Label(self.root)
        self.lp_image_label = Label(self.root)
        self.resampled_lp_image_label = Label(self.root)
        self.status_label = Label(self.root, text="Status", justify="center")

        # Initialize tkinter variables
        self.lp_var = StringVar()
        self.make_var = StringVar()
        self.type_var = StringVar()
        self.colour_var = StringVar()
        self.isback_var = BooleanVar()
        self.env_var = StringVar()

        # Option
        self.vehicle_makes = self.config["vehicle_makes"]
        self.vehicle_types = self.config["vehicle_types"]
        self.vehicle_colors = self.config["vehicle_colors"]
        self.environment = self.config["environment"]
        self.bool_option = (True, False)

    def start(self):
        # Setup UI components
        self.__setup_ui()
        self.__setup_keybind()

        # Start from the first unprocessed image
        self.__start_from_first_unprocessed()
        self.root.mainloop()

    def __setup_ui(self):
        # Image display area
        self.image_label.grid(columnspan=2, padx=10, pady=10)

        self.root.call("grid", self.lp_image_label, self.resampled_lp_image_label)  # fmt: skip

        # Status label
        self.status_label.grid(columnspan=2, padx=10, pady=10)

        # # Entry fields for annotation
        self.__create_entry("License Plate (lp):", self.lp_var)
        self.__create_combobox("Make:", self.make_var, self.vehicle_makes)
        self.__create_combobox("Type:", self.type_var, self.vehicle_types)
        self.__create_combobox("Colour:", self.colour_var, self.vehicle_colors)
        self.__create_combobox("isBack:", self.isback_var, self.bool_option, False)
        self.__create_combobox("environment:", self.env_var, self.environment, self.environment[0])

        # Control buttons
        Button(self.root, text="Update", command=self.__update_entry).grid(column=0, columnspan=2, pady=10)
        self.root.call(
            "grid",
            Button(self.root, text="Previous", command=self.__load_previous_image),
            Button(self.root, text="Next", command=self.__load_next_image),
            "-padx",
            "10",
            "-pady",
            "10",
        )
        self.root.call(
            "grid",
            Button(self.root, text="Go to Row N", command=self.__go_to_row_n),
            Button(
                self.root,
                text="Go to First Unprocessed",
                command=self.__start_from_first_unprocessed,
            ),
            "-padx",
            "10",
            "-pady",
            "10",
        )

    def __setup_keybind(self):
        # Update and delete entry
        self.root.bind("<Return>", lambda event: self.__update_entry())
        self.root.bind("<Control-s>", lambda event: self.__update_entry())
        self.root.bind("<Control-Delete>", lambda event: self.__delete_entry())

        # Navigation
        self.root.bind("<Control-Right>", lambda event: self.__load_next_image())
        self.root.bind("<Next>", lambda event: self.__load_next_image())
        self.root.bind("<Control-Left>", lambda event: self.__load_previous_image())
        self.root.bind("<Prior>", lambda event: self.__load_previous_image())

        # Big Jump Navigation
        self.root.bind("<Control-f>", lambda event: self.__go_to_row_n())
        self.root.bind("<Control-r>", lambda event: self.__start_from_first_unprocessed())
        self.root.bind("<Home>", lambda event: self.__start_from_first_unprocessed())

        # Special action
        self.root.bind("<Control-w>", lambda event: self.root.quit())

    # Helper function
    def __create_entry(self, label_text, variable):
        """Helper method to create labeled entry fields."""
        self.root.call(
            "grid",
            Label(self.root, text=label_text),
            Entry(self.root, textvariable=variable),
            "-padx",
            "10",
            "-pady",
            "5",
        )

    def __create_combobox(self, label_text, variable, values, default=None):
        """Helper method to create labeled entry fields."""
        label = Label(self.root, text=label_text)
        combobox = AutocompleteCombobox(self.root, textvariable=variable, completevalues=values)
        self.root.call("grid", label, combobox, "-padx", "10", "-pady", "5")

        if default:
            combobox.set(default)

    def __validate_inputs(self, lp, make, car_type, colour, env):
        """Validate the input values."""
        if not lp:
            messagebox.showerror("Error", f"Error: {lp}, Please enter a valid car plate, e.g. ABC1234")
            return False
        if make not in self.vehicle_makes:
            messagebox.showerror("Error", f"Error: Invalid make '{make}'")
            return False
        if car_type not in self.vehicle_types:
            messagebox.showerror("Error", f"Error: Invalid type '{car_type}'")
            return False
        if colour not in self.vehicle_colors:
            messagebox.showerror("Error", f"Error: Invalid colour '{colour}'")
            return False
        if env not in self.environment:
            messagebox.showerror("Error", f"Error: Invalid environment '{env}'")
            return False
        return True

    def __display_image(self):
        """Display the current image with annotations."""
        row = self.data.iloc[self.index]
        image_path = row.iloc[0]
        image_name = row.iloc[1]
        full_image_path = Path(image_path) / image_name

        # fmt: off
        # Overwrite the display value
        if "lp" in row:
            self.lp_var.set(row["lp"])
        if "make" in row:
            self.make_var.set(row["make"]) if not pd.isna(row["make"]) else self.make_var.set("")
        if "type" in row:
            self.type_var.set(row["type"]) if not pd.isna(row["type"]) else self.type_var.set("")
        if "colour" in row:
            self.colour_var.set(row["colour"]) if not pd.isna(row["colour"]) else self.colour_var.set("")
        if "environment" in row:
            if not pd.isna(row["environment"]): self.env_var.set(row["environment"])
        if "isBack" in row:
            self.isback_var.set(str(row["isBack"])) if not pd.isna(row["isBack"]) else self.isback_var.set(False)

        processed_status = "✔️ Processed ✔️" if row["processed"] else "✗ Not Processed ✗"

        if os.path.exists(full_image_path):
            img = Image.open(full_image_path)
            draw = ImageDraw.Draw(img)
            lp_img = None

            if np.isin(['x1', 'y1', 'x2', 'y2'], row.keys()).all():
                lp_img = img.crop((row['x1'], row['y1'], row['x2'], row['y2']))

                draw.rectangle(
                    [row["x1"], row["y1"], row["x2"], row["y2"]],
                    outline="aquamarine",
                    width=2,
                )

            img.thumbnail((500, 440))
            img_tk = ImageTk.PhotoImage(img)

            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk  # Keep a reference to avoid garbage collection
            self.status_label.config(
                text=f"File: {image_name} \n {self.index + 1}/{len(self.data)}\n{processed_status}"
            )

            # Display zoom license plate image
            if lp_img:
                (width, height) = (lp_img.width * 3, lp_img.height * 3)
                im_resized = lp_img.resize((width, height))
                lp_img_tk = ImageTk.PhotoImage(im_resized)
                self.lp_image_label.config(image=lp_img_tk, text='ORIGINAL', compound='bottom')
                self.lp_image_label.image = lp_img_tk  # Keep a reference to avoid garbage collection

                resampled_im_resized = lp_img.resize((width, height), Image.LANCZOS)
                resampled_lp_img_tk = ImageTk.PhotoImage(resampled_im_resized)
                self.resampled_lp_image_label.config(image=resampled_lp_img_tk, text='LANCZOS', compound='bottom')
                self.resampled_lp_image_label.image = resampled_lp_img_tk  # Keep a reference to avoid garbage collection
        else:
            self.status_label.config(text=f"Image not found: {full_image_path}")
        # fmt: on

    # Event related function
    def __update_entry(self):
        """Validate and update the current entry."""
        new_lp = self.lp_var.get().upper()
        new_make = self.make_var.get()
        new_type = self.type_var.get()
        new_colour = self.colour_var.get()
        new_env = self.env_var.get()
        try:
            new_isback = self.isback_var.get()
        except ValueError:
            messagebox.showerror("Error", f"Error: Invalid isback")
            return

        if self.__validate_inputs(new_lp, new_make, new_type, new_colour, new_env):
            self.data.at[self.index, "lp"] = new_lp
            self.data.at[self.index, "make"] = new_make
            self.data.at[self.index, "type"] = new_type
            self.data.at[self.index, "colour"] = new_colour
            self.data.at[self.index, "environment"] = new_env
            self.data.at[self.index, "isBack"] = new_isback
            self.data.at[self.index, "processed"] = True
            self.data.to_csv(self.csv_file, index=False)
            messagebox.showinfo("Info", "Updated filename successfully!")
            self.__load_next_image()

    def __delete_entry(self):
        """Delete the current entry."""
        selected = messagebox.askquestion("Delete", "Are you sure you want to delete this image?", icon="warning")

        if selected == "yes":
            self.data.drop(self.index, inplace=True)
            self.data.reset_index(inplace=True, drop=True)
            self.data.to_csv(self.csv_file, index=False)
            messagebox.showinfo("Info", "Deleted successfully!")
            self.__display_image()

    def __load_next_image(self):
        """Load the next image."""
        if self.index < len(self.data) - 1:
            self.index += 1
            self.__display_image()
        else:
            messagebox.showinfo("Info", "Already at the last image.")

    def __load_previous_image(self):
        """Load the previous image."""
        if self.index > 0:
            self.index -= 1
            self.__display_image()
        else:
            messagebox.showinfo("Info", "Already at the first image.")

    def __go_to_row_n(self):
        """Prompt for a row number and display that image."""
        n = simpledialog.askinteger("Go to Row", "Enter the row number:", minvalue=1, maxvalue=len(self.data))
        if n is not None and 1 <= n <= len(self.data):
            self.index = n - 1  # Convert to 0-based index
            self.__display_image()

    def __start_from_first_unprocessed(self):
        """Start displaying images from the first unprocessed entry."""
        unprocessed = self.data[self.data["processed"] == False]
        if not unprocessed.empty:
            self.index = unprocessed.index[0]
            self.__display_image()
        else:
            messagebox.showinfo("Info", "All entries are processed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Annotate vehicle image, except license plate box.")

    # Add arguments
    parser.add_argument("csv", type=str, help="Input csv that generate from yolo_to_csv")
    parser.add_argument("-c", "--config", type=str, help="Config file path", default="config.yml")

    args = parser.parse_args()

    # Check that output file ends with .csv
    if not args.csv.endswith(".csv"):
        parser.error(Fore.RED + "Input file must end with .csv")

    app = ImageAnnotatorApp(args.csv, config_file=args.config)
    app.start()
