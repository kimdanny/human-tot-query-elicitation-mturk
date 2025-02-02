import sys
import requests
import xml.etree.ElementTree as ET
import re
import json
import os
import urllib.parse

# header to comply with User-Agent policy
headers = {
    "User-Agent": "<FILL YOUR USER AGENT DETAILS>",
}


def extract_title_from_xml(xml_path):
    """Extract the title of the Wikipedia page from the XML file."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    title = root.find(".//title")
    return title.text if title is not None else None


def get_pageviews(title, start_date, end_date):
    """Get the total pageviews for a Wikipedia page."""
    formatted_title = title.replace(" ", "_")  # Replace spaces with underscores
    encoded_title = urllib.parse.quote(formatted_title)  # URL encode the title
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{encoded_title}/monthly/{start_date}/{end_date}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        total_views = sum(item["views"] for item in data["items"])
        return total_views
    except requests.RequestException as e:
        print(f"Failed to fetch pageviews for {title}: {e}")
        return None


def process_xml_files_in_folder(folder_path, start_date, end_date):
    """Process all XML files in the given folder and save the pageviews."""
    pageviews_data = {"pageviews": {}, "start_time": start_date, "end_time": end_date}

    for xml_file in os.listdir(folder_path):
        if xml_file.endswith(".xml"):
            xml_path = os.path.join(folder_path, xml_file)
            title = extract_title_from_xml(xml_path)
            if title:
                # don't remove any special characters in the title here, since some name looks like this: "Lübeck"
                # title = re.sub(r"[^a-zA-Z0-9\s]", "", title).replace(" ", "_")
                total_views = get_pageviews(title, start_date, end_date)
                if total_views is not None:
                    pageviews_data["pageviews"][title] = total_views

    output_file = os.path.join(folder_path, "pageviews.txt")
    with open(output_file, "w") as f:
        json.dump(pageviews_data, f, indent=4)
        print(f"Saved pageviews data to {output_file}")


def main(base_path, start_date, end_date):
    topic_folders = [
        os.path.join(base_path, folder)
        for folder in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, folder))
    ]

    for folder in topic_folders:
        process_xml_files_in_folder(folder, start_date, end_date)


if __name__ == "__main__":
    base_path = "/YOUR/BASE/PATH/data_infobox/film"
    start_date = "2022110100"
    end_date = "2023110100"
    main(base_path, start_date, end_date)
