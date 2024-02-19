########################################################################################################################################################################
#
# Simples und einheitliches Logging
#
#########################################################################################################################################################################

class RadiotracksLog:

    #Logge in die Konsole
    #@param String Name der Quelle (Modul/Sektion)
    #@param String Die Log-Nachricht
    def log(source,message):
        print("* (" + source + ") " + message)