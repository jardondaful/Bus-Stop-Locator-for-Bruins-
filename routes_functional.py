import arcpy
import os 

# Setting up folder paths and workspace
FolderPath = r"C:\Users\lexiw\Desktop\181C\FinalProject\MyProject26"   #### CHANGE TO PROJECT 1
arcpy.env.workspace = FolderPath
arcpy.env.overwriteOutput = True


# set variables for new GDB
GDBName = "NewGDbase"
ProjectGDB = os.path.join(FolderPath, "NewGDbase.gdb")

# create new file geodatabase (parallel to the project gdb), PTMD requires gdb without any existing transit data, seems cleanest to create new gdb
arcpy.management.CreateFileGDB(FolderPath, GDBName, "CURRENT")
print("new file geodatabase created")


# Set variables for creating new feature dataset
OutPath = os.path.join(FolderPath, "NewGDbase.gdb")
OutName = "PTDM_fds"
    # the target feature dataset having a spatial reference is ESSENTIAL, PTDM will not be created without
SpatialRef = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'

# Create new feature dataset
FDS = arcpy.management.CreateFeatureDataset(OutPath, OutName, SpatialRef)
print("new feature dataset created")

# set variables for public transit data model
#BruinBus = os.path.join(FolderPath, "Bruinbus_gtfs")
BigBlue = os.path.join(FolderPath, "BigBlue_gtfs")
CulverCity = os.path.join(FolderPath, "CulverCity_gtfs")
AVTA = os.path.join(FolderPath, "AVTA_gtfs")
LAdot = os.path.join(FolderPath, "LAdot_gtfs")
LAX = os.path.join(FolderPath, "LAX_gtfs")
SantaClarita = os.path.join(FolderPath, "SantaClarita_gtfs")        # FULLY FUNCTIONAL JUST TAKES AWHILE
LBT = os.path.join(FolderPath, "LBT_gtfs")

In_gtfs = [BigBlue, CulverCity, AVTA, LAdot, LAX, SantaClarita, LBT]



# Create public transit data model
print("creating public transit data model....this will take a minute")
arcpy.transit.GTFSToPublicTransitDataModel(In_gtfs, FDS, "INTERPOLATE", "NO_APPEND")
print("Data Model created")

# update clear path to access new feature dataset/public transit data model 
PDTM_Path = FolderPath + "\\" + "NewGDbase.gdb" + "\\" + "PTDM_fds"

# set street variables
streets = os.path.join(FolderPath, "Streets")
StreetsName = "Streets"
OutStreets = os.path.join(PDTM_Path, StreetsName)

# Copy streets into our 
arcpy.management.CopyFeatures(streets, OutStreets)
print("streets copied")


# connect streets to PTDM
arcpy.transit.ConnectPublicTransitDataModelToStreets(PDTM_Path, OutStreets)
print("streets connected")
print("Public transit data model completed")


# variables for creating network dataset
Template = os.path.join(FolderPath, "TransitNetworkTemplate")

# Create Network Dataset Utilizing Template
ND = arcpy.na.CreateNetworkDatasetFromTemplate(Template, PDTM_Path)
print("break. ND created")


#Build Network
NW = arcpy.na.BuildNetwork(ND)
print("network built. good job")

##### ROUTE NETWORK 

arcpy.env.workspace = ProjectGDB
arcpy.env.overwriteOutput = True

#make Route  analysis layer
route_object = arcpy.na.MakeRouteAnalysisLayer(
    network_data_source=NW,
    layer_name="Route",
    travel_mode="Public transit time",
    sequence="USE_CURRENT_ORDER",
    time_of_day=None,
    time_zone="LOCAL_TIME_AT_LOCATIONS",
    line_shape="ALONG_NETWORK",
    accumulate_attributes=None,
    generate_directions_on_solve="DIRECTIONS",
    time_zone_for_time_fields="LOCAL_TIME_AT_LOCATIONS",
    ignore_invalid_locations="SKIP")
print("Route analysis layer created")

# access route analysis layer as objects
route_layer_object = route_object.getOutput(0)
route_output_layer = os.path.join(ProjectGDB, route_layer_object.name + ".lyrx")
sublyrNames = arcpy.na.GetNAClassNames(route_layer_object)
stops_lyrName = sublyrNames["Stops"]

# add locations to route analysis layer
arcpy.na.AddLocations(
    in_network_analysis_layer=route_layer_object,
    sub_layer=stops_lyrName,
    in_table= os.path.join(FolderPath, "Test_Points.shp"),
    field_mappings="Name # #;RouteName # #;Sequence # #;TimeWindowStart # #;TimeWindowEnd # #;LocationType # 0;CurbApproach # 0;Attr_PublicTransitTime # 0;Attr_WalkTime # 0;Attr_Length # 0",
    search_tolerance="5000 Meters",
    sort_field=None,
    search_criteria="StopConnectors SHAPE;Streets SHAPE;Stops SHAPE;StopsOnStreets SHAPE;TransitNetwork_ND_Junctions NONE",
    match_type="MATCH_TO_CLOSEST",
    append="APPEND",
    snap_to_position_along_network="NO_SNAP",
    snap_offset="5 Meters",
    exclude_restricted_elements="EXCLUDE",
    search_query=None,
    allow_auto_relocate="ALLOW")
print("Add locations completed")

# solve route analysis layer
arcpy.na.Solve(route_layer_object)
print("Route Solved")

# Save solved route analysis layer
route_layer_object.saveACopy(route_output_layer)

print("route layer saved. slay")

