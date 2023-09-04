SA for EclecticIQ
=========================================
Version 2.5.5

"EclecticIQ Platform App for Splunk” integrates Splunk Enterprise and EclecticIQ Platform.

Requirements:

"EclecticIQ Platform App for Splunk" version 2.5.x supports:
  - Splunk versions 6.3+ and 7.0+ on Linux and Windows.
  - EclecticIQ Threat Intelligence Platform 2.0+ with minor releases.
  - EclecticIQ Fusion Center as data source not for sightings generation.
 
### Support ###

Contact us at splunk@eclecticiq.com for any of the following:
- Share your feedback or request any support concerning the app.
- To request further documentation.
- For bugs or feature requests.

## Description ##

EclecticIQ Platform App for Splunk is an app for Splunk Enterprise. It enables Splunk Enterprise users to ingest large quantities of threat intelligence by integrating EclecticIQ Platform feeds with Splunk and use this threat intelligence within the Splunk Enterprise.

EclecticIQ Platform acquires cyber threat intelligence in different formats from multiple sources. It de-duplicates, normalizes, and enriches source data with additional contextual details, and then it uses feeds to output relevant information to Splunk Enterprise, where it can be analyzed and filtered by a set of rules to identify matching threats that may target your organization. 

This integration generates sightings and alerts that Splunk feeds back to EclecticIQ Platform, providing a rich threat intelligence dataset that allows you to efficiently tune your SIEM prevention and detection system.

EclecticIQ Platform App for Splunk ships with:
- Scripts to ingest threat intelligence platform Outgoing Feed and to upload sightings back.
- Script for creation Custom Alert Action / Response Action in Splunk Enterprise Security.
- A default set of dashboards to make it easier for Splunk users to monitor feed data collection.
- A default savedsearches to generate alerts in the Splunk app.
- A default set of dashboards to allows Splunk users to monitor matching between Threat Intelligence and logs in Splunk (Alerting workflow).
- Workflow actions to quickly get more details about a sighting in the EclecticIQ platform.

## Quick start guide ##

### Install the app ###

- Verify that the Splunk server you want to install the "SA for EclecticIQ" App on matches the versions reported in the *Version compatibility* section.
- In the Splunk Platform go to **Apps > Manage Apps** and click **Install app from file**.
- Browse to the location where the *threat-intelligence-eclecticiq-platform-app_xxx.tar.gz* file is stored, and then click **Upload**.
- After successfully completing the upload and the installation, configure the app to download the threat intelligence from the EclecticIQ platform.

### Configure the app ###

Configuring the app for first time use can be done in the following ways:

1) App
    - Open the app and click the **Continue to app setup page** button.

2) Manage apps
    - In the **Apps menu** select **Manage apps**.
    - In the app list, find **SA for EclecticIQ**.
    - In the action column, click **Set up**.

3) App menu, this is mostly for search head clustering.
    - Open the app. 
      A pop should be displayed.
    - Click the **Continue to app setup page** button in the popup.
      If the pop up is not displayed, do the following:
    - Go to "Information" > "Edit app settings"

In the **EclecticIQ configuration** page, define the following configuration
options:

**Feeds setup**
   - **url of EclecticIQ...**: The FQDN or IP of the EclecticIQ platform or Fusion Center.
   - Select the **Verify the SSL connection If SSL is used** to verify the SSL certificate used by the platform.
   - **ID of feeds for collection from EclecticIQ Platform**: A comma separated list of feed ID's that can be downloaded from the platform.
   - **EclecticIQ Platform source group name**: The case sensitive name of the EclecticIQ Platform group you want to use as a source to create sightings.

**Credentials**
  - **Username**: Enter a valid user name to log in to the Platform.
  - **Password**: Enter a valid password.
  - **Confirm password**: Repeat the password.

**Sightings setup**
  - **Sightings query**: A Splunk query to look for events in Splunk for alerting.
  - **Send the following sightings**: Select all applicable checkboxes corresponding to the data types you want to use.  This is used to generate the sightings that are then sent to EclecticIQ Platform for ingestion.
  - **Set script log level**: Set the log level of the scripts that are in the app. If you want to check logs related to the app go to the **Information > Application logs**.

Click **Save** to save your configuration. 

### Alerts in app ###

App contains two saved searches generate alerts in the app. First search is "EclecticIQ alert" scheduled in every hour to run and contains search based on free text conditions. Second search is "EclecticIQ tstats Threat Intelligence alert" scheduled in every hour to run and it uses DataModels for searching, if your Splunk installation uses CIM application / Data Models it's recommended to enable it. For better performance and accuracy it's recommended to use "EclecticIQ tstats Threat Intelligence alert". CIM application can be downloaded https://splunkbase.splunk.com/app/1621/ and documentation availble there as well. 

By default both searches are disabled and you need to select one which fits best and enable it. If both searches will be enabled you will have duplicating of some alerts in the app.

### Scripts ###

**Collection script**

By default, the collection script is configured to run every 20 minutes (cron schedule: */20 * * * *). You can change this in the inputs.conf but please take note of the following:
- inputs stanza: [script://$SPLUNK_HOME/etc/apps/SA-EclecticIQ/bin/eiq_collect_feeds.py]

- Do not change eiq_feeds_list lookup.

- App will automatically update data, if you make any changes in app settings page.

- The collection script writes the downloaded threat intelligence directly to the Splunk KV store and not to a local (csv) lookup file. This is to prevent bundle replication problems with large feeds.

- The collection script is search head cluster aware. This means that in a search head cluster only the searchhead captain will download the feeds from the EclecticIQ platform and then update the Splunk KVstore, the KVStore is automatically replicated between the cluster members. This way all the systems have the same information but the EclecticIQ platform doesn't get a feed update request from all the members. This prevents a "DDOS" attack on the platform in large search head clusters, it also prevents unnecessary replications and possible conflicts of exactly the same data between cluster members.

**Sightings script**

By default the sightings script is configured to send the sightings back to the EclecticIQ platform every 15 minutes (cron schedule: */15 * * * *). You can change this in the inputs.conf but please take note of the following:
- inputs stanza: [script://$SPLUNK_HOME/etc/apps/SA-EclecticIQ/bin/eiq_send_sightings.py]

- After correctly configuring EclecticIQ Platform App to work with Splunk, the corresponding dashboard view should become populated with relevant results.

- Sighting creation feature doesn't work with Eclectic IQ Fusion Center
