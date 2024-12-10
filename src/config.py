import json
import os
import logging
import marshmallow_dataclass
from marshmallow import ValidationError
from data_classes import Agency, Signature, TaxCertificateTemplate


def load_config(file_path: str = "config.json") -> dict:
    """
    Load a JSON configuration file and return the contents as a dictionary.

    Args:
        file_path (str): Path to the config file. Defaults to 'src/config.json'.

    Returns:
        dict: Configuration data as a dictionary.

    Raises:
        FileNotFoundError: If the file is not found.
        JSONDecodeError: If there is an issue parsing the file.
        PermissionError: If the program lacks permissions to read the file.
        OSError: For other OS-related errors (e.g., issues opening the file).
    """
    logging.debug(f"Attempting to load config file from {file_path}")
    if not os.path.exists(file_path):
        error_msg = f"Configuration file not found: {file_path}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        with open(file_path, "r") as file:
            config = json.load(file)
            logging.debug(f"Config successfully loaded from {file_path}")
            return config
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {file_path}: {e.msg}")
        raise
    except PermissionError as e:
        logging.error(f"Permission denied when trying to read the file: {file_path}")
        raise
    except OSError as e:
        logging.error(f"Error opening or reading the file {file_path}: {e.strerror}")
        raise


def save_config(config: dict, file_path: str = "src\\config.json") -> None:
    """
    Save the configuration to a JSON file.

    Args:
        config (dict): Configuration data to save.
        file_path (str): Path where the config will be saved. Defaults to 'src/config.json'.

    Raises:
        TypeError: If the provided `config` is not a dictionary.
        PermissionError: If the program lacks permissions to write to the file.
        OSError: For other OS-related errors (e.g., issues opening the file).
    """
    logging.debug(f"Saving config to {file_path}")
    if not isinstance(config, dict):
        error_msg = "Invalid config format; expected a dictionary."
        logging.error(error_msg)
        raise TypeError(error_msg)

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as file:
            json.dump(config, file, indent=4)
        logging.debug(f"Config successfully saved to {file_path}")
    except PermissionError as e:
        logging.error(
            f"Permission denied when trying to write to the file: {file_path}"
        )
        raise
    except OSError as e:
        logging.error(f"Error writing to the file {file_path}: {e.strerror}")
        raise


def read_agency(config_data: dict):
    """
    Loads and validates agency configuration data using a Marshmallow schema.

    Args:
        config_data (dict): The dictionary containing agency configuration data.

    Returns:
        Agency: An instance of the Agency class created from the configuration data.

    Raises:
        ValidationError: If the provided configuration data is invalid or doesn't match the schema.
        TypeError: If the provided `config_data` is not a dictionary.
    """
    logging.debug("Attempting to load and convert agency data.")
    if not isinstance(config_data, dict):
        error_msg = "The config_data parameter must be a dictionary."
        logging.error(error_msg)
        raise TypeError(error_msg)

    try:
        # Generate Marshmallow schema for the Agency class
        AgencySchema = marshmallow_dataclass.class_schema(Agency)
        agency: Agency = AgencySchema().load(config_data)
        logging.debug("Succesfully loaded and converted agency data.")
        return agency
    except ValidationError as e:
        logging.error(f"Invalid agency configuration data: {e.messages}")
        raise


def read_signature(config_data: dict):
    """
    Loads and validates signature configuration data using a Marshmallow schema.

    Args:
        config_data (dict): The dictionary containing signature configuration data.

    Returns:
        Signature: An instance of the Signature class created from the configuration data.

    Raises:
        ValidationError: If the provided configuration data is invalid or doesn't match the schema.
        TypeError: If the provided `config_data` is not a dictionary.
    """
    logging.debug("Attempting to load and convert signature data.")
    if not isinstance(config_data, dict):
        error_msg = "The config_data parameter must be a dictionary."
        logging.error(error_msg)
        raise TypeError(error_msg)

    try:
        # Generate Marshmallow schema for the Signature class
        SignatureSchema = marshmallow_dataclass.class_schema(Signature)
        signature: Signature = SignatureSchema().load(config_data)
        logging.debug("Succesfully loaded and converted signature data.")
        return signature
    except ValidationError as e:
        logging.error(f"Invalid signature configuration data: {e.messages}")
        raise


def read_tax_certificate_template_data(user_config: dict):
    """
    Reads the tax certificate template data from the user configuration.

    Args:
        user_config (dict): The dictionary containing the configuration data
                            with keys such as "general_info",
                            "certification_agency", and "certificate_signature".

    Returns:
        TaxCertificateTemplate: An instance of the `TaxCertificateTemplate` class
                                populated with the corresponding agency and signature data.

    Raises:
        KeyError: If any required key is missing in the `user_config`.
        TypeError: If the provided `user_config` is not a dictionary.
    """
    logging.debug("Attempting to load and convert Tax Certificate template data.")
    if not isinstance(user_config, dict):
        error_msg = "The user_config parameter must be a dictionary."
        logging.error(error_msg)
        raise TypeError(error_msg)

    try:
        template: TaxCertificateTemplate = TaxCertificateTemplate(
            read_agency(user_config["organisation"]["general_info"]),
            read_agency(user_config["certification_agency"]),
            read_signature(user_config["organisation"]["certificate_signature"]),
        )
        logging.debug("Succesfully loaded and converted Tax Certificate template data.")
        return template
    except KeyError as e:
        logging.error(f"Missing required configuration key: {e}")
        raise


def read_age_group_data(user_config: dict):
    """
    Reads the age group data and the first registration year from the user configuration.

    Args:
        user_config (dict): The dictionary containing age group data and registration year,
                            with keys such as "takken" (age groups) and "first_registration_year".

    Returns:
        tuple: A tuple containing the age groups (from "takken") and the first registration year.

    Raises:
        KeyError: If any required key is missing in the `user_config`.
        TypeError: If the provided `user_config` is not a dictionary.
    """
    logging.debug("Attempting to load age group data.")
    if not isinstance(user_config, dict):
        error_msg = "The user_config parameter must be a dictionary."
        logging.error(error_msg)
        raise TypeError(error_msg)
    try:
        age_group_config_data: dict = user_config["organisation"]["takken"]
        first_registration_year: int = user_config["organisation"][
            "first_registration_year"
        ]
        logging.debug("Succesfully loaded age group data.")
        return age_group_config_data, first_registration_year
    except KeyError as e:
        logging.error(f"Missing required configuration key: {e}")
        raise
