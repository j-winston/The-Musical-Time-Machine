import datetime as dt
from bs4 import BeautifulSoup
import requests




# # TODO 1. Get user input
# billboard_date = input("Which year do you want to travel to? "
#                        "Type the date in this format YYYY-MM-DD:")
# billboard_date = dt.datetime.strptime(billboard_date, "%Y-%m-%d")
#
# # So that we can preserve the leading zero for our billboard URL
# billboard_date = billboard_date.strftime("%Y-%m-%d")
# year = billboard_date.split('-')[0]
# month = billboard_date.split('-')[1]
# day = billboard_date.split('-')[2]
#


# TODO 2. Scrape top 100 songs for that date
# 2.1 Get url for that date
top100_url = f"http://billboard.com/charts/hot-100/1999-01-12/"
# 2.2 Get request
response = requests.get(url=top100_url)

# 2.2 Get the entire page for that date
soup = BeautifulSoup(response.text, features='html.parser')

# # 2.3 Isolate the song tags and extract
# song_tags = soup.find_all('h3', id='title-of-a-story', class_=["c-title",
# "a-no-trucate a-font-primary-bold-s",
# "u-letter-spacing-0021",
# "u-font-size-23@tablet",
# "lrv-u-font-size-16",
# "u-line-height-125",
# "u-line-height-normal@mobile-max",
# "a-truncate-ellipsis u-max-width-245",
# "u-max-width-230@tablet-only u-letter-spacing-0028@tablet"])
#
# for tag in song_tags:
#     print(tag.get_text(strip=True))

top100_list = []
# 2.3 Isolate the song tags and extract
all_song_tags = soup.select("li > ul > li > h3")
all_artist_tags = soup.select("h3 ~ span", class_="c-label")

for song_tag, artist_tag in zip(all_song_tags, all_artist_tags):
    song_name = song_tag.get_text(strip=True)
    artist_name = artist_tag.get_text(strip=True)
    top100_list.append((song_name, artist_name))

print(top100_list)


#
# artist_tags = soup.select("h3 ~ span", class_="c-label")
# for tag in artist_tags:
#     print(tag.get_text(strip=True))














# TODO 3. Search spotify for songs from that list


# TODO 4. Create a spotify playlist with 'date-billboard top 100'

# TODO 5. Add songs to that playlist