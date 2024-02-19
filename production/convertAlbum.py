########################################################################################################################################################
#
# Konvertiert ein Album aus meiner Sammlung in MP3-Dateien
#
########################################################################################################################################################

import threading

import jfiles
from pyffmpeg import FFmpeg

########################################################################################################################################################
#-- Konfiguration --

#In welchem Pfad die Alben sind (OHNE / AM ENDE!)
pathOfAlbums = "C:/Users/User/Musik/Some nice Album"

#Welche Dateiendung die Songs haben (ohne ".")
filesExtension = "mp4"

#Pfad von FFmpeg
pathOfFFmpeg = "C:/dir/ffmpeg.exe"

#Ob die Originaldatei nach dem konvertieren automatisch gelöscht werden soll
deleteAfterConvert = True

########################################################################################################################################################
#-- Konverter-Logik --

#Alle Dateien eines Ordners konvertieren
#@param String Pfad eines Ordners
def convertAllFilesInFolder(pathOfAlbum):
    global deleteAfterConvert

    #FFmpeg-Objekt erstellen
    f = FFmpeg(pathOfFFmpeg)

    if jfiles.pathExists(pathOfAlbum):
        
        #Alle Song-Dateipfade
        albumFiles = jfiles.getAllFilesInPath(pathOfAlbum,filesExtension,False,True,True)
        albumFiles = [x for x in albumFiles if not "-video" in x.lower()] #Alle Dateien mit "-video" im Namen aussortieren
        
        print("-> Found " + str(len(albumFiles)) + " songfiles in '" + pathOfAlbum + "'")

        if len(albumFiles) > 0:

            #Alle Dateien konvertieren
            for path in albumFiles:
                output = pathOfAlbum + "/" + jfiles.getFilenameNoExtension(path) + ".mp3"
                print(output)
                f.convertToMp3(output,path)
                if deleteAfterConvert: jfiles.deleteFile(path)

########################################################################################################################################################

#Pfade von den Alben (in diesen Ordnern befinden sich die Songs)
albumPaths = []

#Die Album-Pfade herausfinden
print("Found these albums: ")
albumFolders = jfiles.getAllDirectoriesInPath(pathOfAlbums)
for folder in albumFolders:
    albumPath = pathOfAlbums + "/" + folder
    albumPaths.append(albumPath)
    print("- " + albumPath)
print("")

#Threads für Konverter-Prozesse
converterThreads = []

#Für jeden Album-Ordner einen Thread erstellen
for albumPath in albumPaths:
    converterThreads.append(threading.Thread(target=convertAllFilesInFolder,args=[albumPath]))

#Threads starten
for thread in converterThreads:
    thread.start()

#Auf Beendigung aller Threads warten
for thread in converterThreads:
    thread.join()

print("Done")