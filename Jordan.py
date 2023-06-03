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


def get_user_location():
    # Prompt user for current location coordinates (latitude, longitude)
    user_input = input("Enter the coordinates of the user's current location (latitude, longitude): ")
    user_latitude, user_longitude = map(float, user_input.split(','))

    return user_latitude, user_longitude


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
        print("Stop Name:", closest_stop_name)
        print("Latitude:", closest_stop_location[0])
        print("Longitude:", closest_stop_location[1])
    else:
        print("No closest stop found.")

    return closest_stop_location


def search_gtfscomplete_for_location(shapefile_path, closest_stop_destination):
    with arcpy.da.SearchCursor(shapefile_path, ["stop_lat", "stop_lon", "route_long"]) as cursor:
        for row in cursor:
            lat = row[0]
            lon = row[1]

            # Check if the latitude and longitude match
            if lat == closest_stop_destination[0] and lon == closest_stop_destination[1]:
                # Extract the bus system from the shapefile path
                folder_name = os.path.dirname(shapefile_path)
                bus_system = os.path.basename(folder_name).split("_")[0]
                route_long = row[2]

                return bus_system, route_long

    # No matching location found in the shapefile
    return None, None


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

#     #Generate the stops
#     convert_gtfs_stops_to_features(FolderPath, GTFSFolders)

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

    # Get user location
    user_location = get_user_location()

    # Find closest stop
    print("\nFinding the closest stop to the user's current location...")
    closest_stop_start = find_closest_stop(user_location, FolderPath, GTFSFolders)

    print("\n--------------------------------------------------------------------------------------")

    # Get desired destination from the user
    print("\nEnter the desired destination:")
    destination_location = get_user_location()

    # Find closest stop to desired destination
    print("\nFinding the closest stop to the desired destination...")
    closest_stop_destination = find_closest_stop(destination_location, FolderPath, GTFSFolders)


if __name__ == "__main__":
    main()

