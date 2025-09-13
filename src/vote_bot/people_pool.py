class PeoplePool:
    def __init__(self, people = []):
        self.people = set()
        self.voteContexts = set()
        for p in people:
            self.addPerson(p)
    def addPerson(self, person):
        self.people.add(person)
        for voteContext in self.voteContexts:
            voteContext._setRepresentative(person, person)
    def removePerson(self, person):
        self.people.discard(person)
    def _addVoteContext(self, voteContext):
        self.voteContexts.add(voteContext)
        for person in self.people:
            voteContext._setRepresentative(person, person)