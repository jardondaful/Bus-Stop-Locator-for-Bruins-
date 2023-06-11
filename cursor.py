import arcpy
from arcpy import env
import os

#Set environment settings
#folder_path = r"C:\Users\julyquintero\Downloads\MyProject1" # output_dir
folder_path = r"C:\Users\julyquintero\Downloads\Find_Closest_Facility\MyProject1New"
ProjectGDB = os.path.join(folder_path, "MyProject1.gdb") 
#The NA layer's data will be saved to the workspace specified here
env.workspace = ProjectGDB #
env.overwriteOutput = True



DirectionPoints = os.path.join(ProjectGDB, "ClosestFacilitySolver15zctac", "ClosestFacilitySolver15zctac_DirectionPoints")

with arcpy.da.SearchCursor(DirectionPoints, ["ObjectID", "DisplayText", "FacilityID"]) as cursor:
    for row in cursor:
        object_id = row[0]
        display_text = row[1]
        facility_id = row[2]

        print(f"Display Text: {display_text}")
        
        if facility_id is not None:
            print(f"Incident ID: {facility_id}")
