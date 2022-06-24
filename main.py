import datetime as dt
import urllib.request
from pprint import pprint
from api_config import CLIENT_ID, CLIENT_SECRET, USER_ID, CODE, ACCESS_TOKEN, REFRESH_TOKEN
from bs4 import BeautifulSoup
import requests
import webbrowser
import base64
import json
from selenium import webdriver



BASE_URL = 'https://api.spotify.com/v1'

# def scrape_top_100(billboard_date):
#     year = billboard_date.split('-')[0]
#     month = billboard_date.split('-')[1]
#     day = billboard_date.split('-')[2]
#
#     top100_url = f"http://billboard.com/charts/hot-100/{year}-{month}-{day}/"
#     response = requests.get(url=top100_url)
#
#     soup = BeautifulSoup(response.text, features='html.parser')
#     all_song_tags = soup.select("li > ul > li > h3")
#     all_artist_tags = soup.select("h3 ~ span", class_="c-label")
#
#     top100_playlist = []
#     for song_tag, artist_tag in zip(all_song_tags, all_artist_tags):
#         song_title = song_tag.get_text(strip=True)
#         artist = artist_tag.get_text(strip=True)
#         top100_playlist.append((song_title, artist))
#
#     return top100_playlist
#
#
# def create_playlist(time_machine_playlist):
#     pass


def get_auth_code():
    auth_url = 'https://accounts.spotify.com/authorize'
    scope = 'user-library-read user-library-modify playlist-modify-private playlist-modify-public'

    auth_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': 'http://localhost:8888/callback',
        'scope': scope
    }

    # The response object contains the link to authorize app
    spotify_response = requests.get(url=auth_url, params=auth_params)
    auth_link = spotify_response.url

    # Now open browser window with link
    webbrowser.open(auth_link)



def get_access_token():
    base64_credentials = base64.b64encode(CLIENT_ID.encode() + b':' + CLIENT_SECRET.encode()).decode("utf-8")

    auth_url = "https://accounts.spotify.com/api/token"
    token_headers = {
        "Authorization": "Basic " + base64_credentials,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    token_data = {
        "grant_type": "authorization_code",
        "code": CODE,
        "redirect_uri": "http://localhost:8888/callback"
    }

    spotify_response = requests.post(url=auth_url, headers=token_headers, data=token_data)
    response_json = spotify_response.json()
    print(response_json)

    token = response_json['access_token']
    refresh_token = response_json['refresh_token']

    return token, refresh_token


def search_songs(song_title, access_token):

    auth_headers = {
        'Authorization': "Bearer " + access_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    query = "remaster%20track:Doxy+artist:Miles%20Davis"
    search_url = f"https://api.spotify.com/v1/search+{query}"

    search_results = requests.get(url=search_url)

    print(search_results.text)



def create_new_playlist(access_token):

    access_headers = {
        'Authorization': "Bearer " + access_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    post_data = {
        "name": "james playlist2",
        "description": "test",
        "public": "true"
    }
    # Critical step
    post_data = json.dumps(post_data)

    playlist_response = requests.post(url=f"https://api.spotify.com/v1/users/{USER_ID}/playlists", data=post_data, headers=access_headers)
    try:
        playlist_response.json()['error']
    except KeyError:
        pass
    else:
        status_code = playlist_response.json()['error']['status']
        if status_code == 401:
            print('Token expired')
            # Later you implement refresh token here
    list_id = playlist_response.json()['id']

    return list_id


def add_to_playlist(list_id, access_token):
    playlist_headers = {
        'Authorization': "Bearer " + access_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    post_data = {
        "uris": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
                 "spotify:track:1301WleyT98MSxVHPZCA6M"]
    }
    post_data = json.dumps(post_data)

    playlist_url = BASE_URL + f"/{list_id}/tracks"
    r = requests.post(url=f"https://api.spotify.com/v1/users/{USER_ID}/playlists/{list_id}/tracks",
                      headers=playlist_headers,
                      data=post_data)
    print(r.json())
# # --------MAIN----------#
#
# date = input("Which year do you want to travel to? "
#              "Type the date in this format YYYY-MM-DD:")
# date_dt = dt.datetime.strptime(date, "%Y-%m-%d")
#
# # Convert back to string to keep leading zero in our month
# date_formatted = date_dt.strftime("%Y-%m-%d")
# time_machine_songs = scrape_top_100(date_formatted)

get_auth_code()

# TODO 4. Create a spotify playlist with 'date-billboard top 100'





# print(playlist_id)

# TODO 5. Add songs to that playlist
