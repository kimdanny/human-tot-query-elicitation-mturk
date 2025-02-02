# End to End pipeline from image drawing to publishing a HIT to MTurk
import pandas as pd
import numpy as np
from requests.utils import quote
import sys
import os
import json
from random import randint
from collections import Counter
from datetime import datetime
from s3.s3_handler import upload_object_to_s3_bucket
from mturk.create_hit import CreateHIT
from dynamo_db.dynamo_db_handler import DynamoDBHandler


def read_param_file():
    """
    Get a dict that contains the contents of the parameter file.
    """
    # Remind the forgetful.
    if len(sys.argv) != 3:
        print("Usage: python e2e_create.py <ParamFile> <Seed>\n\n")
        sys.exit(1)

    if not os.path.exists(sys.argv[1]):
        print(f"Can't find {sys.argv[1]}.")
        sys.exit(1)

    # Read the .param file into a dict.
    with open(sys.argv[1]) as f:
        d = json.load(f)

    # set the seed
    global SEED
    SEED = int(sys.argv[2])
    if SEED < 1:
        print("Please provide seed bigger than 0")
        sys.exit(1)

    return d


def make_wiki_url(page_name: str):
    return f"https://en.wikipedia.org/wiki/{quote(page_name)}"


@DeprecationWarning
def __draw_image_batch_randomly_from_bins(page_views_fp, k=20, stratify=False):
    """
    Draw image paths and their corresponding wikipedia urls

    One batch drawn from this function is use in one HIT
    4 drawing strategies:
        1. draw_image_batch_from_bins(page_views_fp, k=20, stratify=True)
        2. draw_image_batch_from_bins(page_views_fp, k=20, stratify=False)
        3. draw_image_batch_from_bins(page_views_fp, k=50, stratify=True)
        4. draw_image_batch_from_bins(page_views_fp, k=50, stratify=False)

    :param
        page_views_fp: csv file path
        k: how many to draw in total
        stratify: boolean if you need stratification in drawing
    :returns
        list of local image file path (not just the name. whole absolute path)
    """
    fps_drew = []
    wiki_urls_drew = []

    page_views_df = pd.read_csv(page_views_fp)
    # select how many to draw from each bin depending on k and stratification strategy
    if stratify:
        num_per_bin = k // 5
        remainder = k - num_per_bin
        bins_drawsize = {
            "VeryLow": num_per_bin,
            "Low": num_per_bin,
            "Medium": num_per_bin,
            "High": num_per_bin,
            "VeryHigh": num_per_bin + remainder,
        }
    else:
        bins_drawsize = {"VeryHigh": k}

    for bin, drawsize in bins_drawsize.items():
        df = page_views_df[page_views_df["PageViewsBin"] == bin]
        # Randomly draw
        random_indices = np.random.choice(df.index, drawsize, replace=False)
        df = df.loc[random_indices]

        sampled_paths = list(df["ImageFilePath"])
        fps_drew.extend(sampled_paths)

        sampled_page_name = list(df["PageName"])
        sampled_wiki_urls = map(make_wiki_url, sampled_page_name)
        wiki_urls_drew.extend(sampled_wiki_urls)

    return fps_drew, wiki_urls_drew


@DeprecationWarning
def __draw_image_batch_randomly_cand_fall(
    candidates_fp, fallbacks_fp, k=20
) -> tuple[list]:
    """
    Draw image paths and their corresponding wikipedia urls randomly
    from both candidates and fallbacks file.

    :param
        candidates_fp: csv file path
        fallbacks_fp: csv file path
        k: how many to draw in total including fallbacks
    :returns
        list of local image file path (not just the name. whole absolute path)
            and corresponding wikipedia page url
            for both candidates and fallbacks
    """
    candidates_df = pd.read_csv(candidates_fp)
    fallbacks_df = pd.read_csv(fallbacks_fp)

    def draw_from_df(df, draw_size):
        fps_drew = []
        wiki_urls_drew = []

        # random draw
        random_indices = np.random.choice(df.index, draw_size, replace=False)
        df = df.loc[random_indices]

        sampled_paths = list(df["ImageFilePath"])
        fps_drew.extend(sampled_paths)

        sampled_page_name = list(df["PageName"])
        sampled_wiki_urls = map(make_wiki_url, sampled_page_name)
        wiki_urls_drew.extend(sampled_wiki_urls)

        return fps_drew, wiki_urls_drew

    # set fallback drawing size for each df
    fallback_size = 2 if k > 20 else 1

    candidate_fps_drew, candidate_wiki_urls_drew = draw_from_df(
        candidates_df, k - fallback_size
    )
    fallbacks_fps_drew, fallbacks_wiki_urls_drew = draw_from_df(
        fallbacks_df, fallback_size
    )

    images_fps = candidate_fps_drew + fallbacks_fps_drew
    wiki_urls = candidate_wiki_urls_drew + fallbacks_wiki_urls_drew

    return images_fps, wiki_urls


