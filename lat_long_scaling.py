import os
import pandas as pd

# Get relative directory.
relativeDir = os.path.dirname(__file__)


def scale_x_y(lat, long, latLongDataFrame):

    try:

        # Get the maximum and minimum values of the Latitude and Longitude columns.
        maxX = latLongDataFrame['Latitude'].max()
        minX = latLongDataFrame['Latitude'].min()
        maxY = latLongDataFrame['Longitude'].max()
        minY = latLongDataFrame['Longitude'].min()

        # The absolute value of the maximum longitude - minimum longitude.
        W = abs(maxY - minY)

        # The absolute value of the maximum longitude - minimum longitude.
        L = abs(maxX - minX)

        # Obtain the larger side (be it length or width).
        B = max(W, L)

        # The total width of square in Unreal Units that we are scaling points to fill.
        D = 8000

        # The scale factor.
        a = D / B

        # Determines how far we need to shift the center of the scaled bounding rectangle so that it exists on the
        # origin.
        xOffset = a * minY + (a * L) / 2
        yOffset = a * minX + (a * W) / 2

        # The final scaled x and y points.
        x = a * lat - yOffset
        y = a * long - xOffset

        return x, y

    except FileNotFoundError:

        print('The LAT/LONG file was not found.')

    except PermissionError:

        print('Please close the `calculated_coordinates` file before running this command.')


def produce_scaled_file(esriDataFrame):

    try:

        # Pull in LAT/LONG file.
        esriDataFrame = pd.read_csv(esriDataFrame)

        # Add a temporary row for the vectors to live in.
        esriDataFrame.insert(1, 'Temporary', 'N/A')

        # Add a 'Row Name' 1-based index column for Unreal Engine's Data Table formatting.
        esriDataFrame.insert(0, 'Row Name', esriDataFrame.index + 1)

        # Calculate the normalized X and Y values.
        esriDataFrame['Temporary'] = esriDataFrame.apply(lambda x: scale_x_y(x.Latitude, x.Longitude, esriDataFrame),
                                                         axis=1)

        # Split the vector into two columns.
        esriDataFrame[['X', 'Y']] = pd.DataFrame(esriDataFrame['Temporary'].tolist(), index=esriDataFrame.index)

        # Retain only the required columns.
        esriDataFrame = esriDataFrame[['Row Name', 'X', 'Y']]

        # Generate .csv file for the 'mergedData' dataframe.
        esriDataFrame.to_csv(relativeDir + '/Data/calculated_coordinates.csv', header=True, index=False)
        print('The coordinate values were successfully generated.')

    except FileNotFoundError:

        print('The LAT/LONG file was not found.')

    except PermissionError:

        print('Please close the `calculated_coordinates` file before running this command.')
