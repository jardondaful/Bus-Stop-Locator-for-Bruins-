import arcpy

def generate_feature_dataset(gtfs_folders, feature_dataset_path):
    # Create the feature dataset
    arcpy.management.CreateFeatureDataset(
        out_dataset_path=feature_dataset_path,
        out_name="Public_transit_model",
        spatial_reference="PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]"
    )

    # Convert GTFS to Public Transit Data Model for each agency within its own dataset
    arcpy.transit.GTFSToPublicTransitDataModel(
        in_gtfs_folders=gtfs_folders,
        target_feature_dataset=feature_dataset_path,
        interpolate="NO_INTERPOLATE",
        append="NO_APPEND"
    )

    # Connect streets to transit data model
    arcpy.transit.ConnectPublicTransitDataModelToStreets(
        target_feature_dataset=feature_dataset_path,
        in_streets_features="tl_2018_06037_roads",  # Update with your streets shapefile
        search_distance="100 Meters",
        expression=""
    )

    # Create network dataset utilizing feature dataset
    arcpy.na.CreateNetworkDataset(
        feature_dataset=feature_dataset_path,
        out_name="Network_Dataset",
        source_feature_class_names="Stops;LineVariantElements;StopsOnStreets;StopConnectors",
        elevation_model="ELEVATION_FIELDS"
    )

    # Build network dataset
    arcpy.na.BuildNetwork(
        in_network_dataset=feature_dataset_path + "/Network_Dataset"
    )

    # Make Service Area analysis layer
    arcpy.na.MakeServiceAreaAnalysisLayer(
        network_data_source="https://www.arcgis.com/",
        layer_name="Service_Area",
        travel_mode="Driving Time",
        travel_direction="FROM_FACILITIES",
        cutoffs=[5, 10, 15],
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

    # Solve
    arcpy.na.Solve(
        in_network_analysis_layer="Service_Area",
        ignore_invalids="SKIP",
        terminate_on_solve_error="TERMINATE",
        simplification_tolerance=None,
        overrides=""
    )

# Usage example
gtfs_folders = [
    r"C:\path\to\CulverCity_GTFS",
    r"C:\path\to\BigBlue_gtfs",
    r"C:\path\to\BruinBus_gtfs"
]
feature_dataset_path = r"C:\path\to\output.gdb\featuredataset"

generate_feature_dataset
