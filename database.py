import sqlite3
import re
import random

def thread_db(fn):
    def set_up(self, *args, **kwargs):
        con = sqlite3.connect("kaboom" + ".db")
        cur = con.cursor()
        con.create_function('regexp', 2, lambda x, y: 1 if re.search(x,y) else 0)
        thread_cur = fn(self, con, cur, *args, **kwargs)
        con.close()
        return thread_cur
    return set_up

class Database(object):
    def __init__(self) -> None:
        pass
    
    # Called upon initialization of the server to create a new table to store unique user info, as well as messages
    @thread_db
    def create_table(self, con, cur):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uuid integer PRIMARY KEY,
                username text,
                character_prompt text
            )
        """)
        # create a conversations table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id integer PRIMARY KEY,
                uuid_list text
            )
        """)
        # create a messages table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                msgid integer PRIMARY KEY,
                conversation_id integer,
                timestamp integer,
                send_id integer,
                message text,
                message_metadata text,
                prompt text
            )
        """)
        con.commit()
    
    @thread_db
    def delete_table(self, con, cur):
        cur.execute("DROP table IF EXISTS messages")
        cur.execute("DROP table IF EXISTS conversations")
        cur.execute("DROP table IF EXISTS users")
        con.commit()
    
    @thread_db
    def add_users(self, con, cur, username, character_prompt):
        # Random generation of uuid for thread safety
        uuid = random.randint(1, 2**20)
        cur.execute("""
            INSERT INTO users (uuid, username, character_prompt)
                VALUES (?, ?, ?)
        """, [uuid, username, character_prompt])
        con.commit()

    # Pulls the unique id for each name during message sending/ receiving
    @thread_db
    def get_uuid(self, con, cur, username):
        # Given the username, it returns the uuid
        cur.execute("""
            SELECT uuid FROM users WHERE name = ?
        """, [username])
        val = cur.fetchone()
        if val is None:
            # Raise exception if no user is found in the database
            raise Exception("No user found for this name")
        return val[0]
    
    # Pulls the username from the unique id, used primarily for formatting and user comfort when reading messages
    @thread_db
    def get_username(self, con, cur, uuid):
        try:
            cur.execute("""
                SELECT username FROM users WHERE (uuid = ?)
            """, [uuid])
        except Exception as e:
            print(e)
        
        user = cur.fetchone()
        if user is None:
            # Raises exception if there is no user under the particular uuid in the database
            raise Exception("No user found for this uuid")
        return user[0]
    
    # If a conversation, create a new conversation id and add the list of users that are in the conversation
    @thread_db
    def add_conversation(self, con, cur):
        pass
        
    # Adds messages sent from the clients into the database.  Names the messages by pulling the most recent entry
    # in the database and adding 1 to create a unique message id.
    @thread_db
    def add_message(self, con, cur, timestamp, conversation_id, send_id, message, message_metadata, image_prompt):
        
        # Selects the most recent message
        cur.execute("""
            SELECT msgid FROM messages ORDER BY msgid DESC LIMIT 1
        """)
        latest = cur.fetchone()
        if latest is None:
            latest = 0
        else:
            # Identify the latest message id (most recent message)
            latest = latest[0]
        try:
            cur.execute("""
                INSERT INTO messages (msgid, timestamp, conversation_id, send_id, message, message_metadata, image_prompt)
                    VALUES (?, ?, ?)
            """, [latest + 1, conversation_id, send_id, message, message_metadata, image_prompt])
        except Exception as e:
            print(e)
        con.commit()

    # Get full message history for a conversation
    @thread_db
    def get_message(self, con, cur, conversation_id):
        # Given a conversation_id, pull all messages in
        cur.execute("""
            SELECT msgid, send_id, message 
            FROM messages
            WHERE (conversation_id = ?)
            ORDER BY msgid ASC
        """, [conversation_id])
        rows = cur.fetchall()
        if rows is None or len(rows) == 0:
            raise Exception("No message history")
        history = []
        for row in rows:
            cur.execute("SELECT username FROM users WHERE (uuid = ?)", [row[1]])
            send_name = cur.fetchone()
            if send_name is None:
                raise Exception("Sender doesn't exist")
            history.append({"msgid": row[0], "send_name": send_name[0], "message": row[2]})
        return history
    
    # Pulled by general client/ server to get full message history
    @thread_db
    def get_all_history(self, con, cur, receive_id):
        # Given a receiver_id, and the sender_id get the message history between the two users
        try:
            cur.execute("""
                SELECT msgid, send_id, receive_id, message 
                FROM messages
                WHERE (receive_id = ?)
                ORDER BY msgid ASC
            """, [receive_id])
            rows = cur.fetchall()
        except Exception as e:
            print(e)
        
        history = []
        if rows is None or len(rows) == 0:
            raise Exception
        for row in rows:
            history.append({'send_id': row[1], 'message': row[3]})
        return history