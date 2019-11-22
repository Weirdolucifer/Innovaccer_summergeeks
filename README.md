# Innovaccer SDE Summergeeks Assignment
> An Entry Management software

## Approach

### Visitor Check-n
When a Visitor visits the event, he/she needs to fill his/her details like Name, Phone, and Email. If there is no host available or email doesn't exist (we are using `Py3DNS` to validate email) or Visitor has already checked-in or database server is down then the software will throw a respective error. If everything works well, then it will assign a random available host to that visitor and these records will be stored in the database using timestamp (`Datetime`). A message will be generated having all details of Visitor and an Email (using `flask_mail` )and SMS
(using `Twilio`) will be sent to the respective Host.


### Host-Details
The host will add all his/her details like Name, Phone, and Email. We are validating email through `Py3DNS` and phone no through `phonenumbers` an API of google phone's directory. If everything works fine, It will redirect to a success message otherwise it will throw the respective error.
### Visitor Check-out
When Visitor is checking out, we are asking for his/her Email id (`Primary Key`). We are fetching his/her details including respective host information. If he/she has already checked out, then it will throw an error. As soon as a person checked out we are sending an email to a visitor having details (`Name, Phone, Check-in time, Check-out time, Host Name, Address Visited`).

# Production Deployment
This software is already deployed on PythonAywhere. Give it a try 
## http://weirdolucifer.pythonanywhere.com/

# Software Requirements:

+ HTML, CSS, JS - Front End
+ MySql - Database(flask_mysqldb)
+ Flask - Python Backend Engine
+ Jinja - Templating Engine

# Installation

## Local Machine setup for Linux :

```sh
git clone https://github.com/weirdolucifer/Innovaccer_summergeeks
```

If you don't have installed pip, use pip3 for installation 
```
sudo apt-get install python3-pip
```

Set up a virtual environment and activate it to avoid dependency issues.

```
virtualenv venv
.venv/bin/activate
```

Install the required dependencies using the following command
```
pip3 install -r requirements.txt
```

Run the following command to set up local server
```
python3 app.py
```

Navigate to http://localhost:5000




