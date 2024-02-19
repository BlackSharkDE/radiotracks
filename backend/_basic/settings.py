########################################################################################################################################################################
#
# Alles was mit der "settings.json" (im Hauptverzeichnis vom backend) zutun hat
#
########################################################################################################################################################################

import json

import jfiles

########################################################################################################################################################################
#-- Exception für nicht gefundene "settings.json"-Datei --

class SettingsFileNotFound(Exception):

    #-- Konstruktor --
    #@param String Angenommener Pfad der "settings.json"-Datei
    def __init__(self,filePath):
        self.message = "Could not find '" + filePath + "' !"
        super().__init__(self.message)
    
    #Stringrepräsentation
    def __str__(self):
        return f'{self.message}'

########################################################################################################################################################################
#-- Exception für nicht gefundene Einstellung in "settings.json"-Datei --

class SettingNotFound(Exception):
    
    #-- Konstruktor --
    #@param String Name der Einstellung
    def __init__(self,settingName):
        self.message = "Setting '" + settingName + "' not found in 'settings.json'-File!"
        super().__init__(self.message)
    
    #Stringrepräsentation
    def __str__(self):
        return f'{self.message}'

########################################################################################################################################################################

#Gibt den Pfad der "settings.json" zurück
#@return String Gesamter Pfad der "settings.json"-Datei auf dem Dateisystem
def getSettingsfilePath():
    p = jfiles.getScriptDirectory(__file__)
    p = p[:p.rfind('/')]
    p += "/settings.json"
    return p

#Abrufen einer Einstellungskategorie aus "settings.json"
#@param String Überkategorie / erste Ebene in der "settings.json", z.B: "database"
#@return Dict  Dictionary bzw. die Settings der Kategorie / Exception bei Fehlschlag
def getSetting(settingSection):
    sp = getSettingsfilePath()

    sf = jfiles.readInFile(sp,"utf8")
    if sf is None:
        raise SettingsFileNotFound(sp)

    sj = json.loads(sf)

    if settingSection in sj:
        return sj.get(settingSection)
    
    raise SettingNotFound(settingSection)