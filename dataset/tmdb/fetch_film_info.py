import sys
import os
import re
import requests
import json
from xml.etree import ElementTree


def extract_imdb_ids(xml_text):
    # Isolate the External links section, stopping until we see the next "[[Category"
    external_links_pattern = r"==\s*External links\s*==\n(.*?)(\n\n|\[\[Category)"
    external_links_match = re.search(external_links_pattern, xml_text, re.DOTALL)

    # If there's no "External links" section, return an empty list
    if not external_links_match:
        return []

    external_links_section = external_links_match.group(1)

    # some regex patterns to search IMDb IDs within the "External links" section
    # Ensure there are 6 to 8 digits following/without 'tt'
    search_patterns = [
        r"\*\s*\{\{IMDb title\|id=(tt\d{6,8})",
        r"\*\s*\{\{IMDb title\|id=(\d{6,8})",
        r"\*\s*\{\{IMDb title\|(tt\d{6,8})\|\w+",
        r"\*\s*\{\{IMDb title\|(\d{6,8})\|\w+",
        r"\*\s*\{\{IMDb title\|(tt\d{6,8})\}\}",
        r"\*\s*\{\{IMDb title\|(\d{6,8})\}\}",
        r"\{\{IMDb title\|(\d{6,8})\|[^}]+\}\}",
    ]

    imdb_ids = []
    for pattern in search_patterns:
        imdb_ids.extend(re.findall(pattern, external_links_section))

    # Add IMDb prefix if not present and avoid duplicates
    return [
        "tt" + imdb_id if not imdb_id.startswith("tt") else imdb_id
        for imdb_id in set(imdb_ids)
    ]


def extract_infobox_content(text):
    infobox_start = text.find("{{Infobox film")
    if infobox_start == -1:
        return None  # Infobox not found

    brace_count = 0
    infobox_content = []

    for char in text[infobox_start:]:
        if char == "{":
            brace_count += 1
        if char == "}":
            brace_count -= 1
        infobox_content.append(char)
        if brace_count == 0:
            break  # End of infobox

    return "".join(infobox_content)


def extract_movie_details(xml_text, title_content):
    # Initialize both movie_name and movie_year
    movie_name = None
    movie_year = None

    # Extract the infobox content
    infobox_content = extract_infobox_content(xml_text)

    # If an infobox is found
    if infobox_content:
        # Extract movie name from "name" in infobox, if available
        name_match = re.search(r"\|\s*name\s*=\s*(.*?)\n", infobox_content)
        movie_name = name_match.group(1).strip() if name_match else None

        # Extract movie year from "released" in infobox, if available
        released_match = re.search(r"\|\s*released\s*=\s*.*?(\d{4})", infobox_content)
        movie_year = released_match.group(1) if released_match else None

    # use title as the movie name, as a back up
    if not movie_name:
        title_raw = title_content.split("(")[0].strip()
        # remove things like "(1931 film)" after the actual film name
        movie_name = re.sub(r"\s*\([^)]*\)", "", title_raw).strip()

    # find movie year in short description, as a back up
    if not movie_year:
        short_description_match = re.search(
            r"\{\{Short description\|(.*?)\}\}", xml_text, re.IGNORECASE
        )
        if short_description_match:
            movie_year_match = re.search(
                r"(\d{4})", short_description_match.group(1), re.IGNORECASE
            )
            movie_year = movie_year_match.group(1) if movie_year_match else None

    return movie_name, movie_year


def fetch_movie_info_by_imdb_id(imdb_id):
    """Fetch movie info by IMDb ID."""
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?external_source=imdb_id"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer use_your_own_api_key_here",
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200 and response.text:
        response_data = response.json()

        # Check if there are any movie results
        if not response_data.get("movie_results"):
            return None

        # Check if backdrop_path is null for the first movie result
        if response_data["movie_results"][0].get("backdrop_path") is None:
            return None

        return response_data
    else:
        # Return None if the response is invalid
        return None


def fetch_movie_info_by_details(movie_name, movie_year):
    """Fetch movie info by movie name and year."""
    movie_name_encoded = requests.utils.quote(movie_name)
    url = f"https://api.themoviedb.org/3/search/movie?query={movie_name_encoded}&primary_release_year={movie_year}"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer use_your_own_api_key_here",
    }
    response = requests.get(url, headers=headers)
    response_data = response.json()

    # Filter out results that do not match the movie_name exactly
    filtered_results = [
        result
        for result in response_data["results"]
        if result["original_title"].lower() == movie_name.lower()
    ]

    # Update the total_results with the count of filtered results
    total_results = len(filtered_results)
    response_data["results"] = filtered_results
    response_data["total_results"] = total_results

    # Check the total_results field after filtering
    if total_results > 1:
        print(f"Warning: More than one result found in {movie_name}.")

    # Return the modified response data as JSON text
    return json.dumps(response_data)


