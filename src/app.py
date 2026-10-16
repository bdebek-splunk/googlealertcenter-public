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
import re
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


def _soar_severity(alert: dict) -> str:
    google_severity = (alert.get("metadata") or {}).get("severity", "")
    return {
        "HIGH": "high",
        "MEDIUM": "medium",
        "LOW": "low",
    }.get(str(google_severity).upper(), "medium")


def _alert_to_cef(alert: dict) -> dict[str, str]:
    metadata = alert.get("metadata") or {}
    cef = {
        "externalId": alert.get("alertId"),
        "deviceVendor": "Google",
        "deviceProduct": "Alert Center",
        "deviceEventCategory": alert.get("type"),
        "sourceServiceName": alert.get("source"),
        "startTime": alert.get("startTime"),
        "endTime": alert.get("endTime"),
        "receiptTime": alert.get("createTime"),
    }

    custom_fields = (
        ("Google Customer ID", alert.get("customerId")),
        ("Alert Status", metadata.get("status")),
        ("Alert Assignee", metadata.get("assignee")),
    )
    for index, (label, value) in enumerate(custom_fields, start=1):
        if value not in (None, ""):
            cef[f"deviceCustomString{index}"] = str(value)
            cef[f"deviceCustomString{index}Label"] = label

    cef.update(_flatten_cef_values(alert.get("data"), "googleAlertData"))
    return {key: str(value) for key, value in cef.items() if value not in (None, "")}


def _flatten_cef_values(value: object, prefix: str) -> dict[str, str]:
    if isinstance(value, dict):
        flattened = {}
        for key, nested_value in value.items():
            safe_key = re.sub(r"[^A-Za-z0-9_]", "_", str(key))
            if safe_key:
                flattened.update(
                    _flatten_cef_values(nested_value, f"{prefix}_{safe_key}")
                )
        return flattened
    if value is None:
        return {}
    if isinstance(value, list):
        return {prefix: json.dumps(value, ensure_ascii=False)}
    return {prefix: str(value)}


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


def _resolve_customer_id(
    action_customer_id: str | None, asset_customer_id: str | None
) -> str | None:
    customer_id = action_customer_id or asset_customer_id
    return customer_id.lstrip("C") if customer_id else None


def _paginate(
    soar: SOARClient, asset: Asset, params: OnPollParams, service
) -> tuple[list[dict], dict | None]:
    last_polled_time = asset.cache_state.get("last_polled_time")
    parameters = {}

    # Add customer ID if available
    if asset.customer_id:
        parameters["customerId"] = asset.customer_id.lstrip("C")

    if not last_polled_time:
        # If we don't have a last polled time, default to polling alerts from the last 24 hours
        yesterday_date = dt.datetime.now(dt.UTC) - dt.timedelta(days=1)
        last_polled_time = yesterday_date.isoformat()
        logger.info(
            f"No last polled time found in cache, defaulting to polling alerts from the last 24 hours: {last_polled_time}"
        )

    limit = int(params.artifact_count) if params.artifact_count else None

    # Manual polls are intentionally independent of the scheduled poll cursor.
    if params.is_manual_poll():
        alert_list = []
        page_token = None
        if limit:
            parameters["pageSize"] = min(limit, 100)

        while True:
            try:
                request_parameters = parameters.copy()
                if page_token:
                    request_parameters["pageToken"] = page_token
                response = service.alerts().list(**request_parameters).execute()
                page_alerts = response.get("alerts", [])
                alert_list.extend(page_alerts)
                if limit and len(alert_list) >= limit:
                    return alert_list[:limit], None
                page_token = response.get("nextPageToken")
                if not page_token:
                    break
            except Exception as e:
                raise ActionFailure(
                    f"Error paginating through alerts from Google Alert Center: {e!s}"
                ) from e

        return alert_list, None

    parameters["filter"] = f'createTime > "{last_polled_time}"'
    parameters["orderBy"] = "createTime asc"
    if limit:
        parameters["pageSize"] = min(limit, 100)

    pending_alerts = list(asset.cache_state.get("pending_alerts", []))
    page_token = asset.cache_state.get("page_token")
    latest_alert_time = asset.cache_state.get("poll_latest_time", last_polled_time)
    alert_list = []

    logger.debug(f"Starting pagination with parameters: {parameters}")

    while not limit or len(alert_list) < limit:
        try:
            if not pending_alerts:
                request_parameters = parameters.copy()
                if page_token:
                    request_parameters["pageToken"] = page_token

                response = service.alerts().list(**request_parameters).execute()
                pending_alerts = response.get("alerts", [])
                page_token = response.get("nextPageToken")
                logger.info(
                    f"Polled {len(pending_alerts)} alerts from Google Alert Center"
                )

                if not pending_alerts and not page_token:
                    logger.info("No more pages to fetch, stopping pagination")
                    break

            remaining_capacity = limit - len(alert_list) if limit else len(
                pending_alerts
            )
            page_alerts = pending_alerts[:remaining_capacity]
            pending_alerts = pending_alerts[remaining_capacity:]
            alert_list.extend(page_alerts)

            for alert in page_alerts:
                alert_time = alert.get("createTime")
                if alert_time and (
                    not latest_alert_time
                    or _parse_time(alert_time) > _parse_time(latest_alert_time)
                ):
                    latest_alert_time = alert_time
        except Exception as e:
            raise ActionFailure(
                f"Error paginating through alerts from Google Alert Center: {e!s}"
            ) from e

    has_more_alerts = bool(pending_alerts or page_token)
    next_poll_state = {
        "last_polled_time": last_polled_time,
        "pending_alerts": pending_alerts if has_more_alerts else [],
        "page_token": page_token if has_more_alerts else None,
        "poll_latest_time": latest_alert_time if has_more_alerts else None,
    }
    if not has_more_alerts:
        next_poll_state["last_polled_time"] = latest_alert_time

    return alert_list, next_poll_state


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


