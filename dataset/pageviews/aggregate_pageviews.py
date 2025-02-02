import os
import json
from tqdm import tqdm
import pandas as pd
from typing import List


def read_pageviews_data(file_path):
    """Read the pageviews data from a file."""
    with open(file_path, "r") as f:
        data = json.load(f)

    return data["pageviews"]


def aggregate_pageviews(base_path, image_dir_name) -> List[tuple]:
    """Aggregate pageviews from all subfolders."""
    aggregated_data = []
    for _, dirs, _ in os.walk(base_path):
        for dir in tqdm(dirs):
            has_image = 0
            image_fp = "None"
            if os.path.exists(f"{base_path}/{dir}/{image_dir_name}/"):
                has_image = 1
                # get image file path
                files = os.listdir(f"{base_path}/{dir}/{image_dir_name}/")
                try:
                    image_fp = os.path.join(
                        f"{base_path}/{dir}/{image_dir_name}/", files[0]
                    )  # pick the first image
                except IndexError as e:
                    continue

            page_view_fp = os.path.join(base_path, dir, "pageviews.txt")
            if os.path.exists(page_view_fp):
                pageviews = read_pageviews_data(page_view_fp)
                for page, views in pageviews.items():
                    aggregated_data.append(
                        (views, page, f"{base_path}/{dir}", has_image, image_fp)
                    )
            else:
                # pageviews.txt does not exist
                pass

    return aggregated_data


def write_to_csv(data: List[tuple], file_path: str) -> None:
    """Write the aggregated data to a CSV file.
    :param
        data: tuple of 5 values
        file_path: file path to write to
    """
    data.sort(reverse=True)  # Sort by pageviews in descending order
    df = pd.DataFrame(
        data,
        columns=["PageViews", "PageName", "FolderPath", "HasImage", "ImageFilePath"],
    )
    df.index = range(1, len(df) + 1)
    df.index.name = "Rank"
    df.to_csv(file_path, index=True, index_label="Rank")
    print(f"Aggregated pageviews data written to {file_path}")


def main():
    CATEGORY_NAME = "movie"
    IMAGE_DIR_NAME = "backdrops_imgs"

    # CATEGORY_NAME = "landmark"
    # IMAGE_DIR_NAME = "infobox_image"

    # CATEGORY_NAME = "celebrity"
    # IMAGE_DIR_NAME = ""

    BASE_PATH = f"/YOUR/BASE/PATH/data_infobox/{CATEGORY_NAME}"
    OUTPUT_FILE = os.path.join(BASE_PATH, "pageviews_rank.csv")

    if os.path.exists(OUTPUT_FILE):
        ans = input(
            "you already have the csv file in this path. Do you want to overwrite? yes/no"
        )
        if ans == "yes":
            aggregated_data: List[tuple] = aggregate_pageviews(
                BASE_PATH, IMAGE_DIR_NAME
            )
            write_to_csv(aggregated_data, OUTPUT_FILE)
    else:
        aggregated_data: List[tuple] = aggregate_pageviews(BASE_PATH, IMAGE_DIR_NAME)
        write_to_csv(aggregated_data, OUTPUT_FILE)


if __name__ == "__main__":
    main()
