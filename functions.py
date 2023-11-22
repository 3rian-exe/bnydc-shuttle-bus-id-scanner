import json
import urllib3
import datetime
import xmltodict
from typing import Union, Tuple
from requests import post
from passenger import Passenger

urllib3.disable_warnings()

#******************************************************************************
# load the required S2 credentials.
# This function opens a JSON file path and returns a tuple containing 
# the s2 credentials.
def load_s2_credentials(json_file_path):
    with open(json_file_path) as json_credentials:
        credentials = json.load(json_credentials)

        endpoint_url = credentials['S2_HOSTNAME']
        
        return (endpoint_url,)
#******************************************************************************


#******************************************************************************
# Load the card formats and proxyclick format from the json config file.
# This function recieves a JSON file path and returns the proxyclick format
# and the valid RFID card bit lengths in a tuple.
def load_card_formts(json_file_path):
    with open(json_file_path) as json_formats:
        formats = json.load(json_formats)

        proxyclick_format = formats['PROXYCLICK']
        card_fomats_26_bit = formats['26']
        
        return (proxyclick_format, card_fomats_26_bit)
#******************************************************************************


proxyclick_format, card_formats_26_bit = load_card_formts('card_formats.json')
endpoint_url = load_s2_credentials("s2_credentials.json")[0]


#******************************************************************************
# Recieves a scan (string) and returns a tuple containing either the RFID scan 
# or ProxyClick QR code number formatted as a string in the 0th index and a 
# boolean value indicating what's in the 0th index. The 1st index contains True 
# if it's an RFID card scan and False if it's a QR code scan.
# If the input is invalid it will return None. 
def validate_input(scan: str) -> Union[Tuple[str, bool], None]:
    # Scan is a ProxyClick QR code.
    if len(scan) >= proxyclick_format['length'] and not scan.isnumeric():
        qr_code_hotstamp = ''
        qr_code_hotstamp = scan[ proxyclick_format['start'] : proxyclick_format['end'] ]

        # double checking that the QR code number is formatted correctly.
        if qr_code_hotstamp.isnumeric():
            return (qr_code_hotstamp, False)
        
        # Scan is not valid.
        else:
            return None
    
    # Scan is an RFID card scan.
    elif scan.isnumeric():
        return (scan, True)
    
    # Scan is not valid.
    else:
        return None
#******************************************************************************


#******************************************************************************
# Takes a valid session ID, and a hotstamp as arguments.
# Performs a post request to retrieve and return the PERSON dictionary if
# only one person is found and a list of dictionaries if multiple are
# found. This PERSON dictionary will contatin all the required data.
# If the post request fails it will return None.
#******************************************************************************
def get_person_with_hotstamp(session_id: str, hotstamp: str) -> Union[dict, None]:
    
    body = '''
        <NETBOX-API sessionid="{session_id}">
            <COMMAND name="SearchPersonData" num="1">
                <PARAMS>
                    <HOTSTAMP>{hotstamp}</HOTSTAMP>
                </PARAMS>
            </COMMAND>
        </NETBOX-API>
        '''.format(session_id=session_id, hotstamp=hotstamp)
    
    try:
        response = post(endpoint_url, body, verify=False)
        response = response.content.decode("utf8")
        response = xmltodict.parse(response)
        response = response['NETBOX']['RESPONSE']
                
        if response['CODE'] != 'SUCCESS':
            return None
        else: 
            return response['DETAILS']['PEOPLE']['PERSON']
    except:
        return None
#******************************************************************************


# Note!
# The following function is only defined for the wiegand 26 bit RFID card and
# tested on a select few. 

# Todo Todo Todo Todo Todo Todo Todo Todo Todo Todo Todo Todo Todo Todo Todo 
#******************************************************************************
# Recieves an RFID scan in the form of a decimal number as a string and 
# extracts the card format and hotstamp.
# It returns the card format and hotstamp both as a string and both in a tuple.
def extract_card_format_hotstamp(scan: str) -> Union[Tuple[str, str], None]:

    if scan:
        if len(scan) == 8:
            fc = scan[0:3]
            hotstamp = scan[3:]

            fc = str(int(fc))
            card_formats = card_formats_26_bit

            return (card_formats[fc], hotstamp)
        else:
            return (None, None)
    else:
        return (None, None)       
#******************************************************************************

            
#******************************************************************************
# This function recieves a dictionary of a passengers data obtained from 
# an API call. It extracts all the required data and returns it in a Passenger
# object.               
def get_passenger_details(passenger_data: dict, portal_id: str) -> Passenger:
    # Get the current date and time to compare with.
    current_date_time = datetime.datetime.now() 

    # Get the passengers name.
    passenger_name = passenger_data['FIRSTNAME'] + " " + passenger_data['LASTNAME']
    passenger_personID = passenger_data['PERSONID']
    # Get the passengers ID card (or visitor pass) activation date.
    passenger_activation_date = datetime.datetime.strptime(passenger_data['ACTDATE'], "%Y-%m-%d %H:%M:%S")

    # If it exists, get the passengers ID card (or visitor pass) expiration date.
    try:
        passenger_expiration_date = passenger_data['EXPDATE']
        passenger_expiration_date = datetime.datetime.strptime(passenger_data['EXPDATE'], "%Y-%m-%d %H:%M:%S")
    except:
        passenger_expiration_date = None

    # If the employees ID card (or visitor pass) activation date is in the future, deny access.
    if passenger_activation_date > current_date_time:
        passenger_access = False
    else:
        passenger_access = True
    # If the employees ID card (or visitor pass) has an expiration date check if it passed.
    if passenger_expiration_date:
        if passenger_expiration_date <= current_date_time:
            passenger_access = False

    return Passenger(passenger_access, passenger_name, portal_id, current_date_time,passenger_personID)