@app.action(read_only=True)
def list_alerts(
    params: ListAlertsParams, asset: Asset, soar: SOARClient
) -> ListAlertsOutput:
    """List alerts from Google Alert Center."""
    credentials = _load_credentials(soar, asset)
    service = build("alertcenter", "v1beta1", credentials=credentials)

    # Build params for API call based on requirements
    parameters = {}
    if params.pageSize is not None:
        if params.pageSize < 1:
            raise ActionFailure("pageSize must be a positive integer")
        parameters["pageSize"] = params.pageSize
    if params.orderBy:
        parameters["orderBy"] = params.orderBy
    if params.filter:
        parameters["filter"] = params.filter
    customer_id = _resolve_customer_id(params.customerId, asset.customer_id)
    if customer_id:
        parameters["customerId"] = customer_id

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


@app.action(read_only=True)
def get_alert(
    params: GetAlertParams,
    asset: Asset,
    soar: SOARClient,
) -> AlertDetails:
    """Retrieve an alert by its ID."""
    credentials = _load_credentials(soar, asset)
    alert_id = params.alertId
    service = build("alertcenter", "v1beta1", credentials=credentials)
    parameters = {"alertId": alert_id}
    customer_id = _resolve_customer_id(params.customerId, asset.customer_id)
    if customer_id:
        parameters["customerId"] = customer_id

    try:
        response = service.alerts().get(**parameters).execute()
        return AlertDetails(**response)
    except Exception as e:
        raise ActionFailure(
            f"Error retrieving alert with ID {alert_id} from Google Alert Center: {e!s}"
        ) from e


@app.action(read_only=False)
def delete_alert(
    params: GetAlertParams,
    asset: Asset,
    soar: SOARClient,
) -> ActionOutput:
    """Mark an alert for deletion in Google Alert Center."""
    credentials = _load_credentials(soar, asset)
    alert_id = params.alertId
    service = build("alertcenter", "v1beta1", credentials=credentials)
    parameters = {"alertId": alert_id}
    customer_id = _resolve_customer_id(params.customerId, asset.customer_id)
    if customer_id:
        parameters["customerId"] = customer_id

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
    alerts, next_poll_state = _paginate(soar, asset, params, service)
    if alerts:
        logger.info(f"Found {len(alerts)} alerts from Google Alert Center")

        # Create one container and artifact per alert
        for alert in alerts:
            alert_id = alert.get("alertId", "unknown_alert_id")
            severity = _soar_severity(alert)

            # Yield container first
            yield Container(
                name=f"Google Alert {alert_id}",
                description=f"Alert from Google Alert Center - ID: {alert_id}",
                source_data_identifier=alert_id,
                severity=severity,
            )

            # Then immediately yield the artifact(s) for this container
            # All artifacts yielded after a container belong to that container
            # until the next container is yielded
            artifact = Artifact(
                name=f"Alert {alert_id}",
                description=f"Alert with ID {alert_id} polled from Google Alert Center",
                severity=severity,
                source_data_identifier=alert_id,
                type="alert",
                data=alert,
                cef=_alert_to_cef(alert),
                run_automation=True,
            )
            yield artifact

    if next_poll_state is not None:
        asset.cache_state.update(next_poll_state)
        logger.info(
            "Google Alerts Connector: Saved polling progress; checkpoint is "
            f"{asset.cache_state.get('last_polled_time')}"
        )


if __name__ == "__main__":
    app.cli()
