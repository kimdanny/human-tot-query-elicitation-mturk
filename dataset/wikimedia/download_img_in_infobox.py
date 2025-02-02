import os
import re
import sys
import requests

# header to comply with User-Agent policy
headers = {
    "User-Agent": "<FILL YOUR USER AGENT DETAILS>",
}

# Wikipedia API query string to get images in original resolution
# query = 'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='

# Wikipedia API query string to get images in 450px width resolution
query = "http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&pithumbsize=450&titles="


def extract_infobox_content(text):
    """Extract infobox content from the text."""
    infobox_start = text.find("{{Infobox")
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


def extract_image_file_name(infobox_content):
    """Extract image file name from the infobox content."""
    image_match = re.search(r"\|\s*image\s*=\s*([^\|\n]+)", infobox_content)
    if image_match:
        # Extracts file name and removes extra information after the file name
        file_name = image_match.group(1).strip()
        # Handles cases where additional parameters are present after the file name
        file_name = re.split(r"\||<", file_name)[0].strip()
        return file_name


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


def download_media(url, file_name, folder_path):
    """Download the media file."""
    if not url:
        return

    file_path = os.path.join(folder_path, "infobox_image", file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        with open(file_path, "wb") as file:
            file.write(response.content)

        print(f"Downloaded and saved image to {file_path}")
    except Exception as exc:
        print(f"Failed to download image from {url}: {exc}")


def process_xml_files(topic_folder):
    """Process all XML files in a given topic folder."""
    for xml_file in os.listdir(topic_folder):
        if xml_file.endswith(".xml"):
            xml_path = os.path.join(topic_folder, xml_file)
            with open(xml_path, "r", encoding="utf-8") as file:
                content = file.read()

            infobox_content = extract_infobox_content(content)
            if infobox_content:
                image_file_name = extract_image_file_name(infobox_content)
                if image_file_name:
                    image_url = get_media_url(image_file_name)
                    download_media(image_url, image_file_name, topic_folder)


if __name__ == "__main__":
    base_path = "/YOUR/BASE/PATH/"
    topic_folders = [
        os.path.join(base_path, folder)
        for folder in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, folder))
    ]

    for topic_folder in topic_folders:
        process_xml_files(topic_folder)
