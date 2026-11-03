# Analyzing Engagement Metrics on r/simonfraser
Ananga Bajgai, Ewan Brinkman, and Ellie Neufeld

# Introduction
Our project investigates what leads to engagement among SFU Reddit posts (submissions). This can also help people who want to know what types of posts do well (and which don’t). To refine the topic more, our group ended up looking at posts’ score and number of comments as a metric of success. The score is the number of upvotes minus downvotes, but can’t be negative.

We analyzed two major properties of submissions to see how they affect the score and number of comments:
- The presence of keywords in the post title and body text. For example, comparing how posts that mention “UBC” affect the post score and number of comments, when compared with posts that do not mention “UBC”. Post keywords analyzed include:
  - General keywords (ex. “raccoon”, “UBC”)
  - Course id keywords (ex. “CMPT 105W”)
  - Instructor full name keywords (ex. “Gregory Baker”)
  - Instructor last name keywords (ex. “Fraser”)
- The readability score of the body text


# Setup

Do the following:
1. `pip install pipenv`
2. `pipenv install`

NOTE: if running pipenv directory doesn't work, you can run pipenv with `python -m pipenv install`. For running pipenv scripts below, you can do the same too like `python -m pipenv run <script_name>`. 

# Running Code

See `[scripts]` in `Pipfile` for various preset scripts to run.

Scripts can be run with `pipenv run <script_name>`. In some computers you might have to do 'python -m pipenv run <script_name>'

# Pipeline Steps

## 1 - Extract 

There are `Pipfile` scripts to extract the data. Data is dumped to `/data/pipeline/1-extract`. Note that the reddit data does not have
a `Pipfile` script to get it. It was acquired by running
`src/pipeline/1-extract/reddit_simonfraser/extract_reddit_simonfraser.py` on the cluster. Reddit data was then copied to
`/data/raw/reddit_simonfraser` (for all data) and `/data/raw/reddit_simonfraser` (for year=2022 only).

The scripts for the extract steps are: 

- `extract:coursesAndInstructors` - This command scrapes data through the SFU API, and generates raw datasets of courses and instructors.
- `extract:instructors_coursys` - This command ultimately wasn't used, but scrapes data through the SFU CourSys, to generate a list of instructors.

## 2 - Transform
The raw data from `/data/pipeline/1-extract` get transformed and cleaned up here and are placed in `/data/pipeline/2-transform` mostly. The files of keywords however, are placed in '/data'. This stage generates unique list of instructors, sfu courses, and generates keywords to do analysis with using those generated generates unique lists. Furthermore, we do clean up on the raw reddit data as well.

The scripts for the Transform steps are: 

- `transform:courses` - Generates a csv file of unique SFU courses, based on raw data from the `extract:coursesAndInstructors` step.

- `transform:instructors_fullname` - Generates a csv file of unique SFU instructors and a count of how many courses they have taught or will teach in 2015-2025, based on raw data from the extract:coursesAndInstructors step.
- `transform:instructors_lastname` - Generates a csv file of unique SFU instructor's last name, based on raw data from the extract:coursesAndInstructors step.
- `transform:instructors_coursys` - Generates a csv file of unique SFU instructor's full names and sfu id, using data from gathered from the extract:instructors_coursys step.
- `transform:keywords:instructors_fullname` - generates a single column list of keywords, which are just instructors full name, to use for analysis later
- `transform:keywords:instructors_lastname` - generates a single column list of keywords, which are just instructors last name, to use for analysis later
- `transform:keywords:courses` - generates a single column list of keywords, which are just course codes, to use for analysis later
- `transform:submissions` - cleans up reddit data by removing posts that were deleted before engagement could have happened (for ex. posts that were deleted automatically by mods as soon as it was posted)

## 3 - Analyze

The keywords generated from the last stage and our manually written general list of keywords, get analyized in this step. Here we compare these keywords against scores and number of comments in each post. The data from this section is stored in `/data/pipeline/3-analyze`.

The scripts for the Transform steps are: 

- `analyze:readability:score` -  analyzes whether there is a linear relationship between readability and scores of reddit posts and prints out the pvalue
- `analyze:readability:num_comments` -  analyzes whether there is a linear relationship between readability and number of comments of reddit posts and prints out the pvalue
- `analyze:keywords:x:y` - Analyzes a list of keywords against reddit data, and can either look at scores or number of comments in posts. This commands take in parameters x, and y, where x species the keyword type (options for x: "general", "courses", "instructors_fullname","instructors_lastname") and the (options for y: "num_comments" or "score").

- `analyze:keywords:x:y:filter` - This command looks at the output of 'analyze:keywords:x:y' and filters out certains keywords that either dont have at least 10 occurences, and also does a bonoferri corrections for all the keywords. The parameters: x, and y, where x species the keyword type (options for x: "general", "courses", "instructors_fullname","instructors_lastname") and the (options for y: "num_comments" or "score").

- `analyze:keywords:x:filter_compare` -  This command looks at the output of `analyze:keywords:x:num_comments:filter` and `analyze:keywords:x:score:filter`and prints out different lists of keywords. It prints out keywords that are statistically significant for just one of "num_comments" or "score", or for both, and also prints out list of keywords that have the smallest pvalues. Here the x species the keyword type (options for x: "general", "courses", "instructors_fullname","instructors_lastname").

filters out certains keywords that either dont have at least 10 occurences, and also does a bonoferri corrections for all the keywords. The parameters: x, and y, where x species the keyword type (options for x: "general", "courses", "instructors_fullname","instructors_lastname") and the (options for y: "num_comments" or "score").

## 4 - Plot 

The results from the last stage, can have it's plot generated here. The plots from this section is stored in `/data/pipeline/4-plot`.

The scripts for the Plot steps are: 

- `plot:keywords:x:y` - Plots are generated corresponding to the `analyze:keywords:x:y` outputs, from the prior stage. Furthermore, inside the 3-analyze folders, there are files called "to_plot.csv" which specifies which keywords shoud plots generated. This commands take in parameters x, and y, where x species the keyword type (options for x: "general", "courses", "instructors_fullname","instructors_lastname") and the (options for y: "num_comments" or "score").
- `plot:readability:score` - plot a best fit linear line and check if it is significant that slope is nonzero, for submission readability compared with score
- `plot:readability:num_comments` - plot a best fit linear line and check if it is significant that slope is nonzero, for submission readability compared with num_comments
