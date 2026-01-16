class TempPath:
    def __init__(self, suffix=""):
        import tempfile
        import os
        self.suffix = suffix
        self.fd = None
        self.path = None

    def __enter__(self):
        import tempfile
        import os
        self.fd, self.path = tempfile.mkstemp(suffix=self.suffix)
        os.close(self.fd)
        os.unlink(self.path)
        return self.path

    def __exit__(self, exc_type, exc_value, traceback):
        import os
        if self.path and os.path.exists(self.path):
            os.unlink(self.path)

class VoteBotCallbackTracker:
    def __init__(self):
        from io import StringIO
        self.log = StringIO()

    def add_poll_callback(self, poll):
        self.log.write(f"add_poll: {poll.short}\n")
        poll.addVotesUpdateCallback(self.votes_update_callback)
        poll.pollSuccessCallbacks.add(self.poll_success_callback)

    def votes_update_callback(self, poll):
        self.log.write(f"votes_update: {poll.short}\n")
        # sort options by short for consistent logging
        sorted_options = sorted(poll.validVotes.keys(), key=lambda o: o.short)
        for scenario in sorted_options:
            voters = poll.validVotes[scenario]
            # sort voters by id for consistent logging
            voters = sorted(voters, key=lambda v: v.id)
            self.log.write(f"  {scenario.short}: {[voter.id for voter in voters]}\n")

    def poll_success_callback(self, poll):
        self.log.write(f"poll_success: {poll.short}\n")

def test_core():
    import asyncio
    from vote_bot import getPerson, PeoplePool, VoteContext, Poll, PollOption, SQLiteActionLogger, DeadlinePoll
    with TempPath(suffix=".sqlite") as temp_db_path:
        async def run():
            actionLogger = SQLiteActionLogger(temp_db_path)
            pool = PeoplePool(actionLogger=actionLogger, loadOldActions=False)
            tracker = VoteBotCallbackTracker()
            pool.addAddPollCallback(tracker.add_poll_callback)
            tom = getPerson("Tom")
            pool.addPerson(tom)
            rootContext = VoteContext(peoplePool=pool, name="root")
            option1 = PollOption("Option 1", short="Opt1")
            option2 = PollOption("Option 2", short="Opt2")
            poll = DeadlinePoll(question="Test Poll?", options=[option1, option2], short="TestPoll", timespan=1)
            rootContext.addPoll(poll)
            assert tom.voteForPoll(option1)
            async def wait_poll_end():
                await asyncio.sleep(2)
                pool.timeEvents.stop()
            await asyncio.gather(pool.runTimeEvents(), wait_poll_end())
            log_contents = tracker.log.getvalue()
            print(f"Log contents ------------:\n{log_contents}")
            assert log_contents == "add_poll: TestPoll\nvotes_update: TestPoll\n  Opt1: []\n  Opt2: []\nvotes_update: TestPoll\n  Opt1: ['Tom']\n  Opt2: []\npoll_success: TestPoll\n"
        asyncio.run(run())