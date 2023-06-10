import arcpy
arcpy.ImportToolbox(r"@\Network Analyst Tools.tbx")
arcpy.na.MakeClosestFacilityAnalysisLayer(
    network_data_source="https://www.arcgis.com/",
    layer_name="Closest Facility 2",
    travel_mode="Driving Time",
    travel_direction="TO_FACILITIES",
    cutoff=None,
    number_of_facilities_to_find=1,
    time_of_day=None,
    time_zone="LOCAL_TIME_AT_LOCATIONS",
    time_of_day_usage="START_TIME",
    line_shape="ALONG_NETWORK",
    accumulate_attributes=None,
    generate_directions_on_solve="NO_DIRECTIONS",
    ignore_invalid_locations="SKIP"
)

arcpy.na.AddLocations(
    in_network_analysis_layer="Closest Facility 2",
    sub_layer="Facilities",
    in_table="StopsOnStreets",
    field_mappings="Name # #;CurbApproach # 0;Attr_Minutes # 0;Attr_TravelTime # 0;Attr_Miles # 0;Attr_Kilometers # 0;Attr_TimeAt1KPH # 0;Attr_WalkTime # 0;Attr_TruckMinutes # 0;Attr_TruckTravelTime # 0;Cutoff_Minutes # #;Cutoff_TravelTime # #;Cutoff_Miles # #;Cutoff_Kilometers # #;Cutoff_TimeAt1KPH # #;Cutoff_WalkTime # #;Cutoff_TruckMinutes # #;Cutoff_TruckTravelTime # #",
    search_tolerance="20000 Meters",
    sort_field=None,
    search_criteria="main.Routing_Streets SHAPE",
    match_type="MATCH_TO_CLOSEST",
    append="APPEND",
    snap_to_position_along_network="NO_SNAP",
    snap_offset="5 Meters",
    exclude_restricted_elements="EXCLUDE",
    search_query=None,
    allow_auto_relocate="ALLOW"
)

arcpy.na.Solve(
    in_network_analysis_layer="Closest Facility 2",
    ignore_invalids="SKIP",
    terminate_on_solve_error="TERMINATE",
    simplification_tolerance=None,
    overrides=""
)
