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

    fig, ax = plt.subplots()

    orig_id = {}

    plot_entries = []
    for entry in entries:
        title_orig, year_orig, title_remake, year_remake = entry
        if title_orig not in orig_id:
            orig_id[title_orig] = len(orig_id) + 1
        year_orig = int(year_orig)
        year_remake = int(year_remake)
        rating_orig = compute_avg_rating(
            get_movie_metadata(title_orig, year_orig))
        rating_remake = compute_avg_rating(
            get_movie_metadata(title_remake, year_remake))
        plot_entries.append(
            (orig_id[title_orig], title_orig, year_orig, rating_orig, False))
        plot_entries.append(
            (orig_id[title_orig], title_remake, year_remake, rating_remake,
            True))
        xs = [year_orig, year_remake]
        ys = [rating_orig, rating_remake]
        ax.plot(xs, ys, color="lightgrey", linestyle="dashed",
            linewidth=1)

    ids, titles, years, ratings, remakes = list(zip(*plot_entries))
    color_mapping = { True: "red", False: "blue"}
    colors = [color_mapping[r] for r in remakes]
    ax.scatter(years, ratings, c=colors, s=120)
    for i, title, year, rating, remake in zip(
        ids, titles, years, ratings, remakes):
        ax.annotate(i, (year + 2, rating), color=color_mapping[remake])
    
    legend = sorted([(orig_id[title], title) for title in orig_id])
    legend = [f"{i}: {title}" for i, title in legend]
    ax.legend(legend)
    ax.set_ylabel("Avg. rating on imdb")
    ax.set_xlabel("year")
    plt.show()
