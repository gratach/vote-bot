from .actions import Actions

class PeoplePool:
    def __init__(self, people = [], actionLogger = None, loadOldActions = True):
        self.people = set()
        self.voteContexts = {}
        self.addPollCallbacks = set()
        self.actionLogger = None
        for p in people:
            self.addPerson(p)
        if loadOldActions and self.actionLogger:
            for actionDict in self.actionLogger.iterateActions():
                Actions.executeAction(self, actionDict)
        self.actionLogger = actionLogger
    def addPerson(self, person):
        self.people.add(person)
        for voteContext in self.voteContexts.values():
            voteContext._updateAllPolls()
        self._logAction("addPersonToPool", person)
    def removePerson(self, person):
        self.people.discard(person)
        for voteContext in self.voteContexts.values():
            voteContext._updateAllPolls()
        self._logAction("removePersonFromPool", person)
    def _addVoteContext(self, voteContext):
        if voteContext.name in self.voteContexts:
            raise Exception("A vote context with the name '" + voteContext.name + "' already exists in this people pool.")
        self.voteContexts[voteContext.name] = voteContext
        for person in self.people:
            voteContext._setRepresentative(person, person)
    def _logAction(self, actionName, *args):
        actionDict = Actions.getAction(actionName, *args)
        if self.actionLogger:
            self.actionLogger.logAction(actionDict)
    def findVoteContextFromPath(self, path):
        if path == "" or path == []:
            raise Exception("The root context cannot be accessed through this method.")
        if isinstance(path, list):
            parts = path
        else:
            parts = path.split(".")
        if not parts[0] in self.voteContexts:
            raise Exception("No vote context with the name '" + parts[0] + "' exists in this people pool.")
        return self.voteContexts[parts[0]].findContextByParts(parts[1:])
    def addAddPollCallback(self, callback):
        self.addPollCallbacks.add(callback)
    def removeAddPollCallback(self, callback):
        self.addPollCallbacks.discard(callback)
    def triggerAddPollCallbacks(self, poll):
        for callback in self.addPollCallbacks:
            callback(poll)