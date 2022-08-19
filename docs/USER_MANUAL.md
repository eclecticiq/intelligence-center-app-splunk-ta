# EclecticIQ Splunk Addon & App User Manual


# 1. Introduction
EclecticIQ Intelligence Platform

1. EclecticIQ Intelligence Center is the threat intelligence solution that unites machine-powered threat data processing and dissemination with human-led data analysis without compromising analyst control, freedom or flexibility.
2. Intelligence Manager consolidates vast amounts of internal and external structured and unstructured threat data in diverse formats from open sources, commercial suppliers, and industry partnerships. This data becomes a collaborative, contextual intelligence source of truth.
3. EIQ data processing pipeline ingests, normalizes, transforms, and enriches this incoming threat data into a complex, and flexible data structure. Next, our technology optimizes and prioritizes this data to help identify the most critical threats more rapidly.
4. For total flexibility, Intelligence Manager disseminates intelligence as reports for stakeholders or as machine-readable feeds that integrate with third-party controls to improve detection, hunting, and response.
5. Intelligence Manager offers cloud-like scalability and cost-effectiveness within your trusted environment.

## 1.1 Prerequisites

1. Splunk Enterprise version 8.2
2. EclecticIQ Intelligence Center 2.12.
3. Outgoing feeds should be set up on EclecticIQ Intelligence Center.
4. API key generated from EIQ platform.
5. The app will use EIQ’s V1 public API endpoints.

## 1.2 Modules
Below mentioned modules will be covered as part of this document.
1.     Splunk Addon
            ConfigurationAccount
            Proxy
            Logging
            Additional Settings
        Input
             Collect Observables
             Delete Observables
        Sighting
             Create Sighting
             Lookup Observable
             Alert
2.     Splunk App
             Dashboards
             Saved Searches


## 1.2 Installation

### 1.2.1 Installation of Splunk Enterprise

