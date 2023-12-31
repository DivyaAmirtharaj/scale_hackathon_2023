from flask import Flask, request, jsonify
import threading
import time

from message_manager import MessageManager

app = Flask(__name__)

global_queue = []


@app.route("/kaboom", methods=["POST"])
def post_data():
    # Get JSON data from the request
    channel_id = request.form.get("channel_id")
    text = request.form.get("text")
    user_id = request.form.get("user_id")

    data = [channel_id, text, user_id]
    global_queue.append(data)

    # Do something with the data here

    # Send a response
    return jsonify({"status": "success", "data": "\n".join(data)}), 200


def monitor_list():
    while True:
        if len(global_queue) > 0:
            print("List is populated: ", global_queue)
            channel = global_queue.pop()[0]
            manager = MessageManager(channel)
            manager.conversation_id = channel
            print("List is populated: ", global_queue)
            manager.slack_api_manager.upload_image(channel, "prod/processed (1).png")
            print("hi!")
            # logic for getting image, save to img.jpg
        time.sleep(1)  # Pause for a second between checks


# Create a thread that runs the monitor_list function
monitor_thread = threading.Thread(target=monitor_list)

# Start the thread
# monitor_thread.start()

if __name__ == "__main__":
    monitor_thread.start()
    app.run(debug=True)
