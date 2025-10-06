from .person import getPerson
from .vote_context import VoteContext
from .deadline_poll import DeadlinePoll

class Actions:
    @classmethod
    def executeAction(cls, peoplePool, actionDict, timestamp=None):
        if actionDict["action"] == "addPersonToPool":
            person = getPerson(actionDict["personId"])
            peoplePool.addPerson(person, timestamp)
        elif actionDict["action"] == "removePersonFromPool":
            person = getPerson(actionDict["personId"])
            peoplePool.removePerson(person, timestamp)
        elif actionDict["action"] == "voteForPerson":
            person = getPerson(actionDict["personId"])
            representative = getPerson(actionDict["representativeId"])
            voteContext = peoplePool.findVoteContextFromPath(actionDict["voteContextPath"])
            person.voteForPerson(representative, voteContext, timestamp)
        elif actionDict["action"] == "unvoteForPerson":
            person = getPerson(actionDict["personId"])
            voteContext = peoplePool.findVoteContextFromPath(actionDict["voteContextPath"])
            person.unvoteForPerson(voteContext, timestamp)
        elif actionDict["action"] == "voteForPoll":
            person = getPerson(actionDict["personId"])
            voteContext = peoplePool.findVoteContextFromPath(actionDict["voteContextPath"])
            poll = voteContext.polls[actionDict["pollShort"]]
            pollOption = poll.options[actionDict["optionShort"]]
            person.voteForPoll(pollOption, timestamp)
        elif actionDict["action"] == "unvoteForPoll":
            person = getPerson(actionDict["personId"])
            voteContext = peoplePool.findVoteContextFromPath(actionDict["voteContextPath"])
            poll = voteContext.polls[actionDict["pollShort"]]
            person.unvoteForPoll(poll, timestamp)
        elif actionDict["action"] == "addPollToContext":
            voteContext = peoplePool.findVoteContextFromPath(actionDict["voteContextPath"])
            pollDescription = actionDict["pollDescription"]
            if pollDescription["type"] == "deadline":
                poll = DeadlinePoll.fromDescription(pollDescription, timestamp)
            else:
                raise Exception("Unknown poll type: " + pollDescription["type"])
            voteContext.addPoll(poll, timestamp)
        elif actionDict["action"] == "removePollFromContext":
            voteContext = peoplePool.findVoteContextFromPath(actionDict["voteContextPath"])
            poll = voteContext.polls[actionDict["pollShort"]]
            voteContext.removePoll(poll, timestamp)
    @classmethod
    def getAction(cls, actionName, *args):
        if actionName == "addPersonToPool":
            return {"action": "addPersonToPool", "personId": args[0].id}
        elif actionName == "removePersonFromPool":
            return {"action": "removePersonFromPool", "personId": args[0].id}
        elif actionName == "voteForPerson":
            return {"action": "voteForPerson", "personId": args[0].id, "representativeId": args[1].id, "voteContextPath": args[2].getPath()}
        elif actionName == "unvoteForPerson":
            return {"action": "unvoteForPerson", "personId": args[0].id, "voteContextPath": args[1].getPath()}
        elif actionName == "voteForPoll":
            return {"action": "voteForPoll", "personId": args[0].id, "voteContextPath": args[1].poll.voteContext.getPath(), "pollShort": args[1].poll.short, "optionShort": args[1].short}
        elif actionName == "unvoteForPoll":
            return {"action": "unvoteForPoll", "personId": args[0].id, "voteContextPath": args[1].voteContext.getPath(), "pollShort": args[1].short}
        elif actionName == "addPollToContext":
            return {"action": "addPollToContext", "pollShort": args[0].short, "voteContextPath": args[1].getPath(), "pollDescription": args[0].getDescription()}
        elif actionName == "removePollFromContext":
            return {"action": "removePollFromContext", "pollShort": args[0].short, "voteContextPath": args[1].getPath()}
        else:
            raise Exception("Unknown action name: " + actionName)