#******************************************************************************


#******************************************************************************
# Recieves either an RFID card number from the scanner or the encoded/hotstamp 
# from a ProxyClick QR code scan. Both as a string. Both in a tuple.
# The 0th index is the RFID card scan or the QR code scan formatted.
# The 1st index is a boolean indicating which one the 0th index is. 
# The 1st index is True for an RFID card scan, and False for a QR code scan.
# It returns an object of type Passenger which has the following attributes:
#   - access: a boolean indicating whether or not the passenger is authorized 
#           to ride the bus or not.
#   - date_time: a date object from the datetime module. it contains the date 
#                and time of the scan.
#   - name: a string containing the name of the passenger. Contains 'UNKNOWN' 
#           if the scan was invalid or not found.
#   - access_portal: a string identifying the bus portal where the passenger scanned 
#             thier credentials.
def get_eligibility(session_id: str, portal_id: str, input_scan: Union[Tuple[str, bool], None]) -> Passenger:

    # If input_scan isn't None, then it was a valid scan.
    if input_scan:
        # If the scan is a Proxyclick QR code.
        if input_scan[1] == False:
            # Recieves a dictionary of the visitors data.
            visitor = get_person_with_hotstamp(session_id, input_scan[0])
            
            if visitor:
                return get_passenger_details(visitor, portal_id)
            # If it failed to retrieve the person data.
            else:
                return Passenger(False, 'UNKNOWN', portal_id, datetime.datetime.now())
            
        # If the scan is an RFID scan.
        elif input_scan[1] == True:

            # Get the card format, and the hotstamp. 
            card_format, hotstamp = extract_card_format_hotstamp(input_scan[0])

            if card_format != None and hotstamp != None:
                hotstamp = str(int(hotstamp))
                employee_data = get_person_with_hotstamp(session_id, hotstamp)

                # If there's only one person.
                if type(employee_data) == dict:
                    return get_passenger_details(employee_data, portal_id)
                
                # If there're multiple PERSONs with that hotstamp.
                elif type(employee_data) == list:    
                    for employee in employee_data:
                        access_cards = employee['ACCESSCARDS']

                        # This employee has multiple cards.
                        if type(access_cards['ACCESSCARD']) == list:
                            for card in access_cards['ACCESSCARD']:
                                employee_card_format = card['CARDFORMAT']

                                # If this employees card format matches return.
                                if employee_card_format == card_format:
                                    return get_passenger_details(employee, portal_id)
                
                        # This employee has only one card.                                    
                        elif type(access_cards['ACCESSCARD']) == dict:
                            if access_cards['ACCESSCARD']['CARDFORMAT'] == card_format:
                                return get_passenger_details(employee, portal_id)

                    # A card format match could not be found.
                    return Passenger(False, 'UNKNOWN', portal_id, datetime.datetime.now())
            else:
                return Passenger(False, 'UNKNOWN', portal_id, datetime.datetime.now())
            
        # Unknown error occured.
        else:
            return Passenger(False, 'UNKNOWN', portal_id, datetime.datetime.now())

    # input_scan was not valid.
    else:
        return Passenger(False, 'UNKNOWN', portal_id, datetime.datetime.now())
#******************************************************************************


#******************************************************************************
# This function recieves a Passenger object containing the necessary details
# to be inserted into the s2 activity feed. The details are concatenated into
# a sting which is then inserted into the activity feed as a user-defined 
# activity text.
def insert_activity(session_id: str, passenger: Passenger, encodednum) -> str:
    
    if passenger.access:
          body = '''
                <NETBOX-API sessionid="{session_id}"> 
                    <COMMAND name="InsertActivity" num="1">
                        <PARAMS>
                            <ACTIVITYTYPE>ACCESSGRANTED</ACTIVITYTYPE>
                            <PORTALKEY>{portal_key}</PORTALKEY>
                            <PERSONID>{person_id}</PERSONID>
                            <READERKEY>{reader_key}</READERKEY>
                            <CARDFORMAT>{format}</CARDFORMAT>
                            <ENCODEDNUM>{encodednum}</ENCODEDNUM>
                        </PARAMS>
                    </COMMAND>
                </NETBOX-API>'''.format(session_id=session_id,
                                        person_id=passenger.personId,
                                        encodednum=encodednum,
                                        portal_key= passenger.access_portal)
                                        #reader_key = lastest_act['READERKEY'] # needs to be resolved ,
                                        #format =  ) #Use brian code here
    else:
    
        body = '''
                <NETBOX-API sessionid="{session_id}"> 
                    <COMMAND name="InsertActivity" num="1">
                        <PARAMS>
                            <ACTIVITYTYPE>ACCESSDENIED</ACTIVITYTYPE>
                            <DETAILS>TIME</DETAILS>
                            <PORTALKEY>{portal_key}</PORTALKEY>
                            <PERSONID>{person_id}</PERSONID>
                            <READERKEY>{reader_key}</READERKEY>
                            <CARDFORMAT>{format}</CARDFORMAT>
                            <ENCODEDNUM>{encodednum}</ENCODEDNUM>
                        </PARAMS>
                    </COMMAND>
                </NETBOX-API>'''.format(session_id=session_id,
                                        person_id=passenger.personId,
                                        encodednum=encodednum,
                                        portal_key= passenger.access_portal)
                                        #reader_key = lastest_act['READERKEY'] # needs to be resolved ,
                                        #format =  ) #Use brian code here
  
  
        
    response = post(endpoint_url, body, verify=False)
    response = response.content.decode("utf8")
    response = xmltodict.parse(response)
    response = response['NETBOX']['RESPONSE']['CODE']
    return response
#******************************************************************************