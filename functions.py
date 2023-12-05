import json
import string
import urllib3
import datetime
import xmltodict
from typing import Union, Tuple
from requests import post
from passenger import Passenger

urllib3.disable_warnings()


#******************************************************************************
# Recieves a scan (string), credential formats (dict), and returns a tuple containing either the RFID scan
# or ProxyClick QR code number formatted as a string in the 0th index and a
# boolean value indicating what's in the 0th index. The 1st index contains True
# if it's an RFID card scan and False if it's a QR code scan.
# If the input is invalid it will return None.
def validate_input(scan: str, credential_formats: dict) -> Union[Tuple[str, bool], None]:
    # Scan is a ProxyClick QR code.
    if len(scan) >= credential_formats['PROXYCLICK']['length'] and not all(c in string.hexdigits for c in scan):
        qr_code_hotstamp = ''
        qr_code_hotstamp = scan[ credential_formats['PROXYCLICK']['start'] : credential_formats['PROXYCLICK']['end'] ]

        # double checking that the QR code number is formatted correctly.
        if qr_code_hotstamp.isnumeric():
            return (qr_code_hotstamp, False)

        # Scan is not valid.
        else:
            return None

    # Scan is an RFID card scan.
    elif all(c in string.hexdigits for c in scan):
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
def get_person_with_hotstamp(session_id: str, s2_endpoint_url: str, hotstamp: str) -> Union[dict, list, None]:

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
        response = post(s2_endpoint_url, body, verify=False)
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


#******************************************************************************
# Recieves an RFID scan in the form of a hexadecimal number as a string and
# extracts the card format and hotstamp.
# It returns the card format and hotstamp both as a string in a tuple.
def extract_card_format_hotstamp(scan: str, credential_formats: dict) -> Union[Tuple[str, str], None]:

    # If the scan was valid.
    if scan:
        # The scan will contain a hex number where the first two digits
        # represent the cards bit length. This will be campared to a
        # dictionary where the key is a string of the length. Hence str().
        bit_length = str( int( scan[0:2], 16 ))
        # Convert the scan to binary and remove the '0b' in the front for
        # easier processing.
        card_bits = bin( int( scan[2:], 16 ))
        card_bits_in_binary = card_bits[2:]

        # Loop through the credential formats to find the matching bit length.
        for length, formats in credential_formats.items():

            if length == bit_length:

                for format in formats:
                    format_facility_code = formats[format]['FACILITY_CODE']
                    card_facility_code = card_bits_in_binary[ formats[format]['FC_START'] : formats[format]['FC_END'] ]
                    if card_facility_code != '':
                        card_facility_code = int(card_facility_code, 2)

                    if card_facility_code == format_facility_code:
                        encodedd_num = card_bits_in_binary[ formats[format]['ENCODED_NUM_START'] : formats[format]['ENCODED_NUM_END'] ]
                        encodedd_num = int(encodedd_num, 2)

                        return (format, encodedd_num)
    return (None, None)
#******************************************************************************


#******************************************************************************
# This function recieves a dictionary of a passengers data obtained from
# an API call. It extracts all the required data and returns it in a Passenger
# object.
def get_passenger_details(passenger_data: dict, passenger_id_number: str, passenger_card_format: str, passenger_encoded_number: str, credential_formats: dict, portal: dict) -> Passenger:

    # Get the passengers ID card (or visitor pass) activation date.
    passenger_activation_date = datetime.datetime.strptime(passenger_data['ACTDATE'], "%Y-%m-%d %H:%M:%S")

    # If it exists, get the passengers ID card (or visitor pass) expiration date.
    try:
        passenger_expiration_date = passenger_data['EXPDATE']
        passenger_expiration_date = datetime.datetime.strptime(passenger_data['EXPDATE'], "%Y-%m-%d %H:%M:%S")
    except:
        passenger_expiration_date = None

    # Make sure the time zone is correct.
    current_date_time = datetime.datetime.now()

    # If the employees ID card (or visitor pass) activation date is in the future, deny access.
    if passenger_activation_date > current_date_time:
        passenger_access = False
    else:
        passenger_access = True
    # If the employees ID card (or visitor pass) has an expiration date check if it passed.
    if passenger_expiration_date:
        if passenger_expiration_date <= current_date_time:
            passenger_access = False
    
    # Check for proxy click qr code format and assign the appropriate reader key.
    if passenger_card_format == 'Proxyclick QR code':
        reader_key = portal['bc_reader_key']
    else:
        reader_key = portal['rdr_reader_key']
    portal_key = portal['portal_key']

    return Passenger(passenger_access, portal_key, reader_key, passenger_id_number, passenger_card_format, passenger_encoded_number)
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
def get_eligibility(session_id: str, s2_endpoint_url: str, input_scan: Union[Tuple[str, bool], None], credential_formats: dict, portal: dict) -> Passenger:

    # If input_scan isn't None, then it was a valid scan.
    if input_scan:
        # If the scan is a Proxyclick QR code.
        if input_scan[1] == False:
            # Recieves a dictionary of the visitors data.
            visitor = get_person_with_hotstamp(session_id, s2_endpoint_url, input_scan[0])

            if visitor:
                return get_passenger_details(visitor, visitor['PERSONID'], visitor['ACCESSCARDS']['ACCESSCARD']['CARDFORMAT'], visitor['ACCESSCARDS']['ACCESSCARD']['ENCODEDNUM'], credential_formats, portal)
            # If it failed to retrieve the person data.
            else:
                return Passenger(False, None, None, None, None, None)

        # If the scan is an RFID scan.
        elif input_scan[1] == True:
            # Get the card format, and the hotstamp.
            card_format, hotstamp = extract_card_format_hotstamp(input_scan[0], credential_formats)

            if card_format != None and hotstamp != None:
                hotstamp = str(int(hotstamp))
                employee_data = get_person_with_hotstamp(session_id, s2_endpoint_url, hotstamp)

                # If there's only one person.
                if type(employee_data) == dict:

                    # If they have only one access card.
                    if type(employee_data['ACCESSCARDS']['ACCESSCARD']) == dict:
                        if employee_data['ACCESSCARDS']['ACCESSCARD']['CARDFORMAT'] == card_format:
                            return get_passenger_details(employee_data, employee_data['PERSONID'], card_format, employee_data['ACCESSCARDS']['ACCESSCARD']['ENCODEDNUM'], credential_formats, portal)
                        else:
                            return Passenger(False, None, None, None, None, None)
                        
                    # If they have multiple access cards.
                    elif type(employee_data['ACCESSCARDS']['ACCESSCARD']) == list:
                        for access_card in employee_data['ACCESSCARDS']['ACCESSCARD']:
                            if access_card['CARDFORMAT'] == card_format:
                                return get_passenger_details(employee_data, employee_data['PERSONID'], card_format, access_card['ENCODEDNUM'], credential_formats, portal)
                        return Passenger(False, None, None, None, None, None)
                    else:
                        return Passenger(False, None, None, None, None, None)

                # If there're multiple PERSONs with that hotstamp.
                elif type(employee_data) == list:
                    for employee in employee_data:
                        access_cards = employee['ACCESSCARDS']

                        # This employee has multiple cards.
                        if type(employee['ACCESSCARDS']['ACCESSCARD']) == list:
                            for access_card in employee['ACCESSCARDS']['ACCESSCARD']:
                                
                                # If this employees card format matches return.
                                if access_card['CARDFORMAT'] == card_format:
                                    return get_passenger_details(employee, employee['PERSONID'], card_format, access_card['ENCODEDNUM'], credential_formats, portal)
                                    #return get_passenger_details(employee, credential_formats, portal)
                                

                        # This employee has only one card.
                        elif type(employee['ACCESSCARDS']['ACCESSCARD']) == dict:
                            if employee['ACCESSCARDS']['ACCESSCARD']['CARDFORMAT'] == card_format:
                                return get_passenger_details(employee, employee['PERSONID'], card_format, employee['ACCESSCARDS']['ACCESSCARD']['ENCODEDNUM'], credential_formats, portal)
                                #return get_passenger_details(employee, credential_formats, portal)

                    # A card format match could not be found.
                    return Passenger(False, None, None, None, None, None)
                else:
                    return Passenger(False, None, None, None, None, None)
            else:
                return Passenger(False, None, None, None, None, None)

        # Unknown error occured.
        else:
            return Passenger(False, None, None, None, None, None)

    # input_scan was not valid.
    else:
        return Passenger(False, None, None, None, None, None)
