# classes.py
# python
from typing import Optional, Dict, List
# external
from pydantic import BaseModel


class Freelancer(BaseModel):
    id: str
    name: str
    title: Optional[str]
    img_url: Optional[str]
    payment_price: float
    payment_rate: Optional[str]
    total_earnings: Optional[str]
    hours_worked: int
    job_count: Dict[str, int]
    job_success_rate: Optional[float]
    description: str
    skills: List[str]
    badge: Optional[str]


class User(BaseModel):
    username: str
    password: str
    secret_answer: str
    authenticator_key: Optional[str]


class Address(BaseModel):
    street: str
    street2: Optional[str]
    city: str
    state: str
    zipcode: str
    country: str


class Contact(BaseModel):
    id: str
    fullname: str
    email: str
    timezone: str
    phone: Optional[str]
    address: Address
