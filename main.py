import os
import time
import pytz

from datetime import datetime, timedelta
from O365 import Account
from progress.bar import IncrementalBar


from dotenv import load_dotenv
load_dotenv()

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

def new_calendar_event(calendar, subject, start, end):
    new_event = calendar.new_event()
    new_event.subject = subject

    new_event.start = start
    new_event.end = end

    new_event.save()

def extend_calendar_event(calendar, subject, original_start, new_end):
    query = calendar.new_query('start').greater_equal(original_start)
    query.new('end').less_equal(new_end)
    query.chain('and').on_attribute('subject').contains(subject)

    # For somereason the example shows the get_event output as an itterable but it doesnt seem to work properly
    matching_events = [ event for event in calendar.get_events(query = query, include_recurring = False)]

    for event in matching_events:
        print("Found '%s' starting at %s, extending out to %s" % ( event.attachment_name, original_start.strftime("%H:%M:%S"), new_end.strftime("%H:%M:%S")))
        event.end = new_end
        event.save()

class Cube():
    def __init__(self, timezone):
        self.current_face = "off"
        self.start_time_of_face = pytz.timezone(timezone).localize(datetime.now())
        self.previous_face = "off"
        self.time_on_current_face = 0

        self.cube_face_map = {
            "one": "Engineering Leadership",
            "two": "Internal",
            "three": "Client",
            "four": "Off",
            "five": "Recruitment",
            "six": "personal",
        }

    def has_face_changed_in_the_last_x_minutes(self, minutes_elapsed):
        # TODO: Zigbee checks here
        # from random import randint
        # self.current_face = self.__cube_face_map[randint(1,6)]
        # self.previous_face = self.current_face
        # self.current_face = self.cube_face_map["four"]
        path_to_face_file = "./cur_face"

        if os.path.exists(path_to_face_file):
            self.previous_face = self.current_face

            with open(path_to_face_file) as f:
                face_from_file = [line.strip() for line in f.readlines()][0]

            self.cube_face_map[face_from_file]

            if self.previous_face == self.current_face:
                self.time_on_current_face += minutes_elapsed
                return False
            else:
                # print("Face has changed to", self.current_face)
                self.time_on_current_face = 0
                self.start_time_of_face = pytz.timezone(timezone).localize(datetime.now())
                return True


if __name__ == '__main__':
    tick_length_mins = 5 #15
    timezone = 'Europe/London'

    account = o365_auth()

    schedule = account.schedule(resource = os.getenv('CALENDAR_OWNER'))
    calendar = schedule.get_calendar(calendar_name=os.getenv('CALENDAR_NAME'))

    TheCube = Cube(timezone)

    while True:
        print("Checking cube faces...")

        if TheCube.has_face_changed_in_the_last_x_minutes(minutes_elapsed = tick_length_mins):
            print("Cube face has changed to %s, saving calendar event" % (TheCube.current_face))

            if TheCube.current_face != "Off":
                new_calendar_event(
                    calendar = calendar,
                    subject = "Focus was on: %s" % (TheCube.current_face),
                    start = TheCube.start_time_of_face,
                    end = pytz.timezone(timezone).localize(datetime.now()),
                )

        else:
            print("Cube face has not changed, its still %s, extending the event" % (TheCube.current_face))

            extend_calendar_event(
                calendar = calendar,
                subject = "Focus was on: %s" % (TheCube.current_face),
                original_start = TheCube.start_time_of_face - timedelta(minutes = 1),
                new_end = pytz.timezone(timezone).localize(datetime.now()),
            )

        for i in IncrementalBar("Sleeping for %s minutes" % (tick_length_mins), suffix='%(percent).0f%% (%(eta)ds)').iter(range(tick_length_mins * 60)):
            time.sleep(1)

        print()
