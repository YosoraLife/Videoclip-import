# Videoclip Importer

I created this script to automatically import video clips from Sony Action cameras including making a metadata file for Davinci Resolve.

I have tested this with the 3 Sony Action Cameras that I have: the FDR-X3000, FDR-X1000 and HDR-AS100V action. But this script should be able to work with any Sony camara that has the follow folder structure:


SD Card
- 📁 AVF_INFO
- 📁 PRIVATE
    - 📁 M4ROOT
        - 📁 CLIP -> Contains the videoclips + .xml files with the metadata
        - 📁 GENERAL
        - 📁 SUB
        - 📁 THMBNL -> Contains the videoclip tumbernails
        - 📄 MEDIAPRO.XML -> XML files with data of the videoclips stored on the SD card
    - 📁 SONY
        - 📁 GPS -> Contains the GPS log files

The important files are the MEDIAPRO.XML and the videoclips in the CLIP folder. Without those the script wont work. The script will also search for the .xml files with the metadata, the thumbernails and GPS log files. When it can find those files it will process them, if those files cannot be found they will be skipped and only the files (and videoclips) that could be found will be processed.


# Credits
Reverse geocoding (convering GPS data to an adress) provided by © [OpenStreetMap](https://www.openstreetmap.org/)
NMEA to GPX converter (converting GPS log file to GPX file) by [Peter Pearson](https://gist.github.com/ppearson/52774#file-gistfile1-py) 