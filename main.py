from datetime import datetime, date, timedelta
import google.oauth2.id_token
import random, time
from flask import Flask, render_template, url_for, request, redirect
from google.cloud import datastore
from google.auth.transport import requests

app = Flask(__name__)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

#USER
def retrieveUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore_client.get(entity_key)
    return entity

def createUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'email': claims['email'],
        'name': claims['name'],
        'calendarList': []
    })
    datastore_client.put(entity)

def getUserByEmail(email):
    query = datastore_client.query(kind='UserInfo')
    query.add_filter('email', '=', email)
    result = list(query.fetch())
    return result[0]

def getAllUsers():
    query = datastore_client.query(kind='UserInfo')
    result = list(query.fetch())
    return result

#EVENT
def retrieveEvent(id):
    entity_key = datastore_client.key('EventInfo', id)
    entity = datastore_client.get(entity_key)
    return entity

def createEvent(name, eventDate, startTime, endTime, notes):
    id = random.getrandbits(63)

    entity_key = datastore_client.key('EventInfo', id)
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'name': name,
        'eventDate': eventDate,
        'startTime': startTime,
        'endTime' : endTime,
        'notes' : notes,
        'clashesWith' : []
    })
    datastore_client.put(entity)
    return entity

def updateEventInfo(id, name, eventDate, startTime, endTime, notes):
    entity_key = datastore_client.key('EventInfo', id)
    entity = datastore_client.get(entity_key)
    entity.update({
        'name': name,
        'eventDate': eventDate,
        'startTime': startTime,
        'endTime' : endTime,
        'notes' : notes
    })
    datastore_client.put(entity)


def addEventClashes(new_event_entity, clashes_event_entity):
    clashesWithList = new_event_entity['clashesWith']

    if clashes_event_entity.id not in clashesWithList:
        clashesWithList.append(clashes_event_entity.id)
    new_event_entity.update({
        'clashesWith': clashesWithList
    })
    datastore_client.put(new_event_entity)

    new_event_entity = retrieveEvent(new_event_entity.id)
    clashes_event_clashesWithList = clashes_event_entity['clashesWith']
    if new_event_entity.id not in clashes_event_clashesWithList:
        clashes_event_clashesWithList.append(new_event_entity.id)
    clashes_event_entity.update({
        'clashesWith': clashes_event_clashesWithList
    })
    datastore_client.put(clashes_event_entity)

def updateEventClashes(updated_event_entity, clashes_event_entity):
    clashesWithList = updated_event_entity['clashesWith']
    if clashes_event_entity.id not in clashesWithList and updated_event_entity.id != clashes_event_entity.id:
        clashesWithList.append(clashes_event_entity.id)

    updated_event_entity.update({
        'clashesWith': clashesWithList
    })
    datastore_client.put(updated_event_entity)

    updated_event_entity = retrieveEvent(updated_event_entity.id)
    clashes_event_clashesWithList = clashes_event_entity['clashesWith']
    if updated_event_entity.id not in clashes_event_clashesWithList and updated_event_entity.id != clashes_event_entity.id:
        clashes_event_clashesWithList.append(updated_event_entity.id)
    clashes_event_entity.update({
        'clashesWith': clashes_event_clashesWithList
    })
    datastore_client.put(clashes_event_entity)


def removeClashesBetweenTwoEvent(event_one_entity, event_two_entity):
    one_clashesWithList = event_one_entity['clashesWith']
    if event_two_entity.id in one_clashesWithList:
        one_clashesWithList.remove(event_two_entity.id)
    event_one_entity.update({
        'clashesWith': one_clashesWithList
    })
    datastore_client.put(event_one_entity)

    event_one_entity = retrieveEvent(event_one_entity.id)
    two_clashesWithList = event_two_entity['clashesWith']
    if event_one_entity.id in two_clashesWithList:
        two_clashesWithList.remove(event_one_entity.id)
    event_two_entity.update({
        'clashesWith': two_clashesWithList
    })
    datastore_client.put(event_two_entity)

