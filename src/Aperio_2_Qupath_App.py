import os
import xml.etree.ElementTree as ET
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Define the conversion function
def convert_aperio_xml_to_geojson(xml_file_path, output_geojson_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }

    for region_elem in root.findall(".//Region"):
        classification_elem = region_elem.find(".//Attribute[@Name='classification']")
        if classification_elem is not None:
            classification_name = classification_elem.find(".//Attribute[@Name='name']").get("Value")
            classification_color = classification_elem.find(".//Attribute[@Name='color']").get("Value")
            classification_color = list(map(int, classification_color.split(',')))
        else:
            classification_name = "DefaultName"
            classification_color = [0, 0, 0]

        feature = {
            "type": "Feature",
            "properties": {
                "objectType": "annotation",
                "classification": {
                    "name": classification_name,
                    "color": classification_color
                }
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[]]
            }
        }

        for vertex_elem in region_elem.findall(".//Vertex"):
            x_coord = float(vertex_elem.get("X"))
            y_coord = float(vertex_elem.get("Y"))
            feature["geometry"]["coordinates"][0].append([x_coord, y_coord])

        feature["geometry"]["coordinates"][0].append(feature["geometry"]["coordinates"][0][0])
        geojson_data["features"].append(feature)

    with open(output_geojson_path, 'w') as geojson_file:
        json.dump(geojson_data, geojson_file, indent=2)

# Tkinter Application
class AperioToQuPathConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aperio to QuPath Converter")
        self.root.geometry("500x300")
        self.create_widgets()

    def create_widgets(self):
        # Description Paragraph
        description = ("This software converts Aperio XML data to GeoJSON format "
                       "and deposits it to the specified output folder. "
                       "Provide the input XML file location, output GeoJSON file location, "
                       "and click 'Execute' to perform the conversion.")

        description_label = tk.Label(self.root, text=description, wraplength=480, justify="left", padx=10, pady=10)
        description_label.grid(row=0, column=0, columnspan=3)

        # Input File Location
        input_label = tk.Label(self.root, text="Input XML Location:")
        input_label.grid(row=1, column=0, sticky="e", padx=10, pady=5)

        self.input_path_var = tk.StringVar()
        input_entry = ttk.Entry(self.root, textvariable=self.input_path_var, width=40)
        input_entry.grid(row=1, column=1, padx=10, pady=5)

        input_button = ttk.Button(self.root, text="Browse", command=self.browse_input)
        input_button.grid(row=1, column=2, pady=5)

        # Output File Location
        output_label = tk.Label(self.root, text="Output GeoJSON Location:")
        output_label.grid(row=2, column=0, sticky="e", padx=10, pady=5)

        self.output_path_var = tk.StringVar()
        output_entry = ttk.Entry(self.root, textvariable=self.output_path_var, width=40)
        output_entry.grid(row=2, column=1, padx=10, pady=5)

        output_button = ttk.Button(self.root, text="Browse", command=self.browse_output)
        output_button.grid(row=2, column=2, pady=5)

        # Execute Button
        execute_button = ttk.Button(self.root, text="Execute", command=self.execute_conversion)
        execute_button.grid(row=3, column=0, columnspan=3, pady=20)

        # About Button
        about_button = ttk.Button(self.root, text="About", command=self.show_about)
        about_button.grid(row=4, column=0, columnspan=3, pady=5)

    def browse_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_path:
            self.input_path_var.set(file_path)

    def browse_output(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_path_var.set(folder_path)

    def execute_conversion(self):
        input_path = self.input_path_var.get()
        output_folder = self.output_path_var.get()

        if not os.path.isfile(input_path):
            tk.messagebox.showerror("Error", "Invalid input file path.")
            return

        if not os.path.isdir(output_folder):
            tk.messagebox.showerror("Error", "Invalid output folder path.")
            return

        convert_aperio_xml_to_geojson(input_path, os.path.join(output_folder, "output.geojson"))
        tk.messagebox.showinfo("Conversion Complete", "Aperio to QuPath conversion completed successfully.")

    def show_about(self):
        about_text = "Aperio to QuPath Converter\n\n" \
                     "This software is developed by Shad Arif Mohammed\n" \
                     "Date: 27.11.2023\n" \
                     "Location: Mannheim/Germany"
        messagebox.showinfo("About", about_text)

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = AperioToQuPathConverterApp(root)
    root.mainloop()
