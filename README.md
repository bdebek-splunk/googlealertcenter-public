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
[list alerts](#action-list-alerts) - List alerts from Google Alert Center. <br>
[get alert](#action-get-alert) - Retrieve an alert by its ID. <br>
[delete alert](#action-delete-alert) - Mark an alert for deletion in Google Alert Center. <br>
[make request](#action-make-request) - Send an authenticated request to a Google Alert Center v1beta1 endpoint. <br>
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

List alerts from Google Alert Center.

Type: **generic** <br>
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**customerId** | optional | Customer ID in format C01234567. This overrides the customer ID in the asset. | string | |
**filter** | optional | Filter expression for alert retrieval. | string | |
**pageSize** | optional | Maximum number of alerts to return. | numeric | |
**orderBy** | optional | Field to order alerts by. | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.customerId | string | | |
action_result.parameter.filter | string | | |
action_result.parameter.pageSize | numeric | | |
action_result.parameter.orderBy | string | | |
action_result.data.\*.data.\*.alertId | string | | |
action_result.data.\*.data.\*.customerId | string | | |
action_result.data.\*.data.\*.createTime | string | | |
action_result.data.\*.data.\*.startTime | string | | |
action_result.data.\*.data.\*.endTime | string | | |
action_result.data.\*.data.\*.type | string | | |
action_result.data.\*.data.\*.source | string | | |
action_result.data.\*.data.\*.securityInvestigationToolLink | string | | |
action_result.data.\*.data.\*.deleted | boolean | | True False |
action_result.data.\*.data.\*.updateTime | string | | |
action_result.data.\*.data.\*.etag | string | | |
action_result.data.\*.data.\*.metadata.customerId | string | | |
action_result.data.\*.data.\*.metadata.alertId | string | | |
action_result.data.\*.data.\*.metadata.status | string | | |
action_result.data.\*.data.\*.metadata.assignee | string | | |
action_result.data.\*.data.\*.metadata.updateTime | string | | |
action_result.data.\*.data.\*.metadata.severity | string | | |
action_result.data.\*.data.\*.metadata.etag | string | | |
action_result.data.\*.data.\*.data | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get alert'

Retrieve an alert by its ID.

Type: **generic** <br>
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alertId** | required | ID of the Google Alert Center alert. | string | |
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
action_result.data.\*.securityInvestigationToolLink | string | | |
action_result.data.\*.deleted | boolean | | True False |
action_result.data.\*.updateTime | string | | |
action_result.data.\*.etag | string | | |
action_result.data.\*.metadata.customerId | string | | |
action_result.data.\*.metadata.alertId | string | | |
action_result.data.\*.metadata.status | string | | |
action_result.data.\*.metadata.assignee | string | | |
action_result.data.\*.metadata.updateTime | string | | |
action_result.data.\*.metadata.severity | string | | |
action_result.data.\*.metadata.etag | string | | |
action_result.data.\*.data | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'delete alert'

Mark an alert for deletion in Google Alert Center.

Type: **generic** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alertId** | required | ID of the Google Alert Center alert. | string | |
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

## action: 'make request'

Send an authenticated request to a Google Alert Center v1beta1 endpoint.

Type: **generic** <br>
Read only: **False**

'make request' action for the app. Used to handle arbitrary HTTP requests with the app's asset

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**http_method** | required | The HTTP method to use for the request. | string | |
**endpoint** | required | The endpoint to send the request to. | string | |
**headers** | optional | The headers to send with the request (JSON object). An example is {'Content-Type': 'application/json'} | string | |
**query_parameters** | optional | Parameters to append to the URL (JSON object or query string). An example is ?key=value&key2=value2 | string | |
**body** | optional | The body to send with the request (JSON object). An example is {'key': 'value', 'key2': 'value2'} | string | |
**timeout** | optional | The timeout for the request in seconds. | numeric | |
**verify_ssl** | optional | Verify the Google API TLS certificate. Defaults to True. | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.http_method | string | | |
action_result.parameter.endpoint | string | | |
action_result.parameter.headers | string | | |
action_result.parameter.query_parameters | string | | |
action_result.parameter.body | string | | |
action_result.parameter.timeout | numeric | | |
action_result.parameter.verify_ssl | boolean | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"key": "value"} |
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
