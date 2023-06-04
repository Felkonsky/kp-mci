import os
import shutil
import uvicorn
from fastapi import FastAPI, Request,File, UploadFile, Form, Depends
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


# run as local server without container (pgadmin still necessary)
"""
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""