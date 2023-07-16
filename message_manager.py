import threading
from database import Database
from slack import SlackAPIManager
from slack_helper import clean_user_list, clean_message_list

class MessageManager():
    def __init__(self) -> None:
        self.database = Database()
        self.database.delete_table()
        self.database.create_table()
        
        self.slack_api_manager = SlackAPIManager('xoxb-5571078244199-5571084859927-Q6uxPD2B9SfiZW8ceQChd5qy')
        user_json = self.slack_api_manager.get_user_list()
        messages_json = self.slack_api_manager.get_conversation_history('C05H7ET044T')

        user_dict = clean_user_list(user_json)
        for key, value in user_dict:
            character_prompt = ""
            self.database.add_users(key, value["name"], character_prompt)

        # Populate conversation/ messages table
        messages_json = self.slack_api_manager.get_conversation_history('C05H7ET044T')
        message_dict, conversation_dict = clean_message_list(messages_json)
        for key, value in conversation_dict:
            self.database.add_conversation(key, value)
        for key, value in message_dict:
            image_prompt = ""
            self.database.add_message(key, value["conversation_id"], value["send_id"], value["message"], image_prompt)

