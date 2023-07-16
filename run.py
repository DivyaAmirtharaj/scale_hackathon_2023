from message_manager import MessageManager

def run():
    manager = MessageManager()
    manager.set_up()
    message_history = manager.get_data()
    print(message_history)

if __name__ == '__main__':
    run()