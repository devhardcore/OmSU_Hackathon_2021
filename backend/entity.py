class Event:
    def __init__(self, name, event_id, summary, end, start, capacity, url):
        self.name = name
        self.summary = summary
        self.start = start
        self.end = end
        self.event_id = event_id
        self.capacity = capacity
        self.url = url
