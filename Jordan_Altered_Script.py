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
        arcpy.management.JoinField(stop_times_table, "stop_id", stops_table, "stop_id", stops_table_name)

        # Join trips to stop_times via trip_id
        arcpy.management.JoinField(stop_times_table, "trip_id", trips_table, "trip_id", trips_table_name)

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
        i += 1
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

def find_closest_source_stop(user_latitude, user_longitude, merged_stop_times_table):
    # Set the workspace
    arcpy.env.workspace = arcpy.env.workspace
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

def find_closest_valid_dest_stop(user_latitude, user_longitude, merged_stop_times_table):
    # Set the workspace
    arcpy.env.workspace = arcpy.env.workspace
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

def main():
    folder_path = r"C:\Users\Jordan Lin\Downloads\GEOG_181C\MyProject26\MyProject26"
    gtfs_folders = [
        "AVTA-GTFS",
        "BigBlue_GTFS"
    ]
    
    gtfs_joined_folders = [
        "AVTA_GTFS_StopTimes",
        "BigBlue_GTFS_StopTimes"
    ]

#     # Convert GTFS text files to tables
#     convert_gtfs_txt_to_tables(folder_path, gtfs_folders)
#     print("\n")
    
#     # Create joins between tables
#     create_joins(folder_path, gtfs_folders)
#     print("\n")
    
#     # Add agency_id field
#     add_agency_id_field(folder_path, gtfs_folders, gtfs_joined_folders)
#     print("\n")
    
#     # Merge stop_times tables
#     merge_stop_times_tables(folder_path, gtfs_folders, "MergedTable")
#     print("\n")
    
    user_latitude, user_longitude = get_user_location()
    
    # Find closest source stop
    closest_source_stop_id, closest_source_distance = find_closest_source_stop(user_latitude, user_longitude, os.path.join(folder_path, "MergedTable"))
    
    print("\nSearching...\n")
    print(f"The closest source bus stop is {closest_source_stop_id} which is {closest_source_distance} units away from your location.")
    print("\n")
    
    # Define the source_route_id variable here or retrieve it from your data
    source_route_id = "your_source_route_id"
    
    dest_latitude, dest_longitude = get_user_location()
    closest_destination_stop_id, closest_destination_distance = find_closest_valid_dest_stop(dest_latitude, dest_longitude, os.path.join(folder_path, "MergedTable"))
    
    print("\nSearching...")
    print(f"The closest valid destination bus stop is {closest_destination_stop_id} which is {closest_destination_distance} units away from your location.")
    print("\n")

main()
