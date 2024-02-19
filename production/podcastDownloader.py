########################################################################################################################################################
#
# Downloaded mittels der "GooglePodcastApi" Podcast-Episoden von Podcasts
#
########################################################################################################################################################

import json
import requests
import emoji

import jfiles

########################################################################################################################################################
#-- Konfiguration --

#Alle Podcasts, die abgearbeitet werden sollen
podcastDict = {
    #"Podcast-ID" (siehe GPA): "Ausgabepfad" (Ordner muss bereits bestehen), kein "/" am Ende!
    "abcdefghij": "C:/dir/pod"
}

#Die URL für die "GooglePodcastApi"-API
gpaApiUrl = ""

########################################################################################################################################################
#-- Logik --

#Entfernt ungültige Zeichen aus einem Text, die für den Radiotracks-Indexer ungeeignet sind
#@param String  Text
#@return String Bereinigter Text
def sanitizeText(textToSanitize):

    #Emojis entfernen
    textToSanitize = emoji.replace_emoji(textToSanitize,replace="")
    
    #New-Lines durch Leerzeichen ersetzen
    textToSanitize = textToSanitize.replace("\\n"," ")

    return textToSanitize

#Downloadet eine Podcast-Episode. (void - Funktion)
#@param String Podcast-ID
#@param String Ausgabeverzeichnis
def downloadNextEpisode(givenPodcastId,outputDirectory):

    #Teste, ob Ausgabepfad verfügbar ist
    if jfiles.pathExists(outputDirectory):

        #Teste, wie viele Episoden im Ausgabeverzeichnis vorhanden sind
        fileList = jfiles.getAllFilesInPath(outputDirectory,"mp3")

        #Nächste Episode (Index startet bei der API bei 1)
        nextEpisode = len(fileList) + 1

        #GPA-API abfragen
        apiJson = requests.get(gpaApiUrl + '?feedid=' + str(givenPodcastId) + "&episode=" + str(nextEpisode))

        #Wenn valide (Request-) Antwort
        if apiJson is not None and apiJson.status_code == 200:
            
            #Decode - Fehler bei Zeichen werden ignoriert (diese werden also weggelassen)
            apiJson = str(apiJson.content,encoding="utf8",errors="ignore")

            #JSON einlesen
            apiJson = json.loads(apiJson)

            #Valides API-Ergebnis
            if apiJson["success"] == True:

                #Download der Episode
                fileContent = requests.get(apiJson["episodeDownloadUrl"])

                if fileContent is not None and fileContent.status_code == 200:
                    
                    #Schreibe die Bytes vom Download in eine Datei
                    if jfiles.writeToFile(fileContent.content,outputDirectory + "/" + str(nextEpisode) + ".mp3",None,"w","b",True):
                        
                        #Podcast-Episode-JSON-Inhalt
                        podcastEpisodeDescription = {
                            "title"      : sanitizeText(apiJson["episodeTitle"]),
                            "description": sanitizeText(apiJson["episodeDescription"])
                        }

                        #Schreibe die Podcast-Beschreibung
                        if jfiles.writeToFile(json.dumps(podcastEpisodeDescription),outputDirectory + "/" + str(nextEpisode) + ".json","utf8","w","t",True):
                            return
                        else:
                            print("Konnte Episode-Beschreibung nicht schreiben!")
                    else:
                        print("Konnte Episode-MP3-Datei nicht schreiben!")
                else:
                    print("Download fehlgeschlagen!")
            else:
                print("GooglePodcastApi-Resultat nicht ok: " + str(apiJson['reason']))
        else:
            print("GooglePodcastApi nicht erreichbar!")
    else:
        print("Ausgabeverzeichnis nicht verfügbar!")

#Jeden Podcast durchgehen
for podcastId in podcastDict.keys():
    downloadNextEpisode(podcastId,podcastDict[podcastId])