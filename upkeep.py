from datetime import datetime
from ..secrets import spotify_user_id, spotify_token
import requests
import json


class PlaylistMaintenance:
    def __init__(self):
        self.spotify_query = "https://api.spotify.com/v1/"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)}

    # 1. Find playlist by name and return id
    def playlist_id(self, pl_name):
        query = self.spotify_query + f"users/{spotify_user_id}/playlists/"
        response = requests.get(
            query,
            headers=self.headers
        )
        if response.status_code != 200:
            raise Exception(response.status_code)
        response_json = response.json()

        for i in response_json['items']:
            if i['name'] == pl_name:
                return i["id"]

    # 2. Checks # of songs in playlist to see if upkeep is necessary
    def playlist_upkeep(self, pl_id):
        # Grab playlist info
        query = self.spotify_query + f"playlists/{pl_id}/tracks"
        response = requests.get(
            query,
            headers=self.headers
        )
        response_json = response.json()
        pl_items = response_json['items']
        song_uris = {'tracks': []}

        # how many songs (x) to remove?
        if (num := (len(pl_items) - 30)) > 0:
            items = []
            # Reorder tracks by date
            for track in pl_items:
                items.append(track['added_at'])
            items.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ'))
            oldest = items[:num]

            # Find x oldest songs
            for track in pl_items:
                for dates in oldest:
                    if track['added_at'] == dates:
                        uri = {'uri': track['track']['uri']}
                        song_uris['tracks'].append(uri)

            self.remove_song(song_uris, pl_id)

    # 3. Remove songs from playlist
    def remove_song(self, song_uris, pl_id):
        query = self.spotify_query + f"playlists/{pl_id}/tracks/"
        response = requests.delete(
            query,
            headers=self.headers,
            data=json.dumps(song_uris)
        )
        if response.status_code != 200:
            raise Exception(response.status_code)

        self.add_song(song_uris, self.playlist_id('X'))

    # 4. Add songs to another playlist
    def add_song(self, song_uris, pl_id):
        # reformat uri's such that appropriate request data is submitted
        uri_add = {'uris': []}
        for i in song_uris['tracks']:
            uri_add['uris'].append(i['uri'])

        query = self.spotify_query + f"playlists/{pl_id}/tracks/"
        response = requests.post(
            query,
            headers=self.headers,
            data=json.dumps(uri_add)
        )
        print(response.status_code)
        if response.status_code != 201:
            raise Exception(response.status_code)


if __name__ == '__main__':
    pm = PlaylistMaintenance()
    pm.playlist_upkeep(pm.playlist_id('Current Favorites'))
