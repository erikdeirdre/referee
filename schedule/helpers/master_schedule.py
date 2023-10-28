import logging
from datetime import datetime
from google import auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

logger = logging.getLogger(__name__)

def get_age_gender(field):
    age_group_gender = field.split(' ')
    return age_group_gender[2], f"{age_group_gender[0]} {age_group_gender[1]}"

def process_row(row):
    gender, age_group = get_age_gender(row[0])

    temp_date = None
    try:
        cr_date = datetime.strptime(row[2], "%m/%d/%y")
        temp_date = cr_date.strftime("%m/%d/%Y")
    except ValueError as error:
        logging.warning(f'Date Error: {error}, for line {row}')

    game_info = {
        'gender': gender,
        'age_group': age_group,
        'date': temp_date,
        'home_team': f"{row[3]}-{row[4]}",
        'away_team': f"{row[5]}-{row[6]}"
    }
             
    return game_info


class MasterSchedule():
    def __init__(self, id, sheet_range) -> None:
        self.id = id
        self.sheet_range = sheet_range
        self.values = None
        self.referee_games = []
        self.se_games = []

    def load_sheet(self) -> None:
        credentials, _ = auth.default()

        try:
            service = build('sheets', 'v4', credentials=credentials)
            sheet = service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=self.id, range=self.sheet_range).execute()
            self.values = result.get('values', [])
            logger.info(f"{len(self.values)} rows retrieved")
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
        
    def process_master_schedule(self,town_team) -> None:
        for row in self.values:
            # If the town matches and games are scheduled.
            if row[3].lower() == town_team and \
               row[5].lower() not in ['bye', 'no game']:
                game_data = process_row(row)
                self.se_games.append(game_data)
                self.referee_games.append({
                    'game_id': '',
# Need to add game type to age group translation.
                    'game_type': 'Coastal',
                    'gender': game_data['gender'],
                    'age_group': game_data['age_group'],
                    'date': game_data['date'],
                    'league': town_team.title(),
                    'home_team': game_data['home_team'],
                    'away_team': game_data['away_team']                  
                })
            elif row[5].lower() == town_team:
                game_data = process_row(row)
                self.se_games.append(game_data)