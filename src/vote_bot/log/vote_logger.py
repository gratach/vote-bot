import json

class VoteLogger:
    def __init__(self, logToConsole=False):
        from io import StringIO
        self.log = []
        self.logToConsole = logToConsole

    def convertLogToString(self, log):
        return json.dumps(log, indent=2)
    
    def logAppend(self, entry):
        self.log.append(entry)
        if self.logToConsole:
            print(self.convertLogToString(entry))

    def addPollCallback(self, poll):
        self.logAppend({"action": "add_poll", "poll_short": poll.short})
        poll.addVotesUpdateCallback(self.votesUpdateCallback)
        poll.pollSuccessCallbacks.add(self.pollSuccessCallback)

    def votesUpdateCallback(self, poll):
        current_log = {"action": "votes_update", "poll_short": poll.short}
        # sort options by short for consistent logging
        voting_status = []
        sorted_options = sorted(poll.validVotes.keys(), key=lambda o: o.short)
        for scenario in sorted_options:
            voters = poll.validVotes[scenario]
            # sort voters by id for consistent logging
            voters = sorted(voters, key=lambda v: v.id)
            voting_status.append({"option_short": scenario.short, "voters": [v.id for v in voters]})
        current_log["voting_status"] = voting_status
        self.logAppend(current_log)

    def pollSuccessCallback(self, poll):
        self.logAppend({"action": "poll_success", "poll_short": poll.short})

    def takeAllLogs(self):
        ret = self.log
        self.log = []
        return ret