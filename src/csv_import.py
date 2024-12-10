import logging
import pandas as pd

from data_classes import Activity
from utils import parse_date


def read_activity_data(csv_file: str) -> dict:
    """
    Reads activity data from a CSV file and returns it as a dictionary.
    Each age group is associated with multiple activities containing start date, end date, and price information.

    Args:
        csv_file (str): The path to the CSV file containing activity data.

    Returns:
        dict: A nested dictionary where each age group is a key and its value is another dictionary of activities.
              Each activity has a name (key) and an `Activity` object (value) containing the start date, end date, and price.

    Raises:
        FileNotFoundError: If the CSV file cannot be found at the provided path.
        ValueError: If any of the start date, end date, or price cannot be properly parsed.
        TypeError: If the `csv_file` argument is not a string.
        Warning: Logs a warning if any required field for an activity (start date, end date, or price) is missing.
    """
    logging.debug(f"Reading activity data from {csv_file}")

    if not isinstance(csv_file, str):
        raise TypeError(
            "The 'csv_file' argument must be a string representing the path to the CSV file."
        )

    ROW_INCREMENT = 3
    # Read the CSV file into a pandas DataFrame
    try:
        csv_data = pd.read_csv(csv_file, header=None)
    except FileNotFoundError | pd.errors.EmptyDataError:
        logging.error(f"Error: CSV file '{csv_file}' not found.")
        raise  # Re-raise the exception after logging the error

    # Initialize the activity data dictionary
    activity_data = {}

    # Extract column headers (activities) from the second row (index 0), skipping the first column (group names)
    activities = csv_data.iloc[0, 1:].tolist()
    logging.debug(f"Activities found: {activities}")

    # Iterate through the groups and activities
    for row in range(
        1, len(csv_data), ROW_INCREMENT
    ):  # Step by 3 rows (start date, end date, and price)
        age_group_name = csv_data.iloc[row, 0]  # Group name is in the first column

        if pd.isna(age_group_name):
            continue  # Skip rows with no group name

        # Initialize the data structure for the group
        activity_data[age_group_name.lower()] = {}

        # Iterate over each activity and populate the dictionary
        for index, activity_name in enumerate(activities):
            col = index + 1
            if pd.isna(activity_name):
                continue  # Skip if there's no activity name in the column

            try:
                # Get the start date, end date, and price for the current activity directly
                start_date = (
                    csv_data.iloc[row, col]
                    if not pd.isna(csv_data.iloc[row, col])
                    else None
                )
                end_date = (
                    csv_data.iloc[row + 1, col]
                    if not pd.isna(csv_data.iloc[row + 1, col])
                    else None
                )
                price = (
                    csv_data.iloc[row + 2, col]
                    if not pd.isna(csv_data.iloc[row + 2, col])
                    else None
                )

                if start_date is None or end_date is None or price is None:
                    logging.warning(
                        f"Missing activity data for age group: {age_group_name} and activity: {activity_name}"
                    )
                    continue  # Skip this row if any critical field is empty

                # Add an Activity object to the dictionary
                activity_data[age_group_name.lower()][activity_name.lower()] = Activity(
                    parse_date(start_date), parse_date(end_date), float(price)
                )

            except ValueError as e:
                logging.error(
                    f"Error parsing activity data for {activity_name} in age group {age_group_name}: {e}"
                )
                raise  # Raise a ValueError if parsing fails
            except Exception as e:
                logging.error(
                    f"Unexpected error for activity '{activity_name}' in group '{age_group_name}': {e}"
                )
                raise  # Raise any other unexpected errors

    return activity_data


def read_presence_data(csv_file: str) -> dict:
    """
    Reads presence data from a CSV file and returns it as a dictionary.
    Each member is associated with a list of activities they attended.

    Args:
        csv_file (str): The path to the CSV file containing presence data.

    Returns:
        dict: A dictionary where the keys are member names (in lowercase) and the values
              are lists of activity names (in lowercase) that the member attended.

    Raises:
        FileNotFoundError: If the CSV file cannot be found at the provided path.
        TypeError: If the `csv_file` argument is not a string.
        Warning: Logs a warning if any member has no activities recorded.
    """

    if not isinstance(csv_file, str):
        logging.error(
            "The 'csv_file' argument must be a string representing the path to the CSV file."
        )
        raise TypeError()

    # Try to read the CSV file into a pandas DataFrame
    try:
        csv_data = pd.read_csv(csv_file, header=None)
    except FileNotFoundError:
        logging.error(f"Error: CSV file '{csv_file}' not found.")
        raise  # Re-raise the exception after logging the error

    presence_data = {}

    # Iterate over rows starting from the second row (index 1) to read member data
    for row in range(1, len(csv_data)):
        member_name = csv_data.iloc[
            row, 0
        ]  # First column contains the name of the member

        if pd.isna(member_name):
            logging.warning(f"Skipping row {row + 1}: No member name found.")
            continue  # Skip rows with no member name

        # Initialize a list to store activities for this member
        activities = []

        # Iterate over the columns starting from the second column (index 1)
        for col in range(1, csv_data.shape[1]):
            # Check if the member is present for the activity (non-null value)
            if pd.notna(csv_data.iloc[row, col]):
                # Append the activity name (from the first row) in lowercase
                activity_name = csv_data.iloc[0, col]
                if pd.isna(activity_name):
                    logging.error(
                        f"Skipping column {col + 1}: No activity name found in the header."
                    )
                    continue
                activities.append(activity_name.lower())

        # If the member has any activities, add them to the presence data
        if activities:
            presence_data[member_name.lower()] = activities

    return presence_data
