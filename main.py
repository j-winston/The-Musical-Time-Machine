import datetime as dt
from pprint import pprint
from api_config import CLIENT_ID, CLIENT_SECRET
from bs4 import BeautifulSoup
import requests
BASE_URI = "https://api.spotify.com/v1"

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


def create_playlist(time_machine_playlist):
    pass

def authenticate_spotify():

    url = f"{BASE_URI}/authorize"
    scope = "playlist-modify-private"
    redirect_uri = "http://localhost:8888/callback"

    parameters = {
        "client_id": CLIENT_ID,
        "scope": scope,
        "redirect_uri": redirect_uri
    }
    response = requests.get(url=url, params=parameters)









# --------MAIN----------#

date = input("Which year do you want to travel to? "
             "Type the date in this format YYYY-MM-DD:")
date_dt = dt.datetime.strptime(date, "%Y-%m-%d")

# Convert back to string to keep leading zero in our month
date_formatted = date_dt.strftime("%Y-%m-%d")
time_machine_songs = scrape_top_100(date_formatted)

authenticate_spotify()


# TODO 3. Search spotify for songs from that list
create_playlist(time_machine_songs)












# TODO 4. Create a spotify playlist with 'date-billboard top 100'

# TODO 5. Add songs to that playlist