import sys
import requests
import json
import os
import time
import pandas as pd

COURSES_OUTPUT_DIR = sys.argv[1]
INSTRUCTOR_OUTPUT_DIR = sys.argv[2]

SFU_BASE_URL = "http://www.sfu.ca/bin/wcm/course-outlines"


# get possible year values
get_year_success = False
possible_year_values = []

while not get_year_success:
    api_request = requests.get(SFU_BASE_URL + "?")
    if api_request.status_code == 200:
        api_possible_years_output = json.loads(api_request.text)
        possible_year_values = [
            element["text"] for element in api_possible_years_output
        ]
        if len(possible_year_values) > 0:
            get_year_success = True


# returns a list of values composing a row in a dataframe
def get_courses_row_data(
    year,
    semester_value,
    department_value,
    course_value,
    section_value,
    outline,
    id,
):
    # get course data to append
    courses_appending_data = [
        year,
        semester_value,
        department_value,
        course_value,
        section_value,
    ]
    # get course title
    if "info" in outline.keys() and "title" in outline["info"].keys():
        courses_appending_data.append(outline["info"]["title"])
    else:
        courses_appending_data.append("")

    courses_appending_data.append(id)

    return courses_appending_data


def get_instructor_rows_data(outline, id, instructor_df):
    if "instructor" in outline.keys():
        for instructor in outline["instructor"]:
            # Using .get() to avoid KeyError if any key is missing
            appending_data = [
                id,
                instructor["name"],
                instructor["firstName"],
                instructor["lastName"],
                instructor["commonName"],
                instructor["email"],
            ]
            instructor_df.loc[len(instructor_df)] = appending_data

    return instructor_df