def fetch_movie_backdrops(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/images"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer Bearer use_your_own_api_key_here",
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        backdrops = response_data.get("backdrops", [])
        if backdrops:
            return json.dumps({"backdrops": backdrops}, indent=4)

    return None


def process_xml_file(xml_path, txt_path):
    try:
        # Parse the XML content
        tree = ElementTree.parse(xml_path)
        root = tree.getroot()
        text_content = root.find(".//text").text
        title_content = root.find(".//title").text

        # Extract IMDb IDs
        imdb_ids = extract_imdb_ids(text_content)

        # Initialize an empty string to hold all movie info
        all_movie_info = ""
        found_info = False  # Flag to check if we found any movie info
        valid_imdb_ids = []  # To store valid IMDb IDs after filtering
        movie_id = None  # To store the ID of the movie

        movie_name, movie_year = extract_movie_details(text_content, title_content)

        # Fetch movie info by IMDb ID or by movie details
        if imdb_ids:
            for imdb_id in imdb_ids:
                movie_info = fetch_movie_info_by_imdb_id(imdb_id)
                if movie_info:  # Check if movie_info is not empty
                    if (
                        movie_info.get("movie_results", [{}])[0].get("title")
                        != movie_name
                    ):
                        continue
                    valid_imdb_ids.append(imdb_id)
                    movie_id = movie_info["movie_results"][0]["id"]
                    all_movie_info += (
                        f'<imdb_id_match>, imdb_id="{imdb_id}"\n{movie_info}\n'
                    )
                    found_info = True
        else:
            if movie_name and movie_year:
                movie_info = fetch_movie_info_by_details(movie_name, movie_year)
                if movie_info:
                    movie_info_dict = json.loads(movie_info)
                    if movie_info_dict.get("total_results") == 1:
                        movie_id = movie_info_dict["results"][0]["id"]
                        all_movie_info += f'<title_year_match>, movie_name = "{movie_name}", movie_year = "{movie_year}"\n{movie_info}\n'
                        found_info = True

        # Check if multiple valid IMDb IDs exist after filtering
        if len(valid_imdb_ids) > 1:
            print(
                f"Warning: Still more than one IMDB ID exist in {xml_path} after filtering by exact name match, this might be a movie series."
            )

        # If we found any movie info and a movie ID, we save it to the txt file
        if found_info and movie_id:
            # Save the response to a txt file at the same level as the XML file
            with open(txt_path, "w") as file:
                file.write(all_movie_info)

            # Initialize backdrops_txt_path outside the if condition
            backdrops_txt_path = os.path.splitext(txt_path)[0] + "_backdrops_list.txt"

            # Fetch backdrops info
            backdrops_info = fetch_movie_backdrops(movie_id)
            if backdrops_info:
                with open(backdrops_txt_path, "w") as file:
                    file.write(backdrops_info)
                return f"Process completed and data saved to {txt_path} and {backdrops_txt_path}"
            else:
                return f"Process completed and data saved to {txt_path}. No backdrops info found."
        else:
            return f"Movie details not found or we filtered it in {xml_path}"

    except ElementTree.ParseError as e:
        return f"XML parsing error in {xml_path}: {e}"
    except Exception as e:
        return f"An error occurred while processing {xml_path}: {e}"


def download_first_backdrop(backdrops_txt_path, topic_folder_path):
    # Create the backdrops_imgs directory within the topic folder if it does not exist
    backdrops_img_dir = os.path.join(topic_folder_path, "backdrops_imgs")
    if not os.path.exists(backdrops_img_dir):
        os.makedirs(backdrops_img_dir)

    # Read the backdrops list from the txt file
    with open(backdrops_txt_path, "r") as file:
        backdrops_data = json.load(file)

    # Extract the file path of the first backdrop
    if backdrops_data.get("backdrops") and backdrops_data["backdrops"]:
        first_backdrop_path = backdrops_data["backdrops"][0]["file_path"]
        image_url = f"https://image.tmdb.org/t/p/original{first_backdrop_path}"

        # Download the image
        response = requests.get(image_url)
        if response.status_code == 200:
            # Extract file name and save the image
            file_name = os.path.basename(first_backdrop_path)
            image_path = os.path.join(backdrops_img_dir, file_name)
            with open(image_path, "wb") as img_file:
                img_file.write(response.content)
            print(f"Downloaded and saved image to {image_path}")
        else:
            print(f"Failed to download image from {image_url}")
    else:
        print("No backdrops data available to download.")


def main(base_path):
    topic_folders = [
        os.path.join(base_path, folder)
        for folder in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, folder))
    ]

    for full_topic_folder_path in topic_folders:
        xml_files = [
            file for file in os.listdir(full_topic_folder_path) if file.endswith(".xml")
        ]
        for xml_file in xml_files:
            xml_path = os.path.join(full_topic_folder_path, xml_file)
            txt_path = os.path.join(
                full_topic_folder_path, os.path.splitext(xml_file)[0] + "_tmdb.txt"
            )

            # Process each XML file and save the response in a corresponding txt file
            result = process_xml_file(xml_path, txt_path)
            print(result)

    # Iterate over all topic folders
    topic_folders = [
        os.path.join(base_path, folder)
        for folder in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, folder))
    ]
    for topic_folder in topic_folders:
        # Iterate over all _tmdb_backdrops_list.txt files in the topic folder and download the first backdrop
        for file in os.listdir(topic_folder):
            if file.endswith("_tmdb_backdrops_list.txt"):
                backdrops_txt_path = os.path.join(topic_folder, file)
                download_first_backdrop(backdrops_txt_path, topic_folder)


if __name__ == "__main__":
    base_path = "/YOUR/SAVE/PATH/data_infobox/film"
    main(base_path)
