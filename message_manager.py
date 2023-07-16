import threading
from database import Database
from slack import SlackAPIManager
from slack_helper import clean_user_list, clean_message_list

class MessageManager():
    def __init__(self) -> None:
        self.database = Database()
        self.database.delete_table()
        self.database.create_table()
        
        # Get data from Slack
        self.slack_api_manager = SlackAPIManager('xoxb-5571078244199-5571084859927-pqptQYWdvcpz26jvBYYgFfXM')
        user_json = self.slack_api_manager.get_user_list()
        messages_json = self.slack_api_manager.get_conversation_history('C05H7ET044T')

        
        # Populate users table
        user_dict = clean_user_list(user_json)
        for key, value in user_dict.items():
            character_prompt = ""
            self.database.add_users(key, value["name"], character_prompt)

        # Populate conversation/ messages table
        message_dict, conversation_dict = clean_message_list(messages_json)
        for key, value in conversation_dict.items():
            self.database.add_conversation(key, value)
        for key, value in message_dict.items():
            image_prompt = ""
            self.database.add_message(key, value["conversation_id"], value["send_id"], value["message"], image_prompt)

