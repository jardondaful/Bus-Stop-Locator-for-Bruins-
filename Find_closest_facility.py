# Name: MakeClosestFacilityAnalysisLayer_Workflow.py
# Description: Find the closest bus stop from the user location and save the
#              results to a layer file on disk.
# Requirements: Network Analyst Extension

#Import system modules
import arcpy
from arcpy import env
import os

try:
    #Check out Network Analyst license if available. Fail if the Network Analyst license is not available.
    if arcpy.CheckExtension("network") == "Available":
        arcpy.CheckOutExtension("network")
    else:
        raise arcpy.ExecuteError("Network Analyst Extension license is not available.")
    
    #Set environment settings
    #output_dir = "C:/Data"
    #The NA layer's data will be saved to the workspace specified here
    #env.workspace = os.path.join(output_dir, "Output.gdb")
    #env.overwriteOutput = True

    #Set environment settings
    #folder_path = r"C:\Users\julyquintero\Downloads\MyProject1" # output_dir
    folder_path = r"C:\Users\julyquintero\Downloads\Find_Closest_Facility\MyProject1"
    ProjectGDB = os.path.join(folder_path, "MyProject1.gdb") 
    #The NA layer's data will be saved to the workspace specified here
    env.workspace = ProjectGDB #
    env.overwriteOutput = True


    #Set local variables
    #input_gdb = "C:/Data/Paris.gdb" #because already project GDB
    network = "https://www.arcgis.com/"
    layer_name = "ClosestBusStop" #
    travel_mode = "Walking Distance" #
    facilities = os.path.join(ProjectGDB, "TransitInfo", "StopsOnStreets")
    incidents = os.path.join(folder_path, "Geocoded_points.shp")
    output_layer_file = os.path.join(ProjectGDB, layer_name + ".lyrx")

    #Create a new closest facility analysis layer. 
    #result_object = arcpy.na.MakeClosestFacilityAnalysisLayer(network,
                                    #layer_name, travel_mode, "TO_FACILITIES",
                                    #number_of_facilities_to_find=1, generate_directions_on_solve="DIRECTIONS")


    #Create Closest Facility Analyst Layer
    #arcpy.ImportToolbox(r"@\Network Analyst Tools.tbx")
    result_object = arcpy.na.MakeClosestFacilityAnalysisLayer(
        network_data_source="https://www.arcgis.com/",
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


    #Get the layer object from the result object. The closest facility layer can
    #now be referenced using the layer object.
    layer_object = result_object.getOutput(0)

    #Get the names of all the sublayers within the closest facility layer.
    sublayer_names = arcpy.na.GetNAClassNames(layer_object)
    #Stores the layer names that we will use later
    facilities_layer_name = sublayer_names["Facilities"]
    incidents_layer_name = sublayer_names["Incidents"]

    # Add this line to define directions_layer_name
    #directions_layer_name = sublayer_names["Directions"]

    #Load the bus stops as Facilities using the default field mappings and
    #search tolerance
    arcpy.na.AddLocations(layer_object, facilities_layer_name,
                            facilities, "", "")
    print("adding bus stop locations")

    #Load the user location as Incidents. Map the Name property from the NOM field
    #using field mappings
    field_mappings = arcpy.na.NAClassFieldMappings(layer_object,
                                                    incidents_layer_name)
    field_mappings["Name"].mappedFieldName = "NOM"
    arcpy.na.AddLocations(layer_object, incidents_layer_name, incidents,
                          field_mappings, "")
    print("loading user location")

    #Solve the closest facility layer
    arcpy.na.Solve(layer_object)

    #CHAT
    # Check if the directions sublayer exists
    if "Directions" in sublayer_names:
        directions_sublayer = layer_object.listLayers("Directions")[0]

    # Print the directions
        with arcpy.da.SearchCursor(directions_sublayer, ["Text", "Length"]) as cursor:
            for row in cursor:
                direction_text = row[0]
                direction_length = row[1]
                print("Direction: {}, Length: {}".format(direction_text, direction_length))
    else:
        print("Directions sublayer does not exist.")

    #Save the solved closest facility layer as a layer file on disk
    layer_object.saveACopy(output_layer_file)

    print("Script completed successfully")

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print("An error occurred on line %i" % tb.tb_lineno)
    print(str(e))