def removeEventClashes(removed_event_entity, clashes_event_entity):
    clashes_event_clashesWithList = clashes_event_entity['clashesWith']
    if removed_event_entity.id in clashes_event_clashesWithList:
        clashes_event_clashesWithList.remove(removed_event_entity.id)
    clashes_event_entity.update({
        'clashesWith': clashes_event_clashesWithList
    })
    datastore_client.put(clashes_event_entity)

def deleteEventInfo(id):
    event_info_key = datastore_client.key('EventInfo', id)
    datastore_client.delete(event_info_key)

#CALENDAR
def retrieveCalendar(id):
    entity_key = datastore_client.key('CalendarInfo', id)
    entity = datastore_client.get(entity_key)
    return entity


def createCalendar(name, createdDay, createdMonth, createdYear, email):
    id = random.getrandbits(63)

    entity_key = datastore_client.key('CalendarInfo', id)
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'name': name,
        'createdDay': createdDay,
        'createdMonth': createdMonth,
        'createdYear': createdYear,
        'user' : email,
        'shared_users' : {}
    })
    datastore_client.put(entity)
    return entity


def updateCalendarInfo(id, name):
    entity_key = datastore_client.key('CalendarInfo', id)
    entity = datastore_client.get(entity_key)
    entity.update({
        'name': name
    })
    datastore_client.put(entity)

def updateUserCalendarList(user_entity, old_calendar_entity, new_calendar_name):
    new_calendar_entity = getCalendarByName(new_calendar_name)

    deleteCalendarFromUserCalendarList(user_entity, old_calendar_entity)
    addCalendarToUser(user_entity, new_calendar_entity)


def deleteCalendarInfo(id):
    calendar_info_key = datastore_client.key('CalendarInfo', id)
    datastore_client.delete(calendar_info_key)

def deleteCalendarFromUserCalendarList(user_entity, calendar_entity):
    userCalendarList = user_entity['calendarList']
    print(userCalendarList)
    if calendar_entity in userCalendarList:
        userCalendarList.remove(calendar_entity)

    user_entity.update({
        'calendarList': userCalendarList
    })

    datastore_client.put(user_entity)

#CALENDAR-EVENT
def createCalendarEvent(calendar, event):
    id = random.getrandbits(63)
    entity_key = datastore_client.key('CalendarEventInfo', id)
    entity = datastore.Entity(key = entity_key)

    entity.update({
        'calendarId': calendar.id,
        'eventId': event.id
    })
    datastore_client.put(entity)

def deleteCalendarEventInfoByCalendar(calendarId):
    query = datastore_client.query(kind='CalendarEventInfo')
    query.add_filter('calendarId', '=', calendarId)
    calendarEvent_list = list(query.fetch())

    for calendarEvent in calendarEvent_list:
        calendarEvent_info_key = datastore_client.key('CalendarEventInfo', calendarEvent.id)
        datastore_client.delete(calendarEvent_info_key)


def deleteCalendarEventInfoByEvent(eventId):
    query = datastore_client.query(kind='CalendarEventInfo')
    query.add_filter('eventId', '=', eventId)
    calendarEvent_list = list(query.fetch())

    for calendarEvent in calendarEvent_list:
        calendarEvent_info_key = datastore_client.key('CalendarEventInfo', calendarEvent.id)
        datastore_client.delete(calendarEvent_info_key)


def addCalendarToUser(user_entity, calendar_entity):
    calendarList = user_entity['calendarList']
    calendarList.append(calendar_entity)
    user_entity.update({
        'calendarList': calendarList
    })
    datastore_client.put(user_entity)

def getCalendarListForUser(user_info):
    query = datastore_client.query(kind='CalendarInfo')
    query.add_filter('user', '=', user_info['email'])
    result = list(query.fetch())
    return result


def getAllEvents():
    query = datastore_client.query(kind='EventInfo')
    result = list(query.fetch())
    return result

def getAllEventsByCalendar(calendarId):
    eventList = []
    query = datastore_client.query(kind='CalendarEventInfo')
    query.add_filter('calendarId', '=', calendarId)
    result = list(query.fetch())

    for calendarEventEntity in result:
        eventList.append(retrieveEvent(calendarEventEntity['eventId']))

    return eventList


