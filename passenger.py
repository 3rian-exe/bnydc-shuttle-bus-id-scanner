import datetime
class Passenger():

    #Changes to get the personID: 
    def __init__(self, access: bool, name: str, portal: str, date_time: datetime.date, personId: str):
        self.access = access
        self.name = name
        self.access_portal = portal
        self.date_time = date_time
        # personID
        self.personId = personId
        # self.card_type = card_type # str
        # self.hotstamp = hotstamp # str
        # self.visitor = visitor # bool