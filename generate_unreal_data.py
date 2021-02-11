import os
import shutil
import PySimpleGUI as simpleGUI
from unreal_merge import unreal_merge
from lat_long_scaling import produce_scaled_file

# Get relative directory.
relativeDir = os.path.dirname(__file__)

# Set GUI theme.
simpleGUI.theme("LightGrey1")

# Builds the layout.
layout = [

    # Gather all of the necessary files for merging and scaling for the unreal engine.
    [simpleGUI.Text("")],
    [simpleGUI.Text("Please specify the path to 'GA lab Data 11_17_2020.xlsx': ", size=(53, 1),),
     simpleGUI.Input(), simpleGUI.FileBrowse(key="GA-lab-Data")],
    [simpleGUI.Text("Please specify the path to 'Oregon Moisture 10_8_2020.xlsx': ", size=(53, 1),),
     simpleGUI.Input(), simpleGUI.FileBrowse(key="Oregon-Moisture")],
    [simpleGUI.Text("Please specify the path to 'Oregon_Fall_2020_2021-01-14_12-35-36.xlsx': ", size=(53, 1),),
     simpleGUI.Input(), simpleGUI.FileBrowse(key="Oregon-Fall")],
    [simpleGUI.Text("Please specify the path to 'clean_esri_data.csv': ", size=(53, 1),),
     simpleGUI.Input(), simpleGUI.FileBrowse(key="clean-esri-data")],
    [simpleGUI.Text("")],
    [simpleGUI.Button("Submit"), simpleGUI.Exit()]

]

# Building window.
window = simpleGUI.Window("Unreal Engine Merges", layout, size=(860, 230))

# Application run.
while True:

    event, values = window.read()

    if event == simpleGUI.WIN_CLOSED or event == "Exit":
        break

    # Run merge scripts and produce files in a 'Data' directory.
    elif event == "Submit":

        # Override the current "Data" directory if it exists. Otherwise, create it.
        if not os.path.exists(relativeDir + "/Data"):
            os.makedirs(relativeDir + "/Data")
        else:
            shutil.rmtree(relativeDir + "/Data")
            os.makedirs(relativeDir + "/Data")

        # Run the 'unreal_merge' script.
        unreal_merge(values["GA-lab-Data"], values["Oregon-Moisture"], values["Oregon-Fall"], values["clean-esri-data"])

        # Run the 'produce_scaled_file' script.
        produce_scaled_file(values["clean-esri-data"])

        # Stop the program.
        break
