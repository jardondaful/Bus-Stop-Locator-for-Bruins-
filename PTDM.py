
import arcpy
import os 

# Setting up folder paths and workspace
FolderPath = r"C:\Users\lexiw\Desktop\181C\FinalProject\MyProject26"   #### CHANGE TO PROJECT 1
arcpy.env.workspace = FolderPath
arcpy.env.overwriteOutput = True


# set variables for new GDB
GDBName = "NewGDbase"

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
arcpy.na.BuildNetwork(ND)
print("network built. good job")


