# Videoclip Importer

I created this script to automaticly import video clips from Sony Action cameras including the metadata.

I have tested this with the 3 Sony Action Cameras that I have: the FDR-X3000, FDR-X1000 and HDR-AS100V action. But this script should be able to work with any Sony camara that has the follow folder structure:

- SD Card
 - :fa-folder: AVF_INFO
 - :fa-folder: PRIVATE
  - :fa-folder: M4ROOT
    - :fa-folder: CLIP -> Contains the videoclips + .xml files with the metadata
    - :fa-folder: GENERAL
    - :fa-folder: SUB
    - :fa-folder: THMBNL -> Contains the videoclip tumbernails
    - :fa-file-text-o: MEDIAPRO.XML -> XML files with data of the videoclips stored on the SD card
  - :fa-folder: SONY
    - :fa-folder: GPS -> Contains the GPS log files