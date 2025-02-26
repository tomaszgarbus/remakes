import matplotlib.pyplot as plt
import csv
import requests
import os
import json
import numpy as np

API_KEY = "c628745f"
CSV_PATH = "remakes.csv"


def get_movie_metadata(title: str, year: str):
    cache_key = f"{year},{title}"
    cache_path = os.path.join("cache/", cache_key)
    if os.path.exists(cache_path):
        return json.load(open(cache_path))
    url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={API_KEY}"
    response = requests.get(url).json()
    json.dump(response, open(cache_path, "w"))
    return response


def compute_avg_rating(response) -> float:
    """Computes an average rating from different sources, on a scale 0 to 1."""
    ratings = []
    for rating in response["Ratings"]:
        val = rating["Value"]
        source = rating["Source"]
        if source == "Internet Movie Database":
            ratings.append(float(val.split("/")[0]) / 10.)
        if source == "Rotten Tomatoes":
            ratings.append(float(val.split("%")[0]) / 100.)
        if source == "Metacritic":
            ratings.append(float(val.split("/")[0]) / 100.)
    ratings.append(float(response["imdbRating"]) / 100.)
    return np.mean(ratings)

if __name__ == "__main__":
    entries = []
    with open(CSV_PATH, "r") as fp:
        rdr = csv.reader(fp)
        for line in rdr:
            entries.append(tuple(line))

    plot_entries = []
    for entry in entries:
        for year, remake in [(entry[1], False), (entry[2], True)]:
            response = get_movie_metadata(entry[0], year)
            rating = compute_avg_rating(response)
            print(entry[0], year, rating)
            plot_entries.append((year, rating, remake))

    years, ratings, remakes = *zip(*plot_entries)

    plt.scatter(years, ratings, c=colors)
    plt.show()
