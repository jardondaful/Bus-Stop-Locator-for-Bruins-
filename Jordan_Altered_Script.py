import os
import arcpy
import math

def convert_gtfs_txt_to_tables(folder_path, gtfs_folders):
    print("CONVERTING GTFS TXT TO TABLES")
    # Convert GTFS text files to editable tables
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = folder_path

    for gtfs_folder in gtfs_folders:
        gtfs_path = os.path.join(folder_path, gtfs_folder)

        gtfs_stop_times = os.path.join(gtfs_path, "stop_times.txt")
        gtfs_stops = os.path.join(gtfs_path, "stops.txt")
        gtfs_trips = os.path.join(gtfs_path, "trips.txt")

        # Output geodatabase for the editable tables
        export_gdb = os.path.join(gtfs_path, "GTFSExport.gdb")

        # Create the geodatabase if it doesn't exist
        if not arcpy.Exists(export_gdb):
            arcpy.management.CreateFileGDB(gtfs_path, "GTFSExport.gdb")

        # Generate a valid table name based on the bus system
        stop_times_table_name = arcpy.ValidateTableName(f"{gtfs_folder}_StopTimes", export_gdb)
        stops_table_name = arcpy.ValidateTableName(f"{gtfs_folder}_Stops", export_gdb)
        trips_table_name = arcpy.ValidateTableName(f"{gtfs_folder}_Trips", export_gdb)

        # Export stop times text file to editable table
        stop_times_table = os.path.join(export_gdb, stop_times_table_name)
        arcpy.conversion.TableToTable(gtfs_stop_times, export_gdb, stop_times_table_name)

        # Export stops text file to editable table
        stops_table = os.path.join(export_gdb, stops_table_name)
        arcpy.conversion.TableToTable(gtfs_stops, export_gdb, stops_table_name)

        # Export trips text file to editable table
        trips_table = os.path.join(export_gdb, trips_table_name)
        arcpy.conversion.TableToTable(gtfs_trips, export_gdb, trips_table_name)

        print(f"GTFS text files converted to editable tables for {gtfs_folder}!")

    # Set the workspace to the geodatabase
    arcpy.env.workspace = export_gdb

    # Alter field types to text for all fields in the tables
    arcpy.management.AlterFields(stop_times_table, "agency_id TEXT; stop_id TEXT; trip_id TEXT; arrival_time TEXT; departure_time TEXT; stop_sequence TEXT; pickup_type TEXT; drop_off_type TEXT; shape_dist_traveled TEXT")
    arcpy.management.AlterFields(stops_table, "stop_id TEXT; stop_code TEXT; stop_name TEXT; stop_desc TEXT; stop_lat TEXT; stop_lon TEXT; zone_id TEXT; stop_url TEXT; location_type TEXT; parent_station TEXT; wheelchair_boarding TEXT")
    arcpy.management.AlterFields(trips_table, "route_id TEXT; service_id TEXT; trip_id TEXT; trip_headsign TEXT; direction_id TEXT; block_id TEXT; shape_id TEXT")

    print("Field types converted to text for all tables.")

    # Return the paths to the exported tables
    return stop_times_table, stops_table, trips_table

        
def create_joins(folder_path, gtfs_folders):
    print("CREATING JOINS")
    # Set the workspace
    arcpy.env.workspace = folder_path

    for gtfs_folder in gtfs_folders:
        gtfs_path = os.path.join(folder_path, gtfs_folder)

        # Get the unique names for the output joined tables
        stops_table_name = f"{gtfs_folder}_StopsJoin"
        stop_times_table_name = f"{gtfs_folder}_StopTimesJoin"
        trips_table_name = f"{gtfs_folder}_TripsJoin"

        # Get the paths of the editable tables
        stops_table = os.path.join(gtfs_path, "StopsExport")
        stop_times_table = os.path.join(gtfs_path, "StopTimesExport")
        trips_table = os.path.join(gtfs_path, "TripsExport")

        # Join stops to stop_times via stop_id
        # Specify the field mapping with explicit field types as text
        arcpy.management.JoinField(stop_times_table, "stop_id", stops_table, "stop_id", stops_table_name, "agency_id TEXT;stop_name TEXT;stop_lat TEXT;stop_lon TEXT")

        # Join trips to stop_times via trip_id
        # Specify the field mapping with explicit field types as text
        arcpy.management.JoinField(stop_times_table, "trip_id", trips_table, "trip_id", trips_table_name, "route_id TEXT")

        print(f"Joins created for {gtfs_folder}!")