def getEventForDate(date):
    query = datastore_client.query(kind='EventInfo')
    query.add_filter('eventDate', '=', date)
    result = list(query.fetch())
    return result

def getAllCalendars():
    query = datastore_client.query(kind='CalendarInfo')
    result = list(query.fetch())
    return result

def getCalendarByName(name):
    query = datastore_client.query(kind='CalendarInfo')
    query.add_filter('name', '=', name)
    result = list(query.fetch())
    return result[0]

def getAllSharedCalendars():
    query = datastore_client.query(kind='CalendarInfo')
    query.add_filter('shared_users', '!=', {})
    result = list(query.fetch())
    return result

def shareCalendarWithUser(calendar_entity, shared_user_entity):
    #dicValue = { shared_user_entity['email']: False }
    calendar_entity['shared_users'][shared_user_entity['email']] = False
    datastore_client.put(calendar_entity)

def getSharedCalendarRequestsForTheUser(user_entity):
    sharedCalendars = []
    allCalendars = getAllCalendars()
    user_email = user_entity['email']

    for calendar in allCalendars:
        shared_users = calendar.get('shared_users', {})
        if user_email in shared_users and shared_users[user_email] == False:
            sharedCalendars.append(calendar)

    return sharedCalendars


def checkCalendarNameInDatastore(calendar_name):
    calendarNameList = []
    calendars = getAllCalendars()
    for calendar in calendars:
        calendarNameList.append(calendar['name'])

    if calendar_name in calendarNameList:
        return True
    else:
        return False

@app.route('/calendar/<int:calendarId>/<string:weekCount>', methods=['GET', 'POST'])
def calendar(calendarId, weekCount):
    id_token = request.cookies.get("token")
    error_message = None
    user_info = None
    dates = {}
    current_date = datetime.now().date()
    intWeekCount = int(weekCount)
    eventList = getAllEventsByCalendar(calendarId)

    if id_token:
        if request.method == "POST":
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                user_info = retrieveUserInfo(claims)
                calendarName = retrieveCalendar(calendarId)['name']

                if intWeekCount > 0:
                    last_date = current_date + timedelta(days = intWeekCount * 7)
                    for i in range(7):
                        date = (last_date + timedelta(days=i)).strftime("%d-%m-%Y")
                        dayName = (last_date + timedelta(days=i)).strftime("%A")
                        dates[date] = dayName

                elif intWeekCount == 0:
                    for i in range(7):
                        date = (current_date + timedelta(days=i)).strftime("%d-%m-%Y")
                        dayName = (current_date + timedelta(days=i)).strftime("%A")
                        dates[date] = dayName

                else:
                    last_date = current_date - timedelta(days = abs(intWeekCount) * 7)
                    for i in range(7):
                        date = (last_date - timedelta(days=i)).strftime("%d-%m-%Y")
                        dayName = (last_date - timedelta(days=i)).strftime("%A")
                        dates[date] = dayName

            except ValueError as exc:
                error_message = str(exc)
        else:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                user_info = retrieveUserInfo(claims)
                calendarName = retrieveCalendar(calendarId)['name']

                for i in range(7):
                    date = (current_date + timedelta(days=i)).strftime("%d-%m-%Y")
                    dayName = (current_date + timedelta(days=i)).strftime("%A")
                    dates[date] = dayName


            except ValueError as exc:
                error_message = str(exc)
    return render_template('calendar.html', user_info = user_info, calendarId = calendarId, calendarName = calendarName, dates = dates, weekCount = str(intWeekCount), eventList = eventList, error_message=error_message)

