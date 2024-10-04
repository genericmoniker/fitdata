"""Data from the Fitbit API.

A note on "creds" parameters:

The dict is expected to have these keys:
    - client_id
    - client_secret
    - authorization_code

It may also have these keys, and they may be updated during function calls:
    - access_token
    - refresh_token
"""

from base64 import b64encode
from datetime import datetime

import httpx


class CredentialsError(Exception):
    """Credentials are invalid (e.g. empty or expired)."""


def get_spo2(creds: dict, date: datetime, end: datetime | None = None) -> list[dict]:
    """Get SpO2 data for a day or date range.

    If end is not provided, the data for a single day is returned. If end is provided,
    the data for a range of days is returned.

    SpO2 applies specifically to a user’s “main sleep”, which is the longest single
    period of time asleep on a given date.

    The measurement is provided at the end of a period of sleep. The data returned
    usually reflects a sleep period that began the day before. For example, if you
    request SpO2 levels for 2021-12-22, it may include measurements that were taken the
    previous night on 2021-12-21 when the user fell asleep.

    The data returned includes average, minimum, and maximum SpO2 levels.

    Example:

    [{'dateTime': '2024-10-02', 'value': {'avg': 94.2, 'min': 89.0, 'max': 98.1}}]
    """
    end = end or date
    date_str = date.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")
    url_path = f"spo2/date/{date_str}/{end_str}.json"
    return _api_request(creds, url_path)


def _api_request(creds: dict, url_path: str) -> list[dict]:
    """Make a request to the Fitbit API.

    If the request fails due to an expired access token, the token is refreshed, the
    creds dict is updated and the request is retried.
    """
    if not creds:
        raise CredentialsError
    access_token = creds.get("access_token", "")
    with httpx.Client(timeout=10) as client:
        url = "https://api.fitbit.com/1/user/-/" + url_path
        try:
            return _do_resource_get(client, access_token, url)
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 401:  # noqa: PLR2004
                try:
                    access_token = _refresh_access_token(client, creds)
                    return _do_resource_get(client, access_token, url)
                except httpx.HTTPStatusError as ex:
                    raise CredentialsError(ex.response.json()) from ex
            raise


def get_access_token(
    client: httpx.Client,
    authorization_code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> tuple[str, str]:
    """Exchange an authorization code for an access token and refresh token.

    The return value is a tuple of (access_token, refresh_token).

    https://dev.fitbit.com/build/reference/web-api/oauth2/#access_token-request
    """
    post_data = {
        "code": authorization_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    data = _do_auth_post(client, client_id, client_secret, post_data)
    return data["access_token"], data["refresh_token"]


def _refresh_access_token(client: httpx.Client, creds: dict) -> str:
    """Exchange a refresh token for a new access token and refresh token.

    The creds dict is updated with the new tokens, and the new access token is
    also returned.

    https://dev.fitbit.com/build/reference/web-api/oauth2/#refreshing-tokens
    """
    post_data = {
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token",
    }
    data = _do_auth_post(
        client,
        creds["client_id"],
        creds["client_secret"],
        post_data,
    )
    creds["access_token"] = data["access_token"]
    creds["refresh_token"] = data["refresh_token"]
    return data["access_token"]


def _do_resource_get(
    client: httpx.Client,
    access_token: str,
    url: str,
) -> list[dict]:
    """Make a GET request to the resource server."""
    headers = {"Authorization": "Bearer " + access_token}
    response = client.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def _do_auth_post(
    client: httpx.Client,
    client_id: str,
    client_secret: str,
    post_data: dict,
) -> dict:
    """Make a POST request to the authorization server."""
    url = "https://api.fitbit.com/oauth2/token"
    auth_value = b64encode(f"{client_id}:{client_secret}".encode())
    headers = {"Authorization": "Basic " + auth_value.decode()}
    response = client.post(url, headers=headers, data=post_data)
    response.raise_for_status()
    return response.json()
