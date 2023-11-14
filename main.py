from functions import validate_input, get_eligibility, insert_activity
from passenger import Passenger
import datetime
import json
from login_logout_s2 import login, logout


#*******************************************************************************
def setup():
    # Get the sesion ID.
    session_id = login()
    portal_id = "TEST BUS PORTAL"

    # Get the shuttle bus start and end hours for that day.
    shuttle_bus_start_date_time = None
    shuttle_bus_end_date_time = None

    return session_id, portal_id, shuttle_bus_start_date_time, shuttle_bus_end_date_time
#*******************************************************************************
    

#*******************************************************************************
def loop(session_id: str, portal_id: str) -> None:
        print(session_id)
        input_scan = input("Tap RFID card or scan QR code: ").strip()
        validated_scan = validate_input(input_scan)

        passenger_scan = get_eligibility(session_id, portal_id, validated_scan)
        insert_activity(session_id, passenger_scan)
        if passenger_scan.access:
            # Beep and set led to green for 2 seconds.
            print("Green")
            pass
        else:
            # Alt beep set led to green for 1.5 seconds.
            print("Red")
            pass
#*******************************************************************************



# Main
session_id, portal_id, start_time, end_time = setup()

# Bus schedule: Mon-Fri, 5:00-22:30
weekday = datetime.datetime.today().weekday()
service_start_time = datetime.time(5, 0, 0)
service_end_time =  datetime.time(22, 30, 0)

while (weekday >= 0 and weekday <= 4) and (datetime.datetime.now().time() >= service_start_time and datetime.datetime.now().time() < service_end_time):
    # loop(session_id, portal_id)
    try:
        loop(session_id, portal_id)
    except Exception as e:
        print(e)
        break

logout(session_id)
