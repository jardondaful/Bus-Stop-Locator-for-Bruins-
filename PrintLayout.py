import arcpy

# Arcgis Project and map 
project = arcpy.mp.ArcGISProject("C:\labs\Bus\MyProject1\MyProject1.aprx")
layout = project.listLayouts()[0]

# Define the name of the closest facility layer
closest_facility_layer_name = "Closest Facility"

# Get the closest facility layer
closest_facility_layer = None
for map in project.listMaps():
    for layer in map.listLayers():
        if layer.name == closest_facility_layer_name:
            closest_facility_layer = layer
            break

# Check if the closest facility layer was found
if closest_facility_layer is not None:
    # Create a new map frame and add the closest facility layer
    map_frame = layout.listElements("MAPFRAME_ELEMENT")[0]
    map_frame.map = map
    map_frame.camera.setExtent(map.defaultCamera.getExtent())
    map_frame.camera.scale *= 1.1  # Adjust the scale if desired, we can worry about this later

    # Export the layout to a PDF file
    pdf_path = "C:\labs\Bus\Output"
    layout.exportToPDF(pdf_path)

    print("Print layout exported successfully.")
else:
    print("Closest Facility layer not found in the project.")


## This only gives like the barebones of a layout project
## I need help adding a legend, scale bar, and title.
## Eventually we will change the project to Claire's project and end up mapping the closes facilty as well as the route 
