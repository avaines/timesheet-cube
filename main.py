
import os
import pytz

from fastapi import FastAPI
from datetime import datetime, timedelta
from O365 import Account
import asyncio

app = FastAPI()

class Cube():
    def __init__(self, timezone):
        self.current_face = "off"
        self.start_time_of_face = pytz.timezone(timezone).localize(datetime.now())
        self.previous_face = "off"
        self.time_on_current_face = 0

        self.cube_face_map = {
            "one": os.getenv('CUBE_FACE_ONE',"1"),
            "two": os.getenv('CUBE_FACE_TWO',"2"),
            "three": os.getenv('CUBE_FACE_THREE',"3"),
            "four": os.getenv('CUBE_FACE_FOUR',"4"),
            "five": os.getenv('CUBE_FACE_FIVE',"5"),
            "six": os.getenv('CUBE_FACE_SIX',"6"),
        }

    def change_face(self, new_face):
        self.previous_face = self.current_face
        self.current_face = self.cube_face_map[new_face]

    def tick(self, minutes_elapsed: int):
        if self.previous_face == self.current_face:
            # Face has NOT changed since last time we checked
            self.time_on_current_face += minutes_elapsed
        else:
            # Face has changed since last time we checked
            self.time_on_current_face = 0
            self.start_time_of_face = pytz.timezone(timezone).localize(datetime.now())
            self.previous_face = self.current_face


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
    adjusted_start = original_start - timedelta(minutes = 2) # Make the window slightly wider

    query = calendar.new_query('start').greater_equal(adjusted_start)
    query.new('end').less_equal(new_end)
    query.chain('and').on_attribute('subject').contains(subject)

    # For somereason the example shows the get_event output as an itterable but it doesnt seem to work properly
    matching_events = [ event for event in calendar.get_events(query = query, include_recurring = False)]

    if len(matching_events) <1:
        print("Couldn't find a matching event, creating one")
        new_calendar_event(
            calendar = calendar,
            subject = "Focus was on: %s" % (TheCube.current_face),
            start = original_start,
            end = new_end,
        )
    else:
        for event in matching_events:
            print("Found '%s' starting at %s, extending out to %s" % ( event.attachment_name, original_start.strftime("%H:%M:%S"), new_end.strftime("%H:%M:%S")))
            event.end = new_end
            event.save()

async def tick(interval: int = 10):
    while True:
        # code to run periodically starts here
        TheCube.tick(int(interval))

        print(f"The '{TheCube.current_face}' face has been active for {TheCube.time_on_current_face} minutes, \
previously it was on the '{TheCube.previous_face}' face, sleeping for {interval} minute(s)")

        if TheCube.current_face.upper() != "OFF":
            if TheCube.current_face != TheCube.previous_face:
                print(f"New calendar entry for {TheCube.current_face}")
                # The Cube face has changed
                new_calendar_event(
                    calendar = calendar,
                    subject = "Focus was on: %s" % (TheCube.current_face),
                    start = TheCube.start_time_of_face,
                    end = pytz.timezone(timezone).localize(datetime.now()),
                )

            else:
                # The Cube Face has not changed since last tick
                print(f"Extending calendar entry for {TheCube.current_face}")
                extend_calendar_event(
                    calendar = calendar,
                    subject = "Focus was on: %s" % (TheCube.current_face),
                    original_start = TheCube.start_time_of_face - timedelta(minutes = int(interval)),
                    new_end = pytz.timezone(timezone).localize(datetime.now()),
                )

        # code to run periodically ends here
        await asyncio.sleep(int(interval) * 60)

# FastAPI Methods
@app.get("/")
async def root():
    return {
        "current_face": TheCube.current_face,
        "face_at_last_interval": TheCube.previous_face,
        "time_on_face": TheCube.time_on_current_face,
        "face_map": TheCube.cube_face_map,
    }

@app.post("/change")
async def change_face(new_face: str = "one"):
    TheCube.change_face(new_face)

    return {
        "new_face": TheCube.current_face,
        "face_at_last_interval": TheCube.previous_face,
    }

# Initialise backup process for looping and time management
@app.on_event("startup")
async def schedule_periodic():
    loop = asyncio.get_event_loop()
    loop.create_task(tick(tick_interval_minutes))


# Globals
timezone = 'Europe/London'
TheCube = Cube(timezone)
tick_interval_minutes = os.getenv("INTERVAL", 1)

account = o365_auth()
schedule = account.schedule(resource = os.getenv('CALENDAR_OWNER'))
calendar = schedule.get_calendar(calendar_name=os.getenv('CALENDAR_NAME'))

# Local Execution
if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    load_dotenv()

    required_env_vars = [
        "CALENDAR_NAME",
        "CALENDAR_OWNER",
        "CLIENT_ID",
        "CLIENT_SECRET",
        "TENANT_ID",
    ]

    for required_env_var in required_env_vars:
        missing_vars = []
        if os.getenv(required_env_var) is None:
            print("Environmental variable:", required_env_var, "unset")
            missing_vars.append(required_env_var)

        if len(missing_vars) > 0:
            raise RuntimeError("The environmental variables %s are missing" % (", ".join(missing_vars)))

        print("%s set to %s" % (required_env_var, os.environ.get(required_env_var)))

    uvicorn.run(app, host="0.0.0.0", port=8000)
