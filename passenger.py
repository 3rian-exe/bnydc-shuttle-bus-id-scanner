from typing import Union
class Passenger():
    def __init__(self, access: bool, portal_key: Union[str, None], reader_key: Union[str, None], person_id: Union[str, None], card_format: Union[str, None], encoded_num: Union[str, None]):
        self.access = access
        self.portal_key = portal_key 
        self.reader_key = reader_key
        self.person_id = person_id
        self.card_format = card_format
        self.hotstamp = encoded_num