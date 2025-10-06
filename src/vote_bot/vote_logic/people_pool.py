from .actions import Actions
from .time_events import TimeEvents
from .vote_context import VoteContext

class PeoplePool:
    def __init__(self, actionLogger = None, loadOldActions = True, addPollCallbacks = None, removePollCallbacks = None):
        self.people = set()
        self.voteContexts = {}
        self.addPollCallbacks = set()
        self.removePollCallbacks = set()
        self.timeEvents = TimeEvents()
        self.actionLogger = None
        if addPollCallbacks:
            for callback in addPollCallbacks:
                self.addAddPollCallback(callback)
        if removePollCallbacks:
            for callback in removePollCallbacks:
                self.addRemovePollCallback(callback)
        if loadOldActions and actionLogger:
            for timestamp, actionDict in actionLogger.iterateActions():
                Actions.executeAction(self, actionDict, timestamp)
        self.actionLogger = actionLogger
    def addPerson(self, person, timeStamp = None):
        timeStamp = self.timeEvents.getRightTimeOrderTimestamp(timeStamp, timeStamp)
        self.people.add(person)
        for voteContext in self.voteContexts.values():
            voteContext._updateAllPolls()
        self._logAction(timeStamp, "addPersonToPool", person)
    def removePerson(self, person, timestamp=None):
        timestamp = self.timeEvents.getRightTimeOrderTimestamp(timestamp, timestamp)
        self.people.discard(person)
        for voteContext in self.voteContexts.values():
            voteContext._updateAllPolls()
        self._logAction(timestamp, "removePersonFromPool", person)
    def _addVoteContext(self, voteContext):
        if voteContext.name in self.voteContexts:
            raise Exception("A vote context with the name '" + voteContext.name + "' already exists in this people pool.")
        self.voteContexts[voteContext.name] = voteContext
        for person in self.people:
            voteContext._setRepresentative(person, person)
    def _logAction(self, timeStamp, actionName, *args):
        actionDict = Actions.getAction(actionName, *args)
        if self.actionLogger:
            self.actionLogger.logAction(actionDict, timeStamp)
    def findVoteContextFromPath(self, path):
        if path == "" or path == []:
            raise Exception("The root context cannot be accessed through this method.")
        if isinstance(path, list):
            parts = path
        else:
            parts = path.split(".")
        if not parts[0] in self.voteContexts:
            self.voteContexts[parts[0]] = VoteContext(name=parts[0], peoplePool=self)
        return self.voteContexts[parts[0]].findContextByParts(parts[1:])
    def addAddPollCallback(self, callback):
        self.addPollCallbacks.add(callback)
    def removeAddPollCallback(self, callback):
        self.addPollCallbacks.discard(callback)
    def triggerAddPollCallbacks(self, poll):
        for callback in self.addPollCallbacks:
            callback(poll)
    def addRemovePollCallback(self, callback):
        self.removePollCallbacks.add(callback)
    def removeRemovePollCallback(self, callback):
        self.removePollCallbacks.discard(callback)
    def triggerRemovePollCallbacks(self, poll):
        for callback in self.removePollCallbacks:
            callback(poll)
    async def runTimeEvents(self):
        await self.timeEvents.run()
    def stopTimeEvents(self):
        self.timeEvents.stop()