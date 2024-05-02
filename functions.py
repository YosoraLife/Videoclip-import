#! /usr/bin/env python3
# Sony actioncam videoclip import

import os
import re
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
# Function to convert GPS coordinates ################
######################################################
def gpsConversion(DATA):
    degree, minute, second = re.split(':', DATA)
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