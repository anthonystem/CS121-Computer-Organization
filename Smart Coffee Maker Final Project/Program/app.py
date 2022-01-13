#
# The Brew Crew's IoT Coffee Maker Flask Application
# Author: Anthony Stem
# Class: CS 121
#

from flask import Flask, url_for, request, redirect, render_template
from crontab import CronTab
import time, datetime, calendar
import RPi.GPIO as GPIO
import mysql.connector
import json
import copy

app = Flask(__name__)

credentials = json.load(open("credentials.json", "r"))

SCHEDULED = 1 # Constant for a Scheduled type brew.
STBE = 0      # Constant for an immediate type brew from the brew menu.

PIN = 26

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN, GPIO.OUT)

global brewTime

##### Brew Time Setter #####
def setBrewTime(time):
    global brewTime
    brewTime = time

##### Brew Time Getter #####
def getBrewTime():
    global brewTime
    return brewTime


##### Takes in a date and splits it into year, month, day, hours, and minutes #####
def fetchSchedulePieces(time):
    # Reformat the time string for easier splicing
    for i in range(0, len(time)):
        if i == len(time) - 1:
            time = time + ","
        elif time[i] == "-" or time[i] == "T" or time[i] == ":":
            time = time.replace(time[i], ",")

    pieces = []
    tempStr = ""
    # Splice the time string and append pieces to pieces list.
    for c in range(0, len(time)):
        if time[c] == ",":
            pieces.append(tempStr)
            tempStr = ""
        else:
            tempStr = tempStr + time[c]
 
    # Assign corresponding values to variables.
    year = pieces[0]
    month = pieces[1]
    day = pieces[2]
    hour = pieces[3]
    minute = pieces[4]

    return year, month, day, hour, minute


##### Schedules a cron job in the crontab #####
def schedule(brewTime, scheduleType, recurring):

    dateTime = datetime.datetime.strptime(brewTime, "%Y-%m-%dT%H:%M")
    print(dateTime)  

    # Calculate brew sequence initiation time/date
    minuteDelta = datetime.timedelta(minutes = 4)
    time = (dateTime - minuteDelta).strftime("%Y-%m-%dT%H:%M")

    # Put back into ISO form to call fetchSchedulePieces
    year, month, day, hour, minute = fetchSchedulePieces(time)

    # Format back to regular date/time again.
    time = formatDatetime(time)

    # Convert day to day of week (e.g. Sunday, Monday, Tue...). Result will be from 0-6.
    formattedDay = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M").strftime("%w")
    
    # Create cron job in crontab.
    cron = CronTab(user='pi')
    job = cron.new(command='python3 /home/pi/FinalProject/IoTCoffeeMachineApp/scheduled-brew.py')

    if scheduleType == SCHEDULED:
        job.minute.on(minute)
        job.hour.on(hour)
        job.day.on(day)
                
        if recurring == "1":
            job.dow.on(formattedDay)
            job.set_comment(str(dateTime.strftime("%Y-%m-%dT%H:%M") + ",1"))
            cron.write()
            return "Done"

        job.month.on(month)
        job.set_comment(str(dateTime.strftime("%Y-%m-%dT%H:%M") + ",0"))
        cron.write()

        return "Done"


##### Gets corresponding error notifications for invalid brew scheduling #####
def getErrorNotification(postType):
    if postType == SCHEDULED:
        return "Invalid Entry: Time should be at least 15 minutes away from other scheduled events and not fall on a recurring time."
    elif postType == STBE:
        return "Invalid Entry: Time should be at least 15 minutes prior to any scheduled events."
    else:
        return ""


##### Formats a Datetime string in the form 'YYYY-mm-ddTHH:MM:SS' into 'YYYY-mm-dd HH:MM:SS' #####
def formatDatetime(timeString):
     dateList = []
     timeList = []
     temp = []
     
     # Loop through datetime string and divide it into the date and time pieces.
     for i in range(0, len(timeString)):
          temp.append(timeString[i])

          if timeString[i] == 'T':
             dateList = copy.deepcopy(temp)
             dateList.remove('T')
             temp = []

          timeList = copy.deepcopy(temp)

     time = ""
     date = ""

     # Combine date and time into YYYY-MM-DD HH:MM:SS.
     for c in timeList:
        time += c

     for c in dateList:
        date += c

     # Create datetime string.
     datetime = date + " " + time

     return datetime


