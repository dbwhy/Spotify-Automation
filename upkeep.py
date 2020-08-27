from datetime import datetime
from SpotifyAutomation.secrets import spotify_user_id, spotify_token
import requests
import json


class PlaylistMaintenance:
    def __init__(self, playlist_name):
        self.spotify_query = "https://api.spotify.com/v1/"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)}
        self.pl_id = self.playlist_id(playlist_name)

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
        return None

    # 2. Finds all playlist items
    def playlist_items(self):
        # Grab playlist info
        query = self.spotify_query + f"playlists/{self.pl_id}/tracks"
        response = requests.get(
            query,
            headers=self.headers
        )
        response_json = response.json()
        playlist_items = response_json['items']
        self.upkeep(playlist_items)

    # 3. Determine if songs should be removed
    def upkeep(self, pl_items):
        uris = []
        # are there songs to remove?
        if (num := (len(pl_items) - 30)) > 0:
            items = {}
            artists = {}
            for track in pl_items:
                t = track['track']
                # have artists been repeated? if so, remove the oldest song from an artist first
                if (artist := t['artists'][0]['name']) in list(artists.keys()):
                    if track['added_at'] > artists[artist][0]:
                        self.remove_song([artists[artist][1]])
                        return self.playlist_items()
                    else:
                        self.remove_song([t['uri']])
                        return self.playlist_items()
                else:
                    artists.update({artist: [(track['added_at']), (t['uri'])]})
                    items.update({track['added_at']: t['uri']})
            # re-order songs by 'date added'
            items_dates = list(items.keys())
            items_dates.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ'))

            for dates in items_dates[:num]:
                uris.append(items[dates])
            self.remove_song(uris)

    # 4. Remove songs from playlist
    def remove_song(self, uris):
        song_uris = {'tracks': []}
        for uri in uris:
            x = {'uri': uri}
            song_uris['tracks'].append(x)

        query = self.spotify_query + f"playlists/{self.pl_id}/tracks/"
        response = requests.delete(
            query,
            headers=self.headers,
            data=json.dumps(song_uris)
        )
        if response.status_code != 200:
            raise Exception(response.status_code)

        self.add_song(song_uris, self.playlist_id('X'))

    # 5. Add songs to another playlist
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
        if response.status_code != 201:
            raise Exception(response.status_code)


if __name__ == '__main__':
    pm = PlaylistMaintenance('Current Favorites')
    pm.playlist_items()
