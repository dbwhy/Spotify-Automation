# Spotify-Automation
some python code to automate certain features of spotify like playlist creation and upkeep

'Current Favorites' is a rotating playlist that features my 30 favorite songs. When I add a song, I take one off and put it into a playlist 'X' which
holds all songs that were once featured in 'Current Favorites'. Sometimes I add a song to but forget to remove one which is where 'upkeep.py' comes in.

'upkeep.py' is used to check if playlist > 30 songs, at which point, the oldest songs will be taken off and added to 'X'.

*Ideally, I would factor in # of plays to determine which song to remove but I haven't found an easy way to grab listening data from spotify directly.
I have set up last.fm to track my listening data, once enough information is gathered, this file will be updated.*
