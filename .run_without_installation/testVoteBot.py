import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from vote_bot import getPerson, PeoplePool, VoteContext, Poll, Scenario, SQLiteActionLogger
from pathlib import Path

tom = getPerson("Tom")
paul = getPerson("Paul")
fred = getPerson("Fred")

#actionLogger = SQLiteActionLogger(Path(__file__).parent / "testVoteBot.sqlite")

pool = PeoplePool([tom, paul, fred])#, actionLogger=actionLogger, loadOldActions=False)

rootContext = VoteContext(peoplePool=pool, name="root")
finances = rootContext.subContext("finances")
administration = rootContext.subContext("administration")
publicRelations = rootContext.subContext("publicRelations")
humanResources = rootContext.subContext("humanResources")
infrastructure = rootContext.subContext("infrastructure")
donations = finances.subContext("donations")
investments = finances.subContext("investments")
servers = infrastructure.subContext("server")
software = infrastructure.subContext("software")

developPrototypeFirst = Scenario("Develop a prototype first", short="ProtoFirst")
startDirectlyWithMainSoftware = Scenario("Start directly with the main software", short="StartWithMain")
howToContinueSoftwareDevelopment = Poll(question="What is the best way to continue with the voting bot software?", options=[developPrototypeFirst, startDirectlyWithMainSoftware], short="SoftwareDevelopment")
software.addPoll(howToContinueSoftwareDevelopment)

def votesUpdate(poll):
    print(f"{poll.short} votes update")
    for scenario, voters in poll.validVotes.items():
        print(f"  {scenario.short}: {[voter.id for voter in voters]}")
howToContinueSoftwareDevelopment.addVotesUpdateCallback(votesUpdate)

print("Tom votes for Paul as his representative in the root context")
assert tom.voteForPerson(paul, rootContext)
print("Tom votes for Fred as his representative in the software context")
assert tom.voteForPerson(fred, software)
print("Paul votes for Tom as his representative in the infrastructure context. However, this would create a delegation loop, so it is not allowed.")
assert not paul.voteForPerson(tom, infrastructure)
print("Paul votes for Fred as his representative in the infrastructure context")
assert paul.voteForPerson(fred, infrastructure)
print("Paul votes for the scenario 'Develop a prototype first'")
assert paul.voteForPoll(developPrototypeFirst)
print("Fred votes for the scenario 'Start directly with the main software'")
assert fred.voteForPoll(startDirectlyWithMainSoftware)
print("Tom removes his vote for Fred as his representative in the software context. Now, Tom's representative in the software context is Paul, as Paul is Tom's representative in the root context and no other representative was actively chosen in the software context.")
assert tom.unvoteForPerson(software)



