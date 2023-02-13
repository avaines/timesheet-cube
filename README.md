# timesheet-cube
A janky Timeular alternative using an Aqara cube and an Office365 calendar

I am not paying £70 for a bit of plastic and £10 a month to use it. But I would find some of the features, namely, a way of tracking which project I'm currently working on and for it to be historically referable. Ideally I would like it to magically fill in my timesheets for various clients automatically, but, I'm a realist and will settle for an Outlook calendar being populated for me.

I already have an Office 365 subscription with calendars and I don't mind spending £20 on AliExpress for some bits.


## Shopping list
1) An Aqara Cube: https://www.aliexpress.com/af/aqara-cube.html
2) A USB Zigbee gateway: https://www.aliexpress.com/af/usb-zigbee.html

## Setup
Create a new calendar
Create an Office365 Enterprise app with the calendar permissions identified in https://github.com/O365/python-o365#calendar
Populate a '.env' file in the root of this repo when cloned with the info for your calendar and EA
```
CALENDAR_NAME="YourNewCalendar"
CALENDAR_OWNER="yourname@domain.com"
CLIENT_ID="0000-0000-0000-0000-0000"
CLIENT_SECRET="000000000000"
TENANT_ID="0000-0000-0000-0000-0000"
```

Add some more to make things a bit more readable
```
INTERVAL=1
CUBE_FACE_ONE="OFF"
CUBE_FACE_TWO="label"
CUBE_FACE_THREE="label"
CUBE_FACE_FOUR="label"
CUBE_FACE_FIVE="label"
CUBE_FACE_SIX="label"
```

## Running it
> docker-compose -f docker-compose.yaml up --build
OR
> ./run-locally

## Using it
You should now have an API that accepts a 'new_face' query string to a 'change' endpoint, eg 127.0.0.1:8000/change?new_face=three.

In my setup I have a HomeAssistance container configured with a ZigBee network and the cube as a registered device. A helper <INSERTIMAGE>
stores the current value of the cube and a custom script for each 'face' triggers a curl to the new API

The blueprint is here: 'misc/homeassistant-automation.yaml'
the 'config/configuration.yaml' looks like
```
shell_command:
  flip_face_one: curl -s --request POST '192.168.111.200:8000/change?new_face=one'
  flip_face_two: curl -s --request POST '192.168.111.200:8000/change?new_face=two'
  flip_face_three: curl -s --request POST '192.168.111.200:8000/change?new_face=three'
  flip_face_four: curl -s --request POST '192.168.111.200:8000/change?new_face=four'
  flip_face_five: curl -s --request POST '192.168.111.200:8000/change?new_face=five'
  flip_face_six: curl -s --request POST '192.168.111.200:8000/change?new_face=six'
```
