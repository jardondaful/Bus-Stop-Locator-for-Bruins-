import arcpy
import os

folder_path = r"C:\Users\julyquintero\Downloads\CodingProject_June7\MyProject26"

"C:\Users\julyquintero\Downloads\CodingProject_June7\MyProject26\Make.gdb"

ProjectGDB = os.path.join(folder_path, "MyProject26.gdb")

# Set up the environment
arcpy.env.workspace = folder_path
arcpy.env.overwriteOutput = True


#### assume the geodatabase and file are already made ### (insert code)



# Set up the network dataset
network_dataset = r"C:\Users\julyquintero\Downloads\CodingProject_June7\MyProject26\Make.gdb"  #the geodatabase made Lexi


# Set up the inputs and outputs
facilities = os.path.join(network_dataset, 'StopsOnStreets.shp') #stopsonstreets !
incidents = os.path.join(folder_path, 'TestPoint/TestPoint.shp') #point
output_routes = os.path.join(network_dataset, 'routes.shp') #output that will be created
output_directions = os.path.join(network_dataset, 'directions.shp') #unsure 

# Create a Closest Facility layer
closest_facility_layer = arcpy.na.MakeClosestFacilityAnalysisLayer(network_dataset, "Closest Facility", "Length")



import arcpy
arcpy.ImportToolbox(r"@\Network Analyst Tools.tbx")

arcpy.na.MakeClosestFacilityAnalysisLayer(
    network_data_source=network_dataset,
    layer_name="Closest Facility 3",
    travel_mode="Walking Time",
    travel_direction="TO_FACILITIES",
    cutoff=10,
    number_of_facilities_to_find=1,
    time_of_day=None,
    time_zone="LOCAL_TIME_AT_LOCATIONS",
    time_of_day_usage="START_TIME",
    line_shape="ALONG_NETWORK",
    accumulate_attributes=None,
    generate_directions_on_solve="DIRECTIONS",
    ignore_invalid_locations="SKIP"
)

# Rest of the code...



# Get the layer names
facilities_layer_name = closest_facility_layer["facilitiesLayerName"]
incidents_layer_name = closest_facility_layer["incidentsLayerName"]
routes_layer_name = closest_facility_layer["routesLayerName"]
directions_layer_name = closest_facility_layer["directionsLayerName"]

# Add facilities and incidents to the layer
arcpy.na.AddLocations(closest_facility_layer, facilities_layer_name, facilities, "", "")
arcpy.na.AddLocations(closest_facility_layer, incidents_layer_name, incidents, "", "")

# Solve the Closest Facility analysis
arcpy.na.Solve(closest_facility_layer)

# Save the resulting routes and directions
arcpy.management.CopyFeatures(closest_facility_layer, output_routes)
arcpy.management.CopyFeatures(arcpy.mapping.ListLayers(closest_facility_layer, directions_layer_name)[0], output_directions)

# Print the closest facility information
with arcpy.da.SearchCursor(output_routes, ["IncidentID", "FacilityID", "Total_Length"]) as cursor:
    for row in cursor:
        incident_id = row[0]
        facility_id = row[1]
        total_length = row[2]
        print(f"Incident ID: {incident_id}, Closest Facility ID: {facility_id}, Total Length: {total_length} meters")

print("Closest facility analysis complete.")



#make public transit data model (lexi code)
#define inputs and outputs
#create closest facility analysis layer
#define walking time, cutoff (want output on solve)
#import facilities (stopsonstreets)
#import incident (user location - shpfile)
        #user address --> geocoded --> made into shp file
#run