@app.route("/add_event/<int:calendarId>/<string:date>", methods=['GET', 'POST'])
def add_event(calendarId, date):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    hours = []
    eventList = getAllEventsByCalendar(calendarId)

    if id_token:
        if request.method == "POST":
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                if request.form.get('event_start') >= request.form.get('event_end'):
                    raise Exception("Sorry, start time should be later than end time!")
                else:
                    calendar_entity = retrieveCalendar(calendarId)
                    event_entity = createEvent(request.form['name'], date, request.form['event_start'], request.form['event_end'], request.form['notes'])
                    createCalendarEvent(calendar_entity, event_entity)

                    for event in eventList:
                        if (event['eventDate'] == event_entity['eventDate']) and (event_entity['startTime'] < event['endTime'] and event_entity['endTime'] > event['startTime']):
                            addEventClashes(event_entity, event)

            except ValueError as exc:
                error_message = str(exc)
            return redirect(url_for('calendar', calendarId = calendarId, weekCount = "0"))
        else:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            calendar = retrieveCalendar(calendarId)

            for hour in range(0, 24):
                for minute in range(0, 60, 15):
                    time_str = f"{hour:02d}:{minute:02d}"
                    hours.append(time_str)

            return render_template('add_event.html', calendar = calendar, date=date, hours = hours, user_info = user_info, error_message=error_message)

    return render_template('index.html', user_info = user_info, error_message=error_message)

@app.route("/event_info/<int:calendarId>/<int:eventId>")
def event_info(calendarId, eventId):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    hours = []

    if id_token:
        claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        user_info = retrieveUserInfo(claims)
        event_entity = retrieveEvent(eventId)

        for hour in range(0, 24):
            for minute in range(0, 60, 15):
                time_str = f"{hour:02d}:{minute:02d}"
                hours.append(time_str)

    return render_template('event_info.html', calendarId = calendarId, hours = hours, event = event_entity, user_info = user_info, error_message=error_message)


@app.route('/edit_event_info/<int:calendarId>/<int:eventId>', methods=['POST'])
def edit_event_info(calendarId, eventId):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    event_entity = retrieveEvent(eventId)
    eventList = getAllEventsByCalendar(calendarId)

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

            if request.form.get('start_time_update') >= request.form.get('end_time_update'):
                raise Exception("Sorry, start time should be later than end time!")
            else:
                if request.form['name_update']:
                    new_eventName = request.form['name_update']
                else:
                    new_eventName = event_entity['name']

                if request.form.get('start_time_update') != event_entity['startTime']:
                    new_startTime = request.form.get('start_time_update')
                else:
                    new_startTime = event_entity['startTime']

                if request.form.get('end_time_update') != event_entity['endTime']:
                    new_endTime = request.form.get('end_time_update')
                else:
                    new_endTime = event_entity['endTime']

                if request.form['notes']:
                    new_notes = request.form['notes']
                else:
                    new_notes = event_entity['notes']

                for event in eventList:
                    if (event['eventDate'] == event_entity['eventDate']) and (new_startTime < event['endTime'] and new_endTime > event['startTime']):
                        updateEventClashes(event_entity, event)
                    else:
                        removeClashesBetweenTwoEvent(event_entity, event)

                updateEventInfo(eventId, new_eventName, event_entity['eventDate'] , new_startTime, new_endTime, new_notes)
        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for('calendar', calendarId = calendarId, weekCount = "0"))

@app.route('/delete_event_info/<int:calendarId>/<int:eventId>', methods=['POST'])
def delete_event_info(calendarId, eventId):
    id_token = request.cookies.get("token")
    error_message = None
    event_entity = retrieveEvent(eventId)
    eventList = getAllEventsByCalendar(calendarId)

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            for event in eventList:
                removeEventClashes(event_entity, event)
            deleteEventInfo(eventId)
            deleteCalendarEventInfoByEvent(eventId)



        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for('calendar', calendarId = calendarId, weekCount = "0"))

@app.route('/chooseCalendar', methods=['GET', 'POST'])
def chooseCalendar():
    id_token = request.cookies.get("token")
    error_message = None
    user_info = None
    weekCount = "0"

    if id_token:
        if request.method == "GET":
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                user_info = retrieveUserInfo(claims)
                calendar_list = user_info['calendarList']

                if len(calendar_list) > 1:
                    return render_template('chooseCalendar.html', user_info = user_info, calendar_list = calendar_list, error_message=error_message)
                else:
                    if len(calendar_list) == 0:
                        currentDay = datetime.now().day
                        currentMonth = datetime.now().month
                        currentYear = datetime.now().year

                        calendar_entity = createCalendar('Default', currentDay, currentMonth, currentYear, claims['email'])
                        addCalendarToUser(retrieveUserInfo(claims), calendar_entity)
                        calendarId = calendar_entity.id
                        return redirect(url_for('calendar', calendarId = calendarId, weekCount = weekCount))
                    else:
                        defaultCalendar = calendar_list[0]
                        return redirect(url_for('calendar', calendarId = defaultCalendar.id, weekCount = weekCount))
            except ValueError as exc:
                error_message = str(exc)
        else:
            calendarName = request.form.get('calendar')
            calendar_entity = getCalendarByName(calendarName)
            return redirect(url_for('calendar', calendarId = calendar_entity.id, weekCount = weekCount))