course_id = 0
for year in possible_year_values:

    # get semesters in year
    semesters_success = False
    semesters = []
    year_url_param = "?" + year
    print("Currently getting data from Year: ", year)

    # make a new data frame for this year
    courses_yearly_df = pd.DataFrame(
        columns=[
            "Year",
            "Semester",
            "Department",
            "Course Number",
            "Course Section",
            "Course Title",
            "Course ID",
        ]
    )

    # instructor df
    instructor_yearly_df = pd.DataFrame(
        columns=[
            "Course ID",
            "Instructor Name",
            "Instructor First Name",
            "Instructor Last Name",
            "Instructor Common Name",
            "Instructor Email",
        ]
    )

    while not semesters_success:
        semesters_request = requests.get(SFU_BASE_URL + year_url_param)
        if semesters_request.status_code == 200:
            semesters = json.loads(semesters_request.text)
            semesters_success = True
        elif semesters_request.status_code == 404:
            semesters_success = True
            semesters = []
            print(
                "404 error: API request to get all departments in: year ",
                year,
                " failed.",
            )
            print("API URL: ", SFU_BASE_URL + year_url_param)
        else:
            print(
                "API request to get all semesters in year ",
                year,
                " failed. Now retrying..",
            )

    # now loop inside semesters
    for semester in semesters:
        semester_value = semester["value"]

        semester_param = "/" + semester_value

        print("Currently getting data from semester: ", semester_value)

        # get departments in each semester
        departments_success = False
        departments = []

        while not departments_success:
            departments_request = requests.get(
                SFU_BASE_URL + year_url_param + semester_param
            )
            if departments_request.status_code == 200:
                departments = json.loads(departments_request.text)
                departments_success = True
            elif departments_request.status_code == 404:
                departments_success = True
                departments = []
                print(
                    "404 error: API request to get all departments in: year ",
                    year,
                    ",  semester: ",
                    semester_value,
                    " failed.",
                )
                print(
                    "API URL: ", SFU_BASE_URL + year_url_param + semester_param
                )

            else:
                print(
                    "API request to get all departments in year ",
                    year,
                    " and semester ",
                    semester_value,
                    " failed. Now retrying..",
                )

        # now loop over departments
        for department in departments:
            department_value = department["value"]
            department_param = "/" + department_value

            # get departments in each semester
            courses_success = False
            courses = []

            while not courses_success:
                courses_request = requests.get(
                    SFU_BASE_URL
                    + year_url_param
                    + semester_param
                    + department_param
                )
                if courses_request.status_code == 200:
                    courses = json.loads(courses_request.text)
                    courses_success = True
                elif courses_request.status_code == 404:
                    print(
                        "404 error: API request to get all courses in: year ",
                        year,
                        ",  semester: ",
                        semester_value,
                        " department: ",
                        department_value,
                        " failed.",
                    )
                    print(
                        "API URL: ",
                        SFU_BASE_URL
                        + year_url_param
                        + semester_param
                        + department_param,
                    )
                    courses = []
                    courses_success = True
                else:
                    print(
                        "API request to get all courses in: year ",
                        year,
                        ",  semester: ",
                        semester_value,
                        " department: ",
                        department_value,
                        " failed. Now retrying..",
                    )
                    print(
                        "API URL: ",
                        SFU_BASE_URL
                        + year_url_param
                        + semester_param
                        + department_param,
                    )
                    print(courses_request.status_code)

            # now loop over courses
            for course in courses:
                course_value = course["value"]
                course_param = "/" + course_value

                # get departments in each semester
                section_success = False
                sections = []

                while not section_success:
                    section_request = requests.get(
                        SFU_BASE_URL
                        + year_url_param
                        + semester_param
                        + department_param
                        + course_param
                    )
                    if section_request.status_code == 200:
                        sections = json.loads(section_request.text)
                        section_success = True
                    elif section_request.status_code == 404:
                        section_success = True
                        sections = []
                        print(
                            "404 error: API request to get all sections in: year ",
                            year,
                            ",  semester: ",
                            semester_value,
                            " department: ",
                            department_value,
                            " course: ",
                            course_value,
                            " failed.",
                        )
                        print(
                            "API URL: ",
                            SFU_BASE_URL
                            + year_url_param
                            + semester_param
                            + department_param
                            + course_param,
                        )

                    else:
                        print(
                            "API request to get all sections in: year ",
                            year,
                            ",  semester: ",
                            semester_value,
                            " department: ",
                            department_value,
                            " course: ",
                            course_value,
                            " failed. Now retrying..",
                        )
                        print(
                            "API URL: ",
                            SFU_BASE_URL
                            + year_url_param
                            + semester_param
                            + department_param
                            + course_param,
                        )
                        print(section_request.status_code)

                    for section in sections:

                        section_value = section["value"]
                        section_param = "/" + section_value

                        # get course outline in each semester
                        outline_success = False
                        outline = []

                        while not outline_success:
                            outline_request = requests.get(
                                SFU_BASE_URL
                                + year_url_param
                                + semester_param
                                + department_param
                                + course_param
                                + section_param
                            )
                            if outline_request.status_code == 200:
                                outline = json.loads(outline_request.text)
                                outline_success = True
                            elif outline_request.status_code == 404:
                                outline_success = True
                                outline = None
                                print(
                                    "404 error: API request to get outline in: year ",
                                    year,
                                    ",  semester: ",
                                    semester_value,
                                    " department: ",
                                    department_value,
                                    " course: ",
                                    course_value,
                                    " sectiion: ",
                                    section_value,
                                    " failed.",
                                )
                            else:
                                print(
                                    "API request to get outline  in: year ",
                                    year,
                                    ",  semester: ",
                                    semester_value,
                                    " department: ",
                                    department_value,
                                    " course: ",
                                    course_value,
                                    " sectiion: ",
                                    section_value,
                                    " failed. Now retrying..",
                                )

                        if outline:
                            appending_data = get_courses_row_data(
                                year,
                                semester_value,
                                department_value,
                                course_value,
                                section_value,
                                outline,
                                course_id,
                            )
                            # add row to dataframe
                            courses_yearly_df.loc[len(courses_yearly_df)] = (
                                appending_data
                            )

                            instructor_yearly_df = get_instructor_rows_data(
                                outline, course_id, instructor_yearly_df
                            )
                            course_id = course_id + 1

    courses_yearly_df.to_csv(
        COURSES_OUTPUT_DIR + "/ " + "sfu_api_data" + year + ".csv"
    )
    instructor_yearly_df.to_csv(
        INSTRUCTOR_OUTPUT_DIR
        + "/instructors_"
        + "sfu_api_data"
        + year
        + ".csv"
    )
