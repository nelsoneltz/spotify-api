import requests
import base64
import json
import pandas as pd
import os
import glob
from time import sleep

# URLS
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
BASE_URL = 'https://api.spotify.com/v1/'

client_id = ''
client_secret = ''

# Make a request to the /authorize endpoint to get an authorization code
auth_code = requests.get(AUTH_URL, {
    'client_id': '71ba07405811465ea14ffef49f9fccad',
    'response_type': 'code',
    'redirect_uri': 'https://open.spotify.com/collection/playlists',
    'scope': 'playlist-modify-private',
})
print(auth_code)

auth_header = base64.urlsafe_b64encode((client_id + ':' + client_secret).encode())
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic %s' % auth_header.decode('ascii')
}

payload = {
    'grant_type': 'client_credentials',
    'code': auth_code,
    'redirect_uri': 'https://open.spotify.com/collection/playlists',
    'client_id': client_id,
    'client_secret': client_secret
}

# Make a request to the /token endpoint to get an access token
access_token_request = requests.post(url=TOKEN_URL, data=payload, headers=headers)

# convert the response to JSON
access_token_response_data = access_token_request.json()

print(access_token_response_data)

# save the access token
access_token = access_token_response_data['access_token']

headers = {
    "Authorization": "Bearer " + access_token
}

def songs_band(banda):
    df = []
    df = pd.DataFrame(columns = ['artist', 'uri','album','song_name', 'song_id', 'danceability', 'energy', 'key', 'loudness', 'mode','speechiness' ,'acousticness' , 'instrumentalness','liveness','valence' , 'tempo','duration_ms' , 'time_signature','popularity'])

    procurar = f'https://api.spotify.com/v1/search?q={banda}&type=artist&market=BR'

    r = requests.get(url=procurar, headers=headers)

    name = json.loads(r.text)['artists']['items'][0]['name']
    band_id = json.loads(r.text)['artists']['items'][0]['id'] #.split(':')[2]
    print(name + ' '+ band_id + '\n\n')

    albuns_search = f'https://api.spotify.com/v1/artists/{band_id}/albums?include_groups=album&market=BR'

    r2 = requests.get(url= albuns_search, headers=headers)
    albuns = json.loads(r2.text)['items']
    for album in albuns:
        print('---------------')
        print('Importando album: '+album['name']+'\n')

        tracks_in_album = 'https://api.spotify.com/v1/albums/{}/tracks'.format(album['id'])
        r3 = requests.get(url=tracks_in_album, headers=headers)
        tracks = json.loads(r3.text)['items']
        for track in tracks:
#             print(track['name'])
            features = 'https://api.spotify.com/v1/audio-features/{}'.format(track['id'])
            r4 = requests.get(url = features, headers=headers)
            popularity = 'https://api.spotify.com/v1/tracks/{}'.format(track['id'])
            r5 = requests.get(url =popularity , headers=headers)
            pop = json.loads(r5.text)['popularity']
            df.loc[df.shape[0]] = [name,
                                   band_id,
                                   album['name'],
                                   track['name'],
                                   track['id'],
                                   json.loads(r4.text)['danceability'],
                                   json.loads(r4.text)['energy'],
                                  json.loads(r4.text)['key'],
                                  json.loads(r4.text)['loudness'],
                                  json.loads(r4.text)['mode'],
                                  json.loads(r4.text)['speechiness'],
                                  json.loads(r4.text)['acousticness'],
                                  json.loads(r4.text)['instrumentalness'],
                                  json.loads(r4.text)['liveness'],
                                  json.loads(r4.text)['valence'],
                                  json.loads(r4.text)['tempo'],
                                  json.loads(r4.text)['duration_ms'],
                                  json.loads(r4.text)['time_signature'],
                                   pop]
        print(album['name']+' importado\n')
    df.to_csv('{}.csv'.format(name), sep= ';')
    return df

def combine_all_csv():
    extension = 'csv'
    filenames = [i for i in glob.glob('*.{}'.format(extension))]
    combined_csv = pd.concat([pd.read_csv(f,sep=';') for f in filenames ],ignore_index=True)
    combined_csv.to_csv( "bandas.csv", index=False,sep=';')
    


lista_artistas = ['electric callboy','black_tide','oitão','men at work']

for banda in lista_artistas:
    songs_band(banda)

    
if 'bandas.csv' in os.listdir():
    os.remove('bandas.csv')
combine_all_csv()

print('---Finalizado---')


