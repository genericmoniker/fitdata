"""Configure authentication for the Fitbit API and Google Sheets API."""

import json

import gspread

from oauth import authorize, fetch_token
from paths import FITBIT_CREDS, GOOGLE_CREDS, GOOGLE_AUTH


def sheets_auth() -> None:
    print("Google Sheets")
    print("-------------")
    if not GOOGLE_CREDS.is_file():
        print(
            "You need to create a project in the Google Cloud Console and enable the "
            "Google Sheets API. See the project README for instructions."
        )
        exit(1)

    print("Launching your browser to continue authorization...")
    try:
        gspread.oauth(
            credentials_filename=GOOGLE_CREDS,
            authorized_user_filename=GOOGLE_AUTH,
        )
        print("Google Sheets authentication successful!")
    except Exception as ex:
        print(f"Google Sheets authentication failed: {ex}")
        exit(1)


def fitbit_auth() -> None:
    print("Fitbit")
    print("------")
    client_id = input("Enter your Fitbit client ID: ")
    client_secret = input("Enter your Fitbit client secret: ")
    redirect_uri = "http://localhost:8000"
    scope = ["oxygen_saturation"]
    auth_url = "https://www.fitbit.com/oauth2/authorize"
    try:
        response, state = authorize(
            auth_url=auth_url,
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            redirect_uri=redirect_uri,
        )
        token_response = fetch_token(
            token_url="https://api.fitbit.com/oauth2/token",
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            auth_response=response,
            state=state,
        )
        creds = {
            "client_id": client_id,
            "client_secret": client_secret,
            "access_token": token_response["access_token"],
            "refresh_token": token_response["refresh_token"],
        }
        with FITBIT_CREDS.open("w") as creds_file:
            creds_file.write(json.dumps(creds))
        print("Fitbit authentication successful!")
    except Exception as ex:
        print(f"Fitbit authentication failed: {ex}")
        exit(1)


def main() -> None:
    try:
        sheets_auth()
        print()
        fitbit_auth()
    except KeyboardInterrupt:
        print("\nAuthentication canceled.")
        exit(1)


if __name__ == "__main__":
    main()
