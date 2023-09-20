# EclecticIQ Intelligence Center App for Splunk documentation

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Features](#features)
- [Install](#install)
    - [Install from file](#install-from-file)
- [Configure](#configure)
    - [Set up outgoing feeds on EclecticIQ Intelligence Center](#set-up-outgoing-feeds-on-eclecticiq-intelligence-center)
    - [Configure app](#configure-app)
- [Objects added](#objects-added)
- [Enable input scripts](#enable-input-scripts)
- [Ingest observables into Splunk](#ingest-observables-into-splunk)
- [Ingest observables into Splunk Enterprise Security Threat Intelligence Framework](#ingest-observables-into-splunk-enterprise-security-threat-intelligence-framework)
- [Workflow action "Create Sighting"](#workflow-action-create-sighting)
- [Workflow action "Lookup Observable"](#workflow-action-lookup-observable)
- [Create Sighting Alert action](#create-sighting-alert-action)
- [Saved searches](#saved-searches)
    - [EclecticIQ alert](#eclecticiq-alert)
    - [tstats searches](#tstats-searches)
- [Dashboards](#dashboards)
    - [Home Dashboard](#home-dashboard)
    - [Matches by IP](#matches-by-ip)
    - [Matches by Domain and URL](#matches-by-domain-and-url)
    - [Matches by File Hashes](#matches-by-file-hashes)
    - [Matches by Email](#matches-by-email)
    - [All Matches](#all-matches)
    - [Observables DB Info](#observables-db-info)
- [Appendix](#appendix)
    - [Find outgoing feed IDs](#find-outgoing-feed-ids)
    - [EclecticIQ Intelligence Center permissions](#eclecticiq-intelligence-center-permissions)
    - [Alert expiry](#alert-expiry)
    - [Sightings query](#sightings-query)
    - [KV Store collections](#kv-store-collections)
- [Troubleshooting](#troubleshooting)
    - [Access the logs](#access-the-logs)
    - [App configuration cannot complete](#app-configuration-cannot-complete)

<!-- markdown-toc end -->


## Introduction

The EclecticIQ Intelligence Center App for Splunk
allows you to connect
[EclecticIQ Intelligence Center](https://www.eclecticiq.com/products/intelligence-center)
with Splunk.

For technical support or queries,
please open a ticket on the
EclecticIQ customer portal:
https://support.eclecticiq.com/.

## Prerequisites

* Splunk Enterprise 8.x, 9.x, or Splunk Cloud.
* EclecticIQ Intelligence Center 2.14, or 3.0 and newer.
* EclecticIQ Intelligence Center user account API token.
* [Splunk Common Information Model](https://splunkbase.splunk.com/app/1621) (Required for [tstats searches](#tstats-searches)).
* Network access between EclecticIQ Intelligence Center
  and your Splunk instance.
* EclecticIQ Intelligence Center outgoing feed(s)
  that provide observables for ingestion/lookup.

## Features

* [Dashboards](#dashboards)
* Workflow actions:
  - Create Sighting in EclecticIQ Intelligence Center from event fields.
  - Lookup observables and related entities in EclecticIQ Intelligence Center from event fields.
* Alerts
* Data input scripts for:
  - Ingesting observables from EclecticIQ Intelligence Center into Splunk.
  - Sending events from Splunk to EclecticIQ Intelligence Center as Sighting entities.
* Provides alert actions that you can use when creating alerts:
  - Create Sighting

## Install

### Install from file

1. Download the `tar.gz` archive from
   [the latest release](https://github.com/eclecticiq/intelligence-center-app-splunk-ta/releases).
1. Log in to Splunk Enterprise.
1. From the navigation menu, select **Apps > Manage Apps**.
1. Select **Install app from file**.
1. Select **Browse**, and locate the downloaded app archive file.
1. (Optional) Select **Upgrade app** to upgrade an existing version of the app.
1. Select **Upload** to install the app.

## Configure

Before using the app, you must:

- Set up outgoing feeds on EclecticIQ Intelligence Center.
  These feeds provide data for lookup and alerting on Splunk.
- Connect the app to an EclectiCIQ Intelligence Center instance
  with one or more outgoing feeds.
- Manually enable app features.
  App objects are not enabled by default
  to give you explicit control over features to run.

### Set up outgoing feeds on EclecticIQ Intelligence Center

To allow the app to work with EclecticIQ Intelligence Center,
you must connect it to at least 1 outgoing feed
on an EclecticIQ Intelligence Center instance.

These outgoing feeds must have these properties:

- **Transport type:** _HTTP download_
- **Content type:** _EclecticIQ Observables CSV_
- **Update strategy:** _Diff_ or _Replace_.
  - **(Recommended)** _Diff_ allows you to update data ingested
    into Splunk incrementally,
    syncing both removed and added observables
    each time the `eiq_collect_feeds.py` data input script runs.
  - _Replace_ removes all observable previously
    ingested from the outgoing feeds, and ingests all data
    provided by the feed, each time the feed is updated.
    Do not use with large feeds.
- **Authorized groups:**
  Must set one or more groups. Feed must be authenticated.
  See [EclecticIQ Intelligence Center permissions](#eclecticiq-intelligence-center-permissions).


Only observables packed by this outgoing feed are ingested into Splunk.

To create an outgoing feed, see EclecticIQ documentation:
[Create and configure outgoing feeds](https://docs.eclecticiq.com/ic/current/integrations/extensions/outgoing-feeds/configure-outgoing-feeds-general-options/).

### Configure app

> ⚠️ **NOTE:**
> For on-premises Splunk instances,
> you must
> [restart Splunk](https://docs.splunk.com/Documentation/Splunk/9.1.1/Admin/StartSplunk)
> **after** configuring the app.

To configure the app for the first time:

1.  From the navigation menu in Splunk, go to
    **Apps > Manage apps**
1.  Locate the record for
    "EclecticIQ Intelligence Center app for Splunk" in the list of apps.
1.  On the right of that record, select **Set up**.

To change the configuration of the app, you can:

1.  Open the app by going to **Apps > EclecticIQ Intelligence Center app for Splunk**
1.  In the app view, from the navigation menu select **Information > Edit app settings**.

In the configuration page, set the following fields:

> 📘 **NOTE:** \* Required fields.

| Field | Description
| - | -
| EclecticIQ Intelligence Center URL\* | Enter the URL for your EclecticIQ Intelligence Center instance.
| EclecticIQ Intelligence Center API version\* | `v1` for EclecticIQ Intelligence Center 2.14; `v2` for EclecticIQ Intelligence Center 3.0 and newer.
| Verify the SSL connection | Selected by default. Remove selection to allow unverified HTTPS connections.
| ID of feeds for collection from EclecticIQ Intelligence Center\* | Set at least 1 outgoing feed ID. Multiple IDs should be separated by commas (e.g.: `6, 13`). To find outgoing feed IDs, see [Find outgoing feed IDs](#find-outgoing-feed-ids).
| Ingest data into Splunk Enterprise Security Threat Intel Framework | Select to enable ingesting data into Splunk Enterprise Security Threat Intel Framework. Requires Splunk Enterprise Security.
| EclecticIQ Intelligence Center Source Group | Enter the name of one EclecticIQ Intelligence Center group. When this app sends events to EclecticIQ Intelligence Center as sightings, this is the group assigned as their source. See [EclecticIQ Intelligence Center permissions](#eclecticiq-intelligence-center-permissions). |
| EclecticIQ Intelligence Center API Token\* | API token from EclecticIQ Intelligence Center user account. See [EclecticIQ Intelligence Center permissions](#eclecticiq-intelligence-center-permissions). |


Optional settings:

| Field | Description
| - | -
| Proxy IP | URL of proxy server. May be IP address and port (e.g.: `10.10.1.1:3000`).
| Proxy username | Username for authenticating with proxy server.
| Proxy password | Password for authenticating with proxy server.
| Sightings query | See [Sightings query](#sightings-query).
| Send the following sightings types | When the `eiq_send_sightings.py` data input script is enabled and an alert from `eiq_alerts` is triggered, only events containing IoCs of these types are sent to EclecticIQ Intelligence Center as sighting entities.
| Scripts Log Level | Log verbosity for logs collected for this app. See [Access the logs](#access-the-logs). |


## Enable input scripts

This app provides the following scripts for data input.
To find these scripts, go to
**Settings > Data input > Script** in Splunk.

You must manually enable these scripts for them to run.

You must manually enable these scripts before
Splunk runs them.

| Script name | Default interval |
| - | - |
| `eiq_collect_feeds.py` | `*/20 * * * *` | Collects data from EclecticIQ Intelligence Center. See [Ingest observables into Splunk](#ingest-observables-into-splunk)
| `eiq_send_sightings.py` | `*/15 * * * *` | Automatically sends alerts created by the EclecticIQ Intelligence Center App for Splunk to EclecticIQ Intelligence Center as Sighting entities.
| `eiq_setup_handler.py` | None | Not used. Only for initializing the app.


> 📘 **NOTE:**
> To change the **Interval** of a script,
> you may need to explicitly set a
> [Source type](https://docs.splunk.com/Documentation/Splunk/latest/Data/Whysourcetypesmatter)
> for it. Create a new source type, or set a manual one:
> 1. Go to **Settings > Data inputs > Script**.
> 1. Select a script to modify.
> 1. From the **Set sourcetype** menu, select **Manual**.
> 1. In the **Source type** field, enter a custom value
>    (e.g., `EclecticIQ:scripts`)


## Ingest observables into Splunk

To periodically ingest observables from
EclecticIQ Intelligence Center into Splunk,
you must enable the `eiq_collect_feeds.py` data input script.
See [Enable input scripts](#enable-input-scripts)

Once observables have been ingested into Splunk,
that data is available through the `eiq_ioc_list` KV Store collection.
You can query this data with:

```
| inputlookup eiq_ioc_list
```

For more information, see [KV Store collections](#kv-store-collections).

## Ingest observables into Splunk Enterprise Security Threat Intelligence Framework

Splunk Enterprise Security (Splunk ES) users who wants to ingest
IoCs into the Threat Intelligence Framework (TIF)
must select **Ingest data into Splunk Enterprise Security Threat
Intel Framework** when [configuring the app](#configure-app).

Once configured, the app ingests observables from
the configured EclecticIQ Intelligence Center outgoing feeds
into the following KV Store collections
[supported by Splunk ES](https://docs.splunk.com/Documentation/ES/7.1.1/Admin/Supportedthreatinteltypes):

| KV Store collection | EclecticIQ observable type |
| - | - |
| `ip_intel` | `ipv4`, `domain` |
| `file_intel` | `hash-md5`, `sha1`, `hash-sha256`, `hash-sha512` |
| `http_intel` | `uri` |
| `email_intel` | `email` |

Notes:

- Because of structure of TIF in Splunk ES only IoC values
  are ingested, no other metadata is included.
- If IoC is part of DIFF feed and is excluded from it on
  some run then it will be disabled in relevant ES lookup
  and not deleted. From EclecticIQ App KV Store
  (`eiq_ioc_list`) it will be removed. That is done because of
  way how Splunk ES TIF API works.
- Removing the app from Splunk does not remove its entries from the Splunk ES TIF store.
  To see what data is stored by this app in Splunk ES, request the content of
  relevant ES TIF KV Store collection.
  For example, to see the contents of the `ip_intel` collection, run this search:
  `| inputlookup ip_intel where threat_key=restapi`
- To manage the lifetime of IoC data in Splunk ES TIF,
  see [configure threat source retention](https://docs.splunk.com/Documentation/ES/7.0.0/Admin/Changethreatintel#Configure_threat_source_retention).

## Workflow action "Create Sighting"

1. Go to **Apps > Searches and Reporting > Search**.
1. Type the Query to get the Events.(Eg: index=”<index name>”)
1. Select the event and expand.
1. Select the down arrow(right side) of the value(IP/URL/Domain/Hash/Email).
1. Select EclecticIQ Create Sighting.
1. A pop-up window will appear to ask for the details below.
   Clicking on save will create sightings in the EIQ platform
   with provided details.

    * Sighting Value: Value which is clicked for Observable
      connected to the Sighting
    * Sighting description: Description of sighting entity
    * Sighting title: Title of sighting entity
    * Sighting tags delimited by a comma: Any tags to attach
      with sighting entity
    * Sighting type: Type for Observable connected to the
      Sighting. Possible values: ip, domain, url, email,
      hash, port.
    * Sighting confidence: Confidence of sighting entity.
      Possible values: low, medium, high, unknown
1. Select Save button (successfully save the sighting).

## Workflow action "Lookup Observable"

1. Go to **Apps > Searches and Reporting > Search**.
1. Type the Query to get the Events.(Eg: index=”<index name>”)
1. Select the event and expand.
1. Select the down arrow(right side) of the
   value(IP/URL/Domain/Hash/Email).
1. Select the EclecticIQ lookup observable.
1. A pop-up window will appear with data based on EclecticIQ
   response.
1. Optionally you can create Sighting with that IoC
   connected, to do that Select "Create Sighting" button.

## Create Sighting Alert action

Alert actions create Sightings in EclecticIQ
Intelligence Center.
The action could be assigned to Splunk
Search or, if you are using Splunk Enterprise Security, to
[correlation search](https://docs.splunk.com/Documentation/ES/7.1.1/Tutorials/CorrelationSearch)
as well.

Action provided by this app only creates
Sighting in connected EclecticIQ Intelligence Center and do
not add any data to Splunk KV Stores.

How to use Alert Action with Splunk Search:

1. Go to **Settings > Searches, reports, and alerts**.
1. From the top right, Select **New Alert**.
1. Fill out the fields in **Create Alert**. In particular:

  1.  Enter the Search query for which the sighting should be
      created. Make sure the search is returning necessary
      fields and data to create Sighting, you can also use
      searches provided with app as a starting point or use as-is.
  1.  Select Alert type and select scheduled options.
  1.  Select Trigger conditions(Trigger alert and trigger).
  1.  Select Add actions dropdown under trigger actions.
  1.  Select Create EclecticIQ Sighting.
  1.  Fill all the fields available in create EclecticIQ
      sighting.

      * **Sighting Title:** Title of sighting
      * **Sighting Description:** Description of sighting
      * **Sighting confidence:** Confidence of sighting. Possible
        values: low, medium, High
      * **Sighting tags delimited by a comma:** Any tags to
        attach with sighting
      * **Observable Type:** Possible values: ip, domain, url,
        email, hash, port
      * **Observable Field:** Name of the field from which
        contains observable value
      * **Observable Confidence:** Confidence of observable.
        Possible value: Low,Medium,High,Unknown

1. Select **Save**.

## Saved searches

This app provides the following saved searches:

- [EcleticIQ alert](#eclecticiq-alert)
- [tstats searches](#tstats-searches)

### EclecticIQ alert

This saved search is a generic query that
searches across non-accelerated
data in Splunk.

### tstats searches

> 📘 **NOTE:**
> Requires the
> [Splunk Common Information Model (CIM)](https://splunkbase.splunk.com/app/1621)

[`tstats` searches](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Tstats)
are a Splunk feature that allows
you make optimized queries on Splunk data.

The following `tstats` saved searches are provided:

- EclecticIQ tstats Threat Intelligence alert - Domain
- EclecticIQ tstats Threat Intelligence alert - Email
- EclecticIQ tstats Threat Intelligence alert - Hash
- EclecticIQ tstats Threat Intelligence alert - Source/Destination
- EclecticIQ tstats Threat Intelligence alert - URL

> 📘 **NOTE:**
> Each of these `tstats` saved search queries the
> following [CIM event data models](https://docs.splunk.com/Documentation/CIM/5.1.1/User/Howtousethesereferencetables):
> [Network Resolution](https://docs.splunk.com/Documentation/CIM/5.1.1/User/NetworkResolutionDNS),
> [Network Sessions](https://docs.splunk.com/Documentation/CIM/5.1.1/User/NetworkSessions),
> and [Web](https://docs.splunk.com/Documentation/CIM/5.1.1/User/Web)
> To use other CIM data models, modify these saved searches.

## Dashboards

This app provides dashboards that
provide insight into the data

### Home Dashboard

1. Login to Splunk Enterprise.
1. Navigate to apps > EclecticIQ App for Splunk.
1. Go to Home.

In Home Dashboard it shows information about collections of
observables and Alerts.

* Total count of observables.
* Shows the details of Alerts: By severity, By Source, By Type.
* Shows the Top detected Observables by types, Taxonomy/Tag.
* Shows Top detected observables and metadata by sourcetype.
* Select table row of top detected observable and metadata
  by source it will navigate to All Matches Dashboard and
  show the information.

### Matches by IP

In Matches by IP Dashboard it shows information about Alerts
by observable type IP.

* Shows the details of Alerts by severity of ipv4 and ipv6.
* Shows the details of top detected connections by Source
  observable and Destination observable.
* Select any row in the table and it will show more
  additional information about that row.

### Matches by Domain and URL

In Matches by Domain and URL Dashboard it shows information
about Alerts by observable type Domain and URL.

* Shows the information of severity of Domain and URL.
* Shows the information of URL observable and Domain
  observable.
* Clicking on any row in the table. It will show the
  additional information of that row.

### Matches by File Hashes

In Matches by File Hashes Dashboard it shows information
about Alerts by observable type File hashes.

* Shows the information about the severity of alerts.
* Shows the information of Alerts by Hashes.
* Clicking on any row in the table. It will show more
  detailed information about that row.

### Matches by Email

In Matches by Email Dashboard it shows information about
Alerts by observable type Email.

* Shows the information of the Email alerts by severity.
* Shows the information of the alerts by sender observable
  and receiver observable.
* Clicking on any row in the more info table. It will show
  more detailed information about that particular clicked
  value.

### All Matches

In All Matches Dashboard it shows information about Alerts
by all types of observables (IP,Domain,URL,File Hash and
Email).

* Shows the information of the severity of all observable types.
* Shows the information of top detected connections by
  source observables.
* Clicking on any row in the table. It will show more
  detailed information about that row.

### Observables DB Info

In Observables DB Info Dashboard shows the information of
observables stored in the KV Store.

* Shows the total count of observables stored in the
  KV Store.
* Shows the information of observables distribution.
* Shows downloaded observables by type.
* Shows the details of count of observables by Type,Tags and
  Confidence.
* Clicking on any row of count of observable type in the
  table will open in another window and show more detailed
  information of that particular row
* Clicking on any row of count of observables by tag in the
  table will open in another window and show more detailed
  information of that particular row
* Clicking on any row of count of observables by Confidence
  in the table will open in another window and show more
  detailed information of that particular row


## Appendix

### Find outgoing feed IDs

To find the ID of an EclecticIQ Intelligence Center outgoing feed:

1.  Log in to EclecticIQ Intelligence Center.
1.  Navigate to **Data configuration > Outgoing feeds**.
1.  Select an outgoing feed to open it.
1.  Inspect the address bar of your browser.
    The ID of this outgoing feed is the value of the `?detail=`
    query parameter.

    **For example:** For an outgoing feed that displays `https://ic-playground.eclecticiq.com/main/configuration/outgoing-feeds?detail=6` in the address bar, its ID is `6`.

### EclecticIQ Intelligence Center permissions

To use this app, you must have an API token from an
EclecticIQ Intelligence Center user account that:

- Has at least these permissions:
  - `read entities`
  - `read extracts`
  - `read outgoing feeds`

To allow this app to send events to EclecticIQ Intelligence Center as sightings,
this user must also:

- Have the following permissions:
  - `modify entities`
  - `modify extracts`
- Belong to the group specified in the
  **EclecticIQ Intelligence Center Source Group**
  field when
  [Configuring the app](#configure-app).

To create an API token on EclecticIQ Intelligence Center,
see EclecticIQ documentation:
[Create an API token](https://docs.eclecticiq.com/ic/current/get-to-know-the-ic/permissions/token-based-authentication/create-an-api-token/).

For information on how permissions are managed,
see [EclecticIQ Intelligence Center permissions](https://docs.eclecticiq.com/ic/current/get-to-know-the-ic/permissions/ic-permissions/#control-access-through-groups-roles-and-permissions)

### Alert expiry

By default, all alerts created by
this app are set to expire in `24 hours`.

### Sightings query

In the app there is Splunk search to
generate alerts based on IoC matching. That search you
can see in list of saved searches in the app with title
"EclecticIQ alert" that search starts with macros
`eiq_sightings_search` which is initial condition for
the search. If you want to create alerts based on Threat
Intel data and want to use that search you could want to
change that macro and you can do it via that setting. Of
course you can do it via default macros settings in
Splunk configuration.

### KV Store collections

This app provides these KV Store collections:

| KV Store collection | Description
| - | -
| `eiq_alerts` | Store of all alerts captured by the app.
| `eiq_feeds_list` | Store of status of all EclecticIQ Intelligence Center outgoing feeds this app is configured to retrieve data from.
| `eiq_ioc_list` | Lookup table that stores all observables ingested from EclecticIQ Intelligence Center outgoing feeds.

You can query each of these KV Store collections with the `| inputlookup` command.

To see fields available for querying:
1. Go to **Apps > Search and Reporting > Datasets**.
2. Filter entries to display only entries starting with `eiq`.
3. Select a dataset to open it.

## Troubleshooting

### Access the logs

Access the logs for this app:

1.  Open the app. In Splunk, from the navigation menu, go to **Apps > EclecticIQ Intelligence Center App for Splunk**.
1.  In the app view, go to **Information > Application Logs**.

You can configure log verbosity in the
[app configuration](#configure-app),
using these values:

| Log level | Description |
| - | - |
| `0` | Debug |
| `20` | Info |
| `30` | Warning |
| `40` | Error |
| `50` | Critical |

### App configuration cannot complete

(On-premises Splunk only)
If you encounter an issue
where Splunk asks you to configure the app,
even after you have saved the app configuration at least once,
you may need to
[restart Splunk](https://docs.splunk.com/Documentation/Splunk/9.1.1/Admin/StartSplunk).
