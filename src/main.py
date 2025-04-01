import logging
from docx import Document
from docx2pdf import convert as convert_to_pdf
import os

from config import load_config, read_tax_certificate_template_data
from data_classes import *
from word_export import write_tax_certificate_template, write_tax_certificate
import test_data


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

        calendar_year = user_config["organisation"]["calendar_year"]

        # B. Get presence data from Groepsadmin API
        # TODO get call to API
        presence_data_array = [
            {
                "member": test_data.member,
                "parent": test_data.parent,
                "activities": test_data.activities,
            }
        ]

        # C. Generate Tax Certificate for every member
        serial_number = (
            int(calendar_year) * 1000
            + user_config["tax_certificate"]["next_serial_number"]
        )
        logging.info(
            f"Starting certificate generation with serial number {serial_number}."
        )

        for presence_data in presence_data_array:
            member = presence_data["member"]
            parent = presence_data["parent"]
            all_activities = presence_data["activities"]

            ### I. Write data to Tax Certificate template
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
