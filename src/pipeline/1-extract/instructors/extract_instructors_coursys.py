import sys
import os
import requests
import json
import time
import string

OUTPUT_DIR = sys.argv[1]
COURSYS_BASE_URL = "https://coursys.sfu.ca/browse"
COURSYS_PARAMS = "/?instructor_autocomplete=yes&term="
COURSYS_URL = COURSYS_BASE_URL + COURSYS_PARAMS

ALPHABET = string.ascii_lowercase

# make requests for all 2 letter alphabetic combinations
prof_list = []
for i in range(26):
    for j in range(26):
        term = ALPHABET[i] + ALPHABET[j]
        print("doing ", term)

        request_url = str(COURSYS_URL + term)
        api_success = False
        while not api_success:
            try:
                profs = json.loads(requests.get(request_url).text)
                prof_list.extend(profs)
                api_success = True
                print("success with ", term)
            except:
                print("Error with API")
                time.sleep(10)

with open(
    os.path.join(OUTPUT_DIR, "instructors_autocomplete_2_letters.json"),
    "w",
    encoding="utf-8",
) as f:
    json.dump(prof_list, f, indent=4)

# make requests for all 3 letter alphabetic combinations
prof_list = []
for i in range(26):
    for j in range(26):
        for k in range(26):
            term = ALPHABET[i] + ALPHABET[j] + ALPHABET[k]
            print("doing ", term)

            request_url = str(COURSYS_URL + term)
            api_success = False
            while not api_success:
                try:
                    profs = json.loads(requests.get(request_url).text)
                    prof_list.extend(profs)
                    api_success = True
                    print("success with ", term)
                except:
                    print("Error with API")
                    time.sleep(10)

with open(
    os.path.join(OUTPUT_DIR, "instructors_autocomplete_3_letters.json"),
    "w",
    encoding="utf-8",
) as f:
    json.dump(prof_list, f, indent=4)
