import os
import datetime
import time
import random
import phonenumbers

from flask import Flask, render_template, request
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from twilio.rest import Client
from dotenv import load_dotenv
from validate_email import validate_email
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type


load_dotenv()
app = Flask(__name__)


account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

app.config['DEBUG'] = True
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mysql = MySQL(app)
mail = Mail(app)

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/check-in', methods=['GET', 'POST'])
def checkin():
    if request.method == "POST":
        #getting details from the form
        details = request.form
        Name  = details['name']
        Email = details['email']
        Phone = details['phone']
        #checking for validity of email entered
        is_valid = validate_email(Email, verify=True, check_mx=True)
        if is_valid :
       
            #creating the mesaage for Host
            message = "Visitor Details:\n Name : %s\n Email: %s\n Phone: %s"  % (Name,Email,Phone)
            subject = "Visitor Detail"
            msg = Message(body=message,subject=subject)
            

            #getting detail of host from database
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT Email,Phone from Host")
            res = cur1.fetchall()
            #In case if there is no host ready for event
            nh= len(res)
            if nh == 0:
                datax = "Hosts are not ready! Please try after some time"
                return render_template('log.html', datax = datax)
            else:
                # Assigning a radnom host
                x = random.randint(1,nh)
                
                #getting details of host to send mail and sms
                mail_rec = res[x-1][0]
                rec = res[x-1][1]
                
                msg.recipients = [mail_rec]
                rec1 = "+91"+str(rec)
                
                try:
                    #inserting the data into database
                    
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO Visitor(Name, Email, Phone, host) VALUES(%s, %s, %s, %s)", (Name, Email, Phone, mail_rec))
                    cur.close()
                    mysql.connection.commit()
                    cur1.close()
                    try:
                        mail.send(msg)
                        #sending sms to the host
                        try:
                            message = client.messages \
                                        .create(
                                             body=message,
                                             from_='+12056192811',
                                             to=rec1
                                         )
                        except:
                            datax = "Some error occurred in sending sms! But you can check in"
                            return render_template('success.html', datax = datax)    
                    except:
                        datax = "Some error occurred in sending mail! But you can check in"
                        return render_template('success.html', datax = datax)
                except:
                    datax = "You have already checked in or database server is down! Please try again"
                    return render_template('log.html', datax = datax)        
        else:
            datax = "This is not a valid email! Please try again"
            return render_template('log.html', datax = datax)

        return render_template('success.html', datax = "Welcome to the event")

    return render_template('checkin.html')



@app.route('/host', methods=['GET', 'POST'])
def host():
    if request.method == "POST":
        details = request.form
        #getting details from teh form 
        Name  = details['name']
        Email = details['email']
        Phone = details['phone']
        #checking for validity of email and phone of host
        number = "+91"+str(Phone)
        v = carrier._is_mobile(number_type(phonenumbers.parse(number)))
        is_valid = validate_email(Email, verify=True, check_mx=True)
        print(v)
        print(is_valid)
        if v == True and is_valid == True:
            try:
                #inserting the host data into database
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO Host(Name, Email, Phone) VALUES(%s, %s, %s)", (Name, Email, Phone))
                mysql.connection.commit()
                cur.close()
            except Exception as e:
                datax = "You have already checked in or database server is down! Please try again"
                return render_template('log.html', datax = datax)
            return render_template('success.html', datax = "Thanks for filling details")
        
        else:
            if v == False:
                datax = "You entered a wrong phone number! Please try again"
                return render_template('log.html', datax = datax)
            else:
                datax = "You entered a wrong email id! Please try again"
                return render_template('log.html', datax = datax)

    return render_template('host.html')



@app.route('/check-out', methods=['GET', 'POST'])
def checkout():
    if request.method == "POST":
        details = request.form
        #At the time of check-out getting email from  visitor
        Email = details['email']
        try:
            cur = mysql.connection.cursor()
            #getting details of visitor from the database 
            cur.execute("SELECT* from Visitor WHERE Email = %s" , (Email,))
            res = cur.fetchone()
            #getting details of host
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT Name from Host WHERE Email = %s", (res[3],))
            res1 = cur1.fetchone()
            
            mysql.connection.commit()
            cur.close()
            cur1.close()

            #preparing message for the emailing
            lis = []
            
            lis.append(res[0])
            lis.append(res[1])
            lis.append(res[2])
            lis.append(res[4].time())
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            lis.append(current_time) 
            lis.append(res1[0])  
            lis.append("XYZ")   
            message = " Name : %s\n Phone: %s\n Check-in Time: %s\n Check-out Time: %s\n Host name: %s\n Address Visited: %s" % (lis[0],lis[2],lis[3],lis[4],lis[5],lis[6])
            subject = "Visitor Detail"
            msg = Message(body=message,subject=subject)
            msg.recipients = [Email]
            try:
                #sending the email to the visitor
                mail.send(msg)
                cur2 = mysql.connection.cursor()
                cur2.execute("DELETE from Visitor WHERE Email= %s", (Email,))
                res1 = cur2.fetchone()
                cur2.close()
                mysql.connection.commit()
                

            except:
                datax = "Some error occurred in sending mail! Please try again"
                return render_template('log.html', datax = datax)
            return render_template('success.html', datax = "Thank you for coming")

        except:
            datax = "You have not checked in or you entered a wrong Email Id ! Please try again"
            return render_template('log.html', datax = datax)
       
        
        
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run()