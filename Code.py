# Printing name and date information
print("Claire Keeshen")
print("Lab 7")
print("05/21/2023")

# Setting up folder paths and creating necessary directories
folder_path = r"C:\Users\crkeeshen\Desktop\Final"
arcpy.env.overwriteOutput = True
Input_folder = os.path.join(folder_path, "LabData")
Output_folder = os.path.join(folder_path, "Output")
#Arc_GIS_Folder = os.path.join(folder_path, "MyProjectKeeshen_C_7")

Roads = os.path.join(Input_folder, "Roads")

#create feature dataset for each agency
with arcpy.EnvManager(outputCoordinateSystem='PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]'):
    arcpy.management.CreateFeatureDataset(
        out_dataset_path=r"C:\Users\crkeeshen\Desktop\MyProject26\MyProject26\MyProject26.gdb",
        out_name="Public_transit_model",
        spatial_reference='PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]];-20037700 -30241100 10000;#;#;0.001;#;#;IsHighPrecision'
    )
#GTFS to public Transit data model for each agency within its own dataset
arcpy.transit.GTFSToPublicTransitDataModel(
    in_gtfs_folders=r"C:\Users\crkeeshen\Desktop\GTFS\BigBlue_gtfs;C:\Users\crkeeshen\Desktop\GTFS\BruinBus_gtfs;'C:\Users\crkeeshen\Desktop\GTFS\CulverCity_GTFS (1)';C:\Users\crkeeshen\Desktop\GTFS\lbt_gtfs;C:\Users\crkeeshen\Desktop\GTFS\LAdot_gtfs;'C:\Users\crkeeshen\Desktop\GTFS\Santa Clarita';C:\Users\crkeeshen\Desktop\GTFS\AVTA-GTFS",
    target_feature_dataset=r"C:\Users\crkeeshen\Desktop\MyProject1\Agencys.gdb\FeatureData",
    interpolate="INTERPOLATE",
    append="NO_APPEND"
)
)
# upload the streets shp file


#write code to move roads to dataset
#Connect streers to transit data model warning happens about projections. 
arcpy.transit.ConnectPublicTransitDataModelToStreets(
    target_feature_dataset=r"C:\Users\crkeeshen\Desktop\MyProject26\MyProject26\test.gdb\featuredtaset",
    in_streets_features="tl_2018_06037_roads",
    search_distance="100 Meters",
    expression=""

#Create netwrod dataset utlizing feature dataset
    
)arcpy.na.CreateNetworkDataset(
    feature_dataset=r"C:\Users\crkeeshen\Desktop\MyProject26\MyProject26\test.gdb\featuredtaset",
    out_name="Natword_dataset", #typo sample name
    source_feature_class_names="Stops;LineVariantElements;StopsOnStreets;StopConnectors",
    elevation_model="ELEVATION_FIELDS"

    
)
#Build network dataset
arcpy.na.BuildNetwork(
    in_network_dataset=r"C:\Users\crkeeshen\Desktop\MyProject26\MyProject26\test.gdb\featuredtaset\Natword_dataset"
)
#make Service area analysis layer
arcpy.na.MakeServiceAreaAnalysisLayer(
    network_data_source="https://www.arcgis.com/",
    layer_name="Service Area",
    travel_mode="Driving Time",
    travel_direction="FROM_FACILITIES",
    cutoffs=[5,10,15],
    time_of_day=None,
    time_zone="LOCAL_TIME_AT_LOCATIONS",
    output_type="POLYGONS",
    polygon_detail="STANDARD",
    geometry_at_overlaps="OVERLAP",
    geometry_at_cutoffs="RINGS",
    polygon_trim_distance="100 Meters",
    exclude_sources_from_polygon_generation=None,
    accumulate_attributes=None,
    ignore_invalid_locations="SKIP"
)
#solve
arcpy.na.Solve(
    in_network_analysis_layer="Service Area",
    ignore_invalids="SKIP",
    terminate_on_solve_error="TERMINATE",
    simplification_tolerance=None,
    overrides=""
)
