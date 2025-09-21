class PollOption:
    def __init__(self, description, short):
        self.description = description
        self.short = short
        self.poll = None

    def getDescription(self):
        return {
            "description": self.description,
            "short": self.short
        }
    @classmethod
    def fromDescription(cls, description):
        return cls(
            description = description["description"],
            short = description["short"]
        )