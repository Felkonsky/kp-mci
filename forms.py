from typing import Optional, List
from fastapi import Request
import re

class AddEmployeeForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.firstname: Optional[str] = None
        self.lastname: Optional[str] = None
        self.role: Optional[str] = None
    
    async def load_data(self):
        form = await self.request.form()
        self.firstname = form.get("firstname")
        self.lastname = form.get("lastname")
        self.role = form.get("role")

    async def is_valid(self):

        if not re.match("^[A-Za-z ,.'-]+$", self.firstname):
            self.errors.append("'First Name' was invalid.")

        if not re.match("^[A-Za-z ,.'-]+$", self.lastname):
            self.errors.append("'Last Name' was invalid.")

        if not self.firstname:
            self.errors.append("First Name is required!")
        if not self.lastname:
            self.errors.append("Last Name is required!")
        if not self.errors:
            return True
        return False 