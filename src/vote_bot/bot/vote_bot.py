from .matrix_bot import MatrixBot
class VoteBot(MatrixBot):
    def __init__(self, peoplePool, botdir_path, autoJoin = False, autoLeave = False):
        self.peoplePool = peoplePool
        super().__init__(botdir_path, autoJoin = autoJoin, autoLeave = autoLeave)
    async def _on_message(self, room, event):
        print(f"Message from {event.sender} in room {room.room_id}: {event.body}")
        if event.sender != self.client.user_id and event.body:
            message = event.body
            promptAndBody = message.split("\n", 1)
            prompt = promptAndBody[0]
            body = promptAndBody[1] if len(promptAndBody) > 1 else ""
            if prompt == "!vote poll":
                print("Vote poll command received")
            elif prompt == "!unvote poll":
                pass
            elif prompt == "!vote person":
                pass
            elif prompt == "!unvote person":
                pass
            elif prompt == "!add poll":
                pass
            elif prompt == "!show poll status":
                pass
            elif prompt == "help":
                pass
