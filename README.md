# Clinic management system
Health clinic management system. Register patients, schedule appointments and save lives.

## Setup
### Secret Key
In your project .env file add SECRET_KEY=your_very_secret_key
### Superuser
To add employees you’ll need a django superuser account. To set one up run 
>django manage.py createsuperuser

### Groups
The whole functionality revolves around users being assigned to two main groups: physicians and nurses. They allow access to key components after user logss in. You’ll have to create those first. To do so, go to the django admin panel and find Groups under AUTHENTICATION AND AUTHORIZATION. Groups are also used to define and assign specializations for physicians. They should not be used for other purposes. Every group you define will appear in the form used to schedule appointments. Nurses should be assigned to one group (nurses) physicians to one group minimum (physicians) or more if they have a specialization (e.g. physicians, internists)

### Users
Add users and assign them to desired groups. Find Users under AUTHENTICATION AND AUTHORIZATION in the admin panel.

## Features

### Schedule
Before you schedule an appointment, you have to organize doctors schedule. Find Schedules under MAIN in the admin panel. If no physician is on the schedule, you won't be able to set up an appointment.  

You can set up a schedule for one day or a range of days.
* Date → schedule day („from” for a range).
* Date to → range last day. optional
* Start → shift start
* End → shift end
* Employee → physician  

You can’t set up two schedules for one physician at the same date.

### User
Any page will redirect an anonymous user to the login page. Users can change their default password (assigned by you) in /account/change-password or by clicking user icon in the nav bar.

### Nurse
Registers patients and schedules appointments.

#### Registration
Register a patient through „Register” form available in the navbar.

#### Schedule appointments
Navbar „Schedule”. Appointments can be set up from today to 7 days ahead. You can filter specialties (query for groups excluding nurses. See Groups for more details) to display schedules for specific physicians which will appear as the third filter. The minimum to see schedules is specialty and date. The results page will display all available appointment times for all doctors on schedule on that day. Appointment time is set up to 30 minutes (can be changed in main/const.py) so physicians shift will be split up in 30 minute intervals and displayed here. Clicking on Schedule will take you to another form. Fill in patients personal id and visit purpose and submit. Appointment scheduled and you are redirected to main page.  
Important 
* you can’t schedule a patient to two physicians at the same time

#### Main page
Different for nurses and physicians. Nurses see a list of all future appointments. They can cancel any of them.

#### Cancel appointments
If an appointment haven’t taken place yet (status took_place=False or None) you can cancel it. Click cancel on any of the ones displayed in the main page will redirect you to a page where you can either confirm you want to delete the appointment or cancel the whole operation. If you confirm, the appointment is canceled and you will be redirected to main page. If you resign it will redirect you to the appointment details page (the one you tried to cancel).

#### Appointment
As a rule – only physicians should edit appointment details. Nurses can too but shouldn’t (I just assumed they are trustworthy). A nurse can also cancel appointment from this page (if it haven’t taken place yet).

#### Searchbar
In the navigation bar you’ll find a search bar. Type in patients first name, last name or personal id and display search results on submition.
* partial matches allowed
* only one of three search criteria mentioned above  

Click on any patients details to display his medical history.

#### Patient detail page
You can edit patient personal details and display his medical history (which is a history of his appointments).

### Physician
Can’t register patients or schedule/delete appointments. He’s here to diagnose, treat and cure patients.

#### Main page
A form with the nearest appointment that haven’t taken place yet. If a patient showed up – fill out the form. If not – mark „Took place” as No and submit. The next appointment will be displayed. If no appointments scheduled for today – you will see a heading informing you about it.

A physician can edit appointment details and display patient details/medical history.
