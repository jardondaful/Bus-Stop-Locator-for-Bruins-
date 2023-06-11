import arcpy
import os

# Define the path to your ArcGIS Pro project file (.aprx)
project_path = r"C:\Users\josel\Downloads\MyProject1 (1)\MyProject1\MyProject1.aprx"

# Open the ArcGIS Pro project
aprx = arcpy.mp.ArcGISProject(project_path)

# Define the layout name or index
layout_name = "Layout"  # Replace with the name of your layout
layout_index = 0  # Alternatively, specify the index of the layout (0 for the first layout)

# Access the layout
layout = aprx.listLayouts(layout_name)[layout_index]

# Get the map frame element from the layout
map_frame = layout.listElements("MAPFRAME_ELEMENT")[0]  # Assuming there's only one map frame in the layout

# Set the map extent
# Replace "Name_of_your_map" with the actual name of your map
map_name = "Map"
map_obj = aprx.listMaps(map_name)[0]
map_frame.map = map_obj
map_frame.camera.setExtent(map_obj.defaultCamera.getExtent())

# Access the title text element
title = layout.listElements("TEXT_ELEMENT", "Text")[0]  # Assuming the title text element has the alias "Text"

# Set the title text
title.text = "Map Print Layout"  # Replace with your desired title

# Access the scale bar element
scale_bar = layout.listElements("MAPSURROUND_ELEMENT", "Scale Bar")[0]  # Assuming the scale bar has the alias "Scale Bar"

# Access the legend element
legend = layout.listElements("LEGEND_ELEMENT", "Legend")[0]  # Assuming the legend has the alias "Legend"

# Set the legend properties
legend.autoAdd = True  # Enable auto adding of legend items

# Export the layout to a PDF file
output_folder = r"C:\Users\josel\Downloads\MyProject1 (1)\Output"
output_filename = "output.pdf"
output_path = os.path.join(output_folder, output_filename)

# Check if the output file already exists
if os.path.exists(output_path):
    os.remove(output_path)  # Delete the existing output file

layout.exportToPDF(output_path)

print("All done generating Closest Facility Map!")

# Save and close the ArcGIS Pro project
aprx.save()
del aprx

## will need to change it later on to take in Claire's Project that has the closest facilities, route, and final destination 
## when we do this, we need to very specific with the map elements, need to have the exact same name 
