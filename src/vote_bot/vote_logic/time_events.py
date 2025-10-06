import time
import asyncio

class TimeEvent:
    def __init__(self, eventTime, callback, timeEvents):
        self.timeEvents = timeEvents
        self.eventTime = eventTime
        self.callback = callback
        self.cancelled = False
        self.triggered = False
    def trigger(self):
        if not self.triggered and not self.cancelled:
            while not self == self.timeEvents.orderedTimeEventTuples[0][1]:
                assert self.eventTime > self.timeEvents.orderedTimeEventTuples[0][0]
                self.timeEvents.orderedTimeEventTuples[-1][1].trigger()
            self.triggered = True
            self.timeEvents.orderedTimeEventTuples.pop()
            self.callback(self.eventTime)

class TimeEvents:
    def __init__(self):
        self.orderedTimeEventTuples = [] # Tuples of (eventTime, TimeEvent), ordered by eventTime descending
        self.lastSelectedTimestamp = None
        self.condition = asyncio.Condition()
        self.running = False
        self.stopRunning = False
    def _makeSureAllEventsUpToNowAreTriggered(self, timestamp):
        while len(self.orderedTimeEventTuples) > 0 and self.orderedTimeEventTuples[-1][0] <= timestamp:
            timeEvent = self.orderedTimeEventTuples[-1][1]
            timeEvent.trigger()
    def getRightTimeOrderTimestamp(self, timestamp = None, currentTime = None):
        if currentTime is None:
            currentTime = time.time()
        if timestamp is None:
            timestamp = currentTime
        currentTime = timestamp
        # Make sure that the timestamp does not match any existing timestamp
        i = len(self.orderedTimeEventTuples) - 1
        while i >= 0:
            if self.orderedTimeEventTuples[i][0] == timestamp:
                timestamp = self.orderedTimeEventTuples[i][0] + 0.000001
            i -= 1
        self._makeSureAllEventsUpToNowAreTriggered(currentTime)
        return timestamp
    def addEvent(self, eventTime, callback, currentTime = None):
        eventTime = self.getRightTimeOrderTimestamp(eventTime, currentTime)
        timeEvent = TimeEvent(eventTime, callback, self)
        i = len(self.orderedTimeEventTuples)
        while i > 0 and self.orderedTimeEventTuples[i - 1][0] < eventTime:
            i -= 1
        self.orderedTimeEventTuples.insert(i, (eventTime, timeEvent))
        if i == len(self.orderedTimeEventTuples) - 1:
            async def notify():
                async with self.condition:
                    self.condition.notify_all()
            asyncio.create_task(notify())
        return timeEvent
    def removeTimeEvent(self, timeEvent, currentTime = None):
        self._makeSureAllEventsUpToNowAreTriggered(currentTime if currentTime is not None else time.time())
        self.orderedTimeEventTuples = [(et, te) for (et, te) in self.orderedTimeEventTuples if not te == timeEvent]

    async def run(self):
        if self.running:
            raise Exception("The TimeEvents is already running.")
        self.running = True
        while not self.stopRunning:
            currentTime = time.time()
            self._makeSureAllEventsUpToNowAreTriggered(currentTime)
            nextTime = None
            if len(self.orderedTimeEventTuples) > 0:
                nextTime = self.orderedTimeEventTuples[-1][0]
            async with self.condition:
                try:
                    if nextTime is None:
                        await asyncio.wait_for(self.condition.wait(), None)
                    else:
                        await asyncio.wait_for(self.condition.wait(), max(0, nextTime - currentTime))
                except asyncio.TimeoutError:
                    pass
        self.running = False

    def stop(self):
        self.stopRunning = True
        async def notify():
            async with self.condition:
                self.condition.notify_all()
        asyncio.create_task(notify())

