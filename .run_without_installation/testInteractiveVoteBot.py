import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from vote_bot import getPerson, PeoplePool, VoteContext, Poll, Scenario, SQLiteActionLogger
from pathlib import Path

actionLogger = SQLiteActionLogger(Path(__file__).parent / "testVoteBot.sqlite")

pool = PeoplePool(actionLogger=actionLogger)

rootContext = VoteContext(peoplePool=pool, name="root")

def votesUpdate(poll):
    print(f"{poll.short} votes update")
    for scenario, voters in poll.validVotes.items():
        print(f"  {scenario.short}: {[voter.id for voter in voters]}")

def addPollCallback(poll):
    print(f"New poll added: {poll.short} in context {poll.voteContext.getPath()}")
    poll.addVotesUpdateCallback(votesUpdate)
pool.addAddPollCallback(addPollCallback)

