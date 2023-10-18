import requests
import xmltodict as xmltodict
from collections import OrderedDict

endpoint_url = 'https://s2.bnydc.org/goforms/nbapi'

def login():
    body = '''
        <NETBOX-API>
            <COMMAND name="Login" num="1" dateformat="tzoffset">
                <PARAMS>
                    <USERNAME>{username}</USERNAME>
                    <PASSWORD>{password}</PASSWORD>
                </PARAMS>
            </COMMAND>
        </NETBOX-API>'''.format(
            username="", 
            password=""
            )
        
    try:
            response = requests.post(endpoint_url, body,verify=False, timeout=5)
            session_id = xmltodict.parse(response.text)['NETBOX']['@sessionid']
            
            return session_id
    except:
            return None
    
def get_person(person_hotstamp, sessionId=None):
    
    session_id = sessionId if sessionId else login()
    
    if not session_id:
        print("No session ID")
        return None
        
    body = '''
        <NETBOX-API sessionid="{session_id}">
            <COMMAND name="SearchPersonData" num="1">
                <PARAMS>
                    <HOTSTAMP>{person_id}</HOTSTAMP>
                </PARAMS>
            </COMMAND>
        </NETBOX-API>
        '''.format(session_id=session_id, person_id=person_hotstamp)

    try:
        response = xmltodict.parse(requests.post(endpoint_url, body, verify=False).content.decode("utf8"))['NETBOX']['RESPONSE']
            
        if not sessionId:
            logout(session_id)
            
            if response['CODE'] == 'FAIL':
                print('FAIL')
                return None
            
            return response['DETAILS']['PEOPLE']['PERSON']
    except:
        return None
        
def logout(session_id):
        body = '''
    <NETBOX-API sessionid="{session_id}">
        <COMMAND name="Logout" num="1">
        </COMMAND>
    </NETBOX-API>
    '''.format(session_id=session_id)
    
###############################################################################

hotstamp = input("Please enter your hotstamp/encoded number credential: ").strip()

while not hotstamp.isnumeric():
    hotstamp = input("Invalid input: credential must be numeric.\nPlease enter your hotstamp/encoded number credential: ").strip()

print(get_person(hotstamp))