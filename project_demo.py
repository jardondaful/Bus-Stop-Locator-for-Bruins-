import os
import arcpy
import math

def process_gtfs_data(folder_path, gtfs_folders):
    # Process GTFS data to create feature classes
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = folder_path

    project_gdb = os.path.join(folder_path, "MyProject26.gdb")

    for gtfs_folder in gtfs_folders:
        gtfs_path = os.path.join(folder_path, gtfs_folder)

        gtfs_shapes = os.path.join(gtfs_path, "shapes.txt")
        gtfs_trips = os.path.join(gtfs_path, "trips.txt")
        gtfs_stop_time = os.path.join(gtfs_path, "stop_times.txt")
        gtfs_stops = os.path.join(gtfs_path, "stops.txt")

        # Create empty feature dataset for the GTFS shapes to features
        shapes_to_features = arcpy.management.CreateFeatureclass(out_path=project_gdb, out_name="GTFSHome")

        # Process: GTFS Shapes To Features (GTFS Shapes To Features) (transit)
        arcpy.transit.GTFSShapesToFeatures(gtfs_shapes, shapes_to_features)

        # Export trips text file to editable table
        export_trips = os.path.join(gtfs_path, "TripsExport.gdb")
        arcpy.conversion.ExportTable(in_table=gtfs_trips, out_table=export_trips)

        # Export stop times text file to editable table
        export_stop_times = os.path.join(gtfs_path, "StopTimesExport.gdb")
        arcpy.conversion.ExportTable(in_table=gtfs_stop_time, out_table=export_stop_times)

        # Export stops text file to editable table
        export_stops = os.path.join(gtfs_path, "StopsExport.gdb")
        arcpy.conversion.ExportTable(in_table=gtfs_stops, out_table=export_stops)

        # Join trips to stop times via trip_id field
        trips2 = arcpy.management.JoinField(in_data=export_trips, in_field="trip_id", join_table=export_stop_times, join_field="trip_id")

        # Join stop times to stops via stop_id field
        trips3 = arcpy.management.JoinField(in_data=trips2, in_field="stop_id", join_table=export_stops, join_field="stop_id")

        # Join all the joined tables with the shapes to features called GTFSHome via the route_id field
        trips_shapes = arcpy.management.JoinField(in_data=shapes_to_features, in_field="route_id", join_table=trips3, join_field="route_id")

        # Get the bus name from the gtfs_folder
        bus_name = gtfs_folder.split('_')[0]

        # Export GTFS shapefile with everything joined
        gtfs_complete = os.path.join(gtfs_path, f"{bus_name}_GTFSComplete.shp")
        arcpy.conversion.ExportFeatures(in_features=trips_shapes, out_features=gtfs_complete)

        print(f"Processing {gtfs_folder} - done!")
        print(f"The complete GTFS shapefile can be found in the {gtfs_folder} folder titled {bus_name}_GTFSComplete.shp")
        print("\n")


def merge_shapefiles(folder_path, gtfs_folders, output_shapefile):
    # Set the workspace and overwrite output
    arcpy.env.workspace = folder_path
    arcpy.env.overwriteOutput = True

    # Create a list to store the paths of the shapefiles to be merged
    shapefiles_to_merge = []

    # Loop through the GTFS folders and add the shapefile paths to the list
    for gtfs_folder in gtfs_folders:
        gtfs_path = os.path.join(folder_path, gtfs_folder)
        shapefile_path = os.path.join(gtfs_path, f"{gtfs_folder}_GTFSComplete.shp")
        shapefiles_to_merge.append(shapefile_path)

    # Merge the shapefiles
    arcpy.management.Merge(shapefiles_to_merge, output_shapefile)

    print("Shapefile merge completed!")


def calculate_distance(lat1, lon1, lat2, lon2):
    # Calculate the Euclidean distance between two sets of coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    distance = math.sqrt(dlat ** 2 + dlon ** 2)
    return distance


def convert_gtfs_stops_to_features(folder_path, gtfs_folders):
    print("GENERATING STOPS")
    # Convert GTFS stops to feature classes
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = folder_path

    project_gdb = os.path.join(folder_path, "MyProject26.gdb")

    for gtfs_folder in gtfs_folders:
        gtfs_path = os.path.join(folder_path, gtfs_folder)

        gtfs_stops = os.path.join(gtfs_path, "stops.txt")

        # Generate a valid feature class name
        feature_class_name = arcpy.ValidateTableName(f"{gtfs_folder}_stops", project_gdb)

        # Output feature class path
        output_feature_class = os.path.join(project_gdb, feature_class_name)

        # Process GTFS Stops To Features
        arcpy.transit.GTFSStopsToFeatures(
            in_gtfs_stops_file=gtfs_stops,
            out_feature_class=output_feature_class
        )

        # Add XY coordinates to the generated feature class
        arcpy.management.AddXY(output_feature_class)

        print(f"GTFS Stops to Features conversion completed for {gtfs_folder}!")
        

