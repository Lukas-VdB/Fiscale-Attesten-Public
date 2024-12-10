from docx.shared import Pt, RGBColor
from datetime import date, datetime


def set_label_font_of_run(run):
    run.font.name = "Arial"
    run.font.size = Pt(11)


def set_written_font_of_run(run):
    set_label_font_of_run(run)
    run.font.color.rgb = RGBColor(0, 0, 255)
    run.italic = True


def add_trailing_spaces(string, total_length):
    if len(string) >= total_length:
        return string  # Return the original string if its length is already greater than or equal to the desired length
    else:
        spaces_to_add = total_length - len(string)
        return string + " " * spaces_to_add


def determine_age_group(age_group_data: dict, registration_year: int):
    for age_group in age_group_data.keys().__reversed__():
        if registration_year <= age_group_data[age_group]["first_registration_year"]:
            return age_group
    return None


def is_member_too_old(date_of_birth: date, reference_date: date, max_age):
    # Calculate age in years
    age = (
        reference_date.year
        - date_of_birth.year
        - (
            (reference_date.month, reference_date.day)
            < (date_of_birth.month, date_of_birth.day)
        )
    )
    # If member is older then max_age -> return False
    return age >= max_age


def parse_date(date_string: str) -> date:
    """Converts a date string in the format 'Day, DD/MM/YYYY' to a date object."""
    if date_string:
        try:
            return datetime.strptime(date_string.strip(), "%d/%m/%Y").date()
        except ValueError:
            return None  # Return None if parsing fails
    return None
