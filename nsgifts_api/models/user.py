from pydantic import BaseModel, Field


class UserLoginSchema(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=255)


class UserSignupSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)


class UserSchema(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=50)
    bybit_deposit: str = Field(default="0", regex=r'^\d+(\.\d+)?$')
