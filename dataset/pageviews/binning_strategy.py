"""
Post-processing after the aggregate_pageviews.py
Read from pageviews_rank.csv
and create pageviews_binned.csv
"""
import pandas as pd
import sys
import os
import re
from collections import Counter
from tqdm import tqdm


CLUSTER_USER = "YOUR_USER_NAME"
BASE_PATH = f"/YOUR/BASE/PATH/"
DATA_BASE_PATH = "/YOUR/BASE/PATH/data_infobox"
PAGEVIEWS_RANK_FILE_NAME = "pageviews_rank.csv"
# PAGEVIEWS_RANK_FILE_NAME = "pageviews_rank_sub-domain.csv"
PAGEVIEWS_BINNED_FILE_NAME = "pageviews_binned.csv"

# CATEGORY_NAME = "landmark"
# CATEGORY_NAME = "movie"
CATEGORY_NAME = "celebrity"

if not os.path.exists(f"{DATA_BASE_PATH}/{CATEGORY_NAME}/{PAGEVIEWS_RANK_FILE_NAME}"):
    print("File does not exist")
    sys.exit(1)

pageviews_df = pd.read_csv(
    f"{DATA_BASE_PATH}/{CATEGORY_NAME}/{PAGEVIEWS_RANK_FILE_NAME}"
)

# 0. if HasImage column is not there, attach.
IMAGE_DIR_NAME = "infobox_image"
if "HasImage" not in pageviews_df.columns:
    dirs = list(pageviews_df["FolderPath"])
    aggregated_data = []
    for dir in tqdm(dirs):
        has_image = 0
        image_fp = "None"
        if os.path.exists(f"{dir}/{IMAGE_DIR_NAME}/"):
            has_image = 1
            # get image file path
            files = os.listdir(f"{dir}/{IMAGE_DIR_NAME}/")
            try:
                image_fp = os.path.join(
                    f"{dir}/{IMAGE_DIR_NAME}/", files[0]
                )  # pick the first image
            except IndexError as e:
                continue
        aggregated_data.append((dir, int(has_image), image_fp))

    interim_df = pd.DataFrame(
        aggregated_data, columns=["FolderPath", "HasImage", "ImageFilePath"]
    )

    pageviews_df = pageviews_df.merge(interim_df, how="left", on="FolderPath")


# 1. filter out files with no images
pageviews_df = pageviews_df[pageviews_df["HasImage"] == 1]
# 2. remove drafts
pageviews_df = pageviews_df[~pageviews_df["PageName"].str.startswith("Draft:")]
# 3. remove NotValid subdomains
pageviews_df = pageviews_df[pageviews_df["WhichSubDomain"] != "NotValid"]

# 4. change filename that contains description
# because these files won't open as image files

problem_df = pageviews_df[
    pageviews_df["ImageFilePath"].str.contains("&lt;")
    & pageviews_df["ImageFilePath"].str.contains("&gt;")
]


def rename_filename(filename: str):
    """
    There are 190 images that looks like the example below
    Example image file:
    Kölner Dom - Westfassade 2022 ohne Gerüst-0968.jpg&lt;!---Do not change this image for a night picture or a long view or a landscape . THIS picture needs to be a straightforward ID of the building itself.---&gt;
    """
    pattern = re.compile(r"&lt;(.*)")
    modified_name = re.sub(pattern, "", filename)
    modified_name = modified_name.strip()
    return modified_name


modified_df = problem_df.copy()
modified_df["ImageFilePath"] = problem_df["ImageFilePath"].apply(rename_filename)
pageviews_df.update(modified_df)

# Post-processing steps
# 5. (introduced after subdomain joining) join the ImageFilePath
original_csv = pd.read_csv(f"{BASE_PATH}/dataset/pageviews/pageviews_binned.csv")
pageviews_df = pd.merge(
    pageviews_df,
    original_csv[["FolderPath", "ImageFilePath"]],
    on="FolderPath",
    how="left",
)
pageviews_df = pageviews_df.dropna()

# It's important to enable this part in landmark
pageviews_df = pageviews_df[~pageviews_df["ImageFilePath"].str.contains("&lt;")]

# removing 195 rows
modified_df = modified_df[~modified_df["ImageFilePath"].str.contains("&lt;")]

# use modified_df to change the filenames of the actual images in the /data folder
# it's okay to iterate rows of modified_df as small number of rows were chosen
for i, row in modified_df.iterrows():
    parent_dir, _ = row["ImageFilePath"].split("/infobox_image/")
    parent_dir = os.path.join(parent_dir, "infobox_image")

    files = os.listdir(parent_dir)
    old_image_fp = os.path.join(parent_dir, files[0])  # pick the first image
    new_image_fp = row["ImageFilePath"]
    os.rename(old_image_fp, new_image_fp)

# Quantile-based discretization (equal-sized buckets)
bin_labels = ["VeryLow", "Low", "Medium", "High", "VeryHigh"]
pageviews_df["PageViewsBin"] = pd.qcut(
    pageviews_df["PageViews"], q=5, labels=bin_labels
)

# to local
pageviews_df.to_csv(
    f"{BASE_PATH}/dataset/pageviews/{CATEGORY_NAME}_{PAGEVIEWS_BINNED_FILE_NAME}",
    index=False,
)
# to remote /data dir
pageviews_df.to_csv(
    f"{DATA_BASE_PATH}/{CATEGORY_NAME}/{PAGEVIEWS_BINNED_FILE_NAME}", index=False
)

total_counter = Counter(pageviews_df["PageViewsBin"].tolist())
print(total_counter)

## Results:

# landmark
# {'VeryLow': 14705, 'High': 14662, 'Medium': 14655, 'VeryHigh': 14652, 'Low': 14622}

# movie
# {'VeryLow': 11656, 'Medium': 11655, 'VeryHigh': 11654, 'Low': 11654, 'High': 11652}

# celebrity
# Counter({'VeryHigh': 2351, 'High': 2351, 'Low': 2351, 'VeryLow': 2351, 'Medium': 2350})
