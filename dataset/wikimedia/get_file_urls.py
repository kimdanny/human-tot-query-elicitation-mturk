import os
import re
import sys
import requests
import csv
import pandas as pd
from tqdm import tqdm


# header to comply with User-Agent policy
headers = {
    "User-Agent": "<FILL YOUR USER AGENT DETAILS>",
}

# Wikipedia API query string to get images in original resolution
# query = 'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='

# Wikipedia API query string to get images in 450px width resolution
query = "http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&pithumbsize=450&titles="


def get_media_url(file_name):
    """Get the URL of the media file from Wikipedia."""
    partial_url = "File:" + file_name
    try:
        api_res = requests.get(query + partial_url, headers=headers).json()
        page = next(iter(api_res["query"]["pages"].values()))
        # return page.get('original', {}).get('source') # for original resolution
        return page.get("thumbnail", {}).get("source")  # for 450px resolution
    except Exception as exc:
        print(f"Failed to fetch media URL for {file_name}: {exc}")
    return None


def extract_file_name(local_fp: str):
    """
    Given /YOUR/SAVE/PATH/data_infobox/celebrity/Jenna Ortega/infobox_image/Jenna Ortega 2022 (cropped).jpg
    return Jenna Ortega 2022 (cropped).jpg
    """
    fn = local_fp.split("/")[-1]
    return fn


if __name__ == "__main__":
    TSV_SAVE_PATH = "/YOUR/SAVE/PATH/"
    tmdb_base_path = "https://image.tmdb.org/t/p/original/"
    filenames = [
        "celebrity_candidates.csv",
        "celebrity_fallbacks.csv",
        "landmark_candidates.csv",
        "landmark_fallbacks.csv",
        "movie_candidates.csv",
        "movie_fallbacks.csv",
    ]
    base_fp = f"/YOUR/SAVE/PATH/dataset/"
    for fn in filenames:
        SAVE_FN = os.path.join(TSV_SAVE_PATH, f"{fn.split('.')[0]}_urls.csv")
        fp = os.path.join(base_fp, fn)

        file_df = pd.read_csv(fp)
        page_names = list(file_df["PageName"])  # id
        image_file_paths = list(file_df["ImageFilePath"])
        file_names_list = list(map(extract_file_name, image_file_paths))

        image_urls = []
        for image_fn in tqdm(file_names_list):
            if fn.startswith("movie"):
                image_url = f"{tmdb_base_path}{image_fn}"
            else:
                image_url = get_media_url(image_fn)  # value
            image_urls.append(image_url)

        with open(SAVE_FN, mode="w", newline="") as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(["PageName", "ImageURL"])
            # Write the data
            for pn, url in zip(page_names, image_urls):
                writer.writerow([pn, url])
