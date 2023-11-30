import requests
import re
import json
from flask import Flask, jsonify, request

tmdb_id = 0
imdb_id = 0
TMDB_API_KEY="your key here"
season = 1
number_of_episodes = 1


#find_tmdb_id_URL = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id"

def get_tmdb_id(imdb_id):
    find_tmdb_id_URL = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id"
    tmdb_id_request = requests.get(find_tmdb_id_URL)

    if tmdb_id_request.status_code == 200:
        data = json.loads(tmdb_id_request.text)
        tmdb_id = data['tv_results'][0]['id']

        if tmdb_id is not 0:
            print("TMDB ID is: ", tmdb_id)
            tmdb_url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season}?api_key={TMDB_API_KEY}"
        else:
            print("No matching TMDB ID found for IMDb ID:", imdb_id)
    else:
        print("Error:", tmdb_id_request.status_code)

    get_number_of_episodes = requests.get(tmdb_url)

    if get_number_of_episodes.status_code == 200:
        data1 = json.loads(get_number_of_episodes.text)
        global number_of_episodes
        number_of_episodes = len(data1['episodes'])

        if number_of_episodes is not None:
            print("Number of episodes in season ",season," is: ", number_of_episodes)
        else:
            print("No matching TMDB ID found.")
    else:
        print("Error:", get_number_of_episodes.status_code)
    return(tmdb_id, number_of_episodes)


def check_for_season(torrents):
    for i in torrents['streams']:
        if 'behaviorHints' in i:
            if len(i["behaviorHints"]["bingeGroup"].split("|")[1]) == 40:
                i['title'] = multiply_file_size(i['title'])
            #print(i['title'])

def multiply_file_size(title):
    #print(text)
    if re.search(r"\d+(?:\.\d+)?\sGB", title) is not None:
        file_size_str = re.search(r"\d+(?:\.\d+)?\sGB", title).group(0)
        file_size = float(file_size_str.replace(" GB", ""))
        file_size_modified = file_size * number_of_episodes
        file_size_modified_string = str(round(file_size_modified,2)) + " GB"
        return re.sub(file_size_str, file_size_modified_string, title)
    elif re.search(r"\d+(?:\.\d+)?\sMB", title) is not None:
        file_size_str = re.search(r"\d+(?:\.\d+)?\sMB", title).group(0)
        file_size = float(file_size_str.replace(" MB", ""))
        file_size_modified = file_size * number_of_episodes
        if file_size_modified < 1000:
            file_size_modified_string = str(round(file_size_modified,2)) + " MB"
            return re.sub(file_size_str, file_size_modified_string, title)
        else:
            file_size_modified = file_size_modified / 1000
            file_size_modified_string = str(round(file_size_modified,2)) + " GB"
            return re.sub(file_size_str, file_size_modified_string, title)



def get_torrentio_results(query):
    qlength = len(query)+2
    query = str(query)[2:qlength]
    print(query)
    url = "https://torrentio.strem.fun/" + str(query)
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    else:
        return None


""" if __name__ == "__main__":
    # Example usage
    query = "Breaking Bad S05E14"
    torrents = search_torrents(query)
    for torrent in torrents:
        print(torrent) """

app = Flask(__name__)

@app.route("/search", methods=["GET"])
def search_torrents_handler():
    query = request.query_string
    torrents = get_torrentio_results(query)
    str_query = str(query)
    if re.search(r"\/stream\/series\/", str_query) is not None:
        imdb_id = re.search(r"(tt\d+)",str_query).group(0)
        season = re.search(r":(\d):",str_query).group(1)
        season = int(season.lstrip("0"))
        print(season)
        get_tmdb_id(imdb_id)
        check_for_season(torrents)
    return jsonify(torrents)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
