import datetime
class Passenger():
    def __init__(self, access: bool, name: str, portal: str, date_time: datetime.date):
        self.access = access
        self.name = name
        self.access_portal = portal
        self.date_time = date_time
        # self.card_type = card_type # str
        # self.hotstamp = hotstamp # str
        # self.visitor = visitor # bool