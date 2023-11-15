from functions import validate_input, get_eligibility, insert_activity
from passenger import Passenger
import datetime
import json
from login_logout_s2 import login, logout
from led import blink_green, blink_red

#*******************************************************************************
def setup():
    # Get the sesion ID.
    session_id = login()
    portal_id = "TEST BUS PORTAL"

    # Shuttle bus start and end hours for weekdays.
    # Bus schedule: Mon-Fri, 5:00-22:30
    shuttle_bus_start_date_time = datetime.time(5, 0, 0)
    shuttle_bus_end_date_time = datetime.time(22, 30, 0)

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
            blink_green(2)
            print("Green")
        else:
            # Alt beep set led to green for 1.5 seconds.
            blink_red(1.5)
            print("Red")
#*******************************************************************************



# Main
session_id, portal_id, service_start_time, service_end_time = setup()
# Gets an integer representing the current day of the week. 0 = Monday, 
# 1 = Tuesday, ..., 4 = Friday
weekday = datetime.datetime.today().weekday()

# Keep calling the loop function while it's a work day and between the 
# hours of 5:00AM to 10:30PM (22:30).
while (weekday >= 0 and weekday <= 4) and (datetime.datetime.now().time() >= service_start_time and datetime.datetime.now().time() < service_end_time):
    try:
        loop(session_id, portal_id)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)
        break

logout(session_id)
print(f"\nSession id: {session_id} has been logged out.")
