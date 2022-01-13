from crontab import CronTab
import RPi.GPIO as GPIO
import time, datetime
import mysql.connector
import json

PIN = 26 # Pin needed to operate coffe machine.

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN, GPIO.OUT)

credentials = json.load(open("/home/pi/FinalProject/IoTCoffeeMachineApp/credentials.json", "r"))

# Open crontab for 'pi' user.
cron = CronTab(user='pi')

##### Returns current datetime in 'YYYY-mm-ddTHH:MM' format #####
def getCurrentDatetime():
    dateTime = datetime.datetime.now()
    date = dateTime.strftime("%Y-%m-%d")
    time = dateTime.strftime("%H:%M")
    dateTime = date + "T" + time
    print(dateTime)
    return dateTime
    

##### Checks to see if cron job at date is recurring.
def checkRecurring(date):
    # Loop through jobs in cron.
    for job in cron:
        # If comment contains ",1", it is recurring.
        if ",1" in job.comment and date in job.comment:
            return True
        # If comment contains ",0", it is not recurring.
        elif ",0" in job.comment and date in job.comment:
            return False
    return "None"

##### Deletes corresponding scheduler database entry and cron job from crontab #####
def deleteCron(date):
    database = mysql.connector.connect(
            host = credentials["host"],
            user = credentials["user"],
            password = credentials["password"],
            database = credentials["database"]
    )

    cursor = database.cursor()
    
    # Delete database entry.
    execute = "DELETE FROM scheduler WHERE brew_time=" + "'" + date + "'"
    print(execute)
  
    cursor.execute(execute)
    
    # Commit
    database.commit()
    
    database.close()
    cursor.close()

    # Delete cron job.
    for job in cron:
        if date in job.comment:
            print("Deleting Cronjob...")
            cron.remove(job)
            cron.write()
            return "Done"
    
    return "Error"


# Runs scheduled brew process.
def scheduledBrew():
    print("On")
    # Turn on coffee maker
    GPIO.output(PIN, GPIO.HIGH)

    print("Off")
    # Sleep for 3 minutes
    time.sleep(180) # 180 seconds

    # Turn off coffee maker
    GPIO.output(PIN, GPIO.LOW)

    time.sleep(60) # Sleep for 60 seconds to let coffee maker stop dripping.

    # Check for non-recurring crontabs. If there are any, delete them from the database and crontab.
    currDateTime = getCurrentDatetime()
    isRecurring = checkRecurring(currDateTime)
    print(isRecurring)
    if isRecurring == False:
        deleteCron(currDateTime)

    return "Done"
    

# Run scheduled brew process on run.
scheduledBrew()
