import threading
from database import Database
from slack import SlackAPIManager

class MessageManager():
    def __init__(self) -> None:
        self.database = Database()
        self.database.create_table()
        self.slack_api_manager = SlackAPIManager('insert_token')

