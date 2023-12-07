from requests import post
import xmltodict as xmltodict
import urllib3
import json

urllib3.disable_warnings()

config_file_path = '/home/scanner/bus_id_scanner/config.json'

# Retrieve s2 credentials from the credentials json file.
def get_credentials(json_file_path):
    with open(json_file_path) as json_credentials:
        credentials = json.load(json_credentials)

        return credentials['s2_credentials']['S2_HOSTNAME'], credentials['s2_credentials']['S2_USERNAME'], credentials['s2_credentials']['S2_PASSWORD']


# Set the end point, username, and password
s2_api_endpoint, s2_username, s2_password = get_credentials(config_file_path)

# Creates and returns a session ID
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

# Closes a session.
def logout(session_id):
    body = '''
    <NETBOX-API sessionid="{session_id}">
        <COMMAND name="Logout" num="1">
        </COMMAND>
    </NETBOX-API>
    '''.format(session_id=session_id)
    post(s2_api_endpoint, body, verify=False)
    return