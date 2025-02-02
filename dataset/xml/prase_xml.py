import os
import re
import multiprocessing


def split_wikipedia_xml(filename):
    # set the path to the output folder here
    output_folder = "/YOUR/SAVE/PATH/data_infobox"

    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
        except FileExistsError:
            pass

    # Define the infoboxes to be extracted
    infoboxes = {
        "film": ["film"],
        "celebrity": [
            "person",
            "Buddha",
            "Christian leader",
            "clergy",
            "Jewish leader",
            "Latter Day Saint biography",
            "religious biography",
            "saint",
            "Egyptian dignitary",
            "noble",
            "pharaoh",
            "pretender",
            "royalty",
            "college football player",
            "Canadian Football League biography",
            "NFL biography",
            "football biography",
            "football official",
            "baseball biography",
            "basketball biography",
            "ice hockey biography",
            "Champ Car driver",
            "F1 driver",
            "Le Mans driver",
            "Motocross rider",
            "motorcycle rider",
            "NASCAR driver",
            "racing driver",
            "racing driver series section",
            "speedway rider",
            "WRC driver",
            "sportsperson",
            "biathlete",
            "boxer (amateur)",
            "climber",
            "professional bowler",
            "sailor",
            "speed skater",
            "sport wrestler",
            "swimmer",
            "bullfighting career",
            "AFL biography",
            "alpine ski racer",
            "amateur wrestler",
            "badminton player",
            "bandy biography",
            "bodybuilder",
            "boxer",
            "cricketer",
            "curler",
            "cyclist",
            "equestrian",
            "fencer",
            "field hockey player",
            "figure skater",
            "Gaelic games player",
            "golfer",
            "gymnast",
            "handball biography",
            "horseracing personality",
            "lacrosse player",
            "martial artist",
            "mountaineer",
            "NCAA athlete",
            "netball biography",
            "pelotari",
            "professional wrestler",
            "rugby biography",
            "rugby league biography",
            "skier",
            "sports announcer details",
            "squash player",
            "sumo wrestler",
            "surfer",
            "table tennis player",
            "tennis biography",
            "volleyball biography",
            "academic",
            "architect",
            "artist",
            "art historian",
            "chef",
            "classical composer",
            "criminal",
            "dancer",
            "economist",
            "engineer",
            "engineering career",
            "medical details",
            "medical person",
            "model",
            "pageant titleholder",
            "philosopher",
            "pirate",
            "police officer",
            "presenter",
            "scientist",
            "sports announcer",
            "spy",
            "theologian",
            "theological work",
            "astronaut",
            "aviator",
            "chess biography",
            "college coach",
            "comedian",
            "comics creator",
            "darts player",
            "FBI Ten Most Wanted",
            "go player",
            "Magic: The Gathering player",
            "military person",
            "musical artist",
            "Nahua officeholder",
            "officeholder",
            "Native American leader",
            "Playboy Playmate",
            "poker player",
            "snooker player",
            "video game player",
            "War on Terror detainee",
            "writer",
            "YouTube personality",
        ],
        "landmark": [
            "British National Vegetation Classification community",
            "Disney resort",
            "Egyptian tomb",
            "NRHP",
            "Pennsylvania historic site",
            "Scottish island",
            "Site of Special Scientific Interest",
            "UNESCO World Heritage Site",
            "amusement park",
            "ancient site",
            "attraction",
            "attraction model",
            "body of water",
            "bridge",
            "bridge type",
            "building",
            "business park",
            "campground",
            "canal",
            "casino",
            "castrum",
            "cave",
            "cemetery",
            "circus",
            "climbing area",
            "climbing route",
            "concentration camp",
            "continent",
            "convention center",
            "dam",
            "desalination plant",
            "docks",
            "dual roller coaster",
            "ecoregion",
            "factory",
            "farm",
            "fault",
            "forest",
            "future infrastructure project",
            "glacier",
            "golf facility",
            "hill of Rome",
            "historic site",
            "hospital",
            "housing project",
            "hut",
            "islands",
            "landform",
            "library",
            "lighthouse",
            "mill building",
            "mine",
            "monument",
            "motorway services",
            "mountain",
            "mountain pass",
            "museum",
            "observatory",
            "oil refinery",
            "park",
            "pier",
            "pipeline",
            "port",
            "power station",
            "power transmission line",
            "prison",
            "property development",
            "pyramid",
            "restaurant",
            "retail market",
            "river",
            "roller coaster",
            "roller coaster/extend",
            "room",
            "seamount",
            "sedimentary basin",
            "shopping mall",
            "spring",
            "superfund",
            "tectonic plate",
            "terrestrial impact site",
            "trail",
            "transmitter",
            "tunnel",
            "urban development project",
            "urban feature",
            "valley",
            "venue",
            "water park",
            "water ride",
            "waterfall",
            "whitewater course",
            "windmill",
            "zoo",
        ],
    }

    with open(filename, "r", encoding="utf-8") as file:
        recording = False
        infobox_recording = False
        content = []
        title = ""
        infobox_content = ""

        for line in file:
            if "<page>" in line:
                recording = True
                content = []

            if recording:
                content.append(line)

            if "{{Infobox" in line and recording:
                infobox_recording = True
                infobox_content = line  # Start capturing the Infobox content

            if infobox_recording and "}}" in line:
                infobox_recording = False
                infobox_content += line  # End capturing the Infobox content

            elif infobox_recording:
                infobox_content += line  # Continue capturing the Infobox content

            if "<title>" in line and recording:
                # Extracting title between the <title> tags
                title = line.split("<title>")[1].split("</title>")[0]
                # Replacing any characters that are not allowed in filenames
                title = "".join(
                    c for c in title if c.isalnum() or c in (" ", ".")
                ).rstrip()

            if "</page>" in line and recording:
                recording = False
                content_str = "".join(content)

                # Check each infobox type
                for main_category, boxes in infoboxes.items():
                    if any(
                        re.search(rf"\bInfobox {box}\b", infobox_content)
                        for box in boxes
                    ):
                        # Create a folder named after the title inside the main category folder
                        title_folder_path = os.path.join(
                            output_folder, main_category, title
                        )
                        if not os.path.exists(title_folder_path):
                            os.makedirs(title_folder_path)

                        # Save the content into an XML file within the title folder
                        output_path = os.path.join(title_folder_path, f"{title}.xml")
                        with open(output_path, "w", encoding="utf-8") as output:
                            output.write(content_str)

                infobox_content = ""


def process_single_xml_file(filename):
    global directory, log_file_path

    # Full path to the file
    file_path = os.path.join(directory, filename)
    print(f"Processing {file_path} ...")

    # Process the XML file with the specified filename
    split_wikipedia_xml(file_path)

    # Write the processed filename to the log
    with open(log_file_path, "a") as log_file:
        log_file.write(filename + "\n")

    print(f"Finished processing {file_path}.")


def process_all_xml_files_in_directory(directory):
    global log_file_path

    # Check and get the list of files in the directory
    all_files = [
        f
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f.startswith("enwiki")
    ]

    # Check processed files from the log
    with open(log_file_path, "a+") as log_file:
        log_file.seek(0)
        processed_files = log_file.readlines()
        processed_files = [f.strip() for f in processed_files]

    # Get the list of unprocessed files
    unprocessed_files = [f for f in all_files if f not in processed_files]

    print(f"Starting processing. {len(unprocessed_files)} files to process.")
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    print(f"Using {multiprocessing.cpu_count()} processes.")

    pool.map(process_single_xml_file, unprocessed_files)
    print("All XML files have been processed.")


log_file_path = "path/to/log"
directory = "path/to/all/xml_files"
process_all_xml_files_in_directory(directory)
