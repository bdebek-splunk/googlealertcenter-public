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
from soar_sdk.params import Param, Params


class ListAlertsParams(Params):
    customerId: str = Param(
        description="Customer ID in format C01234567. This overrides the customer ID in the asset.",
        required=False,
    )
    filter: str = Param(
        description="Filter expression for alert retrieval.", required=False
    )
    pageSize: str = Param(
        description="Maximum number of alerts to return.", required=False
    )
    orderBy: str = Param(description="Field to order alerts by.", required=False)


class GetAlertParams(Params):
    alertId: str = Param(description="ID of the alert to retrieve", required=True)
    customerId: str = Param(
        description="Customer ID in format C01234567. This overrides the customer ID in the asset.",
        required=False,
    )
