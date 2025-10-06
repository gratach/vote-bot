import asyncio
from pathlib import Path
from nio import AsyncClient, AsyncClientConfig, JoinError, RoomMemberEvent, InviteMemberEvent, RoomMessageText
from json import load

class MatrixBot:
    def __init__(self, botdir_path, autoJoin = False, autoLeave = False):
        self.botdirPath = Path(botdir_path)
        if not self.botdirPath.exists():
            raise Exception(f"The botdir has to be created. For setup instructions see: https://github.com/gratach/create-matrix-nio-bot-dir. The created botdir needs to have the path: {self.botdirPath}")
        self.loginPath = self.botdirPath / "login.json"
        self.sotrePath = self.botdirPath / "store"
        self.isRunning = False
        self.autoJoin = autoJoin
        self.autoLeave = autoLeave

    async def run(self):
        print("Starting matrix bot...")
        if self.isRunning:
            print("The matrix bot is already running")
            return
        self.isRunning = True
        # Configuration options for the AsyncClient
        self.config = AsyncClientConfig(
            max_limit_exceeded=0,
            max_timeouts=0,
            store_sync_tokens=True,
            encryption_enabled=True,
        )

        # Load login info from login.json
        with self.loginPath.open() as f:
            self.login_info = load(f)

        # Create a new AsyncClient
        self.client = AsyncClient(
            self.login_info["homeserver"],
            self.login_info["user_id"],
            device_id=self.login_info["device_id"],
            store_path=self.sotrePath,
            config=self.config,
        )
        self.client.user_id = self.login_info["user_id"]
        self.client.access_token = self.login_info["access_token"]

        # Load the stored sync tokens
        self.client.load_store()

        # Upload keys if necessary
        if self.client.should_upload_keys:
            await self.client.keys_upload()

        print("Matrix bot logged in as", self.client.user_id)

        # Syncronize with the server
        resp = await self.client.sync()

        print("Matrix bot synced")

        if self.autoJoin:
            for room_id in self.client.invited_rooms.keys():
                try:
                    # Join the room
                    resp = await self.client.join(room_id)
                    # Check if the response is a nio.responses.JoinError:
                    if isinstance(resp, JoinError):
                        raise Exception("Failed to join room")
                except Exception as e:
                    # Leave the room if joining failed
                    if self.autoLeave:
                        resp = await self.client.room_leave(room_id)

        if self.autoLeave:
            # Iterate over all joined rooms
            for room_id in (await self.client.joined_rooms()).rooms:
                # Get all members in the room
                members = (await self.client.joined_members(room_id)).members
                # If I am the only member, leave the room
                if len(members) == 1:
                    await self.client.room_leave(room_id)

        self.client.add_event_callback(self._on_invite, (InviteMemberEvent,))
        self.client.add_event_callback(self._on_member_event, (RoomMemberEvent,))
        self.client.add_event_callback(self._on_message, RoomMessageText)
        print("Matrix bot is running")

        try:
            await self.client.sync_forever(timeout=30000)
        except Exception as e:
            print(e)
            await self.client.close()

    async def _on_invite(self, room, event):
        if self.autoJoin:
            # If you are invited to a room
            if event.state_key == self.client.user_id:
                # Join the room
                try:
                    resp = await self.client.join(room.room_id)
                    if isinstance(resp, JoinError):
                        raise Exception("Failed to join room")
                except Exception as e:
                    # Leave the room if joining failed
                    if self.autoLeave:
                        resp = await self.client.room_leave(room.room_id)
    
    async def _on_member_event(self, room, event):
        if self.autoLeave:
            # If someone else leaves or is banned from the room
            if (event.membership == "leave" or event.membership == "ban") and event.state_key != self.client.user_id:
                # Get all members in the room
                members = (await self.client.joined_members(room.room_id)).members
                # If I am the only member, leave the room
                if len(members) == 1:
                    await self.client.room_leave(room.room_id)
    
    async def _on_message(self, room, event):
        pass

    async def writeMessage(self, messageText, room):
        if not self.isRunning:
            raise Exception("Can not send message because Matrix bot is not running.")
        await self.client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": messageText,
            }
        )

    async def stop(self):
        if not self.isRunning:
            print("The matrix bot is not running")
            return
        self.isRunning = False
        print("Stopping matrix bot...") 
        await self.client.close()
            
