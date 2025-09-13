from .person import getPerson
from .vote_context import VoteContext

class Actions:
    @classmethod
    def executeAction(cls, peoplePool, actionDict):
        if actionDict["action"] == "addPersonToPool":
            person = getPerson(actionDict["personId"])
            peoplePool.addPerson(person)
        elif actionDict["action"] == "removePersonFromPool":
            person = getPerson(actionDict["personId"])
            peoplePool.removePerson(person)
        elif actionDict["action"] == "voteForPerson":
            person = getPerson(actionDict["personId"])
            representative = getPerson(actionDict["representativeId"])
            voteContext = peoplePool.findVoteContextFromPath(actionDict["voteContextPath"])
            person.voteForPerson(representative, voteContext)
        elif actionDict["action"] == "unvoteForPerson":
            person = getPerson(actionDict["personId"])
            voteContext = peoplePool.findVoteContextFromPath(actionDict["voteContextPath"])
            person.unvoteForPerson(voteContext)
        elif actionDict["action"] == "voteForPoll":
            person = getPerson(actionDict["personId"])
            voteContext = peoplePool.findVoteContextFromPath(actionDict["voteContextPath"])
            poll = voteContext.polls[actionDict["pollShort"]]
            person.voteForPoll(poll)
        elif actionDict["action"] == "unvoteForPoll":
            person = getPerson(actionDict["personId"])
            voteContext = peoplePool.findVoteContextFromPath(actionDict["voteContextPath"])
            poll = voteContext.polls[actionDict["pollShort"]]
            person.unvoteForPoll(poll)
    @classmethod
    def getAction(cls, actionName, *args):
        print(actionName)
        if actionName == "addPersonToPool":
            return {"action": "addPersonToPool", "personId": args[0].id}
        elif actionName == "removePersonFromPool":
            return {"action": "removePersonFromPool", "personId": args[0].id}
        elif actionName == "voteForPerson":
            return {"action": "voteForPerson", "personId": args[0].id, "representativeId": args[1].id, "voteContextPath": args[2].getPath()}
        elif actionName == "unvoteForPerson":
            return {"action": "unvoteForPerson", "personId": args[0].id, "voteContextPath": args[1].getPath()}
        elif actionName == "voteForPoll":
            return {"action": "voteForPoll", "personId": args[0].id, "voteContextPath": args[1].poll.voteContext.getPath(), "pollShort": args[1].poll.short}
        elif actionName == "unvoteForPoll":
            return {"action": "unvoteForPoll", "personId": args[0].id, "voteContextPath": args[1].voteContext.getPath(), "pollShort": args[1].short}