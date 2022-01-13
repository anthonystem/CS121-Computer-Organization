##################################################

Welcome to the Brew Crew's IoT Coffee Maker App!

Author: Anthony Stem
Class: CS 121

Note: All programs and files contained in this zip
are authored by Anthony Stem with the exception of
the LCD-show content which runs the LCD touchscreen.

##################################################

##### OPERATING THE IOT COFFEE MACHINE & APP #####

First, ensure that the switch on the physical coffee maker is turned on (line should be pressed
down on the switch). Note that no current will be flowing into the coffee machine until allowed
by the user operating the Flask application.

NOTE: IN CASES THAT REQUIRE SUCH ACTION, YOU CAN SWITCH OFF THE COFFEE MAKER TO STOP ANY BREWING REGARDLESS
OF WHETHER OR NOT THE PI IS OUTPUTTING.

Also, make sure to be logged in as the "pi" user.

Ensure that the program and all other files have the following file path: /home/pi/FinalProject/IoTCoffeeMachineApp/~

There are two primary features on the application: the Brew option and the Scheduler.

The Brew option on the index page will take you to the Brew menu where you can click the
"Start" button to initiate a brew process immediately. When you click "Start", you will be
taken to the Brew screen where a countdown will be displayed. Once the countdown finishes,
the brew will be ready and you will be taken back to the index page.

On the brew screen, you can click the "Cancel" button to stop the brew. Doing this will turn off the
coffee machine. However, the machine may not stop pouring immediately, so please exercise caution.

The Scheduler option on the index page will take you to the Scheduler menu where there will be two
buttons "Scheduler" and "Scheduler Calendar". The "Scheduler" button will take you to the Scheduler
where you can schedule times to brew your coffee. The "Scheduler Calendar" button will take you to
the Scheduler Calendar.

In the Scheduler, you can fill out the HTML form to schedule a brew time. Select the date and time for
when you want the brew to be ready. In addition, you can select whether or not you want to make the time
recurring by checking the checkbox. Note that recurring times will happen on the same day of week at the same
exact time each week. For example, if you schedule a brew on 12/26/2021 at 7:30 am, which is a Sunday, 
the machine will brew on days 01/02/2022 @ 7:30 am, 01/09/2022 @ 7:30, etc. When you submit, a cron job will
be created in the crontab, and the information will be added to the scheduler table in the scheduler database.

In the Scheduler Calendar, you can view all existing scheduled brew times. You can delete any entry by clicking
their corresponding "Delete" buttons. Deleting an entry will remove it from the scheduler database and remove
the corresponding cron job from the crontab.



##### FILES & BREAKDOWN #####

app.py --> The main Flask app. Written in Python.

scheduled-brew.py --> An additional Python script that carries out
the brewing process for scheduled brew events/cron jobs.

credentials.json --> Contains credentials for MariaDB database.

create_table.sql --> Sets up a table formatted specifically for the application.
Table columns include the following: 
ID 	  # Unique identifier. 
timestamp # Time stamp when entry was created.
brew_time # Time that the brew is scheduled to be finished.
recurring # If 1, brew is recurring. If 0, brew is not recurring

static --> css:
styles.css --> The styling for the Brew Crew's IoT Coffee Machine Flask application.

templates
index.html --> Flask app home page.

brewmenu.html --> Contains the Start button where the user can initiate an immediate
brew process.

brew.html --> The brew screen; shows countdown timer on Flask app.

schedulermenu.html --> The Scheduler menu. Has two buttons that the user can click to
go to either the Scheduler or the Scheduler Calendar.

scheduler.html --> The Scheduler where the user can schedule a time to have their brew ready.

schedulercalendar.html --> Displays the MariaDB scheduler data table showing all the list
of brew times. User can manually delete entries.

LCD-show --> Contains the drivers and files needed for the LCD touchscreen installed on the
IoT Coffee Maker. Note that the contents of this folder are not authored by the Brew Crew.
Drivers Source: https://github.com/goodtft/LCD-show/



##### VIEWING CRON JOBS & CRONTAB #####

To list what cron jobs are scheduled on your Raspberry Pi, type
the following command:
			
			crontab -l


To edit the crontab, type the following command:

			crontab -e



##### IMPORTANT INFORMATION & SAFETY WARNINGS #####

WHEN THE COFFEE MACHINE IS SWITCHED ON AND HAS POWER, IT WILL IMMEDIATELY START TO BREW COFFEE.

DO NOT OPEN THE COFFEE MACHINE LID WHILE RUNNING AS THE COFFEE MACHINE WILL CONTINUE TO BREW.
THE COFFEE MACHINE MODEL USED FOR THIS PROJECT DOES NOT HAVE SAFETY FEATURES IN PLACE WHEN THE LID
IS OPENED.

!!! DO NOT TOUCH THE WIRES AND CONTENTS INSIDE THE PLASTIC BOX INSIDE THE COFFEE MACHINE HOUSING
WHILE THE MACHINE IS PLUGGED IN. TOUCHING THE WIRES CAN POSSIBLY RESULT IN SERIOUS INJURIES BY SHOCK
OR EVEN DEATH. !!!



##### CONTACT #####

If you have questions, comments, or concerns, email the author at 

			anthony_stem@outlook.com
or			anthony.stem@uvm.edu



##### SOURCES #####

Icons used in this project were obtained from font-awesome.
Source: https://fontawesome.com/



##################################################

Enjoy!

- The Brew Crew
