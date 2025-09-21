from .pollOption import PollOption
from .poll import Poll
import time

class DeadlinePoll(Poll):
    def __init__(self, question, options, short, deadline = None, timespan = None, currentTime = None):
        if deadline is None and timespan is None:
            raise Exception("Either a deadline or a timespan must be provided.")
        if deadline is None:
            deadline = time.time() + timespan
        super().__init__(question, options, short)
        self.deadline = deadline
        self.currentTime = currentTime if currentTime is not None else time.time()

    def setVoteContext(self, voteContext):
        super().setVoteContext(voteContext)
        self.voteContext.peoplePool.timeEvents.addEvent(self.deadline, self.deadlineReached, self.currentTime)

    def deadlineReached(self, eventTime = None):
        self._pollSuccess()

    def getDescription(self):
        return {
            "type": "deadline",
            "question": self.question,
            "options": [option.getDescription() for option in self.options.values()],
            "short": self.short,
            "deadline": self.deadline
        }
    
    @classmethod
    def fromDescription(cls, description, currentTime = None):
        if description["type"] != "deadline":
            raise Exception("Invalid description type for DeadlinePoll: " + description["type"])
        options = [PollOption.fromDescription(optDesc) for optDesc in description["options"]]
        return cls(
            question = description["question"],
            options = options,
            short = description["short"],
            deadline = description["deadline"],
            currentTime = currentTime
        )