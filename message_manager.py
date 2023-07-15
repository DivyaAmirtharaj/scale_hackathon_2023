from database import Database

class MessageManager():
    def __init__(self) -> None:
        self.database = Database()
        self.database.create_table()

        # add 
