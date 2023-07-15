import json
import random

def clean_user_list(user_json: dict):
    user_dict = {}
    for i in range(len(user_json["members"])):
        users = user_json["members"][i]
        user_dict[users["id"]] = {"name": users["real_name"]}
    return user_dict

def clean_message_list(messages_json: dict):
    conversation_id = random.randint(1, 2**20)
    conversation_users = []
    message_dict = {}
    for i in range(len(messages_json["messages"])):
        event = messages_json["messages"][i]
        if "client_msg_id" in event:
            message_dict[event["ts"]] = {"conversation_id": conversation_id, "send_id": event["user"], "message": event["text"]}
            if event["user"] not in conversation_users:
                conversation_users.append(event["user"])
    
    conversation_dict = {conversation_id: " ".join(conversation_users)}
    message_dict = dict(sorted(message_dict.items()))
    return message_dict, conversation_dict


"""with open('example_jsons/user.json', 'r') as file:
    user_json = json.load(file)
clean_user_list(user_json)


with open('example_jsons/messages.json', 'r') as file:
    messages_json = json.load(file)
message_dict, conversation_dict = clean_message_list(messages_json)
print(message_dict, conversation_dict)"""
