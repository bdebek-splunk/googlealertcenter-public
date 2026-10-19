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
import json

from pydantic import field_validator
from soar_sdk.action_results import ActionOutput


class AlertMetadata(ActionOutput):
    customerId: str = ""
    alertId: str = ""
    status: str = ""
    assignee: str = ""
    updateTime: str = ""
    severity: str = ""
    etag: str = ""


class AlertDetails(ActionOutput):
    alertId: str = ""
    customerId: str = ""
    createTime: str = ""
    startTime: str = ""
    endTime: str = ""
    type: str = ""
    source: str = ""
    securityInvestigationToolLink: str = ""
    deleted: bool = False
    updateTime: str = ""
    etag: str = ""
    metadata: AlertMetadata | None = None
    data: str | None = None

    @field_validator("data", mode="before")
    @classmethod
    def serialize_type_specific_data(cls, value: object) -> str | None:
        if value is None or isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)


class ListAlertsOutput(ActionOutput):
    data: list[AlertDetails]
