from sqlalchemy import Column, DateTime, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    employee_id = Column("employee_id", Integer, primary_key=True, index=True)
    firstname = Column("firstname", String, nullable=False)
    lastname = Column("lastname", String,  nullable=False)
    time_met = Column("time_met", String)
    place_met = Column("place_met", String)
    role = Column("role", String)
    picture = Column("picture", String)