def add_agency_id_field(folder_path, gtfs_folders, gtfs_joined_folders):
    print("ADDING AGENCY_ID FIELD")
    i = 0
    for gtfs_folder in gtfs_folders:
        gtfs_path = os.path.join(folder_path, gtfs_folder, "GTFSExport.gdb", gtfs_joined_folders[i])

        # Check if agency_id field exists, if not, add it
        field_names = [field.name for field in arcpy.ListFields(gtfs_path)]
        if "agency_id" not in field_names:
            arcpy.AddField_management(gtfs_path, "agency_id", "TEXT")

        # Update agency_id field with bus_name
        bus_name = gtfs_folder.split('_')[0]
        with arcpy.da.UpdateCursor(gtfs_path, ["agency_id"]) as cursor:
            for row in cursor:
                row[0] = bus_name
                cursor.updateRow(row)
        i = i + 1
        print(f"Agency_ID field added to {gtfs_folder}_StopTimes table.")


def merge_stop_times_tables(folder_path, gtfs_folders, output_table):
    print("MERGING STOP_TIMES TABLES")
    # Set the workspace
    arcpy.env.workspace = folder_path
    arcpy.env.overwriteOutput = True

    # Create a list to store the paths of the stop_times tables to be merged
    stop_times_tables_to_merge = []

    # Loop through the GTFS folders and add the stop_times table paths to the list
    for gtfs_folder in gtfs_folders:
        gtfs_path = os.path.join(folder_path, gtfs_folder)
        stop_times_table = os.path.join(gtfs_path, "StopTimesExport")
        stop_times_tables_to_merge.append(stop_times_table)

    # Merge the stop_times tables
    merged_output_table = os.path.join(folder_path, output_table)
    arcpy.management.Merge(stop_times_tables_to_merge, merged_output_table)

    print(f"Stop_times tables merged into {merged_output_table}!")


def calculate_distance(lat1, lon1, lat2, lon2):
    # Calculate the Euclidean distance between two sets of coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    distance = math.sqrt(dlat ** 2 + dlon ** 2)
    return distance

def get_user_location():
    # Prompt user for current location coordinates (latitude, longitude)
    user_input = input("Enter the coordinates of your current location (latitude, longitude): ")
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
    arcpy.env.workspace = FolderPath
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


def main():
    FolderPath = r"C:\Users\Jordan Lin\Downloads\GEOG_181C\MyProject26\MyProject26"
    GTFSFolders = [
        "AVTA-GTFS",
        "BigBlue_GTFS"
    ]

    GTFSJoinedFolders = [
        "AVTA_GTFS_StopTimes",
        "BigBlue_GTFS_StopTimes"
    ]

#     convert_gtfs_txt_to_tables(FolderPath, GTFSFolders)
#     print("\n")
#     create_joins(FolderPath, GTFSFolders)
#     print("\n")
#     add_agency_id_field(FolderPath, GTFSFolders, GTFSJoinedFolders)
#     print("\n")
#     merge_stop_times_tables(FolderPath, GTFSFolders, "MergedTable")
#     print("\n")

    user_latitude, user_longitude = get_user_location()
    print("Finding closest bus stop...")
    closest_stop_id, closest_distance = find_closest_source_stop(
        user_latitude,
        user_longitude,
        os.path.join(FolderPath, "MergedTable"),
        FolderPath
    )

    print("\n")
    print(f"The closest bus stop is {closest_stop_id} which is {closest_distance} units away from your location.")
    print("\n")
    
    # Make sure it has same route ID
    # Either only search within same bus system
    # Or go through ALL of them to see if the closest one also has same route ID

main()