@app.route("/add_calendar", methods=['GET', 'POST'])
def add_calendar():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token and request.method == "POST":
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            calendarName = request.form['name']

            if calendarName:
                isNameExist = checkCalendarNameInDatastore(calendarName)
                if isNameExist:
                    raise Exception("Sorry, the calendar name is already exist!")
                else:
                    currentDay = datetime.now().day
                    currentMonth = datetime.now().month
                    currentYear = datetime.now().year

                    calendar_entity = createCalendar(calendarName, currentDay, currentMonth, currentYear, claims['email'])
                    addCalendarToUser(retrieveUserInfo(claims), calendar_entity)
                    calendarId = calendar_entity.id
        except ValueError as exc:
            error_message = str(exc)
        return redirect(url_for('calendar', calendarId = calendarId, weekCount = "0"))
    else:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
        return render_template('add_calendar.html', error_message=error_message)

@app.route("/calendar_info/<int:calendarId>")
def calendar_info(calendarId):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        user_info = retrieveUserInfo(claims)
        calendar_entity = retrieveCalendar(calendarId)

    return render_template('calendar_info.html', calendar = calendar_entity, calendarId = calendarId, user_info = user_info, error_message=error_message)


@app.route('/delete_calendar_info/<int:calendarId>', methods=['POST'])
def delete_calendar_info(calendarId):
    id_token = request.cookies.get("token")
    error_message = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_entity = retrieveUserInfo(claims)
            calendar_entity = retrieveCalendar(calendarId)
            eventsForCalendar = getAllEventsByCalendar(calendarId)

            if len(eventsForCalendar) == 0:
                deleteCalendarInfo(calendarId)
                deleteCalendarFromUserCalendarList(user_entity, calendar_entity)
            else:
                return render_template('confirm_delete_calendar.html', eventsForCalendar = eventsForCalendar, calendar = calendar_entity, calendarId = calendarId, user_info = user_entity, error_message=error_message)

        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for('chooseCalendar'))

@app.route('/confirm_delete_calendar/<int:calendarId>', methods=['POST'])
def confirm_delete_calendar(calendarId):
    id_token = request.cookies.get("token")
    error_message = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_entity = retrieveUserInfo(claims)
            calendar_entity = retrieveCalendar(calendarId)
            eventsForCalendar = getAllEventsByCalendar(calendarId)

            deleteCalendarInfo(calendarId)
            deleteCalendarEventInfoByCalendar(calendarId)
            deleteCalendarFromUserCalendarList(user_entity, calendar_entity)

            for event in eventsForCalendar:
                deleteEventInfo(event.id)

        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for('chooseCalendar'))

@app.route('/edit_calendar_info/<int:calendarId>', methods=['POST'])
def edit_calendar_info(calendarId):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            calendar_entity = retrieveCalendar(calendarId)

            calendarName = request.form['name_update']

            if calendarName:
                isNameExist = checkCalendarNameInDatastore(calendarName)
                if isNameExist:
                    raise Exception("Sorry, the calendar name is already exist!")
                else:
                    updateCalendarInfo(calendarId, calendarName)
                    updateUserCalendarList(user_info, calendar_entity, calendarName)
        except ValueError as exc:
            error_message = str(exc)
        return redirect(url_for('calendar', calendarId = calendarId, weekCount = "0"))


