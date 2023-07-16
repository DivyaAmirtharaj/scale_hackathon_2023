from message_manager import MessageManager
import subprocess


def run():
    manager = MessageManager()
    # manager.set_up()
    message_history = manager.get_data()
    message_string = "\n".join(message_history)
    print(message_string)
    with open("dialogue.txt", "w") as f:
        # Write the string to the file
        f.write(message_string)
        f.close()
    subprocess.call(["modal", "run", "gen_images.py"])
    print("Done!")


if __name__ == "__main__":
    run()
