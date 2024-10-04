"""Module for reading from and writing to Google Sheets.

This uses the gspread library (https://github.com/burnash/gspread).

Instructions for authentication:
https://docs.gspread.org/en/latest/oauth2.html#for-end-users-using-oauth-client-id
"""

import gspread

from paths import GOOGLE_AUTH, GOOGLE_CREDS


def open_sheet(sheet_name: str) -> gspread.Worksheet:
    """Open the Google Sheet with the given name.

    The sheet must be shared with the email address in the GOOGLE_CREDS file.
    """

    gc = gspread.oauth(
        credentials_filename=GOOGLE_CREDS, authorized_user_filename=GOOGLE_AUTH
    )
    return gc.open(sheet_name).sheet1


def add_spo2_to_sheet(sheet: gspread.Worksheet, spo2_data: list[dict]) -> None:
    """Add SpO2 data to the given Google Sheet.

    The data should be a list of dictionaries with the following keys:
        - dateTime
        - value (a dictionary with keys avg, min, max)
    """

    sheet.append_rows(
        [
            (
                entry["dateTime"],
                entry["value"]["min"],
                entry["value"]["max"],
                entry["value"]["avg"],
            )
            for entry in spo2_data
        ]
    )
