import os
import time

from datetime import datetime, timedelta
from dotenv import load_dotenv
from O365 import Account


def o365_auth():
    credentials = (
        os.getenv('CLIENT_ID'),
        os.getenv('CLIENT_SECRET'),
    )

    # account = Account(credentials)
    account = Account(
        credentials,
        auth_flow_type = 'credentials',
        tenant_id = os.getenv('TENANT_ID'),
    )

    if account.is_authenticated:
        print("Already authenticated")
        return account
    else:
        account.authenticate()
        print('Authenticated')
        return account

def new_calendar_event(calendar, start, end, subject):
    new_event = calendar.new_event()
    new_event.subject = subject

    new_event.start = start
    new_event.end = end

    new_event.save()

class Cube():
    def __init__(self):
        self.current_side = "off"
        self.time_on_current_side = 0

        self.__cube_side_map = {
            1 : "one",
            2 : "two",
            3 : "three",
            4 : "four",
            5 : "five",
            6 : "six",
        }

    def has_face_change(self):
        # Talk to the ZigBee interface, get the current side
        print("Previous side was", self.current_side)

        # TODO: Zigbee checks here
        from random import randint
        new_side = self.__cube_side_map[randint(1,6)]

        if new_side == self.current_side:
            print("Side hasn't changed, it's still", self.current_side)
            return False
        else:
            print("New side is", new_side)
            self.current_side = new_side
            return True


if __name__ == '__main__':
    load_dotenv()

    account = o365_auth()

    schedule = account.schedule(resource = os.getenv('CALENDAR_OWNER'))
    calendar = schedule.get_calendar(calendar_name=os.getenv('CALENDAR_NAME'))

    TheCube = Cube()

    while True:
        print("Checking cube sides")
        if TheCube.has_face_change():
            print("Saving new calendar event")

            new_calendar_event(
                calendar = calendar,
                subject = "Billing for: %s" % (TheCube.current_side),
                start = datetime.now() - timedelta(minutes = TheCube.time_on_current_side),
                end = datetime.now(),
            )

        for i in range(10):
            print("sleeping", 10 - i, "minutes")
            time.sleep(60)


    print()
