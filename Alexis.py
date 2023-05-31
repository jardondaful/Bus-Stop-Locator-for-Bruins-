# Lexi_createBruin_Shp.py  REUPLOAD
# BRUIN BUS ONLY

import os
import arcpy
import gtfs_shapes_to_features

FolderPath = r"C:\Users\lexiw\Desktop\181C\FinalProject\MyProject26"

arcpy.env.overwriteOutput = True
arcpy.env.workspace = FolderPath


ProjectGDB = os.path.join(FolderPath, "MyProject26.gdb")
BruinBusGTFS = os.path.join(FolderPath, "BruinBusGTFS")


BruinShapes = os.path.join (BruinBusGTFS, "shapes.txt")
BruinTrips = os.path.join(BruinBusGTFS, "trips.txt")
BruinStopTime = os.path.join(BruinBusGTFS, "stop_times.txt")
BruinStops = os.path.join(BruinBusGTFS, "stops.txt")


# create empty feature dataset for the gtfs shapes to features
ShapesToFeatures = arcpy.management.CreateFeatureclass(out_path=ProjectGDB, out_name="BruinBusHome")

# Process: GTFS Shapes To Features (GTFS Shapes To Features) (transit)
arcpy.transit.GTFSShapesToFeatures(BruinShapes, ShapesToFeatures)

# export trips text file to editable table
ExportTrips = os.path.join(BruinBusGTFS, "TripsExport.gdb")
arcpy.conversion.ExportTable(in_table=BruinTrips, out_table=ExportTrips)

# export stop times text file to editable table
ExportStopTimes = os.path.join(BruinBusGTFS, "StopTimesExport.gdb")
arcpy.conversion.ExportTable(in_table=BruinStopTime, out_table=ExportStopTimes)

# export stops text file to editable table
ExportStops = os.path.join(BruinBusGTFS, "StopsExport.gdb")
arcpy.conversion.ExportTable(in_table=BruinStops, out_table=ExportStops)



# Process: Join trips to stop times via trip_id field
Trips2 = arcpy.management.JoinField(in_data=ExportTrips, in_field="trip_id", join_table=ExportStopTimes, join_field="trip_id")

# Process: Join stop times to stops via stop_id field
Trips3 = arcpy.management.JoinField(in_data=Trips2, in_field="stop_id", join_table=ExportStops, join_field="stop_id")

# Join all the joined tables with the shapes to features called BruinBusHome via the route_id field
Trips_Shapes = arcpy.management.JoinField(in_data=ShapesToFeatures, in_field="route_id", join_table=Trips3, join_field="route_id")

# Export BruinBus shapefile with everything joined
BruinComplete = os.path.join(BruinBusGTFS, "BruinComplete.shp")
arcpy.conversion.ExportFeatures(in_features=Trips_Shapes, out_features=BruinComplete)


print("done!!!!!!")
print("complete BruinBus shapefile can be found in the BruinBusGTFS folder titled BruinComplete.shp")