##### Compares two database entries to see if they are valid. #####
def compare(row1, row2, scheduleType, recurring):

    d1 = formatDatetime(row1)
    d2 = formatDatetime(row2)
    
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d %H:%M")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d %H:%M")
    
    # Check if d1 is before d2.
    isBefore = False
    if d1 < d2:
        isBefore = True
    
    print(scheduleType)
    print(isBefore)

    # Calculate time and date deltas.
    timeDelta = abs((d2 - d1)).seconds / 60
    dateDelta = abs((d2 - d1)).days
    
    print(dateDelta)
    
    # Validate time. Time must be at least 15 minutes from any existing entries on same date and before existing time if brewing immediately.
    if ((scheduleType == SCHEDULED and dateDelta == 0 and timeDelta < 15) or (dateDelta % 7 == 0 and timeDelta < 15 and recurring == 1)):
        return False
    elif (scheduleType == STBE and (dateDelta == 0 and timeDelta < 15 or isBefore == False)):
        return False
        
    return True
    

##### Validates a brew time #####
def validateTime(brewTime, scheduleType):
    database = mysql.connector.connect(
            host = credentials["host"],
            user = credentials["user"],
            password = credentials["password"],
            database = credentials["database"]
    )
   
    cursor = database.cursor()

    cursor.execute("SELECT * FROM scheduler")

    result = cursor.fetchall()

    # Compare attempted schedule/brew time to any entries in the database.
    for row in result:
        if compare(brewTime, row[2], scheduleType, row[3]) == False:
            cursor.close()
            database.close()
            return False   
    
    cursor.close()
    database.close()

    return True


##### Deletes an entry from database and cron job from crontabe #####
@app.route("/delete", methods=["POST"])
def delete():
    database = mysql.connector.connect(
            host = credentials["host"],
            user = credentials["user"],
            password = credentials["password"],
            database = credentials["database"]
    )
    
    cursor = database.cursor()
   
    rowID = request.form['delete-button']
   
    query = "SELECT * FROM scheduler WHERE id=" + rowID

    cursor.execute(query)

    date = cursor.fetchall()[0][2]
    print(date)
    
    # Delete database entry.
    query = "DELETE FROM scheduler WHERE brew_time=" + "'" + str(date) + "'"

    cursor.execute(query)

    database.commit()
    print(cursor.rowcount, "record deleted")

    cursor.close()
    database.close()

    # Delete cron job from crontab.
    cron = CronTab(user='pi')
    for job in cron:
        print(job)
        if str(date) in job.comment:
            print(job.comment)
            print("Deleting Crontab")
            cron.remove(job)
            cron.write()
    
    # Redirect to scheduler calendar.
    return redirect(url_for('schedulercalendar'))


##### Turns the coffee machine on. #####
def brewStart(brewType):
    print("HIGH")
    # Output.
    GPIO.output(PIN, GPIO.HIGH)
    
    if brewType == SCHEDULED:
        return "Invalid Attempt" 
    elif brewType == STBE:
        print("Brew")
    return "Brewing"


##### Executes when the user wants to cancel a brew while on the brewing screen #####
@app.route("/cancel", methods=["GET"])
def cancel():

    # Stop the brew.
    brewStop()

    database = mysql.connector.connect(
            host = credentials["host"],
            user = credentials["user"],
            password = credentials["password"],
            database = credentials["database"]
    )
    
    cursor = database.cursor()
   
    # Order table by descending order and get the top (gets current brew time)
    query = "SELECT * FROM scheduler ORDER BY id DESC LIMIT 1"

    cursor.execute(query)

    rowID = cursor.fetchall()[0][0]
    print(rowID)

    # Delete current brew time from table.
    query = "DELETE FROM scheduler WHERE id=" + str(rowID)

    cursor.execute(query)

    # Commit.
    database.commit()

    print(cursor.rowcount, "record deleted")

    database.close()
    cursor.close()

    return redirect(url_for('index'))


##### Turns the coffee machine off when the countdown reaches 60 seconds #####
@app.route("/turn_off", methods=["POST"])
def turn_off():
    print("Turning Off Coffee Maker...")
    GPIO.output(PIN, GPIO.LOW)

    return "Coffee Maker Shut Off"


##### Gets the minimum allowable brew time. #####
@app.route("/get_minimum_brew_time", methods=["POST"])
def getMinimumBrewTime():
    # Get current time (local timezone).
    currentTime = datetime.datetime.now()

    # Get time differential (in minutes) for how long it takes to brew.
    timeDelta = datetime.timedelta(minutes=4)

    # Add the current time with the time differential to get the minimum brew time.
    minimumBrewTime = (currentTime + timeDelta).strftime("%H:%M")

    return minimumBrewTime
    

