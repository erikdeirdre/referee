# Schedule

This directory houses the code for creating Assignr game upload file.

The code:
* reads a Google Sheet based 'master' schedule.
* reads in a translation file
* reads a town spreadsheet, currently expected to be an Excel-based sheet. This should be changed to be Google Sheet based as well. Unfortunately, the test town doesn't maintain a standard document so a local copy is made.
* merges the data into a file capable of uploading into Assignr software.

## Setup

This Python script requires Python 3.10 or higher.

**Create a virtual environment.** 

`python3 -m venv <virtual environment name>`

example: `python3 -m venv virtualenv`

**Activate virtual environment.**

Linux or Mac OS: `source ./<virtual environment name>/bin/activate`

example: `source ./virtualenv/bin/activate`

Windows: 

**Install Script Requirements.**

`pip install -r requirements.txt`


## Running the Script

Why Environment variables and arguments? 

Environment variables are used for non-volatile values such as the spreadsheet id of the Master Schedule.

### Environment Variables

| Variable Name                  | Description | Comments |
| ------------------------------ | ----------- | -------- |
| MASTER_SCHEDULE_ID             | Google Spreadsheet id of the master schedule **REQUIRED** |The value is in the URL of the document. It's the value of `<spreadsheet id>` in https://docs.google.com/spreadsheets/d/<spreadsheet id>/edit#gid=12234 |
=1pZGXNY6zR1D7WO8TOQjBZ-ZP_IWb_ze_8y1gL7Wi65s
| RANGE_NAME                     | The sheet name and range of the data in the master spreadsheet **REQUIRED FIELD** | Example: Master!A:G |
| OUTPUT_FILE_PREFIX             | CSV file prefix **OPTIONAL** | Defaults to `schedule` |
| GOOGLE_APPLICATION_CREDENTIALS | location of Google credentials used to access the master schedule **REQUIRED FIELD** | |
| TRANSLATION_FILE   | JSON-based file for translation of age_groups, and fields **OPTIONAL** | Default: `files/translations.json` |
|LOG_LEVEL           | Log level **OPTIONAL** | 20 |

### Arguments

The script requires five arguments:

`-s`, `--town-file` - file location and name of the town's schedule.

`-t`, `--town` - the name of the town. Used as the home town and populate the league field.


## Expected Master Schedule Format

The master schedule is a Google Sheet. The script allows for multiple sheets in the same file. The environment variable, `RANGE_NAME` is used to determine the sheet name processed. `Master!A:G` is the range used for the spreadsheet shown in the image below.

![Alt text](../assets/masterschedule.png?raw=true "Master Schedule")

## Expected Home Town Schedule Format

The team schedule is an Excel-based spreadsheet consisting of several sheets.

![Alt text](../assets/hometownschedule.png?raw=true "Home Team Schedule")

Sheets named '7TH_8TH', '5TH_6TH', '3RD_4TH' are processed.

The script looks for the title line containing 'division', 'field', and 'time'. When found the script processes the remaining rows.

The title line is then queried to determine the column values for field, time, and dates. A lookup map of date, and column number is created.

The script then reads every subsequent row placing populating a map based on the lookup tables.

## Translation file

The environment variable, `TRANSLATION_FILE`, lists the location of the translation file. This is a JSON based file providing translation of age_groups and fields from those found in town/ master schedule to Assignr values.

**Example:**

```json
{
  "age_groups": {
    "3rd_4th": "Grade 3/4",
    "5th_6th": "Grade 5/6",
    "7th_8th": "Grade 7/8"     
  },
  "fields": {
    "hanover": {
      "FFP1": {
        "venue": "Forge Pond Park",
        "sub-venue": "Field One"
      },
      "FFP2": {
        "venue": "Forge Pond Park",
        "sub-venue": "Field Two"
      },
      "FFP3": {
        "venue": "Forge Pond Park",
        "sub-venue": "Field Three"
      },
      "FFP4": {
        "venue": "Forge Pond Park",
        "sub-venue": "Field Four"
      },
      "Forge Soccer 4": {
        "venue": "Forge Pond Park",
        "sub-venue": "Field Four"
      },
      "hhs turf": {
        "venue": "Hanover High School",
        "sub-venue": "Turf Field"
      }
    }
   }
}
```

The age group section converts the town schedule sheet names to an Assignr value.

The fields section includes a town key, "hanover", allowing a single translation file for a group of towns to use.
