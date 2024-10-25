from pydantic import BaseModel

class UserRegister(BaseModel):
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str