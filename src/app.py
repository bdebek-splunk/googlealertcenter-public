# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import datetime as dt
import json
from collections.abc import Iterator

from google.oauth2 import service_account
from googleapiclient.discovery import build
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput
from soar_sdk.app import App
from soar_sdk.asset import AssetField, BaseAsset
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.models.artifact import Artifact
from soar_sdk.models.container import Container
from soar_sdk.params import OnPollParams

from .consts import GOOGLE_API_SCOPES
from .outputs import AlertDetails, ListAlertsOutput
from .params import GetAlertParams, ListAlertsParams


logger = getLogger()


def _parse_time(t: str) -> dt.datetime:
    return dt.datetime.fromisoformat(t.replace("Z", "+00:00"))


class Asset(BaseAsset):
    key_json: str = AssetField(
        required=True,
        description="Contents of Service Account JSON file",
        sensitive=True,
    )
    delegated_account_email: str = AssetField(
        required=True, description="Email of the account to impersonate"
    )
    customer_id: str = AssetField(
        required=False, description="Customer ID in format C01234567."
    )


app = App(
    name="googlealertcenter",
    app_type="endpoint",
    logo="googlealertcenter.svg",
    logo_dark="googlealertcenter_dark.svg",
    product_vendor="Google",
    product_name="Google Alert Center",
    publisher="Splunk",
    appid="ebdef3dd-f65d-4c50-898f-f26d60c36390",
    fips_compliant=False,
    asset_cls=Asset,
)


def _load_credentials(
    soar: SOARClient, asset: Asset
) -> service_account.Credentials | None:
    try:
        service_account_json = json.loads(asset.key_json)
    except json.decoder.JSONDecodeError as e:
        raise ActionFailure("Service Account JSON is not valid JSON") from e

    try:
        credentials = service_account.Credentials.from_service_account_info(
            service_account_json, scopes=GOOGLE_API_SCOPES
        )
        delegated = credentials.with_subject(asset.delegated_account_email)
    except Exception as e:
        raise ActionFailure(
            f"Error creating credentials from Service Account JSON: {e!s}"
        ) from e
    return delegated


def _paginate(
    soar: SOARClient, asset: Asset, params: OnPollParams, service
) -> list[dict]:
    last_polled_time = asset.cache_state.get("last_polled_time")
    page_token = None
    alert_list = []
    parameters = {}

    # Add customer ID if available
    if asset.customer_id:
        parameters["customerId"] = asset.customer_id.lstrip("C")

    if not last_polled_time:
        # If we don't have a last polled time, default to polling alerts from the last 24 hours
        yesterday_date = dt.datetime.now(dt.UTC) - dt.timedelta(days=1)
        last_polled_time = yesterday_date.isoformat()
        asset.cache_state["last_polled_time"] = last_polled_time
        logger.info(
            f"No last polled time found in cache, defaulting to polling alerts from the last 24 hours: {last_polled_time}"
        )

    if not params.is_manual_poll() and last_polled_time:
        parameters["filter"] = f'createTime > "{last_polled_time}"'

    if params.artifact_count:
        parameters["pageSize"] = min(int(params.artifact_count), 100)

    logger.debug(f"Starting pagination with parameters: {parameters}")

    while True:
        try:
            # Add page token to parameters if we have one
            if page_token:
                parameters["pageToken"] = page_token

            response = service.alerts().list(**parameters).execute()
            alerts = response.get("alerts", [])
            logger.info(f"Polled {len(alerts)} alerts from Google Alert Center")

            for alert in alerts:
                alert_list.append(alert)
                # Stop if we've reached the artifact count limit
                if params.artifact_count and len(alert_list) >= int(
                    params.artifact_count
                ):
                    logger.info(
                        f"Reached artifact count limit of {params.artifact_count}"
                    )
                    return alert_list[: int(params.artifact_count)]

            # Get next page token
            page_token = response.get("nextPageToken")
            if not page_token:
                logger.info("No more pages to fetch, stopping pagination")
                break

        except Exception as e:
            raise ActionFailure(
                f"Error paginating through alerts from Google Alert Center: {e!s}"
            ) from e

    return alert_list


@app.test_connectivity()
def test_connectivity(soar: SOARClient, asset: Asset) -> None:
    credentials = _load_credentials(soar, asset)
    service = build("alertcenter", "v1beta1", credentials=credentials)
    try:
        service.alerts().list(pageSize=1).execute()
    except Exception as e:
        raise ActionFailure(
            f"Error testing connectivity to Google Alert Center: {e!s}"
        ) from e


