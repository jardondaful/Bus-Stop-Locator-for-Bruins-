#Julie Quintero
#UID: 405282083
#Week 7


#================================================

import os
import arcpy

# define folder path
folder_path = r'C:\Users\Julie Quintero\Documents\Geog_181C\week_7'

InputFolder = os.path.join(folder_path, 'LabData')
OutputFolder = os.path.join(folder_path, 'Output')

#define workspace as your folder path
arcpy.env.workspace = InputFolder
#allow overwriting output files
arcpy.env.overwriteOutput = True

#=================================================


# Create file variables
finalPDF = os.path.join(OutputFolder, 'Quintero_J_Lab7.pdf')

if os.path.exists(finalPDF): # remove the final pdf if it already exists
    os.remove(finalPDF)

final_file = arcpy.mp.PDFDocumentCreate(finalPDF) # create final pdf
temp_file = os.path.join(OutputFolder, 'temporary.pdf') # create temporary pdf
lake_fc = os.path.join(InputFolder, "NA_Big_Lakes.shp") # lake shapefile path

aprx = arcpy.mp.ArcGISProject(os.path.join(InputFolder, "Quintero_J_Lab7.aprx"))


print("=======================================================================")
print("Creating title page.")


#=================================================

#Alter Symbology

Maps = aprx.listMaps()
for theMap in Maps:
    lyr_list = theMap.listLayers()
    for lyr in lyr_list:
        #print("\t"+lyr.name+": "+lyr.dataSource)
        lyr.visible = True #false
        #lyr.showLabels = True   ##need to alter each individual label
        #need to take them off next time - aprx saved w them on

        #changing symbology
        if lyr.isFeatureLayer:
            sym = lyr.symbology
            #print("Layer: " lyr.name)
            if lyr.name == "North_America":
                print(lyr.symbology)
                sym.renderer.symbol.color = {'RGB' : [243, 237, 211, 100]}
                sym.renderer.symbol.outlineColor = {"RGB": [206, 191, 161, 100]}
                lyr.symbology = sym
                lyr.showLabels = True
                #need to add this
                #change symbolgy of font and color and size

            if lyr.name == "NA_Cities":
                lyr.showLabels = False
                #add later for individual lake maps
            if lyr.name == "NA_Big_Lakes":
                sym.renderer.symbol.color = {'RGB' : [190, 232, 255, 100]}
                sym.renderer.symbol.outlineColor = {"RGB": [128, 185, 215, 100]}
                lyr.symbology = sym
                lyr.showLabels = False
        
aprx.save()

########=====================


# Get the extent of the lake shapefile
desc = arcpy.Describe(lake_fc)
lake_extent = desc.extent
#

theLayout = aprx.listLayouts()[0]
layout_el = theLayout.listElements() #"TEXT_ELEMENT" [0]
for elem in layout_el:
    print(elem.name, ": ", elem.type)
    if elem.type == "TEXT_ELEMENT":
        print(elem.text)


theMapFrame = theLayout.listElements("MAPFRAME_ELEMENT")[0]

theMapFrame.camera.setExtent(lake_extent)
#GreatLakes_ext = arcpy.Extent(255000.0, 25000.0, 1531000.0, 1113000.0) #(Xmin, Ymin, XMax, YMax)
#theMapFrame.camera.setExtent(GreatLakes_ext)
theMapFrame.camera.scale = theMapFrame.camera.scale * 1.2


#Get Lake Data
lake_counter = 0.0
total_area = 0.0
        
for lake in arcpy.da.SearchCursor(lake_fc, ["FID", "Area_km2"]):
    lake_counter += 1.0
    total_area += lake[1]
del lake
    
avg_area = total_area / lake_counter # calculate average area

#Title text element
legend = theLayout.listElements("LEGEND_ELEMENT")[0]  # Replace "LEGEND_ELEMENT_NAME" with the actual name of your legend element
scalebar = theLayout.listElements("MAPSURROUND_ELEMENT")[0]  # Replace "SCALEBAR_ELEMENT_NAME" with the actual name of your scale bar element

# Hide the legend and scale bar
legend.visible = False
scalebar.visible = False
#fix scale bar = still visible

area = theLayout.listElements("TEXT_ELEMENT")[0]
area.text = "Total number of lakes: " + str(int(lake_counter)) + "\n" \
            "Total lake area: " + str(int(total_area)) + " km sq\n" \
            "Average lake area: " + str(int(avg_area)) + " km sq\n"
area.text = "<FNT size = '16'>" + area.text + "</FNT>"  # Font size 24
area.elementPositionX = 0.5   # Adjust the X position
area.elementPositionY = 0.1
area.horizontalAlignment = "LEFT"