def add_route_id_to_stop_shapefile(stop_shapefile, gtfs_complete_folder):
    # Set the workspace and overwrite output
    arcpy.env.workspace = arcpy.Describe(stop_shapefile).path
    arcpy.env.overwriteOutput = True

    # Add a new field to store the route_id
    arcpy.management.AddField(stop_shapefile, "route_id", "TEXT")

    # Get the path to the GTFSComplete route file
    gtfs_complete_route_file = os.path.join(gtfs_complete_folder, "routes.txt")

    # Read the GTFSComplete route file and extract the route_id values
    route_ids = set()
    with open(gtfs_complete_route_file, "r") as file:
        next(file)  # Skip the header line
        for line in file:
            route_id = line.strip().split(",")[0]
            route_ids.add(route_id)

    # Update the route_id field in the stop shapefile
    with arcpy.da.UpdateCursor(stop_shapefile, ["route_id"]) as cursor:
        for row in cursor:
            row[0] = ",".join(route_ids)
            cursor.updateRow(row)

    print("Route IDs added to the stop shapefile for the GTFSComplete folder:", gtfs_complete_folder)
    

def get_user_location():
    # Prompt user for current location coordinates (latitude, longitude)
    user_input = input("Enter the coordinates of your current location (latitude, longitude): ")
    user_latitude, user_longitude = map(float, user_input.split(','))

    return user_latitude, user_longitude

def get_user_destination():
    # Prompt user for current location coordinates (latitude, longitude)
    user_input = input("Enter the coordinates of your desired location (latitude, longitude): ")
    user_latitude, user_longitude = map(float, user_input.split(','))

    return user_latitude, user_longitude

def find_closest_source_stop(user_latitude, user_longitude, merged_stop_times_table, folder_path):
    # Set the workspace
    arcpy.env.workspace = folder_path
    arcpy.env.overwriteOutput = True

    # Create a search cursor to iterate over the merged stop_times table
    fields = ["stop_id", "stop_lat", "stop_lon"]
    with arcpy.da.SearchCursor(merged_stop_times_table, fields) as cursor:
        closest_stop_id = None
        closest_distance = float("inf")

        for row in cursor:
            stop_id, stop_lat, stop_lon = row

            # Calculate the distance between the user location and the current stop
            distance = calculate_distance(user_latitude, user_longitude, stop_lat, stop_lon)

            # Update the closest stop if a closer one is found
            if distance < closest_distance:
                closest_stop_id = stop_id
                closest_distance = distance

    return closest_stop_id, closest_distance


def find_closest_valid_destination_stop(source_stop_id, merged_stop_times_table, stops_table):
    # Set the workspace
    arcpy.env.workspace = folder_path
    arcpy.env.overwriteOutput = True

    # Get the route_id and agency_id of the source stop
    with arcpy.da.SearchCursor(stops_table, ["route_id", "agency_id"], f"stop_id = '{source_stop_id}'") as cursor:
        for row in cursor:
            route_id = row[0]
            source_agency_id = row[1]

    # Create a search cursor to iterate over the merged stop_times table
    fields = ["stop_id", "stop_lat", "stop_lon"]
    with arcpy.da.SearchCursor(merged_stop_times_table, fields) as cursor:
        closest_stop_id = None
        closest_distance = float("inf")

        for row in cursor:
            stop_id, stop_lat, stop_lon = row

            # Check if the stop has the same route_id and agency_id as the source stop
            with arcpy.da.SearchCursor(stops_table, ["route_id", "agency_id"], f"stop_id = '{stop_id}'") as route_cursor:
                for route_row in route_cursor:
                    if route_row[0] == route_id and route_row[1] == source_agency_id:
                        # Calculate the distance between the source stop and the current stop
                        distance = calculate_distance(source_stop_lat, source_stop_lon, stop_lat, stop_lon)

                        # Update the closest stop if a closer one with the same route_id and agency_id is found
                        if distance < closest_distance:
                            closest_stop_id = stop_id
                            closest_distance = distance

    return closest_stop_id, closest_distance


def find_closest_stop(user_location, folder_path, gtfs_folders):
    closest_stop_name = None
    min_distance = float("inf")

    project_gdb = os.path.join(folder_path, "MyProject26.gdb")
    stops_export_path = os.path.join(project_gdb, "MergedStops")

    if arcpy.Exists(stops_export_path):
        user_lat, user_lon = user_location

        # Retrieve the nearest stop from the table
        with arcpy.da.SearchCursor(stops_export_path, ["stop_name", "stop_lat", "stop_lon"]) as cursor:
            for row in cursor:
                stop_name = row[0]
                stop_lat = row[1]
                stop_lon = row[2]

                # Calculate the distance between the user location and the current stop
                distance = calculate_distance(user_lat, user_lon, stop_lat, stop_lon)

                # Check if the current stop is closer than the previous closest stop
                if distance < min_distance:
                    min_distance = distance
                    closest_stop_name = stop_name
                    closest_stop_location = (stop_lat, stop_lon)

    if closest_stop_location is not None:
        print("\nClosest stop found!")
        print("Stop's Name:", closest_stop_name)
        print("Stop's Actual Latitude:", closest_stop_location[0])
        print("Stop's Actual Longitude:", closest_stop_location[1])
    else:
        print("No closest stop found.")

    return closest_stop_location


