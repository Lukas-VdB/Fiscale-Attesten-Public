from docx.shared import Pt, RGBColor
from datetime import date, datetime, timedelta
from data_classes import Activity, Member
import logging


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


def adapt_activity_data_to_member(
    activity: Activity, member: Member, max_age: int
) -> Activity:
    """
    Adapts activity data based on the member's age, discount, and camp participation status.

    This function checks if the member is eligible for the activity based on their age, adjusts
    the total price if they qualify for a discount, and modifies the activity duration and price
    if they didn't attend a precamp. If the member becomes too old during the activity, the end date
    and price are recalculated accordingly.

    Args:
        activity (Activity): The activity object containing start date, end date, and total price.
        member (Member): The member object containing date of birth and discount status.
        full_camp (bool): Whether the member attended the full camp (True) or missed precamp days (False).
        max_age (int): The maximum age a member can be to participate in the activity.

    Returns:
        Activity: The modified activity object if the member is eligible.
        None: If the member is too old for the activity at any point.

    Raises:
        ValueError: If there are issues with date manipulation or invalid data is provided.
    """
    try:
        # Check if the member isn't too old at the start of the activity
        if is_member_too_old(member.date_of_birth, activity.start_date, max_age):
            return None

        # Apply discount if the member qualifies (e.g., Scouting op Maat)
        if member.discount:
            activity.total_price = round(activity.total_price / 3.0, 2)

        # Check if the member becomes too old during the activity
        if is_member_too_old(member.date_of_birth, activity.end_date, max_age):
            activity.end_date = date(
                activity.end_date.year,
                member.date_of_birth.month,
                member.date_of_birth.day - 1,
            )
            activity.recalculate_price_and_days()

        return activity

    except Exception as e:
        error_msg = f"An error occurred while adapting activity data for member {member.full_name}: {e}"
        logging.error(error_msg)
        raise ValueError(error_msg)
