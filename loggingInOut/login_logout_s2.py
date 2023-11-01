from requests import post
import xmltodict as xmltodict
import urllib3
import json

urllib3.disable_warnings()

# Retrieve s2 credentials from the credentials json file.
def get_credentials(json_file_path):
    with open(json_file_path) as json_credentials:
        credentials = json.load(json_credentials)

        return credentials['S2_HOSTNAME'], credentials['S2_USERNAME'], credentials['S2_PASSWORD']


# Set the end point, username, and password
s2_api_endpoint, s2_username, s2_password = get_credentials('../json/s2_credentials.json')

# print(f"endpoint: {s2_api_endpoint}\nusername: {s2_username}\nPW: {s2_password}")

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