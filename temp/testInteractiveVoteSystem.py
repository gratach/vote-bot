import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from vote_bot import getPerson, PeoplePool, VoteContext, Poll, PollOption, SQLiteActionLogger, DeadlinePoll
from vote_bot import PeoplePool, SQLiteActionLogger, VoteBot, interactiveRun
from pathlib import Path
import asyncio

async def run():

    actionLogger = SQLiteActionLogger(Path(__file__).parent / "testVoteBot.sqlite")

    def votesUpdate(poll):
        print(f"{poll.short} votes update")
        for scenario, voters in poll.validVotes.items():
            print(f"  {scenario.short}: {[voter.id for voter in voters]}")

    def addPollCallback(poll):
        print(f"New poll added: {poll.short} in context {poll.voteContext.getPath()}")
        poll.addVotesUpdateCallback(votesUpdate)
        poll.pollSuccessCallbacks.add(pollSuccess)

    def pollSuccess(poll):
        print(f"Poll {poll.short} ended successfully. Final votes:")
        for scenario, voters in poll.validVotes.items():
            print(f"  {scenario.short}: {len(voters)} votes ({[voter.id for voter in voters]})")

    pool = PeoplePool(actionLogger=actionLogger, addPollCallbacks=[addPollCallback])

    # run timevents and interactiveRun concurrently
    await asyncio.gather(pool.runTimeEvents(), interactiveRun(pool))



if __name__ == "__main__":
    asyncio.run(run())