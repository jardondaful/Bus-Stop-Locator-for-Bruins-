
import arcpy
from arcpy import env
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
ProjectGDB = os.path.join(FolderPath, "NewGDbase.gdb")
OutName = "PTDM_fds"
    # the target feature dataset having a spatial reference is ESSENTIAL, PTDM will not be created without
SpatialRef = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'

# Create new feature dataset
FDS = arcpy.management.CreateFeatureDataset(ProjectGDB, OutName, SpatialRef)
print("new feature dataset created")

# set variables for public transit data model
#BruinBus = os.path.join(FolderPath, "Bruinbus_gtfs")
BigBlue = os.path.join(FolderPath, "BigBlue_gtfs")
CulverCity = os.path.join(FolderPath, "CulverCity_gtfs")
##AVTA = os.path.join(FolderPath, "AVTA_gtfs")
##LAdot = os.path.join(FolderPath, "LAdot_gtfs")
##LAX = os.path.join(FolderPath, "LAX_gtfs")
##SantaClarita = os.path.join(FolderPath, "SantaClarita_gtfs")        # FULLY FUNCTIONAL JUST TAKES AWHILE
##LBT = os.path.join(FolderPath, "LBT_gtfs")

#In_gtfs = [BigBlue, CulverCity, AVTA, LAdot, LAX, SantaClarita, LBT]
In_gtfs = [BigBlue, CulverCity]

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


# geocoding 
import requests

def geocode_address(address, label):
    # Set up geocoding service URL
    url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"

    # Create the request payload
    params = {
        "SingleLine": address,
        "f": "json",
        "outSR": "4326"
    }

    # Send the request and retrieve the response
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Check if there are any candidates found
        if "candidates" in data:
            # Get the first candidate
            candidate = data["candidates"][0]

            # Extract the latitude and longitude
            location = candidate["location"]
            latitude = location["y"]
            longitude = location["x"]

            print("{} - Latitude: {}, Longitude: {}".format(label, latitude, longitude))

            return (longitude, latitude)  # Return the coordinates
        else:
            print("No candidates found.")
    else:
        print("Request failed.")

    return None  # Return None if geocoding fails


# Take user input for addresses
starting_address = input("Enter the starting address: ")
desired_address = input("Enter the desired address: ")

starting_coords = geocode_address(starting_address, "Starting Location")
desired_coords = geocode_address(desired_address, "Desired Location")

if starting_coords and desired_coords:
    # Create a new shapefile
    output_shapefile = "geocoded_points.shp"
    arcpy.env.workspace = FolderPath
    arcpy.env.overwriteOutput = True
    arcpy.management.CreateFeatureclass(FolderPath, output_shapefile, "POINT", spatial_reference=arcpy.SpatialReference(4326))

    # Add a field to store the location labels
    arcpy.management.AddField(output_shapefile, "Location", "TEXT")

    # Create a new feature and insert the points
    with arcpy.da.InsertCursor(output_shapefile, ['SHAPE@XY', 'Location']) as cursor:
        cursor.insertRow([(starting_coords[0], starting_coords[1]), "Starting Location"])
        cursor.insertRow([(desired_coords[0], desired_coords[1]), "Desired Location"])

    print("Shapefile created successfully.")


### begin closest facility analysis
try:
    #Check out Network Analyst license if available. Fail if the Network Analyst license is not available.
    if arcpy.CheckExtension("network") == "Available":
        arcpy.CheckOutExtension("network")
    else:
        raise arcpy.ExecuteError("Network Analyst Extension license is not available.")
    
    env.workspace = ProjectGDB 
    env.overwriteOutput = True


    #Create Closest Facility Analyst Layer
    result_object = arcpy.na.MakeClosestFacilityAnalysisLayer(
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
    )
    print("Creating a Closest Facility Analyst Layer ...")

# access closest facility layer and sublayers 
    layer_object = result_object.getOutput(0)
    output_layer_file = os.path.join(ProjectGDB, layer_object.name + ".lyrx")
    sublayer_names = arcpy.na.GetNAClassNames(layer_object)
    facilities_lyrName = sublayer_names["Facilities"]
    incidents_lyrName = sublayer_names["Incidents"]
    facilities_sublyr = arcpy.na.GetNASublayer(layer_object, "Facilities")
    incidents_sublyr = arcpy.na.GetNASublayer(layer_object, "Incidents")

    facilities = os.path.join(ProjectGDB, "PTDM_fds", "StopsOnStreets")
    incidents = os.path.join(FolderPath, output_shapefile)


# Check if the directions sublayer exists
##    if "Facilities" in sublayer_names:
##        print("Faciliteies layer Found")    ###   THIS CAN BE REMOVED COMPLETELY, BUT HELPFUL TO CHECK IF OBJECTS ARE ACCESSED
##
##    else:
##        print("Facilities sublayer does not exist.")


    #Load the bus stops as Facilities using the default field mappings 
    arcpy.na.AddLocations(layer_object, facilities_lyrName, facilities)
    print("adding bus stop locations")

    #Load the user location as Incidents. Map the Name property from the NOM field
    #using field mappings
    field_mappings = arcpy.na.NAClassFieldMappings(layer_object, incidents_lyrName)
    field_mappings["Name"].mappedFieldName = "NOM"
    arcpy.na.AddLocations(layer_object, incidents_lyrName, incidents)   

    print("loading user location")

    #Solve the closest facility layer
    arcpy.na.Solve(layer_object)

    #Save the solved closest facility layer as a layer file on disk
    layer_object.saveACopy(output_layer_file)

    print("Script completed successfully")

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print("An error occurred on line %i" % tb.tb_lineno)
    print(str(e))