##### Gets the minimum allowable brew date #####
@app.route("/get_minimum_date", methods=["POST"])
def getMinimumDate():
    currentTime = datetime.datetime.now()
    
    timeDelta = datetime.timedelta(minutes = 5)
    
    minimumDate = (currentTime + timeDelta).strftime("%Y-%m-%dT%H:%M")
    
    return minimumDate



##### Renders index page #####
@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html", title="IOT Coffee Maker App", name="Anthony Stem")


##### Renders brew menu #####
@app.route("/brewmenu", methods=["GET"])
def brewmenu():
    minBrewTime = getMinimumBrewTime()
    return render_template("brewmenu.html", title="Brew Menu", minBrewTime=minBrewTime)


##### Renders brewing screen #####
@app.route("/brew", methods=["GET"])
def brew():
    return render_template("brew.html")


##### Executes when user starts brew process #####
@app.route("/brew_post", methods=["POST"])
def brewPost():
    database = mysql.connector.connect(
            host = credentials["host"],
            user = credentials["user"],
            password = credentials["password"],
            database = credentials["database"]
    )
    cursor = database.cursor()
    
    # Statement to insert entry into database.
    insertSQL = "INSERT INTO scheduler (timestamp, brew_time, recurring) VALUES (%s, %s, %s);"

    timeStamp = datetime.datetime.now()
    print(timeStamp)

    # Get brew time
    brewTime = request.form["brew-time-input"]

    print(brewTime)
    date = timeStamp.strftime("%Y-%m-%d")

    dateTime = str(date).replace(" ", "") + "T" + brewTime

    # Check if entry is valid.
    entryIsValid = validateTime(dateTime, STBE)
    print("Is Entry Valid?", entryIsValid)
    
    if entryIsValid: 
            # Default to not recurring.
            recurring = "0"

            # Add entry to database.
            data = (timeStamp, dateTime, recurring)
            cursor.execute(insertSQL, data)

            database.commit()

            cursor.close()
            database.close()
        
            # Start brew process.
            brewStart(STBE)
            
            # Direct user to brewing screen.
            return redirect(url_for('brew'))

    # Return user to brew menu and display error notification.
    return render_template('brewmenu.html', errorNotification=getErrorNotification(STBE), minBrewTime=getMinimumBrewTime())


##### Renders scheduler menu #####
@app.route("/schedulermenu", methods=["GET"])
def schedulermenu():
    return render_template("schedulermenu.html", title="Scheduler Menu")


##### Runs when user schedules a brew time using Scheduler #####
@app.route("/scheduler_post", methods=["POST"])
def schedulerPost():
    database = mysql.connector.connect(
            host = credentials["host"],
            user = credentials["user"],
            password = credentials["password"],
            database = credentials["database"]
    )
    cursor = database.cursor()
    
    # Put time into database.
    insertSQL = "INSERT INTO scheduler (timestamp, brew_time, recurring) VALUES (%s, %s, %s);"

    timeStamp = datetime.datetime.now()

    # Get brew time.
    brewTime = request.form["brew-time"]

    if request.form.get("recurring") != "1":
        # Default to not recurring if recurring is not 1.
        recurring = "0"
    else:
        recurring = request.form["recurring"]
    
    # Validate entry.
    entryIsValid = validateTime(brewTime, SCHEDULED)
    print("Is Entry Valid? ", entryIsValid)

    # Run if entry is valid.
    if entryIsValid:          
            data = (timeStamp, brewTime, recurring)
            cursor.execute(insertSQL, data)

            database.commit()

            cursor.close()
            database.close()

            # Schedule cron job.
            schedule(brewTime, SCHEDULED, recurring)
            
            # Redirect to scheduler menu.
            return redirect(url_for('schedulermenu'))

    cursor.close()
    database.close()

    # Return to scheduler and display error notification if invalid.
    return render_template('scheduler.html', errorNotification=getErrorNotification(SCHEDULED), minimumDate=getMinimumDate())


##### Renders Scheduler #####
@app.route("/scheduler", methods=["GET"])
def scheduler():
    # Get minimum date.
    minimumDate = getMinimumDate()

    return render_template("scheduler.html", minimumDate=minimumDate)


##### Renders scheduler calendar #####
@app.route("/schedulercalendar", methods=["GET"])
def schedulercalendar():
    database = mysql.connector.connect(
            host = credentials["host"],
            user = credentials["user"],
            password = credentials["password"],
            database = credentials["database"]
    )
    cursor = database.cursor()
    
    # Get all scheduled events to display on calendar.
    query = "SELECT * FROM scheduler"

    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    database.close()

    return render_template("schedulercalendar.html", data=data, title="Scheduler Calendar")
