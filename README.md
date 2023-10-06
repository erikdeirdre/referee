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

The master schedule is an Excel-based spreadsheet. Our example the main sheet is a summary of sheets of divisional games. This method results in a 'date' fields being displayed as a numeric value.

![Alt text](assets/masterschedule.png?raw=true "Correct Master Schedule")

![Alt text](assets/invalidmasterschedule.png?raw=true "Invalid Dates in Master Schedule")

If the program reports, `ERROR:root:Invalid date value ... make sure all dates are formatted as 'Date'` then the 'date' column is improperly formatted. Format the column as a date to fix this problem.

## Expected Home Town Schedule Format

The team schedule is an Excel-based spreadsheet consisting of several sheets.

![Alt text](assets/hometownschedule.png?raw=true "Home Team Schedule")


Sheets named '7TH_8TH', '5TH_6TH', '3RD_4TH', '1ST_2ND' are processed.

The script looks for the title line containing 'division', 'field', and 'time'. When found the script processes the remaining rows.

The title line is then queried to determine the column values for field, time, and dates. A lookup map of date, and column number is created.

The script then reads every subsequent row placing populating a map based on the lookup tables.

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

