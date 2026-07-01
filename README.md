# googlealertcenter

Publisher: Splunk <br>
Connector Version: 1.0.0 <br>
Product Vendor: Google <br>
Product Name: Google Alert Center <br>
Minimum Product Version: 7.0.0

App integrates with Google Alert Center API

### Configuration variables

This table lists the configuration variables required to operate googlealertcenter. These variables are specified when configuring a Google Alert Center asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**key_json** | required | password | Contents of Service Account JSON file |
**delegated_account_email** | required | string | Email of the account to impersonate |
**customer_id** | optional | string | Customer ID in format C01234567. |

### Supported Actions

[test connectivity](#action-test-connectivity) - test connectivity <br>
[list alerts](#action-list-alerts) - list alerts <br>
[get alert](#action-get-alert) - get alert <br>
[delete alert](#action-delete-alert) - delete alert <br>
[on poll](#action-on-poll) - on poll

## action: 'test connectivity'

test connectivity

Type: **test** <br>
Read only: **True**

Basic test for app.

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'list alerts'

list alerts

Type: **generic** <br>
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**customerId** | optional | Customer ID in format C01234567. This overrides the customer ID in the asset. | string | |
**filter** | optional | Filter expression for alert retrieval. | string | |
**pageSize** | optional | Maximum number of alerts to return. | string | |
**orderBy** | optional | Field to order alerts by. | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.customerId | string | | |
action_result.parameter.filter | string | | |
action_result.parameter.pageSize | string | | |
action_result.parameter.orderBy | string | | |
action_result.data.\*.data.\*.alertId | string | | |
action_result.data.\*.data.\*.customerId | string | | |
action_result.data.\*.data.\*.createTime | string | | |
action_result.data.\*.data.\*.startTime | string | | |
action_result.data.\*.data.\*.endTime | string | | |
action_result.data.\*.data.\*.type | string | | |
action_result.data.\*.data.\*.source | string | | |
action_result.data.\*.data.\*.securityInverstigationToolLink | string | | |
action_result.data.\*.data.\*.deleted | string | | |
action_result.data.\*.data.\*.updateTime | string | | |
action_result.data.\*.data.\*.etag | string | | |
action_result.data.\*.data.\*.metadata.customerId | string | | |
action_result.data.\*.data.\*.metadata.alertId | string | | |
action_result.data.\*.data.\*.metadata.status | string | | |
action_result.data.\*.data.\*.metadata.assignee | string | | |
action_result.data.\*.data.\*.metadata.updateTime | string | | |
action_result.data.\*.data.\*.metadata.severity | string | | |
action_result.data.\*.data.\*.metadata.etag | string | | |
action_result.data.\*.data.\*.data.deviceId | string | | |
action_result.data.\*.data.\*.data.serialNumber | string | | |
action_result.data.\*.data.\*.data.deviceType | string | | |
action_result.data.\*.data.\*.data.deviceModel | string | | |
action_result.data.\*.data.\*.data.resourceId | string | | |
action_result.data.\*.data.\*.data.iosVendorId | string | | |
action_result.data.\*.data.\*.data.deviceCompromisedState | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get alert'

get alert

Type: **generic** <br>
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alertId** | required | ID of the alert to retrieve | string | |
**customerId** | optional | Customer ID in format C01234567. This overrides the customer ID in the asset. | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.alertId | string | | |
action_result.parameter.customerId | string | | |
action_result.data.\*.alertId | string | | |
action_result.data.\*.customerId | string | | |
action_result.data.\*.createTime | string | | |
action_result.data.\*.startTime | string | | |
action_result.data.\*.endTime | string | | |
action_result.data.\*.type | string | | |
action_result.data.\*.source | string | | |
action_result.data.\*.securityInverstigationToolLink | string | | |
action_result.data.\*.deleted | string | | |
action_result.data.\*.updateTime | string | | |
action_result.data.\*.etag | string | | |
action_result.data.\*.metadata.customerId | string | | |
action_result.data.\*.metadata.alertId | string | | |
action_result.data.\*.metadata.status | string | | |
action_result.data.\*.metadata.assignee | string | | |
action_result.data.\*.metadata.updateTime | string | | |
action_result.data.\*.metadata.severity | string | | |
action_result.data.\*.metadata.etag | string | | |
action_result.data.\*.data.deviceId | string | | |
action_result.data.\*.data.serialNumber | string | | |
action_result.data.\*.data.deviceType | string | | |
action_result.data.\*.data.deviceModel | string | | |
action_result.data.\*.data.resourceId | string | | |
action_result.data.\*.data.iosVendorId | string | | |
action_result.data.\*.data.deviceCompromisedState | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'delete alert'

delete alert

Type: **generic** <br>
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alertId** | required | ID of the alert to retrieve | string | |
**customerId** | optional | Customer ID in format C01234567. This overrides the customer ID in the asset. | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.alertId | string | | |
action_result.parameter.customerId | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'on poll'

on poll

Type: **ingest** <br>
Read only: **True**

Callback action for the on_poll ingest functionality

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**start_time** | optional | Start of time range, in epoch time (milliseconds). | numeric | |
**end_time** | optional | End of time range, in epoch time (milliseconds). | numeric | |
**container_count** | optional | Maximum number of container records to query for. | numeric | |
**artifact_count** | optional | Maximum number of artifact records to query for. | numeric | |
**container_id** | optional | Comma-separated list of container IDs to limit the ingestion to. | string | |

#### Action Output

No Output

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2026 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
