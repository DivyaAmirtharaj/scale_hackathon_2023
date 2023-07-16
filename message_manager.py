import json
from database import Database
from slack import SlackAPIManager
from slack_helper import clean_user_list, clean_message_list


class MessageManager:
    def __init__(self) -> None:
        self.conversation_id = None
        self.database = Database()
        # self.database.delete_table()
        # self.database.create_table()

        # Get data from Slack
        # self.slack_api_manager = SlackAPIManager('api-token')
        # self.user_json = self.slack_api_manager.get_user_list()
        # self.messages_json = self.slack_api_manager.get_conversation_history('conversation-token')

    def set_up(self):
        # Populate users table
        user_dict = clean_user_list(self.user_json)
        for key, value in user_dict.items():
            character_prompt = ""
            self.database.add_users(key, value["name"], character_prompt)

        # Populate conversation/ messages table
        message_dict, conversation_dict = clean_message_list(self.messages_json)
        for key, value in conversation_dict.items():
            self.database.add_conversation(key, value)
        for key, value in message_dict.items():
            self.conversation_id = value["conversation_id"]
            image_prompt = ""
            self.database.add_message(
                key,
                value["conversation_id"],
                value["send_id"],
                value["message"],
                image_prompt,
            )

    def get_data(self):
        history = self.database.get_message(79225)
        # history = self.database.get_message(self.conversation_id)
        return history
