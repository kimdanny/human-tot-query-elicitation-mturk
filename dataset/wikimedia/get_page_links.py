import os
import re
import sys
import requests


def extract_files_from_xml(xml_path):
    with open(xml_path, "r", encoding="utf-8") as file:
        content = file.read()
        return re.findall(r"\[\[(File:.*?)(?:\||\])", content)


def get_file_type(file_name):
    _, file_ext = os.path.splitext(file_name)
    file_ext = file_ext.lower()
    if file_ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
        return "image"
    elif file_ext in [".ogg", ".mp3", ".wav", ".flac"]:
        return "audio"
    else:
        return "other"


def get_file_url(file_title):
    api_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url",
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    for _, page_info in pages.items():
        imageinfo = page_info.get("imageinfo", [{}])[0]
        return imageinfo.get("url", "")
    return ""


def save_links_to_txt(media_files, txt_path):
    with open(txt_path, "w", encoding="utf-8") as txt_file:
        for file_name in media_files:
            file_type = get_file_type(file_name)
            link = f"https://commons.wikimedia.org/wiki/{file_name}"
            file_url = get_file_url(file_name)
            txt_file.write(f"{link}, {file_type}, {file_url}\n")


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
                full_topic_folder_path, os.path.splitext(xml_file)[0] + "_links.txt"
            )

            media_files = extract_files_from_xml(xml_path)
            save_links_to_txt(media_files, txt_path)

            print(f"Links saved to {txt_path}")


if __name__ == "__main__":
    base_path = "/YOUR/BASE/PATH/"
    main(base_path)
