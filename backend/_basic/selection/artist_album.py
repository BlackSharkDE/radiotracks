########################################################################################################################################################################
#
# Artist & Album
#
########################################################################################################################################################################

from ..base import AudioCreator, AudioCollection

########################################################################################################################################################################

#Ein Ordner in "media/artist/"
class Artist(AudioCreator):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()

#Ein Ordner in "media/artist/<artist_name>/"
class Album(AudioCollection):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()