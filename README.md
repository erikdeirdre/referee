# Referee

This repo contains code used to supplement Assignr software, and to merge a master schedule with town schedules.

The repo is broken into sub-directories based on functionality.

`assignr` directory hosts code used with Assignr software. [README](assignr/README.md)

`schedule` directory merges a Google sheet master schedule with a town schedule to create a CSV to be uploaded to the Assignr system. [README](schedule/README.md)


## Setup

Both directories have the same Python requirements and use the same setup. The only difference being the directory. Change into the directory you want to use before executing the steps below.

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