# def search_gtfscomplete_for_location(shapefile_path, closest_stop_destination):
#     with arcpy.da.SearchCursor(shapefile_path, ["stop_lat", "stop_lon", "route_long"]) as cursor:
#         for row in cursor:
#             lat = row[0]
#             lon = row[1]

#             # Check if the latitude and longitude match
#             if lat == closest_stop_destination[0] and lon == closest_stop_destination[1]:
#                 # Extract the bus system from the shapefile path
#                 folder_name = os.path.dirname(shapefile_path)
#                 bus_system = os.path.basename(folder_name).split("_")[0]
#                 route_long = row[2]

#                 return bus_system, route_long

#     # No matching location found in the shapefile
#     return None, None


# MIN DISTANCE FORMULA FROM THE WHOLE DATA SET (EX: JUST BIG BLUE BUS, STOPS.txt, CAN WE ONLY LOOK THROUGH THIS SPECIFC BUS SYSTEM)
def main():
    FolderPath = r"C:\Users\Jordan Lin\Downloads\GEOG_181C\MyProject26\MyProject26"
    GTFSFolders = [
        "AVTA-GTFS",
        "BigBlue_gtfs",
        "BruinBus_gtfs",
        "CulverCity_GTFS",
        "LAX_gtfs",
        "LAdot_gtfs",
        "Santa Clarita",
        "lbt_gtfs",
        "metro_gtfs_bus"
    ]

    GTFSCompleteFolders = [
        "AVTA-GTFS_GTFSComplete",
        "BigBlue_gtfs_GTFSComplete",
        "BruinBus_gtfs_GTFSComplete",
        "CulverCity_GTFS_GTFSComplete",
        "LAX_gtfs_GTFSComplete",
        "LAdot_gtfs_GTFSComplete",
        "Santa Clarita_GTFSComplete",
        "lbt_gtfs_GTFSComplete",
        "metro_gtfs_bus_GTFSComplete"
    ]
    GTFSStops = [
        "AVTA_GTFS_stops",
        "BIGBLUE_gtfs_stops",
        "BruinBus_gtfs_stops",
        "CulverCity_GTFS_stops",
        "LAX_gtfs_stops",
        "LAdot_gtfs_stops",
        "Santa_Clarita_stops",
        "lbt_gtfs_stops",
        "metro_gtfs_stops"
    ]
    
#     # Process the data
#     process_gtfs_data(FolderPath, GTFSFolders)

    
#     # Merge the resulting data
#     merge_shapefiles(folder_path, gtfs_folders, output_shapefile)

#     #Generate the stops
#     convert_gtfs_stops_to_features(FolderPath, GTFSFolders)





#=============DISCARD==================
#     #Join route_id
#     i = 0
#     for gtfs_folder in GTFSStops:
#         stop_shapefile = os.path.join(FolderPath, GTFSFolders[i], GTFSCompleteFolders[i])
#         add_route_id_to_stop_shapefile(stop_shapefile, gtfs_folder)
#         i = i + 1
        
#     # Add route_id to MergedStops
#     merged_stops = os.path.join(FolderPath, "MyProject26.gdb", "MergedStops")
#     add_route_id_to_merged_stops(merged_stops, GTFSFolders)
    
#     # Merge all stops
#     project_gdb = os.path.join(FolderPath, "MyProject26.gdb")
#     merged_stops = os.path.join(project_gdb, "MergedStops")
#     stops_export_paths = []
#     for gtfs_folder in GTFSFolders:
#         feature_class_name = arcpy.ValidateTableName(f"{gtfs_folder}_stops", project_gdb)
#         stops_export_path = os.path.join(project_gdb, feature_class_name)
#         stops_export_paths.append(stops_export_path)
#     arcpy.management.Merge(stops_export_paths, merged_stops)
#     print("STOPS MERGED\n")
#=============DISCARD==================




    # Get location (btw. valid ranges of [33.9, -118.38] and [34.076, -118.439])
    user_location = get_user_location()

    # Find closest stop
    print("\nFinding the closest stop to your current destination...")
    closest_stop_start = find_closest_stop(user_location, FolderPath, GTFSFolders)

    print("\n--------------------------------------------------------------------------------------")

    # Get desired destination from the user (btw. valid ranges of [33.9, -118.38] and [34.076, -118.439])
    destination_location = get_user_destination()

    # Find closest stop to desired destination
    print("\nFinding the closest stop to the desired destination...")
    closest_stop_destination = find_closest_stop(destination_location, FolderPath, GTFSFolders)

    
    
if __name__ == "__main__":
    main()
