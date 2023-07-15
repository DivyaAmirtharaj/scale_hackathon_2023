import threading
from database import Database
from slack import SlackAPIManager

class MessageManager():
    def __init__(self) -> None:
        self.database = Database()
        self.database.delete_table()
        self.database.create_table()
        
        self.slack_api_manager = SlackAPIManager('insert_token')

        # fill users table
        self.slack_api_manager.get_user_list()


        # Enter channel, open a thread that starts streaming messages
            # Check if this channel already exists in conversations, if not add
            # 

