# Human TOT Query Elicitation Interface by MTurk
This repository contains the source code used to create an MTurk interface designed for collecting human-elicited Tip of the Tongue (TOT) queries. This version of the interface is intended for internal pilot testing, while the actual data collection was conducted at NIST by trained contractors.
The human-elicited TOT queries will be used as part of the test queries in TREC 2025 TOT track.

Implementation details (frontend and backend) and design can be found in the [Interface Design](media/InterfaceDesign.pdf).

### Python Environment
This codebase is implemented in Python 3.11.5. The necessary libraries can be found in `requirements.txt`. 

## (Offline) Visual Stimuli Collection Process
We collected images from TMDB (for the Movie domain) and Wikipedia (for the Landmark and Person domains). We then deselected some images based on the [Image Deselection Criteria](image_deselection_criteria.md).

The final set of images was sorted by their popularity (measured by Wikipedia page views) and binned into 20 groups. The most popular entities (those in the first bin) were saved in fallback files (`<DOMAIN_NAME>_fallbacks.csv`), while entities in the other 19 bins were saved in candidate files (`<DOMAIN_NAME>_candidates.csv`).

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

