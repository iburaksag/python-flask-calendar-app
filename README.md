# Python Flask Calendar App

> #python #flask #googlecloud #appengine #datastore #firebase #html #css #bootstrap

In this assignment I built a calendar application that will be capable of storing events for a user on any given day. It will also be possible to share events with other users. It should be possible for a user to schedule events in any given day. If an event is to be shared with multiple users it should be possible to find a common free time on their shared calendars to prevent overlap.<br><br>
This assignment required me to use a many to many relationship between calendars and events. A calendar can only belong to one user but can be shared amongst users. An event can belong to one or more calendars. Please check the Assignment folder for more details.<br><br>
In this project, you need to use firebase for authentication purposes. This will keep track of user/password combinations. 
For setting up Firebase, check out the link:
https://console.firebase.google.com/u/0/

## Getting Started 🏁

First before we can start with anything we will need to create a python virtual environment as we will need to install things into it without messing with the local python environment. In the project directory, you can run:

### `python3 -m venv env`

After this we will need to run the following command:

### `source env/bin/activate`

Make sure you have created your environment and sourced it as shown above and run the following command:

### `pip install -r requirements.txt`

Before you go to run this project you will need the JSON file nearby to access the datastore. Before you run your application in your command line you will need to set the session variable GOOGLE_APPLICATION_CREDENTIALS with the location of this JSON file.

### `export GOOGLE_APPLICATION_CREDENTIALS=”../app-engine-3-testing.json”`

Run your application by executing the following command:
 
### `python main.py`