author = theLayout.listElements("TEXT_ELEMENT")[1]
author.text = "Cartographed by: Julie Quintero"
author.text = "<FNT size = '22'>" + author.text + "</FNT>"  # Font size 24
author.elementPositionX = 2.2   # Adjust the X position
author.elementPositionY = 9.6
author.horizontalAlignment = "LEFT"

title = theLayout.listElements("TEXT_ELEMENT")[2]
title.text = "Mapbook of North American Lakes"
title.text = "<FNT size = '36'>" + title.text + "</FNT>"  # Font size 24
title.elementPositionX = 0.7   # Adjust the X position
title.elementPositionY = 10 

if os.path.exists(temp_file):
    os.remove(temp_file)
theLayout.exportToPDF(temp_file)

final_file.appendPages(temp_file)


del theMapFrame, layout_el, area, title, author, elem #unlocked
#maybe no delete aprx, etc still need it for part 2

print("Title page completed.")
print("=======================================================================")


#========================================

print("Begin creating lake pages.")

#Alter Symbology

Maps = aprx.listMaps()
for theMap in Maps:
    lyr_list = theMap.listLayers()
    for lyr in lyr_list:
        if lyr.isFeatureLayer:
            if lyr.name == "NA_Cities":
                lyr.showLabels = True
                #change symbology?
            if lyr.name == "NA_Big_Lakes":
                lyr.showLabels = False
        
aprx.save()


theLayout = aprx.listLayouts()[0]
layout_el = theLayout.listElements() #"TEXT_ELEMENT" [0]
for elem in layout_el:
    print(elem.name, ": ", elem.type)
    if elem.type == "TEXT_ELEMENT":
        print(elem.text)

theMapFrame = theLayout.listElements("MAPFRAME_ELEMENT")[0]

# Use the lake page layout to create a page for each lake; use search cursor to iterate through each lake
for lake in arcpy.da.SearchCursor(lake_fc, ["SHAPE@", "FID", "Area_km2", "CNTRY_NAME", "PERIMETER"]):
    
    print("Creating page for FID " + str(lake[1]))
   
    lake_extent = lake[0].extent # find lake extent based on SHAPE@
    
    theMapFrame.camera.setExtent(lake_extent) # set lake extent
    theMapFrame.camera.scale = theMapFrame.camera.scale * 1.2 # zoom out of lake extent

    #Title text element
    legend = theLayout.listElements("LEGEND_ELEMENT")[0]  # Replace "LEGEND_ELEMENT_NAME" with the actual name of your legend element
    scalebar = theLayout.listElements("MAPSURROUND_ELEMENT")[0]  # Replace "SCALEBAR_ELEMENT_NAME" with the actual name of your scale bar element

    # Hide the legend and scale bar
    legend.visible = True
    scalebar.visible = True
    
    country = theLayout.listElements("TEXT_ELEMENT")[0]
    country.text = "Country: " + str(lake[3])
    #edit bottom ones
    country.text = "<FNT size = '25'>" + country.text + "</FNT>"  # Font size 24
    country.elementPositionX = 0.7   # Adjust the X position
    country.elementPositionY = 9.5
    country.horizontalAlignment = "LEFT"

    area_info = theLayout.listElements("TEXT_ELEMENT")[1]
    area_info.text = "Area: " + str(lake[2]) + " km sq"
    #edit bottom ones
    area_info.text = "<FNT size = '30'>" + area_info.text + "</FNT>"  # Font size 24
    area_info.elementPositionX = 0.7   # Adjust the X position
    area_info.elementPositionY = 10
    area_info.horizontalAlignment = "LEFT"
    
    title = theLayout.listElements("TEXT_ELEMENT")[2]
    title.text = "Lake FID: " + str(lake[1])
    #edit bottom ones
    title.text = "<FNT size = '20'>" + title.text + "</FNT>"  # Font size 24
    title.elementPositionX = 2.2   # Adjust the X position
    title.elementPositionY = 9.6
    title.horizontalAlignment = "LEFT"


#==============================
    
    # Export the lake page layout to tmp pdf
    if os.path.exists(temp_file):
        os.remove(temp_file)
    theLayout.exportToPDF(temp_file)

    final_file.appendPages(temp_file) # add tmp pdf to the final pdf

final_file.saveAndClose()

if os.path.exists(temp_file):
    os.remove(temp_file)
    
del aprx, final_file, theMapFrame, country, area_info, title, lake_fc, lake # unlocked

print("End of map production.")
print("=======================================================================")






#========================================

#next steps
    #edit symbolgy on arc for the labels
    #edit the text on lake page
        #size, font
    #fix scale?


#technical
    #label pretty
    #symbology



