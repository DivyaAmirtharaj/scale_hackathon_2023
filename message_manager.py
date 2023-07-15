import threading
from database import Database
from slack_sdk import WebClient

class MessageManager():
    def __init__(self) -> None:
        self.database = Database()
        self.database.create_table()

    # Function to process a message and perform computations
    def process_message(con, cur, message):
        # Extract relevant message data (e.g., timestamp, sender, text)
        timestamp = message["ts"]
        sender = message.get("user", "")
        text = message.get("text", "")

        # Perform computations on the message, this will be used for prompt generation
        computation_result = text.upper()

        # Insert the message and computation result into the database
        cur.execute("INSERT INTO messages (timestamp, sender, message, computation_result) VALUES (?, ?, ?, ?)",
                    (timestamp, sender, text, computation_result))
        con.commit()

    # Main function to retrieve Slack messages and process them in separate threads
    def retrieve_and_process_messages():
        # Initialize Slack API client with your token
        client = WebClient(token="YOUR_SLACK_TOKEN")

        # Call the conversations.history API method to retrieve messages
        response = client.conversations_history(channel="YOUR_CHANNEL_ID")

        # Establish a database connection
        con = sqlite3.connect("mydatabase.db")
        cur = con.cursor()

        # Iterate over retrieved messages
        for message in response["messages"]:
            # Create a new thread for each message and start it
            thread = threading.Thread(target=process_message, args=(con, cur, message))
            thread.start()

        # Wait for all threads to finish
        for thread in threading.enumerate():
            if thread != threading.current_thread():
                thread.join()

        # Close the database connection
        con.close()

    # Call the main function to retrieve and process Slack messages
    retrieve_and_process_messages()

