from functions import validate_input, get_eligibility, insert_activity
from passenger import Passenger
import datetime
import json
from login_logout_s2 import login, logout
from led import blink_green, blink_red

BUS_PORTAL = 'TEST_BUS'
config_file_path = '/home/scanner/bus_id_scanner/config.json'

#*******************************************************************************
def setup(config_json_path: str):
    # Get the sesion ID.
    session_id = login()

    with open(config_json_path) as config_json:
        config = json.load(config_json)
    
    s2_credentials = config['s2_credentials']
    credential_formats = config['credential_formats']
    portal_info = config['access_portals']
    operating_hours = config['operating_hours']

    # Get the operating days and hours
    start_hour = operating_hours['days_running_hours']['start'][0]
    start_min = operating_hours['days_running_hours']['start'][1]
    start_sec = operating_hours['days_running_hours']['start'][2]

    end_hour = operating_hours['days_running_hours']['end'][0]
    end_min = operating_hours['days_running_hours']['end'][1]
    end_sec = operating_hours['days_running_hours']['end'][2]

    shuttle_bus_operating_hours = {
        'start_day' : operating_hours['days_running_range'][0],
        'end_day' : operating_hours['days_running_range'][1],
        'start_time' : datetime.time(start_hour, start_min, start_sec),
        'end_time' : datetime.time(end_hour, end_min, end_sec)
    }

    # Get s2 endpoint
    s2_endpoint_url = s2_credentials['S2_HOSTNAME'] 

    # Get the portal and reader key info
    portal = {
        'portal_key' : portal_info[BUS_PORTAL]['portal_key'],
        'bc_reader_key' : portal_info[BUS_PORTAL]['readers']['bc_reader_key'],
        'rdr_reader_key' : portal_info[BUS_PORTAL]['readers']['rdr_reader_key']
    }
    
    # Shuttle bus schedule: Mon-Fri, 5:00-22:30

    return session_id, shuttle_bus_operating_hours, s2_endpoint_url, portal, credential_formats
#*******************************************************************************
    

#*******************************************************************************
def loop(session_id: str, s2_endpoint_url: str, portal: dict, credential_formats: dict) -> None:
        print(session_id)
        input_scan = input("Tap RFID card or scan QR code: ").strip()
        validated_scan = validate_input(input_scan, credential_formats)

        passenger_scan = get_eligibility(session_id, s2_endpoint_url, validated_scan, credential_formats, portal)
        insert_activity(session_id, s2_endpoint_url, passenger_scan, BUS_PORTAL)
        if passenger_scan.access:
            # Beep and set led to green for 2 seconds.
            # print("Green")
            blink_green(2)
        else:
            # Alt beep set led to green for 1.5 seconds.
            # print("Red")
            blink_red(1.5)
#*******************************************************************************


# Main
session_id, shuttle_bus_operating_hours, s2_endpoint_url, portal, credential_formats = setup(config_file_path)
# Gets an integer representing the current day of the week. 0 = Monday, 
# 1 = Tuesday, ..., 4 = Friday
weekday = datetime.datetime.today().weekday()

# Make sure the time zone is correct


# Signal for successful startup.
blink_green(0.25)
blink_red(0.25)

# Keep calling the loop function while it's a work day and between the 
# hours of 5:00AM to 10:30PM (22:30).
while (weekday >= shuttle_bus_operating_hours['start_day'] and weekday <= shuttle_bus_operating_hours['end_day']) and (datetime.datetime.now().time() >= shuttle_bus_operating_hours['start_time'] and datetime.datetime.now().time() < shuttle_bus_operating_hours['end_time']):
    try:
        loop(session_id, s2_endpoint_url, portal, credential_formats)
    # Add exception for shutdown.
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)
        continue
    # loop(session_id, s2_endpoint_url, portal, credential_formats) # Debugging purposes

logout(session_id)
print(f"\nSession id: {session_id} has been logged out.") # Debugging purposes