@app.action()
def list_alerts(
    params: ListAlertsParams, asset: Asset, soar: SOARClient
) -> ListAlertsOutput:
    credentials = _load_credentials(soar, asset)
    service = build("alertcenter", "v1beta1", credentials=credentials)

    # Build params for API call based on requirements
    parameters = {}
    if params.pageSize:
        parameters["pageSize"] = int(params.pageSize)
    if params.orderBy:
        parameters["orderBy"] = params.orderBy
    if params.filter:
        parameters["filter"] = params.filter
    if params.customerId:
        parameters["customerId"] = params.customerId.lstrip("C")
    elif asset.customer_id:
        parameters["customerId"] = asset.customer_id.lstrip("C")
    else:
        raise ActionFailure(
            "Customer ID must be provided either in the asset or as a parameter"
        )

    try:
        response = service.alerts().list(**parameters).execute()
        alerts = response.get("alerts", [])
        logger.info(
            f"Listed {len(alerts)} alerts from Google Alert Center with parameters: {parameters}"
        )
        return ListAlertsOutput(data=alerts)
    except Exception as e:
        raise ActionFailure(
            f"Error listing alerts from Google Alert Center: {e!s}"
        ) from e


@app.action()
def get_alert(
    params: GetAlertParams,
    asset: Asset,
    soar: SOARClient,
) -> AlertDetails:
    credentials = _load_credentials(soar, asset)
    alert_id = params.alertId
    customer_id = (
        params.customerId.lstrip("C")
        if params.customerId
        else asset.customer_id.lstrip("C")
    )
    service = build("alertcenter", "v1beta1", credentials=credentials)
    parameters = {"alertId": alert_id, "customerId": customer_id}

    try:
        response = service.alerts().get(**parameters).execute()
        return AlertDetails(**response)
    except Exception as e:
        raise ActionFailure(
            f"Error retrieving alert with ID {alert_id} from Google Alert Center: {e!s}"
        ) from e


@app.action()
def delete_alert(
    params: GetAlertParams,
    asset: Asset,
    soar: SOARClient,
) -> ActionOutput:
    credentials = _load_credentials(soar, asset)
    alert_id = params.alertId
    customer_id = (
        params.customerId.lstrip("C")
        if params.customerId
        else asset.customer_id.lstrip("C")
    )
    service = build("alertcenter", "v1beta1", credentials=credentials)
    parameters = {"alertId": alert_id, "customerId": customer_id}

    try:
        service.alerts().delete(**parameters).execute()
        logger.info(f"Deleted alert with ID {alert_id} from Google Alert Center")
    except Exception as e:
        raise ActionFailure(
            f"Error deleting alert with ID {alert_id} from Google Alert Center: {e}"
        ) from e
    soar.set_message(f"Deleted alert with ID {alert_id} from Google Alert Center")
    return ActionOutput()


@app.on_poll()
def on_poll(
    params: OnPollParams, asset: Asset, soar: SOARClient
) -> Iterator[Container | Artifact]:
    credentials = _load_credentials(soar, asset)
    service = build("alertcenter", "v1beta1", credentials=credentials)
    alerts = _paginate(soar, asset, params, service)
    if alerts:
        logger.info(f"Found {len(alerts)} alerts from Google Alert Center")

        # Create one container and artifact per alert
        for alert in alerts:
            alert_id = alert.get("alertId", "unknown_alert_id")

            # Yield container first
            yield Container(
                name=f"Google Alert {alert_id}",
                description=f"Alert from Google Alert Center - ID: {alert_id}",
                severity="medium",
            )

            # Then immediately yield the artifact(s) for this container
            # All artifacts yielded after a container belong to that container
            # until the next container is yielded
            artifact = Artifact(
                name=f"Alert {alert_id}",
                description=f"Alert with ID {alert_id} polled from Google Alert Center",
                severity="medium",
                source_data_identifier=alert_id,
                type="network",
                data=alert,
                cef=alert,
                run_automation=True,
            )
            yield artifact

        # Save last polled time to cache
        if not params.is_manual_poll():
            latest_alert_time = max(alert.get("createTime", "") for alert in alerts)
            current_last_polled = asset.cache_state.get("last_polled_time", "")

            if latest_alert_time and _parse_time(latest_alert_time) > _parse_time(
                current_last_polled
            ):
                asset.cache_state["last_polled_time"] = latest_alert_time
                logger.info(
                    f"Google Alerts Connector: Updated last polled time to {latest_alert_time}"
                )
            else:
                logger.info(
                    f"Google Alerts Connector: No new alerts found that are newer than the last polled time - {current_last_polled}, not updating cache"
                )


if __name__ == "__main__":
    app.cli()
