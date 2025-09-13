class Person:
    def __init__(self, id):
        self.id = id
    def voteForScenario(self, scenario):
        return scenario.poll._vote(self, scenario)
    def unvoteForScenario(self, scenario):
        pass
    def voteForPerson(self, person, voteContext):
        # Check if any recursion wold occur, voting for oneself is always allowed
        if not self == person and voteContext._checkIfAnyChildDelegatesTo(person, self):
            return False
        voteContext._activelySetRepresentative(self, person)
        return True
    def unvoteForPerson(self, person, voteContext):
        # Check if any recursion wold occur, voting for oneself is always allowed
        parentRepresentative = voteContext.parentContext.representativePerPerson[self] if voteContext.parentContext else self
        if not parentRepresentative == person and voteContext.parentContext._checkIfAnyChildDelegatesTo(parentRepresentative, self):
            return False
        voteContext._activelyUnsetRepresentative(self)
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