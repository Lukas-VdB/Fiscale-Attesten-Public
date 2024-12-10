import logging
from docx import Document
from typing import List
from copy import deepcopy
from datetime import timedelta
from docx2pdf import convert as convert_to_pdf
import os

from config import load_config, read_tax_certificate_template_data, read_age_group_data
from csv_import import read_activity_data, read_presence_data
from data_classes import *
from word_export import write_tax_certificate_template, write_tax_certificate
from utils import determine_age_group, is_member_too_old


def generate_tax_certificate_template(
    file_name: str, template_info: TaxCertificateTemplate
) -> str:
    """
    Generates a tax certificate template by populating the provided Word document template
    with information from the `TaxCertificateTemplate` object.

    Args:
        file_name (str): The path to the Word (.docx) template file to be populated.
        template_info (TaxCertificateTemplate): The data structure containing the tax certificate
                                                template details such as youth movement, certification
                                                agency, and signature information.

    Returns:
        str: The file name of the newly generated tax certificate template.

    Raises:
        FileNotFoundError: If the specified Word template file is not found.
        OSError: If an error occurs while opening, modifying, or saving the file.
        Exception: For any other unforeseen errors during document generation.
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_name):
            raise FileNotFoundError(
                f"Tax Certificate template '{file_name}' not found."
            )

        # Open the document
        doc: Document = Document(file_name)

        # Populate the document with template information
        write_tax_certificate_template(doc, template_info)

        # Generate the output file name
        template_file_name = (
            file_name.split(".")[0]
            + " "
            + template_info.youth_movement.name
            + "."
            + file_name.split(".")[1]
        )

        # Save the populated document
        doc.save(template_file_name)
        return template_file_name

    except FileNotFoundError as e:
        logging.critical(e)
        raise

    except OSError as e:
        logging.critical(
            f"Error while handling the document '{file_name}': {e.strerror}"
        )
        raise

    except Exception as e:
        logging.critical(f"Unexpected error occurred: {e}")
        raise


def generate_age_group_data(age_group_data: dict, first_registration_year: int) -> dict:
    """
    Populates the age group data by adding the first registration year for each group and adjusting
    the year for subsequent groups based on the number of years specified for each group.

    Args:
        age_group_data (dict): A dictionary containing age group information. Each key represents
                               an age group, and its value is a dictionary with details like
                               "nr_of_years" (the number of years in that age group).
        first_registration_year (int): The initial registration year for the first age group.

    Returns:
        dict: The modified age group data, with the "first_registration_year" added for each group.

    Raises:
        TypeError: If `age_group_data` is not a dictionary or `first_registration_year` is not an integer.
        KeyError: If any age group dictionary does not contain the required "nr_of_years" key.
        ValueError: If `nr_of_years` is not a positive integer for any group.
    """
    # Type validation
    if not isinstance(age_group_data, dict):
        raise TypeError("age_group_data must be a dictionary.")

    if not isinstance(first_registration_year, int):
        raise TypeError("first_registration_year must be an integer.")

    try:
        for age_group, group_info in age_group_data.items():
            # Check if the required key "nr_of_years" exists and is valid
            if "nr_of_years" not in group_info:
                raise KeyError(f"Missing 'nr_of_years' in age group: {age_group}")

            nr_of_years = group_info["nr_of_years"]

            if not isinstance(nr_of_years, int) or nr_of_years <= 0:
                raise ValueError(
                    f"'nr_of_years' must be a positive integer for age group: {age_group}"
                )

            # Update the age group with the current first_registration_year
            age_group_data[age_group][
                "first_registration_year"
            ] = first_registration_year

            # Decrease the first_registration_year by the number of years for this group
            first_registration_year -= nr_of_years

        return age_group_data

    except KeyError as e:
        logging.error(f"KeyError: {e}")
        raise

    except ValueError as e:
        logging.error(f"ValueError: {e}")
        raise

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise


def adapt_activity_data_to_member(
    activity: Activity, member: Member, full_camp: bool, max_age: int
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
        # Adjust activity duration if the member missed precamp (very scouts-specific logic)
        if not full_camp:
            activity.start_date += timedelta(days=2)

            # Check again if the member is too old after adjusting the start date
            if is_member_too_old(member.date_of_birth, activity.start_date, max_age):
                return None

            activity.recalculate_price_and_days()

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


def generate_activities_for_member(
    member: Member,
    activity_names: List[str],
    calendar_year: int,
    age_group_data: dict,
    weekend_data: dict,
    max_age: int,
) -> Activities:
    """
    Generates a list of activities for a specific member, adjusting the activity data
    based on the member's age, registration year, and other factors.

    Args:
        member (Member): The member for whom activities are being generated.
        activity_names (List[str]): A list of activity names to check.
        calendar_year (int): The year in which activities are taking place.
        age_group_data (dict): The dictionary containing data about age groups.
        weekend_data (dict): The dictionary containing data about weekends and camps.
        max_age (int): The maximum age allowed for a member to participate in activities.

    Returns:
        Activities: An `Activities` object containing the adapted activities for the member.

    Raises:
        KeyError: If an age group or activity name cannot be found in `weekend_data`.
        ValueError: If there is an issue with determining the age group or adjusting activities.
    """
    try:
        old_year = f"{calendar_year - 1}/{calendar_year}"
        new_year = f"{calendar_year}/{calendar_year + 1}"
        all_activities = Activities()

        for activity_to_check in activity_names:
            # Determine the age group based on the activity's year
            age_group = ""
            if old_year in activity_to_check:
                age_group = determine_age_group(
                    age_group_data, member.registration_year
                )
            elif new_year in activity_to_check:
                age_group = determine_age_group(
                    age_group_data, member.registration_year - 1
                )

            if not age_group:
                raise ValueError(
                    f"Could not determine age group for {activity_to_check}"
                )

            # Scouts-specific logic for precamp determination
            full_camp = True  # Default value (no changes required to activity)
            if (
                "kamp" in activity_to_check.lower()
                and (age_group == "jonggivers" or age_group == "givers")
                and age_group
                == determine_age_group(age_group_data, member.registration_year - 1)
            ):
                full_camp = False

            # Deepcopy the weekend data to avoid altering the original data
            if activity_to_check not in weekend_data[age_group]:
                raise KeyError(
                    f"Activity '{activity_to_check}' not found for age group '{age_group}'."
                )

            adapted_activity = adapt_activity_data_to_member(
                deepcopy(weekend_data[age_group][activity_to_check]),
                member,
                full_camp,
                max_age,
            )

            if adapted_activity:
                all_activities.add_activity(adapted_activity)

        return all_activities

    except KeyError as e:
        logging.error(f"Error accessing data: {e}")
        raise

    except ValueError as e:
        logging.error(f"Value error occurred: {e}")
        raise

    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise


def generate_tax_certificates():
    """
    Generates tax certificates for members based on user configuration, activity data,
    and presence data. Tax certificates are saved as PDF files.

    Raises:
        KeyError: If a required key is missing from the `user_config`.
        FileNotFoundError: If a required file (CSV, template, etc.) is not found.
        Exception: For any unexpected errors during the process.
    """
    try:
        # A. Generate Tax Certificate template
        logging.info("Loading user configuration.")
        user_config = load_config("user_config.json")

        logging.info("Generating tax certificate template file.")
        template_file_name = generate_tax_certificate_template(
            user_config["tax_certificate"]["template_file_name"],
            read_tax_certificate_template_data(user_config),
        )
        max_age_for_certificate = user_config["tax_certificate"]["max_age"]

        # B. Preprocess spreadsheet information and API setup

        ### I. Create dictionary with activity data (Weekenddata)
        logging.info("Reading activity data from CSV.")
        activity_data = read_activity_data(user_config["csv_files"]["activity_data"])

        ### II. Generate dictionary with age group data
        logging.info("Generating age group data.")
        age_group_config_data, first_registration_year = read_age_group_data(
            user_config
        )
        age_group_data = generate_age_group_data(
            age_group_config_data, first_registration_year
        )
        calendar_year = user_config["organisation"]["calendar_year"]

        ### III. Load Spreadsheet with presence data (Aanwezigheden)
        logging.info("Reading presence data from CSV.")
        presence_data = read_presence_data(user_config["csv_files"]["presence_data"])

        ### TODO IV. Establish connection with Groepsadmin API
        logging.info("Skipping API connection setup for now (TODO).")

        # C. Generate Tax Certificate for every member
        serial_number = (
            int(calendar_year) * 1000
            + user_config["tax_certificate"]["next_serial_number"]
        )
        logging.info(
            f"Starting certificate generation with serial number {serial_number}."
        )

        for member_name in presence_data.keys():
            ### TODO I. Retrieve member information from Groepsadmin API
            address = Address("street", 1, 0000, "city")
            parent = Person("last name", "first name", address)
            member = Member(
                "last name", "first name", address, date(2000, 1, 1), 2011, False
            )

            ### II. Generate activities for member
            all_activities = generate_activities_for_member(
                member,
                presence_data[member_name],
                calendar_year,
                age_group_data,
                activity_data,
                max_age_for_certificate,
            )

            ### III. Write data to Tax Certificate template
            tax_certificate = TaxCertificate(
                serial_number, parent, member, all_activities
            )
            document = Document(template_file_name)
            write_tax_certificate(document, tax_certificate)

            file_name = os.path.join(
                os.getcwd(),
                "attesten",
                f"{member.full_name}.docx",
            )

            document.save(file_name)
            convert_to_pdf(file_name)
            os.remove(file_name)

            logging.info(f"Tax certificate generation complete for {member.full_name}.")
            serial_number += 1
            break

    except KeyError as e:
        logging.error(f"Missing configuration key: {e}")
        raise

    except FileNotFoundError as e:
        exit(-1)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise


# ANSI escape sequences for colors
class ColorFormatter(logging.Formatter):
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    COLORS = {
        logging.DEBUG: BLUE,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: MAGENTA,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


# Set up the logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG

# Create console handler
ch = logging.StreamHandler()

# Set the color formatter for the console handler
formatter = ColorFormatter(
    fmt="%(asctime)s - %(levelname)s: %(message)s",  # Indentation for all levels
)
ch.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(ch)

generate_tax_certificates()
