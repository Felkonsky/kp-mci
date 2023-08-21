import os, sys, io
import face_recognition
import cv2
import numpy as np
import math

import PIL.Image as Image
import base64 

import shutil
import uvicorn

from fastapi import FastAPI, Request,File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import DBSessionMiddleware, db

from forms import AddEmployeeForm

from starlette.applications import Starlette
from starlette.responses import (PlainTextResponse, RedirectResponse,
                                 HTMLResponse)
from dotenv import load_dotenv, find_dotenv
from models import Employee


load_dotenv(".env")

app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

## RETURNS FACE-RECOGNITION-CONFIDENCE IN PERCENTAGE
def face_confidence(face_distance, face_match_treshold=0.6):
    range = 1.0 - face_match_treshold
    linear_val  = (1.0 - face_distance) / (range * 2.0)
    if face_distance > face_match_treshold:
        return str(round(linear_val * 100, 2)) + "%"
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + "%"
    
class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []

    def __init__(self):
        self.encode_faces()

    def encode_faces(self):
        for image in os.listdir("static/employee_pics"):
            face_image = face_recognition.load_image_file(f'static/employee_pics/{image}')
            face_encoding = face_recognition.face_encodings(face_image)[0]

            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(image)
        print(self.known_face_names)

    def run_recognition(self):
    
        img = cv2.imread("static/face.jpg")
        small_img = cv2.resize(img, (0,0), fx=0.25, fy=0.25)

        self.face_locations = face_recognition.face_locations(small_img)
        self.face_encodings = face_recognition.face_encodings(small_img, self.face_locations)

        self.face_names = []

        for face_encoding in self.face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "unknown"
            confidence = "unknown"

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
                confidence = face_confidence(face_distances[best_match_index])

            self.face_names.append(f"{name} ({confidence})")
            print("FR SENT TO CLIENT")

            # GET EMPLOYEE WITH SPECIFIC PATH FROM DB AND RETURN ROW FROM DB AS JSON  
            # employees = db.session.query(Employee).where(Employee.picture == name)
            # print (employees)
            return self.face_names


# OTHER SHIT

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("CLIENT CONNECTED")
    
    # INIT FACEREC
    fr = FaceRecognition()

    # OPEN WEBSOCKET
    while True:
        
        try:
            
            await websocket.send_text("HI FROM THE SERVER")
            data = await websocket.receive_bytes()
            #b = base64.b64decode(data)
            img = Image.open(io.BytesIO(data))
            img.save("./static/face.jpg")
            nameslist = fr.run_recognition()

        except WebSocketDisconnect:
            print("CLIENT DISCONNECTED")
            break

        if nameslist != None:
            await websocket.send_text(nameslist)
        
        

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/employees")
def get_employees(request: Request):
    employees = db.session.query(Employee.employee_id, Employee.firstname, Employee.lastname, Employee.role, Employee.picture).all()
    return templates.TemplateResponse("employees.html", {"request": request, "employees": employees})

@app.get("/add-employee")
async def add_employee(request: Request):
    return templates.TemplateResponse("add-employee.html", {"request": request})

@app.post("/add-employee")
async def add_employee(request: Request, file: UploadFile = File(...)):
    
    try:
        file_location = f"static/employee_pics/{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object) 
    except Exception:
        pass
    finally:
        file.file.close()
    
    form = AddEmployeeForm(request)
    await form.load_data()
    
    if await form.is_valid():
        errors = ["success"]
        print("Form has no errors.")

        db_employee = Employee(firstname = form.firstname, lastname = form.lastname, role = form.role, picture = file_location)
        db.session.add(db_employee)
        db.session.commit()

    else:
        print("Form has errors.")
        errors = form.errors

    return templates.TemplateResponse("add-employee.html", {"request": request, "errors": errors})


@app.get("/index", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api-employees/")
def api_employees():
    employees = db.session.query(Employee).all()

    return employees


###################################################################
# run as local server without container (pgadmin still necessary) #
###################################################################


"""
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""