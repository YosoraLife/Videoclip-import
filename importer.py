#! /usr/bin/env python3
# Sony actioncam videoclip import

# import modules
import os
import time
import requests
import xml.etree.ElementTree as ET
from functions import *


print('\nReverse geocoding (convering GPS data to an adress) provided by © OpenStreetMap\n')
print('This script was created to import Sony Action Cam footage including metadata.\nThis has been tested with the FDR-X3000, FDR X1000 and AS100 action cameras from Sony\n')

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
clipLocation = inputSourceLocation + ':/PRIVATE/M4ROOT/CLIP/'
thumbLocation = inputSourceLocation + ':/PRIVATE/M4ROOT/THMBNL/'

# Check if mediapro file excists
if not checkExist(rootLocation + 'MEDIAPRO.XML'):
    print('MEDIAPRO.XML cannot be found.')
    exit()

# Process the data file
tree = ET.parse(rootLocation + 'MEDIAPRO.XML')
root = tree.getroot()

# Find the camera model name
for properties in root.iter('{http://xmlns.sony.net/pro/metadata/mediaprofile}Properties'):
    for system in properties.iter('{http://xmlns.sony.net/pro/metadata/mediaprofile}System'):
        model = system.get('systemKind')[4:]
        print('The following camera is detected: ' + model)


print('The following clips have been found:\n')

# Initilize an array to list all clips
clipList = []

# Search only for .mp4 files
for clip in os.listdir(clipLocation):
    if clip.endswith('.MP4'):

        file = clipLocation + clip
        print('\t' + file)

        # Strip extention from file name
        filename = os.path.splitext(clip)[0]

        # Check if data file can be found
        data = ''
        datafile = clipLocation + filename + 'M01.XML'
        if checkExist(datafile):
            print('\t - ' + datafile)
            # Add to the array
            data = datafile

        # Check if tumbernail can be found
        thumb = ''
        thumbernail = thumbLocation+ filename + 'T01.JPG'
        if checkExist(thumbernail):
            print('\t - ' + thumbernail)
            # Add to the array
            thumb = thumbernail

        # Add clip data to the list
        clipList.append({'file': file, 'data': data, 'thumb': thumb})

proceed = input('\nDo you want to continue? Type \'Y\' to continue or any other key to exit: ')

if not proceed.capitalize() == 'Y':
    exit()

# Ask for destination location
destinationLocation = input('\nWhere do you want the files to be copied to? Destination folder: ')

# Check if there is a trailing /, if not add one
if not destinationLocation[-1] == '/':
    destinationLocation = destinationLocation + '/'

# Check if destination exists
if not checkExist(destinationLocation):
    createFolder = input(destinationLocation + ' Doesn\'t exist yet, do you want to create a new folder? Type \'Y\' to continue or any other key to exit: ')

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

#start a timer, for reverse geocoding, this is limited to 1 request ever second
LoopTime = time.time()

# Process the files
for clip in clipList:
    # Set filename base
    baseFilename = 'C' + str(i).zfill(4) + suffex + model
    i +=1

    # Copy the Tumbernail
    print('Copying tumbernail: ' + baseFilename + '-Thumb.jpg')
    copyFile(clip['thumb'], destinationLocation + baseFilename + '-Thumb.jpg')
    # Copy the Clip
    print('Copying clip: ' + baseFilename + '.mp4')
    copyFile(clip['file'], destinationLocation + baseFilename + '.mp4')

    # Process metadata, first check if the metadata file exists
    if checkExist(clip['data']):
        # Process the data file
        tree = ET.parse(clip['data'])
        root = tree.getroot()

        # Get camera information
        for device in root.iter('{urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.00}Device'):
            manufacturer = device.get('manufacturer')
            modelName = device.get('modelName')
            serialNo = device.get('serialNo')

        # Get creation date
        for device in root.iter('{urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.00}CreationDate'):
            date = device.get('value')

        # Get GPS information
        for gpsData in root.iter('{urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.00}AcquisitionRecord'):
            for data in gpsData[0]:
                # Initilize the variables
                latitude = None
                longtitude = None
                # Only get the latitude and longitude
                if data.get('name') == 'Latitude':
                    latitude = data.get('value')
                if data.get('name') == 'Longitude':
                    longitude = data.get('value')

        # Initalize variable
        location = ''

        # Make sure that reverse geocoding isnt done more then once every 2 seconds to be safe
        timePassed = time.time() - LoopTime
        if timePassed < 2:
            time.sleep(timePassed)

        # Check if there is GPS data
        if latitude and longtitude:
            # GPS data found, convert coordinates and search for the adress
            url = 'https://nominatim.openstreetmap.org/reverse?lat=' + str(gpsConversion(latitude)) + '&lon=' + str(gpsConversion(longtitude)) + '&zoom=17&format=xml'
            response = requests.get(url)

            # Check for response
            if response.ok:
                content = response.content
                root = ET.fromstring(content)

                # Find the adress
                for result in root:
                    if result.tag == 'result':
                        location = result.text
            else:
                print('Was unable to do a reverse geocode for ' + baseFilename + '. GPS coordinates saved instead.')
                location = 'lat: ' + str(gpsConversion(latitude)) + ',lon: ' + str(gpsConversion(longtitude))

        # Write data to csv file
        if writeMetadata(destinationLocation,baseFilename + '.mp4' ,location,modelName,manufacturer,serialNo):
            print('Metadata ' + baseFilename + ' has been writen to file')

# Offer to delete the files
deleteFiles = input('\nAll files are processed. The files can only be deleted automatically when the SD card is read with an SD card reader. Otherwise use the format function on the actioncamera.\nDo you want to delete the files from the actioncam?  Type \'Y\' to continue or any other key to exit: ')
if deleteFiles.capitalize() == 'Y':
    # Delete the files
    for clip in clipList:
        os.remove(clip['file'])
        os.remove(clip['data'])
        os.remove(clip['thumb'])
else:
    exit()
    