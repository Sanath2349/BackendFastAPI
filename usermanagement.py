from fastapi import FastAPI,Query,HTTPException,BackgroundTasks
from pydantic import BaseModel,EmailStr,validator
from datetime import datetime
from pymongo import MongoClient
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from typing import Optional
import re


client = MongoClient("mongodb+srv://exousiatraining:aman994909@cluster0.vkin1.mongodb.net/")
hello_admin = ['apipractice']
admin_user_col = ['task1']


app = FastAPI()


class get_subsequent_admin_user_data(BaseModel):
   full_name : str
   email : EmailStr
   mobile : int
   Date_of_birth : datetime
   address : str
   aadhar_number : int
   pan_number : str
   Joined_date : Optional[datetime] = datetime.now().isoformat()
#    password : Optional[str] = None

   @validator('mobile')
   def validate_mobile(cls, value):
        if len(str(value)) != 10:
            raise ValueError('Mobile number must be 10 digits.')
        return value
    
   @validator('aadhar_number')
   def validate_aadhar(cls, value):
        if len(str(value)) != 12:
            raise ValueError('Aadhar number must be 12 digits.')
        return value
    
   @validator('pan_number')
   def validate_pan(cls, value):
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if not re.match(pan_pattern, value):
            raise ValueError('Invalid PAN number format.')
        return value


def generate_random_password(length=8):
    # I am Generating a random password here.....
    alphabet = string.ascii_letters + string.digits 
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

def creating_userid():
    counter = client.hello_admin.admin_user_col.find_one_and_update(
        {'_id': 'user_id'},
        {'$inc': {'sequence_value': 1}},
        upsert=True,
        return_document=True
    )
    return counter['sequence_value']

def send_email(recipient_email: str, subject: str, body: str):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "amanamn2000@gmail.com"
    sender_password = "joje wkhs utxl flmn"
    
    # Creating the email here
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email
    # Sending the email here
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

@app.post("/create_subsequent_admin")
def post_data(admin_detail: get_subsequent_admin_user_data,background_tasks:BackgroundTasks, gender : str = Query(...,enum=["Male","Female"]),
            state_name: str = Query(..., enum=["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
                                            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand","Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur","Meghalaya", "Mizoram", "Nagaland",
                                            "Odisha", "Punjab","Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura","Uttar Pradesh", "Uttarakhand", "West Bengal"]), 
            city_name: str = Query(..., enum = ["Visakhapatnam", "Vijayawada","Itanagar", "Tawang","Guwahati", "Dibrugarh","Patna","Gaya","Raipur", "Bhilai","Panaji", "Margao","Ahmedabad", "Surat","Gurugram", "Faridabad", 
                                            "Shimla", "Manali","Ranchi", "Jamshedpur","Bengaluru", "Mysuru","Thiruvananthapuram", "Kochi","Indore", "Bhopal","Mumbai", "Pune", "Imphal", "Churachandpur","Shillong", "Tura", 
                                            "Aizawl", "Lunglei","Kohima", "Dimapur","Bhubaneswar", "Cuttack","Ludhiana", "Amritsar","Jaipur", "Udaipur","Gangtok", "Pelling","Chennai", "Coimbatore","Hyderabad", "Warangal", 
                                            "Agartala", "Udaipur","Lucknow", "Varanasi","Dehradun", "Haridwar","Kolkata", "Darjeeling"]),
            status: str = Query(..., enum=["InActive"]), role: str = Query(..., enum = ["Admin","Organisation", "student"])):
    
    generate_password = generate_random_password()
    sequence_value = creating_userid()
    document = admin_detail.dict()
    document["gender"] = gender
    document["state"] = state_name
    document["city"] = city_name
    document["role"] = role
    document["department"] = role
    document["password"] = generate_password
    document["status"] = status
    document["user_id"] = f"UID{sequence_value:06d}"
    
    client.hello_admin.admin_user_col.insert_one(document)

    email_subject = "Your New Account Information"
    email_body = (f"Dear {admin_detail.full_name},\n\n"
                  f"Your account has been created. Please use the following credentials to log in:\n"
                  f"Email: {admin_detail.email}\n"
                  f"Password: {generate_password}\n"
                  f"After logging in, please change your password immediately.\n\n"
                  f"Best regards,\nAI DISHA")
    
    # Below line will send mail automatically when post operation is applied
    background_tasks.add_task(send_email, admin_detail.email, email_subject, email_body)

    return {"status": "success", "user_id": document["user_id"], "generated_password": generate_password}



@app.put("/create_subsequent_admin")
def edit_data(user_id: str, admin_detail: get_subsequent_admin_user_data, gender : str = Query(...,enum=["Male","Female"]),
            state_name: str = Query(..., enum=["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
                                            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand","Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur","Meghalaya", "Mizoram", "Nagaland",
                                            "Odisha", "Punjab","Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura","Uttar Pradesh", "Uttarakhand", "West Bengal"]), 
            city_name: str = Query(..., enum = ["Visakhapatnam", "Vijayawada","Itanagar", "Tawang","Guwahati", "Dibrugarh","Patna","Gaya","Raipur", "Bhilai","Panaji", "Margao","Ahmedabad", "Surat","Gurugram", "Faridabad", 
                                            "Shimla", "Manali","Ranchi", "Jamshedpur","Bengaluru", "Mysuru","Thiruvananthapuram", "Kochi","Indore", "Bhopal","Mumbai", "Pune", "Imphal", "Churachandpur","Shillong", "Tura", 
                                            "Aizawl", "Lunglei","Kohima", "Dimapur","Bhubaneswar", "Cuttack","Ludhiana", "Amritsar","Jaipur", "Udaipur","Gangtok", "Pelling","Chennai", "Coimbatore","Hyderabad", "Warangal", 
                                            "Agartala", "Udaipur","Lucknow", "Varanasi","Dehradun", "Haridwar","Kolkata", "Darjeeling"]),
             role: str = Query(..., enum = ["Admin","Organisation", "student"])): 
    
    Full_name = admin_detail.full_name
    Email = admin_detail.email
    Mobile = admin_detail.mobile 
    DOB = admin_detail.Date_of_birth 
    Address = admin_detail.address
    Anumber = admin_detail.aadhar_number 
    Pnumber = admin_detail.pan_number 
    # Password = admin_detail.password 
    update_details = {
            "full_name" : Full_name,
            "email" : Email,
            "mobile" : Mobile,
            "address" : Address,
            "Date_of_birth":DOB,
            "aadhar_number" : Anumber,
            "pan_number" : Pnumber,
            "gender" : gender,
            "state" : state_name,
            "city" : city_name,
            "role": role,
            "department": role,
            # "password": Password,
    }
    
    document = client.hello_admin.admin_user_col.find_one_and_update({"user_id":user_id},
                        {"$set": update_details},return_document=True)
    document["_id"] = str(document["_id"])
    return document



    
@app.patch("/update_status")
def update_admin_user_status(user_id: str, status: str = Query(..., enum=["Active","InActive"]),):
    document = client.hello_admin.admin_user_col.find_one_and_update({"user_id":user_id},
                        {"$set": {"status":status}},return_document=True)
    document["_id"] = str(document["_id"])
    return document

@app.get("/get_active_user")
def get_All_active_admin():
    document = client.hello_admin.admin_user_col.find({"status":"Active"})
    result = []
    for doc in document:
        doc["_id"] = str(doc["_id"])
        result.append(doc)
    return result
