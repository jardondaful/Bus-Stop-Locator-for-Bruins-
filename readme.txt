# Bus Stop Locator for Bruins 🚌🐻

Welcome to the Bus Stop Locator for Bruins project! 🎉

## About the Project

The Bus Stop Locator for Bruins is a Python-scripted toolbox built in ArcGIS Pro. The purpose of this project is to help locate bus stops within a desired proximity and provide recommendations 
on which buses to take based on current user inputted data. As output, it generates directions on which bus stops and routes to take in terminal and generates visual layouts of such directions 🌟

## Team Members 👋

- Alexis Hatalski
- Claire Keeshen
- Jordan Lin
- Joseline Virgen
- Julie Quintero
- Ricardo Miramontes

## Technologies Used

- Python
- ArcGIS Pro


## Code Description

The main script (`main.py`) contains the following functions:

- `geocode_address(address, label)`: This function takes an address and a label as inputs, geocodes the address using the ArcGIS geocoding service, and retrieves its coordinates (latitude and longitude).
- `create_file_geodatabase(folder_path, gdb_name)`: This function creates a new file geodatabase at the specified folder path with the given name.
- `create_feature_dataset(gdb_path, fds_name, spatial_ref)`: This function creates a new feature dataset within the specified file geodatabase path, using the given feature dataset name and spatial reference.
- `create_public_transit_data_model(in_gtfs, fds)`: This function creates the public transit data model by converting the GTFS data into a feature dataset.
- `connect_streets_to_ptdm(ptdm_path, streets_path)`: This function connects the streets to the public transit data model.
- `create_network_dataset(template_path, ptdm_path)`: This function creates the network dataset using a template and the public transit data model.
- `build_network(network_dataset)`: This function builds the network dataset.
- `run_cursors_ptdm() `: performs cursor operations to extract facility IDs from a dataset and selects features based on those IDs for export to a shapefile.
- `geocode_and_create_shapefile(folder_path, output_shapefile)`: This function prompts the user to enter the starting and desired addresses, geocodes them, and creates a shapefile with the locations.
- `solve_closest_facility(layer_object, stops_path, output_shapefile)`: This function solves the closest facility analysis using the network dataset and the specified stops.
- `solve_route(layer_object, stops_path)`: This function solves the route analysis using the network dataset and the specified stops.
- `generate_map_layout(project_path, layout_name, map_name, output_folder, output_filename)`: This function generates a map layout with a specified title, scale bar, and legend, and exports it as a PDF.

Please note that you may need to install the required dependencies, such as `arcpy` and `requests`, before running the script.

## File Organization

Once you unzip the file, you can see that all of the public transportation data folders and files (bus point shafiles, geocoded points, etc.) are in the same directory as the main .aprx file. 
Although there are a lot of data files, you only need to open the .aprx file if you wish to test our bus stop locator


## How to Use

To use the Bus Stop Locator for Bruins, follow these steps:

To use our bus stop locator, follow these steps:
1) Download the entire .zip file and extract the files to your desired location
2) Locate the .aprx file within the extracted files.
3) Open the .aprx file in ArcGIS Pro and the provided .py file.  
4) Provide your current location and desired destination location as legal addresses when prompted by the script.
5) Review the output, which will provide you with bus stop recommendations and routes to take and visuals representing the results.
6) Follow the map or written walking directions to the bus stop closest to your location, and enjoy the bus ride to your desired destination. 


## Contributing

We welcome contributions from everyone! If you would like to contribute to our project, feel free to open an issue or pull request. We look forward to hearing from you! 💬

## Project Data Links

- [Project Data](https://drive.google.com/file/d/1xl5853m1XHPXUqga_QShV8zxxTCxe0I6/view?usp=sharing)
- [Full Project](https://drive.google.com/file/d/1YjhafOhJ3Ww3cUHywnu-afrHyukXdvde/view?usp=sharing)
