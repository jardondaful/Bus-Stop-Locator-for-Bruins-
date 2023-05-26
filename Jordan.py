import os
import arcpy

        
def process_gtfs_data(folder_path, gtfs_folders):
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

        # Export GTFS shapefile with everything joined
        gtfs_complete = os.path.join(gtfs_path, "GTFSComplete.shp")
        arcpy.conversion.ExportFeatures(in_features=trips_shapes, out_features=gtfs_complete)

        print(f"Processing {gtfs_folder} - done!")
        print(f"The complete GTFS shapefile can be found in the {gtfs_folder} folder titled GTFSComplete.shp")
        print("\n")

def find_closest_stop(user_location, folder_path, gtfs_folders):
    stops_to_user_loc_table = os.path.join(arcpy.env.workspace, "MyProject26.gdb", "StopsToUserLocation.dbf")

    # Create a feature class for the user location
    user_location_feature = arcpy.management.CreateFeatureclass(out_path=arcpy.env.workspace, out_name="UserLocation", geometry_type="POINT")
    with arcpy.da.InsertCursor(user_location_feature, ["SHAPE@"]) as cursor:
        cursor.insertRow([user_location])

    # Find the closest stop from each GTFS folder
    nearest_stops = []

    for gtfs_folder in gtfs_folders:
        stops_export_path = os.path.join(folder_path, gtfs_folder, f"{gtfs_folder}_gtfs_StopsExport.shp")

        if arcpy.Exists(stops_export_path):
            # Use Near tool to find the closest stop to the user location
            arcpy.analysis.Near(stops_export_path, user_location_feature, method="GEODESIC", nearest_location_table=stops_to_user_loc_table)

            # Retrieve the nearest stop from the table
            with arcpy.da.SearchCursor(stops_to_user_loc_table, ["NEAR_FID", "NEAR_DIST"], sql_clause=(None, "ORDER BY NEAR_DIST")) as cursor:
                row = cursor.next()
                nearest_stop = row[0]
                nearest_stops.append(nearest_stop)

    # Find the closest stop among all GTFS folders
    closest_stop = None
    min_distance = float("inf")

    for stop in nearest_stops:
        distance = distance_to(user_location, stop)
        if distance < min_distance:
            min_distance = distance
            closest_stop = stop

    return closest_stop

def distance_to(point1, point2):
    dx = point1.X - point2.X
    dy = point1.Y - point2.Y
    return (dx**2 + dy**2)**0.5

def get_stop_details(stop_id, folder_path, gtfs_folders):
    stop_info = {}

    for gtfs_folder in gtfs_folders:
        stops_export_path = os.path.join(folder_path, gtfs_folder, f"{gtfs_folder}_gtfs_StopsExport.shp")

        if arcpy.Exists(stops_export_path):
            fields = ["STOP_NAME", "STOP_LAT", "STOP_LON"]

            with arcpy.da.SearchCursor(stops_export_path, fields, f"OBJECTID = {stop_id}") as cursor:
                row = cursor.next()
                stop_info["name"] = row[0]
                stop_info["latitude"] = row[1]
                stop_info["longitude"] = row[2]
                break

    return stop_info

def get_user_location():
    # Prompt user for current location coordinates (x, y)
    user_x = float(input("Enter the X coordinate of the user's current location: "))
    user_y = float(input("Enter the Y coordinate of the user's current location: "))

    return arcpy.Point(user_x, user_y)

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

    # Do all of the table joins
    process_gtfs_data(FolderPath, GTFSFolders)
    
    # Get user location
    print("Please enter the user's current location:")
    user_location = get_user_location()

    # Find closest stop
    print("Finding the closest stop to the user's current location...")
    closest_stop = find_closest_stop(user_location, FolderPath, GTFSFolders)

    if closest_stop is not None:
        print("Closest stop found!")

        # Get stop details
        print("Retrieving stop details...")
        stop_info = get_stop_details(closest_stop, FolderPath, GTFSFolders)

        print("Closest stop to user's current location:")
        print(f"Name: {stop_info['name']}")
        print(f"Latitude: {stop_info['latitude']}")
        print(f"Longitude: {stop_info['longitude']}")
    else:
        print("No closest stop found.")
        
if __name__ == "__main__":
    main()
