########################################################################################################################################################################
#
# api
#
# Alles was mit Datenabfrage für Clients zutun hat
#
########################################################################################################################################################################

#app.py
from .app import RadiotracksAPI

#functions.py -> Nach außen hin werden nur diese Funktionen benötigt
from .functions import getIds, getAlbumById