#! /usr/bin/python3
import datetime as dt
from api_config import CLIENT_ID, CLIENT_SECRET, USER_ID, CODE, ACCESS_TOKEN, REFRESH_TOKEN
from bs4 import BeautifulSoup
import requests
import webbrowser
import base64
import json
from urllib import parse
import pprint

BASE_URL = 'https://api.spotify.com/v1'


def scrape_top_100(billboard_date):
    year = billboard_date.split('-')[0]
    month = billboard_date.split('-')[1]
    day = billboard_date.split('-')[2]

    top100_url = f"http://billboard.com/charts/hot-100/{year}-{month}-{day}/"
    response = requests.get(url=top100_url)

    soup = BeautifulSoup(response.text, features='html.parser')
    all_song_tags = soup.select("li > ul > li > h3")
    all_artist_tags = soup.select("h3 ~ span", class_="c-label")

    top100_playlist = []
    for song_tag, artist_tag in zip(all_song_tags, all_artist_tags):
        song_title = song_tag.get_text(strip=True)
        artist = artist_tag.get_text(strip=True)
        top100_playlist.append((song_title, artist))

    return top100_playlist


def need_auth_code():
    if len(CODE) < 1:
        return True
    return False


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
    print("ACCESS_TOKEN:", response_json['access_token'])
    print("REFRESH_TOKEN:", response_json['refresh_token'])

    access_token = response_json['access_token']
    refresh_token = response_json['refresh_token']

    return access_token, refresh_token


def search_songs(song_list, access_token):
    song_id_list = []
    for entry in song_list:
        song_title = entry[0]
        artist_name = entry[1]

        song_title = parse.quote(song_title)
        artist_name = parse.quote(artist_name)

        auth_headers = {
            'Authorization': "Bearer " + access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        query = f"artist:{artist_name}+name:{song_title}&type=track&limit=1"
        search_url = f"https://api.spotify.com/v1/search?query={query}"
        search_results = requests.get(url=search_url, headers=auth_headers)

        try:
            song_id = search_results.json()['tracks']['items'][0]['id']
        except IndexError:
            continue
        else:
            song_id_list.append(song_id)

    pprint.pprint(song_id_list)
    return song_id_list


def create_new_playlist(access_token, playlist_title):

    access_headers = {
        'Authorization': "Bearer " + access_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    post_data = {
        "name": playlist_title,
        "description": "user playlist",
        "public": "false"
    }
    # Critical step
    post_data = json.dumps(post_data)

    playlist_response = requests.post(url=f"https://api.spotify.com/v1/users/{USER_ID}/playlists", data=post_data,
                                      headers=access_headers)
    try:
        playlist_response.json()['error']
    except KeyError:
        pass
    else:
        status_code = playlist_response.json()['error']['status']
        if status_code == 401:
            print('Token expired')

    list_id = playlist_response.json()['id']

    return list_id


def add_to_playlist(song_id_list, access_token, list_id):
    playlist_headers = {
        'Authorization': "Bearer " + access_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    for track_id in song_id_list:
        post_data = {
            "uris": [f"spotify:track:{track_id}"]
        }
        post_data = json.dumps(post_data)

        response = requests.post(url=f"https://api.spotify.com/v1/users/{USER_ID}/playlists/{list_id}/tracks",
                                 headers=playlist_headers,
                                 data=post_data)
        print(f"{track_id} added successfully")


def token_expired(access_token):
    auth_headers = {
        'Authorization': "Bearer " + access_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    query = f"album:gold%20artist:abba&type=album"
    search_url = f"https://api.spotify.com/v1/search?query={query}"

    response = requests.get(url=search_url, headers=auth_headers)

    try:
        response.json()['error']
    except KeyError:
        pass
    else:
        status_code = response.json()['error']['status']
        if status_code == 401:
            print('Token expired')
            return True
        else:
            return False


def need_access_token():
    if len(ACCESS_TOKEN) < 1:
        return True
    return False


def get_new_access_token(refreshed_token):

    base64_credentials = base64.b64encode(CLIENT_ID.encode() + b':' + CLIENT_SECRET.encode()).decode("utf-8")
    auth_url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + base64_credentials,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    post_body = {
        "grant_type": "refresh_token",
        "refresh_token": refreshed_token
    }

    spotify_response = requests.post(url=auth_url, headers=headers, data=post_body)
    response_json = spotify_response.json()
    new_access_token = response_json['access_token']
    print("New access token granted:", response_json['access_token'])

    # Test if there's a new refresh token being sent back
    try:
        new_refresh_token = response_json['refresh_token']
        print("NEW REFRESH TOKEN:", response_json)
    except KeyError:
        pass
    else:
        pass
        # Later, new refresh token should be written to disk
    return new_access_token

# --------MAIN----------#


date = input("Which year do you want to travel to? "
             "Type the date in this format YYYY-MM-DD:")
date_dt = dt.datetime.strptime(date, "%Y-%m-%d")
playlist_date = date_dt.strftime("%Y-%m-%d")



if need_auth_code():
    get_auth_code()

if need_access_token():
    token, refresh_token = get_access_token()
else:
    token = ACCESS_TOKEN
    refresh_token = REFRESH_TOKEN

if token_expired(token):
    token = get_new_access_token(REFRESH_TOKEN)

playlist_id = create_new_playlist(token, playlist_title=playlist_date)
scraped_list = scrape_top_100(playlist_date)
spotify_song_id_list = search_songs(song_list=scraped_list, access_token=token)
add_to_playlist(spotify_song_id_list, token, playlist_id)








