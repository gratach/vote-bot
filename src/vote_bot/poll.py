class Poll:
    def __init__(self, question, options, short):
        self.question = question
        self.options = options
        self.short = short
        self.directVotes = {option: set() for option in options}
        self.directedVotes = {option: set() for option in options}
        self.validVotes = {option: set() for option in options}
        self.votesUpdateCallbacks = set()
        self.voteContext = None
        for option in options:
            option.poll = self

    def _vote(self, voter, option):
        if not option in self.options:
            return False
        for opt, voters in self.directVotes.items():
            voters.discard(voter)
        self.directVotes[option].add(voter)
        self._updateVotes()
        return True

    def setVoteContext(self, voteContext):
        self.voteContext = voteContext

    def addVotesUpdateCallback(self, callback):
        self.votesUpdateCallbacks.add(callback)
        callback(self)

    def removeVotesUpdateCallback(self, callback):
        self.votesUpdateCallbacks.discard(callback)

    def _updateVotes(self):
        oldDirectedVotes = self.directedVotes
        oldValidVotes = self.validVotes
        # Set the directed votes according to the current representatives
        allVoters = {voter : option for option, voters in self.directVotes.items() for voter in voters}
        voterPerPerson = {}
        for person in self.voteContext.peoplePool.people:
            voterPerPerson[person] = self.voteContext.getFinalRepresentative(person, shortcutPersons=allVoters.keys())
        personsPerVoter = {}
        for person, voter in voterPerPerson.items():
            if voter not in personsPerVoter:
                personsPerVoter[voter] = set()
            personsPerVoter[voter].add(person)
        self.directedVotes = {option: set() for option in self.options}
        for option, voters in self.directVotes.items():
            for voter in voters:
                if voter in personsPerVoter:
                    self.directedVotes[option].update(personsPerVoter[voter])
        # Set the valid votes according to the current people in the people pool
        self.validVotes = {option : [voter for voter in voters if voter in self.voteContext.peoplePool.people] for option, voters in self.directedVotes.items()}
        # Call the callbacks if something changed
        if oldDirectedVotes != self.directedVotes or oldValidVotes != self.validVotes:
            for callback in self.votesUpdateCallbacks:
                callback(self)
