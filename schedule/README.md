# Referee

This code reads a master schedule, linking information from a town's schedule to create an Assignr formatted file suitable for uploading.

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

### Arguments

The script requires five arguments:

`-m`, `--master-file` - the file location and name of the master schedule.

`-s`, `--town-file` - file location and name of the town's schedule.

`-t`, `--town` - the name of the town. Used as the home town and populate the league field.

`-o`, `--output-file` - the location and name of the output file.

`-c`, `--conversion` - the name of the file containing field name translations, and spreadsheet names to process.


## Expected Master Schedule Format

The master schedule is an Excel-based spreadsheet consisting of several sheets.

![Alt text](assets/masterschedule.png?raw=true "Master Schedule")

The relevant sheets are identified with the following rules:
* Row One contains the title "<number> Team Template - <number> Games"
* Row Two has columns with the words "Bracket" and "Age Group"

The "Age Group" value provides the Age/Gender for the games listed in the sheet.

The row containing bracket, listing no, town, and number columns are ignored.

The script searches for the row holding titles for "Home Team" and "Away Team".

Once the titles are found, the script searches for the "Home Team" matching the desired town schedule. The assumption is the person executing the script only cares about home games for their respective town.

The script processes the rows until no more rows. It then moves on to the next sheet.

## Expected Home Town Schedule Format

The team schedule is an Excel-based spreadsheet consisting of several sheets.

![Alt text](assets/hometownschedule.png?raw=true "Home Team Schedule")

Sheets named '7TH_8TH', '5TH_6TH', '3RD_4TH' are processed.

The script looks for the title line containing 'division', 'field', and 'time'. When found the script processes the remaining rows.

The title line is then queried to determine the column values for field, time, and dates. A lookup map of date, and column number is created.

The script then reads every subsequent row placing populating a map based on the lookup tables.

## Built-in translations

Translations normally occur regardless of the field's case: upper, lower, or proper.

The script converts:
* Time values are converted to the format 'HH:MM AM/PM'.

**NOTES:** 

The script attempts to complete the proper conversion however it is best to manually check and change as needed the resulting file.

## Translation file

`-c`, `--conversion` arguments provide the location of the translation file. This file is used to translate fields name found in the town schedule file to the correct field name in Assignr.
