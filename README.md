# Human TOT Query Elicitation Interface by MTurk
This repository contains the source code used to create an MTurk interface designed for collecting human-elicited Tip of the Tongue (TOT) queries. This version of the interface is intended for internal pilot testing, while the actual data collection was conducted at NIST by trained contractors.
The human-elicited TOT queries will be used as part of the test queries in TREC 2025 TOT track.

Implementation details (frontend and backend) and design can be found in the [Interface Design](media/InterfaceDesign.pdf).

### Python Environment
This codebase is implemented in Python 3.11.5. The necessary libraries can be found in `requirements.txt`. 

## (Offline) Visual Stimuli Collection Process
We gathered images from TMDB (for the Movie domain) and Wikipedia (for the Landmark and Person domains). Images were filtered based on the predefined [Image Deselection Criteria](image_deselection_criteria.md) to ensure their suitability for the TOT query elicitation process. The final dataset includes a total of 1,687 Movie entities, 1,946 Person entities, and 330 Landmark entities.

### Visual Stimuli Dataset
To structure the dataset, we ranked the collected entities by popularity using Wikipedia page view counts and categorized them into 20 bins. The most popular entities (top bin) were stored separately in fallback files (`<DOMAIN_NAME>_fallbacks.csv`), while entities in the remaining 19 bins were included in candidate files (`<DOMAIN_NAME>_candidates.csv`).

The dataset is available at [Visual Stimuli Dataset](visual_stimuli/).

#### File Structure

Each CSV file contains the following fields:

- `PageName`: The Wikipedia title of the entity  
- `wikidataID`: The corresponding Wikidata identifier  
- `ImageURL`: The source URL of the image from Wikimedia or TMDB  

This dataset supports research on TOT retrieval by providing carefully curated visual stimuli to aid in the elicitation of human-written TOT queries.

### License

The dataset is freely available for research purposes under an open-access license. Please cite our paper if you use this dataset in your work.


## (Online) Creating HITs and Retrieving/Logging Responses

### AWS Configuration
1. Use `aws configure` to set up your credentials: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html
2. Set your permissions to ensure you have access to S3 and DynamoDB.

### S3
1. In our implementation, there are multiple S3 buckets, each dedicated to a specific domain (Movie, Landmark, Person). Bucket names are formatted as `tot-mturk-images-<DOMAIN_NAME>`.
2. There are also buckets that store images used in instructions, named `tot-mturk-instruction-images`.

### DynamoDB
1. There are two tables per stage (`sandbox` and `live`): HIT-Table and Assignment-Table.
2. **HIT-Table** has the following keys:
    - `HITID` (PK)
    - `HITTypeID`
    - `Domain`
    - `AllAssignmentsDone`
    - `AssignmentID`
3. **Assignment-Table** has the following keys:
    - `AssignmentID` (PK)
    - `HITID` (SK)
    - `WorkerID`
    - `Image`
    - `Phase1`
    - `Phase2`
    - `Phase3`
    - `Phase4`
    - `TimeStamps`

