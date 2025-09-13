class Person:
    def __init__(self, id):
        self.id = id
    def voteForPoll(self, scenario):
        ret = scenario.poll._vote(self, scenario)
        if ret:
            scenario.poll.voteContext.peoplePool._logAction("voteForPoll", self, scenario)
        return ret
    def unvoteForPoll(self, poll):
        ret = poll._unvote(self)
        if ret:
            poll.voteContext.peoplePool._logAction("unvoteForPoll", self, poll)
        return ret
    def voteForPerson(self, person, voteContext):
        # Check if any recursion wold occur, voting for oneself is always allowed
        if not self == person and voteContext._checkIfAnyChildDelegatesTo(person, self):
            return False
        voteContext._activelySetRepresentative(self, person)
        voteContext.peoplePool._logAction("voteForPerson", self, person, voteContext)
        return True
    def unvoteForPerson(self, voteContext):
        # Check if any recursion wold occur, voting for oneself is always allowed
        parentRepresentative = voteContext.parentContext.representativePerPerson[self] if voteContext.parentContext else self
        if voteContext.parentContext._checkIfAnyChildDelegatesTo(parentRepresentative, self):
            return False
        voteContext._activelyUnsetRepresentative(self)
        voteContext.peoplePool._logAction("unvoteForPerson", self, voteContext)
        return True

personDict = None
def getPersonDict():
    global personDict
    if personDict == None:
        personDict = {} # Replace with load from DB
    return personDict
def getPerson(id):
    personDict = getPersonDict()
    if not id in personDict:
        personDict[id] = Person(id)
    return personDict[id]