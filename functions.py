#! /usr/bin/env python3
# Sony actioncam videoclip import

import os
import re
import time
import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm


######################################################
# Function to check if a file or directory excist ####
######################################################
def checkExist(DATA):
    if os.path.isfile(DATA):
        return True
    elif os.path.isdir(DATA):
        return True
    else:
        return False


######################################################
# Function to list all videoclips with data ##########
######################################################
def listClips(PATH, DATAFILE):
    # Process the data file
    tree = ET.parse(PATH + DATAFILE)
    root = tree.getroot()

    # Find the camera model name
    for properties in root.iter('{http://xmlns.sony.net/pro/metadata/mediaprofile}Properties'):
        for system in properties.iter('{http://xmlns.sony.net/pro/metadata/mediaprofile}System'):
            model = system.get('systemKind')[4:]

    # Initilize an array to list all clips
    listClips = []
    # Initilize the clip date variable and the clips per day counter
    clipDate = '' 
    clipCount = 0

    # Find the material list
    for contents in root.iter('{http://xmlns.sony.net/pro/metadata/mediaprofile}Contents'):
        for material in contents.iter('{http://xmlns.sony.net/pro/metadata/mediaprofile}Material'):
            if checkExist(PATH + material.get('uri')[2:]):
                # Save video file location
                file = PATH + material.get('uri')[2:]

                # Find the relative info
                for info in material.iter('{http://xmlns.sony.net/pro/metadata/mediaprofile}RelevantInfo'):
                    itemType = info.get('type')
                    if itemType == 'JPG':
                        if checkExist(PATH + info.get('uri')[2:]):
                            # Save tumbernail location
                            thumb = PATH + info.get('uri')[2:]
                        else:
                            thumb = ''

                    elif itemType == 'XML':
                        if checkExist(PATH + info.get('uri')[2:]):
                            # Save data file location
                            data = PATH + info.get('uri')[2:]
                            # Get the metadata
                            meta = getMetadata(PATH, info.get('uri')[2:])
                        else:
                            data = ''
                            meta = ''

                # Check if there is metadata available
                if meta:
                    # Get the date
                    for metadata in meta:
                        if clipDate == '':
                            # First clips, set date
                            clipDate = metadata['date']
                        elif clipDate == metadata['date']: 
                            # Date has previously already been set, add to counter
                            clipCount += 1
                        elif not clipDate == metadata['date']:
                            # New date, set new date and reset counter
                            clipDate = metadata['date']
                            clipCount = 0

                    # Replace part of the folder path
                    gpspath = re.sub("/M4ROOT/", "/SONY/GPS/", PATH)
                    # Try to find a GPS log file
                    if checkExist(gpspath + clipDate + str(clipCount).zfill(2) + '.LOG'):
                        gps = gpspath + clipDate + str(clipCount).zfill(2) + '.LOG'
                    else:
                        gps = ''

                listClips.append({'file': file, 'thumb': thumb, 'data': data, 'gps': gps, 'meta': meta })

            else:
                # Print error message
                print('could not find ' + PATH + material.get('uri')[2:])
    
    return model, listClips


######################################################
# Function to get the metadata #######################
######################################################
def getMetadata(PATH,DATAFILE):
    # Initilize an array to store all metadata
    meta = []

    # Process the data file
    tree = ET.parse(PATH + DATAFILE)
    root = tree.getroot()

    # Get camera information
    for device in root.iter('{urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.00}Device'):
        manufacturer = device.get('manufacturer')
        modelName = device.get('modelName')
        serialNo = device.get('serialNo')

    # Get creation date
    for device in root.iter('{urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.00}CreationDate'):
        date = device.get('value')
        date = dateConvert(date)
    
    # Initilize the variables
    latitude = None
    longitude = None
    # Get GPS information
    for gpsData in root.iter('{urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.00}AcquisitionRecord'):
        for data in gpsData[0]:
            # Only get the latitude and longitude
            if data.get('name') == 'Latitude':
                latitude = data.get('value')
            if data.get('name') == 'Longitude':
                longitude = data.get('value')

    # Initalize variable
    location = ''

    # Check if there is GPS data
    if latitude and longitude:
        # GPS data found, convert coordinates and search for the adress
        url = 'https://nominatim.openstreetmap.org/reverse?lat=' + str(gpsConversion(latitude)) + '&lon=' + str(gpsConversion(longitude)) + '&zoom=17&format=xml'
        headers = { 'User-Agent': 'Videoclip import v1' }
        response = requests.get(url, headers=headers)

        # Check for response
        if response.ok:
            content = response.content
            root = ET.fromstring(content)

            # Find the adress
            for result in root:
                if result.tag == 'result':
                    location = result.text
        else:
            # unable to get adress, safe GPS coordinates instead
            location = 'lat: ' + str(gpsConversion(latitude)) + ',lon: ' + str(gpsConversion(longitude))

        time.sleep(1)

    meta.append({'date': date, 'location': location, 'modelname': modelName, 'manufacturer': manufacturer, 'serialno': serialNo })
    return meta


######################################################
# Function to convert the date #######################
######################################################
def dateConvert(DATE):
    # Split string at the (T) time marker
    date, time = re.split('T', DATE)
    # Split the date at the - symbol
    year, month, day = re.split('-', date)
    # rearrange date format to match Sony style
    sonydate = year[2:] + month + day
    return sonydate


######################################################
# Function to convert GPS coordinates ################
######################################################
def gpsConversion(DATA):
    # Split string at the : symbol
    degree, minute, second = re.split(':', DATA)
    # Convert
    coordinates = float(degree) + float(minute) / 60 + float(second) / (60 * 60)
    return coordinates


######################################################
# Function to copy files with progress bar ###########
######################################################
def copyFile(SOURCE, DESTINATION):
    size = os.stat(SOURCE).st_size
    progress_bar = tqdm(total=size, unit='B', unit_scale=True)

    def copyfileobj(FSRC, FDST, CALLBACK, LENGTH=16*1024):
        copied = 0
        with open(FSRC,"rb") as fr, open(FDST,"wb") as fw:
            while True:
                buff = fr.read(LENGTH)
                if not buff:
                    break
                fw.write(buff)
                copied += len(buff)
                CALLBACK(copied)
    
    def progress_callback(chunk):
        progress_bar.update(chunk)
    
    copyfileobj(SOURCE, DESTINATION, CALLBACK=progress_callback, LENGTH=16*1024)
    progress_bar.close()


######################################################
# Function to write metadata to a csv file ###########
######################################################
def writeMetadata(DESTINATION,FILENAME,LOCATION,TYPE,MANUFACTURER,SERIAL):
    # Check if there is alread a Davinci Resolve metadata file
    if not checkExist(DESTINATION + 'dr_metadata.csv'):
        # No file yet, make a new one and add a header
        f = open(DESTINATION + 'dr_metadata.csv', 'a')
        f.write('File Name,Location,Camera Type,Camera Manufacturer,Camera Serial #\n')
        f.close()
        print('A new Metadata file called dr_metadata.csv was created')

    # Write a new line to the file
    f = open(DESTINATION + 'dr_metadata.csv', 'a')
    f.write(FILENAME + ',"' + LOCATION + '",' + TYPE + ',' + MANUFACTURER + ',' + SERIAL + '\n')
    f.close()
    return True