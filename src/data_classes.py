import logging

from datetime import date, datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Address:
    street: str
    streetnumber: int
    zipcode: int
    city: str


@dataclass
class Agency:
    name: str
    KBO_number: Optional[int]  # Allow None for KBO_number
    address: Address


@dataclass
class Person:
    last_name: str
    first_name: str
    address: Address

    @property
    def full_name(self) -> str:
        """
        Returns the full name of the person by concatenating the first and last names.

        Returns:
            str: The full name in the format "First Last".
        """
        return f"{self.first_name} {self.last_name}"


@dataclass
class Member(Person):
    date_of_birth: date
    registration_year: int
    discount: bool


class Activity:
    def __init__(
        self,
        start_date: date,
        end_date: date,
        total_price: float,
    ):
        self.start_date = start_date
        self.end_date = end_date
        if start_date > end_date:
            logging.warning(
                f"Activity: start date {start_date} is after end date {end_date}."
            )
        self.number_of_days = (end_date - start_date).days + 1
        self.price_per_day = round(total_price / float(self.number_of_days), 2)
        if total_price < 0:
            logging.warning(f"Activity: total price {total_price} is negative.")
        self.total_price = total_price

    def recalculate_price_and_days(self):
        self.number_of_days = (self.end_date - self.start_date).days + 1
        self.total_price = self.price_per_day * self.number_of_days

    def __str__(self):
        return (
            f"van {self.start_date}\t{self.number_of_days} dagen"
            f"\t\t€ {self.price_per_day}\t€ {self.total_price}\n"
            f"tot {self.end_date}"
        )


class Activities:
    def __init__(self) -> None:
        self.list = []
        self.total = 0.0

    def add_activity(self, activity: Activity):
        self.list.append(activity)
        self.total += activity.total_price


@dataclass
class Signature:
    place: str
    name: str
    role: str
    date: datetime = datetime.today().date()  # Default value for date


@dataclass
class TaxCertificateTemplate:
    youth_movement: Agency
    certification_agency: Agency
    signature: Signature


@dataclass
class TaxCertificate:
    serial_number: int
    parent: Person
    member: Member
    activities: Activities
