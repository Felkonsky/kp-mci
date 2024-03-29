# README

## Virtual Environment [optional]

Create virtual environment, then activate:

- *Activate on Mac:* source venv/bin/activate
- *Activate on Windows:* .\venv\Scripts\activate

## Setup and Commands

Install docker desktop in the first place, then:
- docker-compose build
- docker-compose up

Open 2nd terminal:
- docker-compose run app alembic revision --autogenerate -m "migration" (generate migration of db)
- docker-compose run app alembic upgrade head (upgrade db to latest version)

(if no alembic in filesystem -> docker-compose alembic init alembic)

Open browser

-> 127.0.0.1:5050 -> register db to access via pgAdmin (login -> .env file)
-> 127.0.0.1:8000/ for WebApp and API


## Requirements
Not necessary with docker setup.

- *Install:* venv/bin/python -m pip install -r requirements.txt
- *Generate:* venv/bin/python -m pip freeze > requirements.txt

## To-Do

- [] FaceRecognition on Server - return bounding box + description to client
- [] Train Function aka Button on WebApp for the Model to adapt recently added/deleted employee pictures
- [] delete employee, edit employee
- [] add multiple pictures



## misc



