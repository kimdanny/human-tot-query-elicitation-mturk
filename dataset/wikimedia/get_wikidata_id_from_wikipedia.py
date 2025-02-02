import requests
import pandas as pd
import os
import time
from tqdm import tqdm


def get_wikidata_id_from_wikipedia_title_single(page_title: str):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": page_title,
        "prop": "pageprops",
        "format": "json",
    }

    response = requests.get(url, params=params)
    data = response.json()

    pages = data["query"]["pages"]
    for page_id, page_info in pages.items():
        if "pageprops" in page_info and "wikibase_item" in page_info["pageprops"]:
            return page_info["pageprops"]["wikibase_item"]

    return None


def get_wikidata_ids_from_wikipedia_titles_batch(page_titles: list):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": "|".join(page_titles),  # Join titles with |
        "prop": "pageprops",
        "format": "json",
    }

    response = requests.get(url, params=params)
    data = response.json()

    wikidata_ids = {}
    pages = data["query"]["pages"]
    for page_id, page_info in pages.items():
        if "pageprops" in page_info and "wikibase_item" in page_info["pageprops"]:
            wikidata_ids[page_info["title"]] = page_info["pageprops"]["wikibase_item"]

    return wikidata_ids


# Driver
files = [
    "celebrity_candidates_urls",
    "celebrity_fallbacks_urls",
    "landmark_candidates_urls",
    "landmark_fallbacks_urls",
    "movie_candidates_urls",
    "movie_fallbacks_urls",
]
for fn in files:
    fp = os.path.join("nist", f"{fn}.csv")
    df = pd.read_csv(fp)
    entities: list = df["PageName"].tolist()

    all_wikidata_ids = {}
    batch_size = 20

    for i in tqdm(range(0, len(entities), batch_size)):
        batch = entities[i : i + batch_size]
        wikidata_ids = get_wikidata_ids_from_wikipedia_titles_batch(batch)
        all_wikidata_ids.update(wikidata_ids)
        time.sleep(2)  # Add delay to avoid rate limits

    df["WikidataID"] = df["PageName"].map(all_wikidata_ids)
    df = df[["PageName", "WikidataID", "ImageURL"]]

    # Save the updated DataFrame to a new CSV file
    df.to_csv(os.path.join("nist", f"new_{fn}.csv"), index=False)
