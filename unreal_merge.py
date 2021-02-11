import os
import pandas as pd

# Get relative directory.
relativeDir = os.path.dirname(__file__)


def unreal_merge(gaDataFrame, oregonDataFrame, oregonFallDataFrame, cleanEsriDataFrame):

    try:

        # Pull in files.
        gaDataFrame = pd.read_excel(gaDataFrame, skiprows=1)
        oregonDataFrame = pd.read_excel(oregonDataFrame, skiprows=1)
        oregonFallDataFrame = pd.read_excel(oregonFallDataFrame)
        cleanEsriDataFrame = pd.read_csv(cleanEsriDataFrame)

        # Reformat date and time to an ISO8601 compliant format.
        oregonFallDataFrame.insert(1, 'Collection Date', 'N/A')
        oregonFallDataFrame['Tree Soil Time'] = pd.to_datetime(oregonFallDataFrame['Tree Soil Time'], errors='coerce')
        oregonFallDataFrame['Collection Date'] = \
            oregonFallDataFrame['Tree Soil Date'].dt.strftime('%m-%Y-%d') + 'T' + \
            oregonFallDataFrame['Tree Soil Time'].dt.strftime('%H:%M:%S')

        # If no exact time is available, provide only the date.
        oregonFallDataFrame['Collection Date'].fillna(oregonFallDataFrame['Tree Soil Date'].dt.strftime('%m-%Y-%d'),
                                                      inplace=True)

        # Insert a new column into each dataframe after 'vial #'.
        gaDataFrame.insert(1, 'TreeID', 'N/A')
        oregonDataFrame.insert(1, 'TreeID', 'N/A')

        # Copy the values in the 'DATALABELS' column into the 'TreeID' column.
        gaDataFrame['TreeID'] = gaDataFrame['DATALABELS']
        oregonDataFrame['TreeID'] = oregonDataFrame['DATALABELS']

        # Change the name of the column to 'TreeID' from 'DATALABELS' in the 'TreeID' column.
        gaDataFrame.iloc[0, gaDataFrame.columns.get_loc('TreeID')] = 'TreeID'
        oregonDataFrame.iloc[0, oregonDataFrame.columns.get_loc('TreeID')] = 'TreeID'

        # Change the name of the columns to 'Latitude' and 'Longitude' from 'GPS Lat (N)' and 'GPS Long (W)'.
        oregonFallDataFrame = oregonFallDataFrame.rename({'GPS Lat (N)': 'Latitude', 'GPS Long (W)': 'Longitude'},
                                                         axis=1)

        # Round the decimals values of 'cleanEsriDataFrame'.
        cleanEsriDataFrame.round(6)

        # Truncate the '_SC' from the end of the 'DATALABEL' in both files.
        gaDataFrame['TreeID'].replace(to_replace=r'((?:_[^_\r\n]*){1})$', value='', regex=True, inplace=True)
        oregonDataFrame['TreeID'].replace(to_replace=r'((?:_[^_\r\n]*){1})$', value='', regex=True, inplace=True)

        # Create a new column in 'oregonDataFrame' for the average of the MC (%) dry columns.
        oregonDataFrame.insert(len(oregonDataFrame.columns), 'Soil Moisture', '0')

        # Calculate the average soil moisture.
        oregonDataFrame['Soil Moisture'] = oregonDataFrame[['MC (%) dry', 'MC (%) dry.1', 'MC (%) dry.2']].mean(axis=1)

        # Replace elements that are under the detection limit with '0'.
        gaDataFrame['NH4-N'].replace(to_replace=r'[!^<]{1}', value=0, regex=True, inplace=True)
        gaDataFrame['NO2-N'].replace(to_replace=r'[!^<]{1}', value=0, regex=True, inplace=True)
        gaDataFrame['NO3-N'].replace(to_replace=r'[!^<]{1}', value=0, regex=True, inplace=True)

        # Convert the elements.
        gaDataFrame['NH4-N'] = 1.2579 * gaDataFrame['NH4-N']
        gaDataFrame['NO2-N'] = 3.2844 * gaDataFrame['NO2-N']
        gaDataFrame['NO3-N'] = 4.4266 * gaDataFrame['NO3-N']

        # Rename the elements.
        gaDataFrame = gaDataFrame.rename({'NO3-N': 'NO3', 'NO2-N': 'NO2', 'NH4-N': 'Ammonium'}, axis=1)

        # Merge the three files on the 'TreeID' value.
        mergedData = gaDataFrame.merge(oregonDataFrame, on='TreeID', how='inner') \
            .merge(oregonFallDataFrame, on='TreeID', how='inner') \
            .merge(cleanEsriDataFrame, on=['Latitude', 'Longitude'], how='left')

        # Rename the 'DATALABELS_x' to 'SampleID'.
        mergedData = mergedData.rename({'DATALABELS_x': 'Sample ID'}, axis=1)

        # Rename the required columns to match the F.A.I.R data specification.
        mergedData = mergedData.rename({'LBC 1': 'LBC', 'pH 2': 'pH', 'Tree Height (meters)': 'Total Tree Height',
                                        'Tree diameter (cm)': 'DBH'}, axis=1)

        # Create the final dataframe with only the required columns.
        mergedData = mergedData[['LBC', 'LBCeq', 'pH', 'Ca', 'K', 'Mg', 'Mn', 'P', 'Zn', 'Ammonium', 'NO2', 'NO3', 'C',
                                 'N', 'Soil Moisture', 'Longitude', 'Latitude', 'Site', 'DBH', 'Total Tree Height',
                                 'Collection Date', 'Sample ID']]

        # Generate .csv file for the 'mergedData' dataframe.
        mergedData.to_csv(relativeDir + '/Data/unreal_merged_data.csv', header=True, index=False)
        print("Unreal Engine merged files generated successfully.")
        print()

    except FileNotFoundError:

        print("The files to merge were not found.")

    except PermissionError:

        print("Please close the `Merged_Data` file before running this command.")
