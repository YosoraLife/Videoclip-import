#! /usr/bin/env python3
# Sony actioncam videoclip import

import os
from functions import *


print('\nReverse geocoding (convering GPS data to an adress) provided by © OpenStreetMap\n')
print('This script was created to import Sony Action Cam footage including metadata.')
print('This has been tested with the FDR-X3000, FDR X1000 and AS100 action cameras from Sony\n')

inputSourceLocation = ''

# Source locations to check
for location in 'DEFG':
    if checkExist(location + ':/PRIVATE/M4ROOT/MEDIAPRO.XML'):
        print('MEDIAPRO.XML file found on ' + location + ':/')
        inputSourceLocation = location
        break

if inputSourceLocation == '':
    # Wait for input on the source location
    inputSourceLocation = input('Could not automatically detect the right drive. On what drive are the source files? Drive letter: ')

rootLocation = inputSourceLocation + ':/PRIVATE/M4ROOT/'

# Check if mediapro file excists
if not checkExist(rootLocation + 'MEDIAPRO.XML'):
    print('MEDIAPRO.XML cannot be found.')
    exit()

# Read the mediapro file and list all clips
model,clips = listClips(rootLocation, 'MEDIAPRO.XML')

print('The following camera is detected: ' + model + ', ' +str(len(clips)) + ' video(s) where found: \n')

gpsFile = False
for clip in clips:
    # Check if there are any GPS files
    if clip['gps']:
        gpsFile = True

    print('Videoclip: ' + clip['file'])
    print(' - Thumbnail: ' + clip['thumb'])
    print(' - Metadata: ' + clip['data'])
    print(' - GPS data: ' + clip['gps'])
    print('')

if gpsFile and not checkExist(r'C:/Program Files/GPSBabel/gpsbabel.exe'):
    print('GPS data is found, but GPSBabel is not installed. When you proceed the GPS data will not be prcessed.')
    proceed = input('\nDo you want to proceed? Type \'Y\' to proceed or any other key to exit: ')
else:
    proceed = input('Do you want to proceed? Type \'Y\' to proceed or any other key to exit: ')

if not proceed.capitalize() == 'Y':
    exit()

# Ask for destination location
destinationLocation = input('\nWhere do you want the files to be copied to? Destination folder: ')

# Check if there is a trailing /, if not add one
if not destinationLocation[-1] == '/':
    destinationLocation = destinationLocation + '/'

# Check if destination exists
if not checkExist(destinationLocation):
    createFolder = input(destinationLocation + ' Doesn\'t exist yet, do you want to create a new folder? Type \'Y\' to proceed or any other key to exit: ')

    if createFolder.capitalize() == 'Y':
        # Make the (sub)folder(s)
        os.makedirs(destinationLocation)
    else:
        exit()

# Check if there is enough space leftover

# Check if there are any clip in it already.
i = 1
while checkExist(destinationLocation + 'C' + str(i).zfill(4) + '-' + model + '.mp4'):
    i += 1

# Previous files found, ask what to do
if i > 1:
    # Ask if continue count where left, of restart count with duplicate numbering
    print('\nThere are other clips from this camera found in that folder. Do you want to continue the clip count (1) or start a new series with a reset clip count (2).')
    continueCount = input('Type \'1\' to continue or type \'2\' for a new series: ')
else:
    # No previous files found, default to option 1
    continueCount = '1'

# Check if there are any clips with the secondary counter already.
if continueCount == '2':
    # Reset the first counter
    i = 1
    # Start a second series counter
    ii = 1
    # Check if there are other series already
    while checkExist(destinationLocation + 'C' + str(i).zfill(4) + 'S' + str(ii).zfill(2) + '-' + model + '.mp4'):
        ii += 1
    # Set the suffex
    suffex = 'S' + str(ii).zfill(2) + '-'
else:
    suffex = '-'

# Process the files
for clip in clips:
    for meta in clip['meta']:
        latitude = meta['latitude']
        longitude = meta['longitude']
        location = getLocation(latitude, longitude)
        modelName = meta['modelname']
        manufacturer = meta['manufacturer']
        serialNo = meta['serialno']

    # Set filename base
    baseFilename = 'C' + str(i).zfill(4) + suffex + model
    i +=1

    print(baseFilename)

    # Copy the videoclip
    print(' - Copying videoclip: ' + baseFilename + '.mp4')
    copyFile(clip['file'], destinationLocation + baseFilename + '.mp4')

    # Copy the Tumbernail
    if clip['thumb']:
        print(' - Copying tumbernail: ' + baseFilename + '-Thumb.jpg')
        copyFile(clip['thumb'], destinationLocation + baseFilename + '-Thumb.jpg')

    # Convert and copy the GPS log
    if clip['gps']:
        with open(clip['gps'], 'r') as fp:
            lines = len(fp.readlines())
            if lines > 10:
                print(' - Converting and copying GPS log: ' + baseFilename + '-GPS.gpx')
                os.system('\"C:\Program Files\GPSBabel\gpsbabel.exe\" -i nmea -f ' + clip['gps'] + ' -x discard,hdop=10 -o gpx -F ' + destinationLocation + baseFilename + '-GPS.gpx')
            else:
                print(' - Not enough GPS data, GPS log skipped')

    # Write data to csv file
    if writeMetadata(destinationLocation,baseFilename + '.mp4' ,location,modelName,manufacturer,serialNo):
        print(' - Metadata for ' + baseFilename + ' has been writen to file')

# Offer to delete the files
deleteFiles = input('\nAll files are processed. The files can only be deleted automatically when the SD card is read with an SD card reader. Otherwise use the format function on the actioncamera.\nDo you want to delete the files from the actioncam?  Type \'Y\' to proceed or any other key to exit: ')
if deleteFiles.capitalize() == 'Y':
    # Delete the files
    for clip in clipList:
        os.remove(clip['file'])
        os.remove(clip['data'])
        os.remove(clip['thumb'])
        os.remove(clip['gps'])
else:
    exit()
    