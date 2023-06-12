import arcpy
import requests
import os

# Function to geocode an address and retrieve its coordinates
def geocode_address(address, label):
    url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
    params = {
        "SingleLine": address,
        "f": "json",
        "outSR": "4326"
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if "candidates" in data:
            candidate = data["candidates"][0]
            location = candidate["location"]
            latitude = location["y"]
            longitude = location["x"]

            print("{} - Latitude: {}, Longitude: {}".format(label, latitude, longitude))

            return (longitude, latitude)
        else:
            print("No candidates found.")
    else:
        print("Request failed.")

    return None

# Function to create a file geodatabase
def create_file_geodatabase(folder_path, gdb_name):
    arcpy.management.CreateFileGDB(folder_path, gdb_name, "CURRENT")
    print("New file geodatabase created")

# Function to create a feature dataset
def create_feature_dataset(gdb_path, fds_name, spatial_ref):
    fds = arcpy.management.CreateFeatureDataset(gdb_path, fds_name, spatial_ref)
    print("New feature dataset created")
    return fds

# Function to create the public transit data model
def create_public_transit_data_model(in_gtfs, fds):
    print("Creating public transit data model... This might take a while")
    arcpy.transit.GTFSToPublicTransitDataModel(in_gtfs, fds, "INTERPOLATE", "NO_APPEND")
    print("Data Model created")

# Function to connect streets to the public transit data model
def connect_streets_to_ptdm(ptdm_path, streets_path):
    arcpy.transit.ConnectPublicTransitDataModelToStreets(ptdm_path, streets_path)
    print("Streets connected")
    print("Public transit data model completed")

# Function to create the network dataset
def create_network_dataset(template_path, ptdm_path):
    nd = arcpy.na.CreateNetworkDatasetFromTemplate(template_path, ptdm_path)
    print("Network dataset created")
    return nd

# Function to build the network
def build_network(network_dataset):
    nw = arcpy.na.BuildNetwork(network_dataset)
    print("Network built")
    return nw

# Function to run the cursors and perform necessary operations
def run_cursors_ptdm():
    # Set environment settings
    folder_path = r"C:\Users\julyquintero\Downloads\FinalStretch\MyProject1"
    ProjectGDB = os.path.join(folder_path, "NewGDbase.gdb")
    env.workspace = ProjectGDB
    env.overwriteOutput = True

    DirectionPoints = os.path.join(ProjectGDB, "ClosestFacilitySolver6037uo", "ClosestFacilitySolver6037uo_DirectionPoints")
    StopsOnStreets = os.path.join(ProjectGDB, "StopsOnStreets") 

    # Create a list to store the non-null FacilityID values
    facility_ids = []

    with arcpy.da.SearchCursor(DirectionPoints, ["ObjectID", "DisplayText", "FacilityID"]) as cursor:
        print("Directions:")
        for row in cursor:
            object_id = row[0]
            display_text = row[1]
            facility_id = row[2]
            print(display_text)
            
            if facility_id is not None:
                print(f"Incident ID: {facility_id}\n")

    # Open a search cursor to iterate over the rows in the input table
    with arcpy.da.SearchCursor(DirectionPoints, ["FacilityID"]) as cursor:
        for row in cursor:
            facility_id = row[0]
            if facility_id is not None:
                facility_ids.append(facility_id)

    # Check if there are at least two facility IDs in the list
    if len(facility_ids) >= 2:
        # Create a feature layer to perform the selection
        arcpy.MakeFeatureLayer_management(StopsOnStreets, "StopsLayer")

        # Select features based on the facility IDs
        where_clause = "OBJECTID = {} OR OBJECTID = {}".format(facility_ids[0], facility_ids[1])
        arcpy.SelectLayerByAttribute_management("StopsLayer", "NEW_SELECTION", where_clause)

        # Export the selected features to a shapefile
        arcpy.conversion.ExportFeatures("StopsLayer", os.path.join(folder_path, "BusPoints.shp"))

        print("Export completed successfully.")
    else:
        print("Insufficient facility IDs to perform the export.")

    print("Done.")

# Function to geocode addresses and create a shapefile with the locations
def geocode_and_create_shapefile(folder_path, output_shapefile):
    starting_address = input("Enter the starting address: ")
    desired_address = input("Enter the desired address: ")

    starting_coords = geocode_address(starting_address, "Starting Location")
    desired_coords = geocode_address(desired_address, "Desired Location")

    if starting_coords and desired_coords:
        arcpy.env.workspace = folder_path
        arcpy.env.overwriteOutput = True
        arcpy.management.CreateFeatureclass(folder_path, output_shapefile, "POINT",
                                            spatial_reference=arcpy.SpatialReference(4326))

        arcpy.management.AddField(output_shapefile, "Location", "TEXT")

        with arcpy.da.InsertCursor(output_shapefile, ['SHAPE@XY', 'Location']) as cursor:
            cursor.insertRow([(starting_coords[0], starting_coords[1]), "Starting Location"])
            cursor.insertRow([(desired_coords[0], desired_coords[1]), "Desired Location"])

        print("Shapefile created successfully.")

# Function to solve the closest facility analysis
def solve_closest_facility(layer_object, stops_path, output_shapefile):
    arcpy.na.AddLocations(layer_object, "Facilities", stops_path)
    arcpy.na.Solve(layer_object)

    output_layer_file = os.path.join(arcpy.env.workspace, layer_object.name + ".lyrx")
    layer_object.saveACopy(output_layer_file)

    print("Closest facility analysis completed")

    arcpy.conversion.ExportFeatures(layer_object, output_shapefile)
    print("Facilities exported to shapefile")

# Function to solve the route analysis
def solve_route(layer_object, stops_path):
    arcpy.na.AddLocations(layer_object, "Stops", stops_path,
                          field_mappings="Name # #;RouteName # #;Sequence # #;TimeWindowStart # #;TimeWindowEnd # #;LocationType # 0;CurbApproach # 0;Attr_PublicTransitTime # 0;Attr_WalkTime # 0;Attr_Length # 0",
                          search_tolerance="5000 Meters",
                          search_criteria="StopConnectors SHAPE;Streets SHAPE;Stops SHAPE;StopsOnStreets SHAPE;TransitNetwork_ND_Junctions NONE",
                          match_type="MATCH_TO_CLOSEST",
                          append="APPEND",
                          snap_to_position_along_network="NO_SNAP",
                          snap_offset="5 Meters",
                          exclude_restricted_elements="EXCLUDE")
    print("Add locations completed")

    arcpy.na.Solve(layer_object)
    print("Route solved")

    output_layer_file = os.path.join(arcpy.env.workspace, layer_object.name + ".lyrx")
    layer_object.saveACopy(output_layer_file)
    print("Route layer saved")

# Function to generate a map layout and export it as a PDF
def generate_map_layout(project_path, layout_name, map_name, output_folder, output_filename):
    aprx = arcpy.mp.ArcGISProject(project_path)
    layout = aprx.listLayouts(layout_name)[0]
    map_frame = layout.listElements("MAPFRAME_ELEMENT")[0]
    map_obj = aprx.listMaps(map_name)[0]
    map_frame.map = map_obj
    map_frame.camera.setExtent(map_obj.defaultCamera.getExtent())
    title = layout.listElements("TEXT_ELEMENT", "Text")[0]
    title.text = "Map Print Layout"
    scale_bar = layout.listElements("MAPSURROUND_ELEMENT", "Scale Bar")[0]
    legend = layout.listElements("LEGEND_ELEMENT", "Legend")[0]
    legend.autoAdd = True

    output_path = os.path.join(output_folder, output_filename)

    if os.path.exists(output_path):
        os.remove(output_path)

    layout.exportToPDF(output_path)
    print("Map layout generated")

    aprx.save()
    del aprx


def main():
    folder_path = r"C:\Users\lexiw\Desktop\181C\FinalProject\MyProject26"
    gdb_name = "NewGDbase"
    output_shapefile = "geocoded_points.shp"
    template_path = os.path.join(folder_path, "TransitNetworkTemplate")
    project_path = r"C:\Users\josel\Downloads\MyProject1 (1)\MyProject1\MyProject1.aprx"
    layout_name = "Layout"
    map_name = "Map"
    output_folder = r"C:\Users\josel\Downloads\MyProject1 (1)\Output"
    output_filename = "output.pdf"

    # Create a file geodatabase
    create_file_geodatabase(folder_path, gdb_name)
    gdb_path = os.path.join(folder_path, gdb_name + ".gdb")

    # Create a feature dataset
    feature_dataset = create_feature_dataset(gdb_path, "PTDM_fds", arcpy.SpatialReference(4326))

    # Create the public transit data model
    in_gtfs = [os.path.join(folder_path, "BigBlue_gtfs"), os.path.join(folder_path, "CulverCity_gtfs")]
    create_public_transit_data_model(in_gtfs, feature_dataset)
    ptdm_path = os.path.join(gdb_path, "PTDM_fds")

    # Connect streets to the public transit data model
    connect_streets_to_ptdm(ptdm_path, os.path.join(folder_path, "Streets"))

    # Create the network dataset
    network_dataset = create_network_dataset(template_path, ptdm_path)

    # Build the network
    build_network(network_dataset)

    # Run the cursors and perform necessary operations
    run_cursors_ptdm()

    # Geocode addresses and create a shapefile with locations
    geocode_and_create_shapefile(folder_path, output_shapefile)

    # Solve the closest facility analysis
    closest_facility_layer = arcpy.na.MakeClosestFacilityAnalysisLayer(
        network_data_source=r"https://www.arcgis.com/",
        layer_name="ClosestBusStop",
        travel_mode="Walking Distance",
        travel_direction="TO_FACILITIES",
        cutoff=2,
        number_of_facilities_to_find=1,
        time_of_day=None,
        time_zone="LOCAL_TIME_AT_LOCATIONS",
        time_of_day_usage="START_TIME",
        line_shape="ALONG_NETWORK",
        accumulate_attributes=None,
        generate_directions_on_solve="DIRECTIONS",
        ignore_invalid_locations="SKIP"
    ).getOutput(0)

    solve_closest_facility(closest_facility_layer, os.path.join(ptdm_path, "StopsOnStreets"), output_shapefile)

    # Solve the route analysis
    route_layer = arcpy.na.MakeRouteAnalysisLayer(
        network_data_source=network_dataset,
        layer_name="Route",
        travel_mode="Public transit time",
        sequence="USE_CURRENT_ORDER",
        time_of_day=None,
        time_zone="LOCAL_TIME_AT_LOCATIONS",
        line_shape="ALONG_NETWORK",
        accumulate_attributes=None,
        generate_directions_on_solve="DIRECTIONS",
        time_zone_for_time_fields="LOCAL_TIME_AT_LOCATIONS",
        ignore_invalid_locations="SKIP"
    ).getOutput(0)

    solve_route(route_layer, os.path.join(folder_path, "BusPoints.shp"))

    # Generate a map layout and export it as a PDF
    generate_map_layout(project_path, layout_name, map_name, output_folder, output_filename)


if __name__ == '__main__':
    main()
