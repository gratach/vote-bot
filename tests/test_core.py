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




def testContainsLogTreeThisStructure():
    from vote_bot.log.log_compare import containsLogTreeThisStructure
    assert containsLogTreeThisStructure(
        {"a": 1, "b": 2},
        {"a": 1}
    )
    assert not containsLogTreeThisStructure(
        {"a": 1, "b": 2},
        {"a": 2}
    )
    assert containsLogTreeThisStructure(
        {"a": {"b": {"c": 3, "d": 4}}},
        {"a": {"b": {"c": 3}}}
    )
    assert not containsLogTreeThisStructure(
        {"a": {"b": {"c": 3, "d": 4}}},
        {"a": {"b": {"c": 4}}}
    )
    assert containsLogTreeThisStructure(
        {"a": [1, 2, 3], "b": 2},
        {"a": [1, 2]}
    )
    assert not containsLogTreeThisStructure(
        {"a": [1, 2, 3], "b": 2},
        {"a": [2, 1]}
    )
    assert containsLogTreeThisStructure(
        {"a": {"b": [ {"c": 1}, {"c": 2} ] }},
        {"a": {"b": [ {"c": 1} ] }}
    )
    assert not containsLogTreeThisStructure(
        {"a": {"b": [ {"c": 1}, {"c": 2} ] }},
        {"a": {"b": [ {"c": 2} ] }}
    )

def testCore():
    import asyncio
    from vote_bot import getPerson, PeoplePool, VoteContext, Poll, PollOption, SQLiteActionLogger, DeadlinePoll
    from vote_bot.log.vote_logger import VoteLogger
    from vote_bot.log.log_compare import containsLogTreeThisStructure
    with TempPath(suffix=".sqlite") as temp_db_path:
        async def run():
            print("Starting testCore")
            actionLogger = SQLiteActionLogger(temp_db_path)
            pool = PeoplePool(actionLogger=actionLogger, loadOldActions=False)
            tracker = VoteLogger(logToConsole=True)
            pool.addAddPollCallback(tracker.addPollCallback)
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
            assert containsLogTreeThisStructure(tracker.takeAllLogs(), [
                {"action": "add_poll", "poll_short": "TestPoll"},
                {"action": "votes_update", "poll_short": "TestPoll", "voting_status": [
                    {"option_short": "Opt1", "voters": []},
                    {"option_short": "Opt2", "voters": []},
                ]},
                {"action": "votes_update", "poll_short": "TestPoll", "voting_status": [
                    {"option_short": "Opt1", "voters": ["Tom"]},
                    {"option_short": "Opt2", "voters": []},
                ]},
                {"action": "poll_success", "poll_short": "TestPoll"},
            ])  
        asyncio.run(run())    