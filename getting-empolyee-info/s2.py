from requests import post, get
import xmltodict as xmltodict
import urllib3

urllib3.disable_warnings()

s2_api_endpoint = 'https://s2.bnydc.org/goforms/nbapi'
s2_username = 'kot'
s2_password = '2abbf9e2458bc07a307f111e209b5b2b'

# Creates and returns a session ID
# You should consider creating an existing session id if you are going to run 800 API calls
def login():
    body = '''
    <NETBOX-API>
        <COMMAND name="Login" num="1" dateformat="tzoffset">
            <PARAMS>
                <USERNAME>{username}</USERNAME>
                <PASSWORD>{password}</PASSWORD>
            </PARAMS>
        </COMMAND>
    </NETBOX-API>'''.format(username=s2_username, password=s2_password)
    try:
        response = post(s2_api_endpoint, body, verify=False, timeout=5)
        session_id = xmltodict.parse(response.text)['NETBOX']['@sessionid']
        
        return session_id
    except:
        return None

# I assume this closes a session
def logout(session_id):
    body = '''
    <NETBOX-API sessionid="{session_id}">
        <COMMAND name="Logout" num="1">
        </COMMAND>
    </NETBOX-API>
    '''.format(session_id=session_id)
    post(s2_api_endpoint, body, verify=False)
    return

# currently version 5.4.1
def get_api_version(existingSessionId=None):
    session_id = existingSessionId if existingSessionId else login()
    if not session_id:
        print("No session ID")
        return None
    body = '''
        <NETBOX-API sessionid="{session_id}">
            <COMMAND name="GetAPIVersion" num="1">
            </COMMAND>
        </NETBOX-API>
        '''.format(session_id=session_id)
    try:
        response = post(s2_api_endpoint, body, verify=False)
        if not existingSessionId:
            logout(session_id)
        response = response.content.decode("utf8")
        response = xmltodict.parse( response )
        response = response['NETBOX']['RESPONSE']
        if response['CODE'] != 'SUCCESS':
            print(response)
            return None
        return response['DETAILS']['APIVERSION']
    except:
        return None


def get_person_data(personId : str, existingSessionId=None)-> dict:
    session_id = existingSessionId if existingSessionId else login()
    if not session_id:
        print("No session ID")
        return None
    body = '''
        <NETBOX-API sessionid="{session_id}">
            <COMMAND name="SearchPersonData" num="1">
                <PARAMS>
                    <PERSONID>{person_id}</PERSONID>
                </PARAMS>
            </COMMAND>
        </NETBOX-API>
        '''.format(session_id=session_id, person_id=personId)
    try:
        response = post(s2_api_endpoint, body, verify=False)
        if not existingSessionId:
            logout(session_id)
        response = response.content.decode("utf8")
        response = xmltodict.parse( response )
        response = response['NETBOX']['RESPONSE']
            
        if response['CODE'] != 'SUCCESS':
            print(response)
            return None
        return response['DETAILS']['PEOPLE']['PERSON']
    except:
        return None
    

def get_access_cards( personId : str, existingSessionId=None ) -> list:
    person_data = get_person_data( personId, existingSessionId)
    if person_data == None:
        return None
    cards = person_data['ACCESSCARDS']

    if cards == None:                               # no cards
        return None
    
    cards = cards['ACCESSCARD']
    if type(cards) == dict:                         # 1 card
        return [ cards ]
            
    return cards                                    # 2+ cards


def get_latest_card_activity( card : dict, existingSessionId=None ) -> dict:
    session_id = existingSessionId if existingSessionId else login()
    if not session_id:
        print("No session ID")
        return None
    # GetCardAccessDetails command requires CARD_FORMAT and ENCODEDNUM elements
    body = '''
        <NETBOX-API sessionid="{session_id}">
            <COMMAND name="GetCardAccessDetails" num="1">
                <PARAMS>
                    <ENCODEDNUM>{encodednum}</ENCODEDNUM>
                    <CARDFORMAT>{format}</CARDFORMAT>
                    <MAXRECORDS>1</MAXRECORDS>
                </PARAMS>
            </COMMAND>
        </NETBOX-API>
        '''.format(session_id=session_id, encodednum=card['ENCODEDNUM'], format=card['CARDFORMAT'])
    try:
        response = post(s2_api_endpoint, body, verify=False)
        if not existingSessionId:
            logout(session_id)
        response = response.content.decode("utf8")
        response = xmltodict.parse( response )
        response = response['NETBOX']['RESPONSE']
            
        if response['CODE'] != 'SUCCESS':
            print(response)
            return None
        return response['DETAILS']['ACCESSES']['ACCESS']
    except:
        return None


def get_latest_person_activity(personId : str, existingSessionId=None) -> str:
    cards = get_access_cards( personId , existingSessionId )
    if cards == None:
        return None
    
    if len( cards ) == 1:
        return get_latest_card_activity( cards[0], existingSessionId )
    
    last_used_card = cards[0]
    latest_activity = get_latest_card_activity( last_used_card, existingSessionId )
    for card in cards:
        activity = get_latest_card_activity(card)
        if activity == None:
            continue
        if latest_activity == None:
            last_used_card = card
            latest_activity = activity
            continue
        if latest_activity['DTTM'] < activity['DTTM']:
            last_used_card = card
            latest_activity = activity
    return latest_activity


# print( get_api_version() )                      # 5.4.1

# print( get_access_cards("_27298") )             # john rodriguez ( 7 cards )
# print( get_access_cards("kot_355a20bb") )       # darnel gibbs ( 3 cards, 2 active )
# print( get_person_data("kot_f1ca2496") )        # david song (2 cards)
# print( get_person_data("kot_6d6dc517") )        # brian sterfeld (1 card)
# print( get_person_data("BXPvD72334229") )       # dan cutillo (no cards)

# print( get_latest_person_activity("kot_f1ca2496") )        # david song (2 cards)
# print( get_latest_person_activity("kot_6d6dc517") )        # brian sterfeld (1 card)
# print( get_latest_person_activity("BXPvD72334229") )       # dan cutillo (no cards)

# print( get_latest_person_activity("kot_52868673") ) 
