# Referee

This code reads a master schedule, linking information from a town's schedule to create a GameOfficials formatted file suitable for uploading.

The file resulting file can be updated to include the referee information as well.


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

`-m` - the file location and name of the master schedule.

`-s` - file location and name of the town's schedule.

`-t` - the name of the town, or home team.

`-o` - the location and name of the output file.

`-f` - the name of the file containing field name translations.

`python referee.py -m <master schedule file name> -s <town schedule file name> -t <town name> -o <name of the output file>`

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

## Built-in translations

Translations normally occur regardless of the field's case: upper, lower, or proper.

The script converts:
* `Grade X/Y` to `X/Y` to match expected GameOfficial's values.
* `Boys` to `M`, `Girls` to `F`.
* Time values are converted to the format 'HH:MM AM/PM'.

**NOTES:** 

The script attempts to complete the proper conversion however it is best to manually check and change as needed the resulting file.

## Fields file

`-f` argument provides the location of the fields file. This file is used to translate fields name found in the town schedule file to the correct field name in Game Officials.

**NOTE:** If the field names match between GameOfficials and the schedule then set the two columns to the same value:

For matching fields: `"Field One","Field One"`

For Translating: `"Field One","Gillette Stadium - Field"`