def draw_20_images_batch(
    candidates_fp: str, fallbacks_fp: str, seed: int
) -> tuple[list]:
    """
    Draw 20 images deterministically and make their corresponding wikipedia urls
    from both candidates and fallbacks file.

    :param
        candidates_fp: csv file path
        fallbacks_fp: csv file path
        k: how many to draw in total including fallbacks
    :returns
        list of local image file path (not just the name. whole absolute path)
            and corresponding wikipedia page url
            for both candidates and fallbacks
    """
    images_fps = []
    wiki_urls = []
    candidates_df = pd.read_csv(candidates_fp)
    fallbacks_df = pd.read_csv(fallbacks_fp)

    def get_info_from_df(df) -> tuple[str, str]:
        # get image file path
        ifp = str(df["ImageFilePath"])
        # get wiki page url
        url = make_wiki_url(str(df["PageName"]))
        return ifp, url

    # Candidates: draw from 19 buckets
    bucket_counter = Counter(candidates_df["Bucket"].tolist())
    for bucket, bucket_size in bucket_counter.items():
        df = candidates_df[candidates_df["Bucket"] == bucket]
        df = df.iloc[seed % bucket_size]
        fp_drew, url_drew = get_info_from_df(df)
        images_fps.append(fp_drew)
        wiki_urls.append(url_drew)

    # Fallbacks: randomly draw one
    fallbacks_df = fallbacks_df.iloc[randint(0, len(fallbacks_df))]
    fp_drew, url_drew = get_info_from_df(fallbacks_df)
    images_fps.append(fp_drew)
    wiki_urls.append(url_drew)

    return images_fps, wiki_urls


