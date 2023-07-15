from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

global_queue = []

@app.route('/kaboom', methods=['POST'])
def post_data():
    # Get JSON data from the request
    channel_id = request.form.get('channel_id')
    text = request.form.get('text')
    user_id = request.form.get('user_id')

    data = [channel_id, text, user_id]
    global_queue.append(data)

    # Do something with the data here

    # Send a response
    return jsonify({"status": "success", "data": "\n".join(data)}), 200

def monitor_list():
    while True:
        if global_queue:
            print("List is populated: ", global_queue)
        else:
            print("List is empty")
        time.sleep(1)  # Pause for a second between checks