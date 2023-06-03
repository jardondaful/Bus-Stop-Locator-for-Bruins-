import os
import arcpy
import gtfs_shapes_to_features
import math

folder_path = r"C:\Users\julyquintero\Downloads\MyProject26"
GTFSFolders = [
    "AVTA-GTFS",
    "BigBlue_gtfs",
    "BruinBus_gtfs",
    "CulverCity_GTFS",
    "LAdot_gtfs",
    "Santa Clarita",
    "lbt_gtfs"
]


# "metro_gtfs_bus"   - issues w code



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
        trips2 = arcpy.management.JoinField(in_data=export_trips, in_field="trip_id", join_table=export_stop_times,
                                             join_field="trip_id")

        # Join stop times to stops via stop_id field
        trips3 = arcpy.management.JoinField(in_data=trips2, in_field="stop_id", join_table=export_stops,
                                             join_field="stop_id")

        # Join all the joined tables with the shapes to features called GTFSHome via the route_id field
        trips_shapes = arcpy.management.JoinField(in_data=shapes_to_features, in_field="route_id", join_table=trips3,
                                                    join_field="route_id")

        # Get the bus name from the gtfs_folder
        bus_name = gtfs_folder.split('_')[0]

        # Check if agency_id field exists, if not, add it
        field_names = [field.name for field in arcpy.ListFields(trips_shapes)]
        if "agency_id" not in field_names:
            arcpy.AddField_management(trips_shapes, "agency_id", "TEXT")

        # Update agency_id field with bus_name
        with arcpy.da.UpdateCursor(trips_shapes, ["agency_id"]) as cursor:
            for row in cursor:
                row[0] = bus_name
                cursor.updateRow(row)

        print("Done with updating table.")

        # Export GTFS shapefile with everything joined
        gtfs_complete = os.path.join(gtfs_path, f"{bus_name}_GTFSComplete.shp")
        arcpy.conversion.ExportFeatures(in_features=trips_shapes, out_features=gtfs_complete)

        print(f"Processing {gtfs_folder} - done!")
        print(f"The complete GTFS shapefile can be found in the {gtfs_folder} folder titled {bus_name}_GTFSComplete.shp")
        print("\n")


# Call the function with the provided parameters
process_gtfs_data(folder_path, GTFSFolders)