def main():
    params = read_param_file()

    CANDIDATES_FP = params["candidatesFilePath"]
    FALLBACKS_FP = params["fallbacksFilePath"]
    DRAWING_STRATEGY = int(params["drawingStrategy"])
    STAGE = params["stage"]
    DOMAIN = params["domain"]
    del params

    if DRAWING_STRATEGY not in {1, 2}:
        print("Acceptable <DRAWING_STRATEGY> input: 1, 2 ")
        sys.exit(1)

    # configuring DynamoDB Table name depending on the stage
    PARTITION_KEY = "HITID"
    if STAGE == "live":
        HIT_TABLE_NAME = "HIT-Table"
    elif STAGE == "sandbox":
        HIT_TABLE_NAME = f"HIT-Table-{STAGE}"
    else:
        raise NotImplementedError(f"Stage {STAGE} is not supported.")

    # import xml templates depending on the domain
    if DOMAIN == "landmark":
        from mturk.frontend_template_landmark import (
            xml_template_20_urls,
            # xml_template_50_urls,
        )
    elif DOMAIN == "movie":
        from mturk.frontend_template_movie import (
            xml_template_20_urls,
            # xml_template_50_urls,
        )
    elif DOMAIN == "celebrity":
        from mturk.frontend_template_celebrity import (
            xml_template_20_urls,
            # xml_template_50_urls,
        )
    else:
        raise NotImplementedError(f"Domain {DOMAIN} not supported.")

    # set s3 bucket name depending on the domain
    BUCKET_NAME = f"tot-mturk-images-{DOMAIN}"
    # s3 key encoding strategies depending on the domain
    if DOMAIN in {"landmark", "celebrity"}:
        FILENAME_ENCODING = True
    else:
        FILENAME_ENCODING = False

    # set the drawing function and xml template depending on the drawing strategy
    if DRAWING_STRATEGY == 1:
        draw = lambda: draw_20_images_batch(CANDIDATES_FP, FALLBACKS_FP, seed=SEED)
        xml_string = xml_template_20_urls
    # elif DRAWING_STRATEGY == 2:
    #     draw = lambda: draw_image_batch(CANDIDATES_FP, FALLBACKS_FP, k=50)
    #     xml_string = xml_template_50_urls
    else:
        raise NotImplementedError(
            f"Drawing Strategy {DRAWING_STRATEGY} is not supported."
        )

    # 1. Draw a fresh batch and host images to S3
    image_fp_batch, wiki_url_batch = draw()
    s3_keys = []
    s3_urls = []
    for image_fp in image_fp_batch:
        key, url = upload_object_to_s3_bucket(
            image_fp, bucket_name=BUCKET_NAME, filename_encoding=FILENAME_ENCODING
        )
        s3_keys.append(key)
        s3_urls.append(url)

    # 2. Create an xml string that represents front-end of mturk page by injecting urls and image IDs
    for s3_url, s3_key, wiki_url in zip(s3_urls, s3_keys, wiki_url_batch):
        xml_string = xml_string.replace("{{S3_URL}}", s3_url, 1)
        xml_string = xml_string.replace(
            "{{IMAGE_ID}}", s3_key, 1
        )  # s3-key is used as an image id
        xml_string = xml_string.replace("{{WIKI_URL}}", wiki_url, 1)

    # 3. Create an xml file and archive it for better inspectability and reproducibility (recording seed)
    # archiving path is ./mturk/page_archive/<STAGE>/<current date>/<current HHMM>.xml
    curr_dir = os.path.dirname(__file__)
    date_and_time = datetime.now()
    date_foldername = date_and_time.date()
    time_filename = f'{date_and_time.time().strftime("%Hh%Mm%Ss")}'
    save_dir = os.path.join(
        curr_dir, "mturk", "page_archive", STAGE, f"{date_foldername}"
    )
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    xml_fp = os.path.join(save_dir, f"{DOMAIN}_{time_filename}_seed{SEED:02}.xml")
    with open(xml_fp, "w") as xml_file:
        xml_file.write(xml_string)
        xml_file.close()

    # 4. Publish HIT with the xml file (saved in xml_fp)
    create_hit = CreateHIT(stage=STAGE)
    if DOMAIN == "landmark":
        hit_config = {
            "title": "Do you know this place?",
            "keywords": "Recall, Tip of the Tongue, landmarks",
            "description": "See if you recognize the landmarks. If you do but don't remember the name, write a descriptive question you would ask to online communities.",
            "reward": "0.5",
        }
    elif DOMAIN == "movie":
        hit_config = {
            "title": "Do you know this movie?",
            "keywords": "Recall, Tip of the Tongue, movies, scene",
            "description": "See if you recognize the movies. If you do but don't remember the name, write a descriptive question you would ask to online communities.",
            "reward": "0.5",
        }
    elif DOMAIN == "celebrity":
        hit_config = {
            "title": "Do you know this public figure?",
            "keywords": "Recall, Tip of the Tongue, celebrity, public figure, face",
            "description": "See if you recognize the public figure. If you do but don't remember the name, write a descriptive question you would ask to online communities.",
            "reward": "0.5",
        }

    response = create_hit.create(front_end_xml_fp=xml_fp, hit_config=hit_config)
    hit_type_id = response["HIT"]["HITTypeId"]
    hit_id = response["HIT"]["HITId"]
    print("\nCreated HIT: {} with seed {}".format(hit_id, SEED))

    print("\nYou can work the HIT here:")
    print(create_hit.mturk_env["preview"] + "?groupId={}".format(hit_type_id))

    print("\nAnd see results here:")
    print(create_hit.mturk_env["manage"])

    # 5. Log HITID (PK), Domain, and empty AssignmentID list into HIT-Table-{STAGE}
    hit_table_handler = DynamoDBHandler(
        table_name=HIT_TABLE_NAME, partition_key=PARTITION_KEY
    )
    payload = {
        "HITID": {"S": hit_id},
        "HITTypeID": {"S": hit_type_id},
        "Domain": {"S": DOMAIN},
        "AllAssignmentsDone": {"N": "0"},
        "AssignmentID": {"L": [{"S": "placeholder"}]},
        "Seed": {"S": str(SEED)},
    }
    res = hit_table_handler.put_item(payload=payload)
    if res["ResponseMetadata"]["HTTPStatusCode"] == 200:
        print(f"Successfully stored HIT info into table: {HIT_TABLE_NAME}")
    else:
        raise Exception("DB storing has failed")


if __name__ == "__main__":
    main()