@app.route('/share_calendar', methods=['GET', 'POST'])
def share_calendar():
    id_token = request.cookies.get("token")
    error_message = None

    if id_token:
        if request.method == "POST":
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                user_entity = retrieveUserInfo(claims)

                calendar_entity = getCalendarByName(request.form.get('calendar'))
                shared_user_entity = getUserByEmail(request.form.get('user'))
                shareCalendarWithUser(calendar_entity, shared_user_entity)
            except ValueError as exc:
                error_message = str(exc)
        else:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                user_entity = retrieveUserInfo(claims)
                calendar_list_for_user = getCalendarListForUser(user_entity)

                user_list = getAllUsers()
                user_list.remove(user_entity)

                shared_calendar_list_with_user = getSharedCalendarRequestsForTheUser(user_entity)

                logged_users_calendar_shares = []
                for shared_calendar in calendar_list_for_user:
                    for user_email, value in shared_calendar['shared_users'].items():
                        if value == True:
                            myDic = { 'email' : user_email, 'calendar_name' : shared_calendar['name'] }
                            logged_users_calendar_shares.append(myDic)

                return render_template('share_calendar.html', logged_users_calendar_shares = logged_users_calendar_shares, calendar_list = calendar_list_for_user, shared_calendar_list_with_user = shared_calendar_list_with_user, user_list = user_list, user_info = user_entity, error_message=error_message)
            except ValueError as exc:
                error_message = str(exc)
    return redirect(url_for('share_calendar'))


@app.route('/accept_share_request/<int:calendarId>', methods=['POST'])
def accept_share_request(calendarId):
    id_token = request.cookies.get("token")
    error_message = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_entity = retrieveUserInfo(claims)

            sharedCalendar = retrieveCalendar(calendarId)
            user_email = user_entity['email']
            shared_users = sharedCalendar.get('shared_users', {})

            if user_email in shared_users:
                 shared_users[user_email] = True
                 sharedCalendar['shared_users'] = shared_users
                 datastore_client.put(sharedCalendar)
                 addCalendarToUser(user_entity, sharedCalendar)

        except ValueError as exc:
            error_message = str(exc)

    return redirect(url_for('share_calendar'))

@app.route('/reject_share_request/<int:calendarId>', methods=['POST'])
def reject_share_request(calendarId):
    id_token = request.cookies.get("token")
    error_message = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_entity = retrieveUserInfo(claims)

            sharedCalendar = retrieveCalendar(calendarId)
            user_email = user_entity['email']
            shared_users = sharedCalendar.get('shared_users', {})

            if user_email in shared_users:
                del sharedCalendar['shared_users'][user_email]
                datastore_client.put(sharedCalendar)

        except ValueError as exc:
            error_message = str(exc)

    return redirect(url_for('share_calendar'))

@app.route('/remove_user_from_calendar', methods=['POST'])
def remove_user_from_calendar():
    id_token = request.cookies.get("token")
    error_message = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_entity = retrieveUserInfo(claims)
            calendar_entity = getCalendarByName(request.form['calendar_name'])

            user_email = request.form['user_email']
            remove_user_entity = getUserByEmail(user_email)

            myDic = { user_email : True }
            shared_users_dict = calendar_entity['shared_users']
            shared_users_copy = shared_users_dict.copy()


            for key, value in shared_users_copy.items():
                if myDic == {key: value}:
                    deleteCalendarFromUserCalendarList(remove_user_entity,calendar_entity)
                    del shared_users_dict[key]
                    calendar_entity.update({
                        'shared_users': shared_users_dict
                    })
                    datastore_client.put(calendar_entity)

        except ValueError as exc:
            error_message = str(exc)

    return redirect(url_for('share_calendar'))

@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    user_info = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims)

            if user_info is None:
                createUserInfo(claims)
                currentDay = datetime.now().day
                currentMonth = datetime.now().month
                currentYear = datetime.now().year
                defaultCalendar = createCalendar('Default', currentDay, currentMonth, currentYear, claims['email'])
                addCalendarToUser(retrieveUserInfo(claims), defaultCalendar)
                defaultCalendarId = defaultCalendar.id

                return render_template('index.html', calendarId = defaultCalendarId, user_info = user_info, error_message=error_message)
            else:
                calendar_list = user_info['calendarList']
                return render_template('index.html', user_info = user_info, calendar_list = calendar_list, error_message=error_message)

        except ValueError as exc:
            error_message = str(exc)
    return render_template('index.html', user_info = user_info, error_message=error_message)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