#******************************************************************************


#******************************************************************************
# This function recieves a Passenger object containing the necessary details
# to be inserted into the s2 activity feed. The details are concatenated into
# a sting which is then inserted into the activity feed as a user-defined
# activity text.
def insert_activity(session_id: str, endpoint_url: str, passenger: Passenger, bus_portal: str) -> None:

    if passenger.access:
        body = '''
            <NETBOX-API sessionid="{session_id}">
                <COMMAND name="InsertActivity" num="1">
                    <PARAMS>
                        <ACTIVITYTYPE>ACCESSGRANTED</ACTIVITYTYPE>
                        <PORTALKEY>{portal_key}</PORTALKEY>
                        <READERKEY>{reader_key}</READERKEY>
                        <PERSONID>{person_id}</PERSONID>
                        <CARDFORMAT>{card_format}</CARDFORMAT>
                        <ENCODEDNUM>{encoded_num}</ENCODEDNUM>
                    </PARAMS>
                </COMMAND>
            </NETBOX-API>
        '''.format(
            session_id=session_id,
            portal_key=passenger.portal_key,
            reader_key=passenger.reader_key,
            person_id=passenger.person_id,
            card_format=passenger.card_format,
            encoded_num=passenger.hotstamp
            )
    elif passenger.access == False and passenger.hotstamp != None:
        body = '''
            <NETBOX-API sessionid="{session_id}">
                <COMMAND name="InsertActivity" num="1">
                    <PARAMS>
                        <ACTIVITYTYPE>ACCESSDENIED</ACTIVITYTYPE>
                        <DETAILS>UNKNOWN</DETAILS>
                        <PORTALKEY>{portal_key}</PORTALKEY>
                        <READERKEY>{reader_key}</READERKEY>
                        <PERSONID>{person_id}</PERSONID>
                        <CARDFORMAT>{card_format}</CARDFORMAT>
                        <ENCODEDNUM>{encoded_num}</ENCODEDNUM>
                    </PARAMS>
                </COMMAND>
            </NETBOX-API>
        '''.format(
            session_id=session_id,
            portal_key=passenger.portal_key,
            reader_key=passenger.reader_key,
            person_id=passenger.reader_key,
            encoded_num=passenger.hotstamp
            )
    else:
        body = '''
            <NETBOX-API sessionid="{session_id}">
                <COMMAND name="InsertActivity" num="1">
                    <PARAMS>
                        <ACTIVITYTYPE>USERACTIVITY</ACTIVITYTYPE>
                        <ACTIVITYTEXT>UNKNOW ACCESS ATTEMPT at {bus_portal}</ACTIVITYTEXT>
                    </PARAMS>
                </COMMAND>
            </NETBOX-API>
        '''.format(session_id=session_id, bus_portal=bus_portal)

    try:
        response = post(endpoint_url, body, verify=False)
        response = response.content.decode("utf8")
        response = xmltodict.parse(response)
        response = response['NETBOX']['RESPONSE']
    except:
        return None
#******************************************************************************