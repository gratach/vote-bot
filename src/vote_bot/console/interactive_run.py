import asyncio
from ..vote_logic.person import getPerson
from ..vote_logic.pollOption import PollOption
from ..vote_logic.poll import Poll
from ..vote_logic.deadline_poll import DeadlinePoll
from ..vote_logic.people_pool import PeoplePool
from ..vote_logic.sqlite_action_logger import SQLiteActionLogger
from ..vote_logic.vote_context import VoteContext
from pathlib import Path

async def asyncInput(prompt: str = "") -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: input(prompt))

async def interactiveRun(pool, votebot = None):
    while True:
        command = await asyncInput("Enter command: ")
        command = command.strip().lower()
        if command == "exit":
            print("Exiting...")
            pool.timeEvents.stop()
            if votebot:
                await votebot.stop()
            break
        elif command == "help":
            print("Available commands: add person, remove person, list people, create poll, vote poll, unvote poll, vote person, unvote person, help, exit")
        elif command == "add person":
            id = await asyncInput("Enter person ID: ")
            person = getPerson(id)
            pool.addPerson(person)
        elif command == "remove person":
            id = await asyncInput("Enter person ID: ")
            person = getPerson(id)
            pool.removePerson(person)
        elif command == "list people":
            print("People in pool:")
            for person in pool.people:
                print(f" - {person.id}")
        elif command.startswith("create poll"):
            pollType = await asyncInput("Enter poll type (simple/deadline): ")
            question = await asyncInput("Enter poll question: ")
            options = []
            while True:
                optionText = await asyncInput("Enter poll option (or 'done' to finish): ")
                if optionText.lower() == "done":
                    break
                optionShort = await asyncInput("Enter option short name: ")
                options.append(PollOption(optionText, short=optionShort))
            short = await asyncInput("Enter poll short name: ")
            if pollType == "deadline":
                timespan = int(await asyncInput("Enter poll timespan in seconds: "))
                poll = DeadlinePoll(question, options, short, timespan=timespan)
            else:
                poll = Poll(question, options, short)
            contextPath = await asyncInput("Enter context path (e.g., root.finances): ")
            context = pool.findVoteContextFromPath(contextPath)
            context.addPoll(poll)
        elif command == "vote poll":
            personId = await asyncInput("Enter your person ID: ")
            person = getPerson(personId)
            contextPath = await asyncInput("Enter context path of the poll: ")
            context = pool.findVoteContextFromPath(contextPath)
            pollShort = await asyncInput("Enter poll short name: ")
            poll = context.polls.get(pollShort)
            if not poll:
                print(f"No poll found with short name '{pollShort}' in context '{contextPath}'")
                continue
            optionShort = await asyncInput("Enter option short name to vote for: ")
            option = poll.options.get(optionShort)
            if not option:
                print(f"No option found with short name '{optionShort}' in poll '{pollShort}'")
                continue
            if person.voteForPoll(option):
                print(f"{personId} voted for {optionShort} in poll {pollShort}")
            else:
                print(f"Failed to vote for {optionShort} in poll {pollShort}")
        elif command == "unvote poll":
            personId = await asyncInput("Enter your person ID: ")
            person = getPerson(personId)
            contextPath = await asyncInput("Enter context path of the poll: ")
            context = pool.findVoteContextFromPath(contextPath)
            pollShort = await asyncInput("Enter poll short name: ")
            poll = context.polls.get(pollShort)
            if not poll:
                print(f"No poll found with short name '{pollShort}' in context '{contextPath}'")
                continue
            if person.unvoteForPoll(poll):
                print(f"{personId} removed their vote from poll {pollShort}")
            else:
                print(f"Failed to remove vote from poll {pollShort}")
        elif command == "vote person":
            personId = await asyncInput("Enter your person ID: ")
            person = getPerson(personId)
            repId = await asyncInput("Enter representative person ID: ")
            representative = getPerson(repId)
            contextPath = await asyncInput("Enter context path: ")
            context = pool.findVoteContextFromPath(contextPath)
            if person.voteForPerson(representative, context):
                print(f"{personId} voted for {repId} as their representative in context {contextPath}")
            else:
                print(f"Failed to vote for {repId} as representative in context {contextPath}")
        elif command == "show reps":
            contextPath = await asyncInput("Enter context path (or leave empty for root): ")
            if contextPath.strip() == "":
                context = pool.voteContexts["root"]
            else:
                context = pool.findVoteContextFromPath(contextPath)
            print("Representation tree:")
            print(context.getRepresentationTree())
        elif command == "unvote person":
            personId = await asyncInput("Enter your person ID: ")
            person = getPerson(personId)
            contextPath = await asyncInput("Enter context path: ")
            context = pool.findVoteContextFromPath(contextPath)
            if person.unvoteForPerson(context):
                print(f"{personId} removed their representative vote in context {contextPath}")
            else:
                print(f"Failed to remove representative vote in context {contextPath}")
        else:
            print("Unknown command. Type 'help' for a list of commands.")