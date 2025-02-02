# Dealing with very large dataframe (1.6M)

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


def aggregate_pageviews(base_path, dirs) -> List[tuple]:
    """Aggregate pageviews from all subfolders."""
    aggregated_data = []
    for dir in tqdm(dirs):
        page_view_fp = os.path.join(base_path, dir, "pageviews.txt")
        if os.path.exists(page_view_fp):
            pageviews = read_pageviews_data(page_view_fp)
            for page, views in pageviews.items():
                aggregated_data.append((views, page, f"{base_path}/{dir}"))
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
    print("start writing file")
    data.sort(reverse=True)  # Sort by pageviews in descending order
    df = pd.DataFrame(
        data,
        columns=["PageViews", "PageName", "FolderPath"],
    )
    df.index = range(1, len(df) + 1)
    df.index.name = "Rank"
    df.to_csv(file_path, index=True, index_label="Rank")
    print(f"Aggregated pageviews data written to {file_path}")


def main(dirs, output_file):
    if os.path.exists(output_file):
        ans = input(
            "you already have the csv file in this path. Do you want to overwrite? yes/no"
        )
        if ans == "yes":
            aggregated_data: List[tuple] = aggregate_pageviews(BASE_PATH, dirs)
            write_to_csv(aggregated_data, output_file)
    else:
        aggregated_data: List[tuple] = aggregate_pageviews(BASE_PATH, dirs)
        write_to_csv(aggregated_data, output_file)


if __name__ == "__main__":
    CATEGORY_NAME = "celebrity"
    IMAGE_DIR_NAME = "infobox_image"

    BASE_PATH = f"/YOUR/BASE/PATH/data_infobox/{CATEGORY_NAME}"

    dirs = [
        f for f in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, f))
    ]
    chunck_size = len(dirs) // 5

    for iteration_num in range(5):
        output_file = os.path.join(
            "/YOUR/BASE/PATH/", f"pageviews_rank_celebrity_{iteration_num}.csv"
        )
        input_dirs = dirs[
            iteration_num * chunck_size : (iteration_num + 1) * chunck_size
        ]
        main(input_dirs, output_file)
