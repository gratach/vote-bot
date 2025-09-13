class VoteContext:
    def __init__(self, name, peoplePool = None, parentContext = None):
        assert (peoplePool is None) != (parentContext is None)
        assert not "." in (name or "")
        self.peoplePool = parentContext.peoplePool if parentContext else peoplePool
        self.parentContext = parentContext
        self.name = name
        self.subContexts = {}
        self.polls = {}
        self.representativePerPerson = {}
        self.activelyChoosenRepresentativePerPerson = {}
        if parentContext is None:
            self.peoplePool._addVoteContext(self)
    def getFinalRepresentative(self, person, shortcutPersons = set()):
        lastPersonInChain = person
        if person in shortcutPersons:
            return person
        while self.representativePerPerson.get(lastPersonInChain, lastPersonInChain) != lastPersonInChain:
            lastPersonInChain = self.representativePerPerson[lastPersonInChain]
            if lastPersonInChain in shortcutPersons:
                break
        return lastPersonInChain
    def _checkIfAnyChildDelegatesTo(self, person, delegate):
        if person == delegate:
            return True
        lastPersonInChain = person
        while self.representativePerPerson.get(lastPersonInChain, lastPersonInChain) != lastPersonInChain:
            lastPersonInChain = self.representativePerPerson[lastPersonInChain]
            if lastPersonInChain == delegate:
                return True
        for subContext in self.subContexts.values():
            if subContext._checkIfAnyChildDelegatesTo(person, delegate):
                return True
        return False
    def _activelySetRepresentative(self, person, representative):
        self.activelyChoosenRepresentativePerPerson[person] = representative
        self._setRepresentative(person, representative)
    def _activelyUnsetRepresentative(self, person):
        del self.activelyChoosenRepresentativePerPerson[person]
        parentRepresentative = self.parentContext.representativePerPerson[person] if self.parentContext else person
        self._setRepresentative(person, parentRepresentative)
    def _setRepresentative(self, person, representative):
        if self.activelyChoosenRepresentativePerPerson.get(person, representative) != representative:
            return
        self.representativePerPerson[person] = representative
        for subContext in self.subContexts.values():
            subContext._setRepresentative(person, representative)
        for poll in self.polls.values():
            poll._updateVotes()
    def subContext(self, name):
        if not name in self.subContexts:
            self.subContexts[name] = VoteContext(name=name, parentContext=self)
        return self.subContexts[name]
    def addPoll(self, poll):
        pollName = poll.short
        assert not pollName in self.polls
        self.polls[pollName] = poll
        poll.setVoteContext(self)
        poll._updateVotes()
        self.peoplePool.triggerAddPollCallbacks(poll)
    def findContextByParts(self, parts):
        if len(parts) == 0:
            return self
        return self.subContext(parts[0]).findContextByParts(parts[1:])
    def getPath(self):
        if self.parentContext:
            return self.parentContext.getPath() + "." + self.name
        else:
            return self.name
    def _updateAllPolls(self):
        for poll in self.polls.values():
            poll._updateVotes()
        for subContext in self.subContexts.values():
            subContext._updateAllPolls()