To install the splunk enterprise. Follow this manual Splunk Installation Manual.(https://docs.splunk.com/index.php?title=Documentation:Splunk:Installation:Beforeyouinstall:8.1.0&action=pdfbook&version=8.2.2&product=Splunk).

### 1.2.2 Installation for both APP & Addon

##### Step 1. Open Splunk Enterprise.
##### Step 2. Click on Apps and click on Find more Apps.
##### Step 3. Enter the app name to search for . . .
##### Step 4. Check the prerequisites and details.
##### Step 5. Click on Install.
![Installation](/docs/screenshots/1.png)

### 1.2.3 Installation for both APP & Addon(From File)

##### Step 1. Login to Splunk Enterprise.
##### Step 2. Navigate to manage apps and click.
![Installation](/docs/screenshots/2.png)
##### Step 3. Click on Install app from File.
![Installation](/docs/screenshots/3.png)
##### Step 4.Install App From File pop-up window will appear.
##### Step 5.Choose the file and click on checkbox.
##### Step 6.Click on Upload button.
![Installation](/docs/screenshots/4.png)
##### Step 7.Successfully installed message will be displayed.
![Installation](/docs/screenshots/5.png)

After installation, we can see the Addon and App in Apps dropdown list

![Installation](/docs/screenshots/6.png)

# 2. Splunk Addon
* The EIQ app for Splunk will collect the observables data from the EIQ platform and store it in KV store lookups.
* Users will be provided an option for sighting creation by clicking on the events.
* Sighting will be created automatically when a configured search will get triggered with the configured EIQ Custom action.
* Users will be provided an option to lookup observables by clicking on the events.
* Splunk Addon for EIQ will allow automatic deletion of observables.

## 2.1 Features of Splunk Addon

Configuration :
There are 4 configurations for the splunk Addon. Each one of the configurations are explained below.
### 1. Account
After installation of EclecticIQ Intelligence Centre Addon to set up the account follow the below steps.
##### 1. Navigate to apps and select EIQ Intelligence centre Addon.
##### 2. Click on the Configuration tab.
##### 3. In the Accounts Sub tab click on Add.
##### 4. Give a unique name to the configuration and add the URL (https://<hostname>/api/<version>) of the product & API key generated from the Product.
##### 5. Click on Add.
![Account](/docs/screenshots/7.png)

Account should be created successfully
![Account](/docs/screenshots/8.png)

### 2. Proxy
For setting up the proxy for data collection of API data, follow the below-mentioned steps in EclecticIQ Intelligence centre Add-on.
##### 1.Navigate to apps and select EIQ Intelligence centre Addon.
##### 2. Click on the Configuration tab.
##### 3. Click on the Proxy tab under the configuration tab.
##### 4. Fill in all the necessary details. (https://<hostname>/api/<version>) of the product & API key generated from the Product.
##### 5. Click on Save.

![Image](/docs/screenshots/9.png)

### 3. Logging
For setting up the logging for data collection of API data, follow the below-mentioned steps in EclecticIQ Intelligence centre Add-on.
##### 1.Navigate to apps and select EIQ Intelligence centre Addon.
##### 2. Click on the Configuration tab.
##### 3. Click on the Logging tab under the configuration tab.
##### 4. Select the Log level. Available log levels are Debug, Info, Warning, Error and Critical.
##### 5. Click on Save.

![Image](/docs/screenshots/10.png)

### 4. Additional Parameters
For setting up the Additional parameter for API calls and retry mechanism, follow below-mentioned steps in EclecticIQ Intelligence centre Add-on.
##### 1.Navigate to apps and select EIQ Intelligence centre Addon.
##### 2. Click on the Configuration tab.
##### 3. Click on the Add-on Settings tab under the configuration tab..
##### 4.Number of Retries(Number of attempts to be made, default to 3)
##### 5. Sleep time(Wait time in seconds between consecutive retries, default to 100)
##### 6. Page size(Data to fetch in a single rest API call.Default to 100)
##### 7. Click on Save.
![Image](/docs/screenshots/11.png)

# 2. EIQ Observables Collection

After saving the configurations.
1. User is able to go to Inputs Tab.
2. Click on Create New Input button.
3. Select Collect Observables.
4. Fill all the fields.
     * Unique name: Unique name for the data input
     * Interval: Time interval of input in seconds
     * Global account: Name of global account created in configuration screen
     * Outgoing feeds: Outgoing feeds ID’s to collect observables from
     * Select date: Date for observable collection to be entered in yyyy-mm-ddThh:mm:ss.SSSS format
    * Select observable types: Observable types to ingest

5.Click on Add.

![Image](/docs/screenshots/12.png)

6.Successfully creating input message will be displayed.

![Image](/docs/screenshots/13.png)
7.Created input will be displayed in the Inputs Screen.

![Image](/docs/screenshots/14.png)
8.Go to Search Tab.Enter | inputlookup eiq_ioc_list.
9.Verify the collection of observable data.

![Image](/docs/screenshots/15.png)

The below image is the background job to fetch the observables from the EIQ
$SPLUNK_HOME/var/log/splunk/ta_eclecticiq_eiq_observables.log

![Image](/docs/screenshots/16.png)

# 3. Deletion of observables
1. Login to Splunk Enterprises.
2. Navigate to apps and select EIQ Intelligence centre Addon.
3. Go to Inputs Tab.
4. Click on Create New Input button.
5. Select Delete Observables.
6. Fill all the fields.
     * Unique Name: Unique name for data input
     * Interval: Time interval of input in seconds
     * Observable time to live: Observable time to live in days
![Image](/docs/screenshots/17.png)
7. Click on Add button.
8. Deletion of Observables record created successfully.
9. Go to search tab and enter | inputlookup eiq_ioc_list.

Before deletion of observable data in KV store
![Image](/docs/screenshots/18.png)
10. After successfully deleting the data from KV store.
![Image](/docs/screenshots/19.png)

# 4. Create Sighting(From event fields)
1. Navigate to Search Tab.
2. Type the Query to get the Events.(Eg: index=”<index name>”)
3. Click on the event and expand.
4. Click on the down arrow(right side) of the value(IP/URL/Domain/Hash/Email).
5. Click on EclecticIQ Create Sighting.
6. A pop-up window will appear to ask for the details below.
Clicking on save will create sightings in the EIQ platform with provided details.
    * Sighting Value: Value which is clicked
    * Sighting description: Description of sighting
    * Sighting title: Title of sighting
    * Sighting tags delimited by a comma: Any tags to attach with sighting
    * Sighting type: Type of sighting. Possible values: ip, domain, url, email, hash,port
    * Sighting confidence: Confidence of sighting. Possible values: low, medium, high,unknown
![Image](/docs/screenshots/20.png)
7. Click on Save button(successfully save the sighting).
8. Go to Search tab and enter | inputlookup eiq_alerts_list.
9. Verify the created sightings.
![Image](/docs/screenshots/21.png)
10. Verify the sightings in EIQ application.
![Image](/docs/screenshots/22.png)

# 5. Lookup Observable
1. Navigate to Search Tab.
2. Type the Query to get the Events.(Eg: index=”<index name>”)
3. Click on the event and expand.
4. Click on the down arrow(right side) of the value(IP/URL/Domain/Hash/Email).
5. Click on the EclecticIQ lookup observable.
![Image](/docs/screenshots/23.png)
6. A pop-up window will appear.
![Image](/docs/screenshots/24.png)
7. Click on Create Sighting button.
8. A pop-up window will appear to ask for the details below.
Clicking on save will create sightings in the EIQ platform with provided details.
    * Sighting Value: Value which is clicked
    * Sighting description: Description of sighting
    * Sighting title: Title of sighting
    * Sighting tags delimited by a comma: Any tags to attach with sighting
    * Sighting type: Type of sighting. Possible values: ip, domain, url, email, hash,port
    * Sighting confidence: Confidence of sighting. Possible values: low, medium, high,unknown
![Image](/docs/screenshots/25.png)
9. Sighting should be created successfully.
![Image](/docs/screenshots/26.png)

10. Verify the created sightings.
![Image](/docs/screenshots/27.png)

11. Verify the sightings in EIQ application.
![Image](/docs/screenshots/28.png)


# 6. Create Sighting(Automatic Based on Saved Searches)
1. Go to settings dropdown > click on Searches,reports and alerts.
2. Searches, Reports and Alerts page displayed.

![Image](/docs/screenshots/29.png)

3. Click on New Alert button(right side above).
4. Create Alert pop-up page displayed.

![Image](/docs/screenshots/30.png)

5. Provide the values for Fields (Title, Description,App,permissions).
6. Enter the Search query for which the sighting should be created. Make sure the search is returning these fields(index, host, source, sourcetype, _time, src, dest,_raw). Optional fields are (event_hash, feed_id_eiq, meta_entity_url_eiq, observable_id, observable_value).
7. Select Alert type and select scheduled options.
![Image](/docs/screenshots/31.png)

8. Select Trigger conditions(Trigger alert and trigger).
![Image](/docs/screenshots/32.png)
9. Click on Add actions dropdown under trigger actions.
10. Select Create EclecticIQ Sighting.
![Image](/docs/screenshots/33.png)

11. Fill all the fields available in create EclecticIQ sighting.
     * Sighting Title: Title of sighting
     * Sighting Description: Description of sighting
     * Sighting confidence: Confidence of sighting. Possible values: low,medium,High
     * Sighting tags delimited by a comma: Any tags to attach with sighting
     * Observable Type: Possible values: ip, domain, url, email, hash,port
     * Observable Field: Name of the field from which contains observable value
     * Observable Confidence: Confidence of observable. Possible value: Low,Medium,High,Unknown
![Image](/docs/screenshots/34.png)

11. Click on save.
12. An Alert should be created.



# Splunk APP
### Dashboard
App will render the widgets using the SPL queries fired against the splunk lookups for sighting. Sighting details will not be stored in the splunk indexes.

Note: Dashboards available in current application will be used as is with search query modification.
### 1. Home Dashboard
1. Login to Splunk Enterprise.
2. Navigate to apps > EclecticIQ App for splunk.
3. Go to Home.

In Home Dashboard it shows information about collections of observables and Alerts.
* Total count of observables.
* Shows the details of Alerts: By severity, By Source, By Type.
* Shows the Top detected Observables by types, Taxonomy/Tag.
* Shows Top detected observables and metadata by sourcetype.

![Image](/docs/screenshots/app_images/1.png)
![Image](/docs/screenshots/app_images/2.png)
![Image](/docs/screenshots/app_images/3.png)
* Click on table row of top detected observable and metadata by source it will navigate to All Matches Dashboard and show the information.

![Image](/docs/screenshots/app_images/4.png)


### 2. Matches by IP
1. Login to Splunk Enterprise.
2. Navigate to apps > EclecticIQ App for splunk.
3. Go to Dashboard dropdown.
4. Select Matched IP.
![Image](/docs/screenshots/app_images/5.png)

In Matches by IP Dashboard it shows information about Alerts by observable type IP.
* Shows the details of Alerts by severity of ipv4 and ipv6.
* Shows the details of top detected connections by Source observable and Destination observable.
![Image](/docs/screenshots/app_images/6.png)
![Image](/docs/screenshots/app_images/7.png)
* Click on any row in the table and it will show more additional information about that row.
![Image](/docs/screenshots/app_images/8.png)



### 3. Matches by Domain and URL
In Matches by Domain and URL Dashboard it shows information about Alerts by observable type Domain and URL.
* Shows the information of severity of Domain and URL.
* Shows the information of URL observable and Domain observable.

![Image](/docs/screenshots/app_images/9.png)
![Image](/docs/screenshots/app_images/10.png)
* Clicking on any row in the table. It will show the additional information of that row.
![Image](/docs/screenshots/app_images/11.png)
![Image](/docs/screenshots/app_images/12.png)


### 4. Matches by File Hashes
In Matches by File Hashes Dashboard it shows information about Alerts by observable type File hashes.
* Shows the information about the severity of alerts.
* Shows the information of Alerts by Hashes.
![Image](/docs/screenshots/app_images/13.png)
![Image](/docs/screenshots/app_images/14.png)
* Clicking on any row in the table. It will show more detailed information about that row.
![Image](/docs/screenshots/app_images/15.png)

### 5. Matches by Email
In Matches by Email Dashboard it shows information about Alerts by observable type Email.
* Shows the information of the Email alerts by severity.
* Shows the information of the alerts by sender observable and receiver observable.
![Image](/docs/screenshots/app_images/16.png)
![Image](/docs/screenshots/app_images/17.png)

* Clicking on any row in the more info table. It will show more detailed information about that particular clicked value.
![Image](/docs/screenshots/app_images/18.png)


### 6. All Matches

In All Matches Dashboard it shows information about Alerts by all types of observables(IP,Domain,URL,File Hash and Email).
* Shows the information of the severity of all observable types.
* Shows the information of top detected connections by source observables.
![Image](/docs/screenshots/app_images/19.png)
![Image](/docs/screenshots/app_images/20.png)

* Clicking on any row in the table. It will show more detailed information about that cli
![Image](/docs/screenshots/app_images/21.png)

### 7.Observables DB Info

1. Navigate to Information Dropdown in EclecticIQ App for splunk.
2. Select Observable DB Info.

In Observables DB Info Dashboard shows the information of observables stored in the KV store.
* Shows the total count of observables stored in the KV store.
* Shows the information of observables distribution.
* Shows downloaded observables by type.
* Shows the details of count of observables by Type,Tags and Confidence.
![Image](/docs/screenshots/app_images/22.png)
![Image](/docs/screenshots/app_images/23.png)
![Image](/docs/screenshots/app_images/24.png)
* Clicking on any row of count of observable type in the table will open in another window and show more detailed information of that particular row.
![Image](/docs/screenshots/app_images/25.png)

* Clicking on any row of count of observables by tag in the table will open in another window and show more detailed information of that particular row
![Image](/docs/screenshots/app_images/26.png)

* Clicking on any row of count of observables by Confidence in the table will open in another window and show more detailed information of that particular row.
![Image](/docs/screenshots/app_images/27.png)



### 8.Application Logs

In Application logs Dashboard shows the information of the log levels,sourcetype and message in the table.

![Image](/docs/screenshots/app_images/28.png)

## Saved Searches
App will provide the saved searches which will be helpful for customers to map the data from other log sources with the threat intelligence data collected by the Addon in KV store. The app will be using the saved searches already available in the app available on Splunkbase.

To match the data from indexes follow below steps
* Go to Search,reports and alerts.
* From App dropdown select EclecticIQ intelligence centre App for Splunk
* Select owner All
* Click on EclecticIQ alert.
* Adjust the query to match the fields from index data to IOC data
    *  For example if the data is having field local_address which contains the source IP address of attack then in query add the field append it to the list of fields to be matched as given the the screenshot below.
     ![Image](/docs/screenshots/app_images/29.png)
    *  Then add it to the evaluation field which the field is mapped to. For example: if the local_address contains the ip address of the attacker then add it to eval of src field if it is containing destination ip add it to eval of dest field. Example given in below screenshot.
     ![Image](/docs/screenshots/app_images/30.png)
* Adjust the schedule of the query.
* Click on Save.
* Click on Edit > Enable



To match the data from datamodel follow below steps
* Go to Search,reports and alerts.
* From App dropdown select EclecticIQ intelligence centre App for Splunk
* Select owner All
* Click on EclecticIQ tstats threat intelligence alert <type>.Type could be Domain,URL,Email,Hash,Source and Destination based upon the fields that should be matched.
* Adjust the schedule of the query.
* Click on Save.
* Click on Edit > Enable
![Image](/docs/screenshots/app_images/31.png)
