# Splunk Distributed EIQ IC & ER User Manual


## Introduction


**EclecticIQ Intelligence Platform**

* EclecticIQ Intelligence Center is the threat intelligence solution that unites machine-powered threat data processing and dissemination with human-led data analysis without compromising analyst control, freedom or flexibility.
* Intelligence Manager consolidates vast amounts of internal and external structured and unstructured threat data in diverse formats from open sources, commercial suppliers, and industry partnerships. This data becomes a collaborative, contextual intelligence source of truth.
* EIQ data processing pipeline ingests, normalizes, transforms, and enriches this incoming threat data into a complex, and flexible data structure. Next, our technology optimizes and prioritizes this data to help identify the most critical threats more rapidly.
* For total flexibility, Intelligence Manager disseminates intelligence as reports for stakeholders or as machine-readable feeds that integrate with third-party controls to improve detection, hunting, and response.
* Intelligence Manager offers cloud-like scalability and cost-effectiveness within your trusted environment.



## Splunk Distributed deployment installation & configuration
Install three Splunk Enterprise (version 8.2) instances in  AWS infrastructure.
1. One instance should be designated as the Cluster Master
2. The other contains an Indexer 
3. Search head is on the other 
  
[https://crossrealms.com/splunk/build-a-clustered-splunk-environment/] 


## Modules
Below mentioned modules will be covered as part of this document.  
**Splunk Addon**
* Configuration
    * Account
    * Proxy 
    * Logging
    * Additional Setting
* Input
    * Collect Observables

**Splunk App**
* Workflows
    * Create Sighting
    * Lookup Observable
* Alert Action
* Dashboards
* Saved Searches


### Installation & configuration for indexer
Install the EclecticIQ Intelligence Centre Addon for Splunk
#### Installation of Addon in Indexer
1. Login to Splunk Enterprise.
2. Navigate to manage apps and click.

![Image](/Docs/screenshots/1.png)

3. Click on Install app from File.

![Image](/Docs/screenshots/2.png)

4. Install App From File pop-up window will appear.
5. Choose the file and click on checkbox.
6. Click on Upload button.

![Image](/Docs/screenshots/3.png)

After installation, we can see the Addon in Apps dropdown list

![Image](/Docs/screenshots/4.png)

### Restart splunk instance after uploading the builds

1. Go to Settings dropdown
2. Click on Server controls
3. Click on the Restart Splunk button

![image](/Docs/screenshots/63.png)

4. Click on OK in the Pop-up window 

![image](/Docs/screenshots/64.png) 


### Splunk Addon 
**Features of Splunk Addon**
* The EclecticIQ Intelligence Centre Addon for Splunk will collect the observables data from the EIQ platform and store it in index.
* Added the EclecticIQ Threat Investigator sourcetype(i.e,eclecticiq:er:json) in EclecticIQ Intelligence Centre Addon for Splunk will collect the Threat investigator data and store it in index

**Configuration :** 

There are 4 configurations for the splunk Addon. Each one of the configurations are explained below.
##### 1.Account
After installation of EclecticIQ Intelligence Centre Addon to set up the account follow the below steps. 
1. Navigate to apps and select EclecticIQ Intelligence Centre Addon for Splunk 
2. Click on the Configuration tab
3. In the Accounts Sub tab click on Add
4. Give a unique name to the configuration and add the URL (https://<hostname>/api/<version>) of the product & API key generated from the Product
5. Verify SSL Certificate checkbox(Check the checkbox if the URL has an SSL certificate)
6. Click on Add

![Image](/Docs/screenshots/5.png)

7. Account should be created successfully

![Image](/Docs/screenshots/6.png)

##### 2.Proxy
For setting up the proxy for data collection of API data, follow the below-mentioned steps in EclecticIQ Intelligence centre Add-on.
1. Navigate to apps and select EclecticIQ Intelligence Centre Addon for Splunk 
2. Click on the Configuration tab
3. Click on the Proxy tab under the configuration tab
4. Fill in all the necessary details
    * Enable the checkbox(if wants to provide the proxy details)
    * Select http/https from proxy type dropdown
    * Enter Host and Port values in respective fields(optional)
    * Enter Username and Password in fields(optional)
    * Remote DNS resolution checkbox
5. Click on Save

![Image](/Docs/screenshots/7.png)

##### 3.Logging
For setting up the logging for data collection of API data, follow the below-mentioned steps in EclecticIQ Intelligence centre Add-on.
1. Navigate to apps and select EclecticIQ Intelligence Centre Addon for Splunk
2. Click on the Configuration tab
3. Click on the Logging tab under the configuration tab
4. Select the Log level. Available log levels are Debug, Info, Warning, Error and Critical
5. Click on Save

![Image](/Docs/screenshots/8.png)





##### 4.Additional Parameters
For setting up the Additional parameter for API calls and retry mechanism, follow below-mentioned steps in EclecticIQ Intelligence centre Add-on.

1. Navigate to apps and select EclecticIQ Intelligence Centre Addon for Splunk 
2. Click on the Configuration tab
3. Click on the Add-on Settings tab under the configuration tab.
4. Number of Retries(Number of attempts to be made, default to 3) 
5. Sleep time(Wait time in seconds between consecutive retries, default to 100)
6. Page size(Data to fetch in a single rest API call.Default to 100)
7. Click on Save

![Image](/Docs/screenshots/9.png)

## Observables Collection
**Prerequisites**
Users are advised to create separate indexes for storing the data before creating the Observables input. Please create a different indexes for Entities and Observables and select the corresponding indexes while creating the input for collect observables. 
For example, create an indexes named “eiq_entities” and “eiq_observables” select the corresponding index while creating the collect observables input

**Creating Index**
For creating indexes for Entities collection,
1. Login to Splunk Enterprise.
2. Click settings>indexes.
3. Click New index.
4. In the Index name field, specify the index name [eg:eiq_entities].
5. Set the Index data types to Events.
6. Fill in all the necessary fields.
7. Click on Save.

For creating indexes for observables collection,
1. Login to Splunk Enterprise.
2. Click settings>indexes.
3. Click New index.
4. In the Index name field, specify the index name [eg:eiq_observables].
5. Set the Index data types to Events.
6. Fill in all the necessary fields.
7. Click on Save.

After creating  the indexes. 
1. Go to Inputs Tab.
2. Click on Create New Input button.
3. Fill all the fields.
* Unique name: Unique name for the data input
* Interval: Time interval of input in seconds
* Global account: Name of global account created in configuration screen 
* Observables Index: Select the observable index from dropdown
* Entities Index: Select the entities index from dropdown
* Outgoing feeds: Outgoing feeds ID’s to collect observables from
* Select date: Date for observable collection to be entered in yyyy-mm-ddThh:mm:ss.SSSSSS format 
* Select observable types: Observable types to ingest
4. Click on Add.

![Image](/Docs/screenshots/10.png)

5. Created input will be displayed in the Inputs Screen.

![Image](/Docs/screenshots/11.png)

6. Go to Search Tab.Enter index=”<index name>” (Eg:index=”eiq_observables”)

![Image](/Docs/screenshots/12.png)

![Image](/Docs/screenshots/13.png)

### EclecticIQ Threat Investigator data injection and parsing
1. Users need to create an index (optional) to store the EclecticIQ Threat Investigator events 
    
   **Steps for creating an Index**

    1. Login to Splunk Enterprise
    2. Go to the Settings dropdown
    3. Click on indexes
    4. Click on New Index
    5. Enter the Index name(**Eg: index = “er_data”**) and fill all the fields and click on save.
    
    ![image](/Docs/screenshots/65.png)
    
   **Steps for Edit macros**

    1. Login to Splunk Enterprise
    2. Go to the Settings dropdown
    3. Click on Advanced search
    4. Click on Search macros
    5. Click on macro(needs to change, **i.e: eiq_er_index & eiq_sightings_search**)
    6. Respective index pop-up window display
    7. Edit the index name or Add the index name by using "OR" condition in Definition field
    8. Click on Save button.
    
    ![image](/Docs/screenshots/66.png)    
  

2. Create an HTTP Event Collector(HEC), TCP, or UDP on Splunk by selecting the index and source type name as “eclecticiq:er:json”
  
   **Note:** For parsing the fields from EclecticIQ Threat Investigator events the parsing logic is written under the source type named “eclecticiq:er:json”.
   
   **Steps for creating an HTTP Event Collector input**
   
    1. Login to Splunk Enterprise
    2. Go to the settings dropdown
    3. Click on Data inputs
    4. Click on HTTP Event Collector
    5. Click on New Token
    6. Fill all the fields and click on Next
    7. Select value `eclecticiq:er:json` from Source type dropdown 
    8. Select the Index name 
    9. Click on Review and Click on Submit
    
    ![image](/Docs/screenshots/67.png)   
  
   **Steps for creating TCP input**
    
    1. Login to Splunk Enterprises
    2. Go to the Settings dropdown
    3. Click on Data inputs
    4. Click on TCP
    5. Click on New Local TCP
    6. Select TCP and enter the Port number and click on Next
    7. Select value `eclecticiq:er:json` from Source type dropdown  
    8. Select App context as `EclecticIQ Threat Investigator Addon for Splunk` from the dropdown
    9. Select Host 
     * If select IP as Host. value of host field will set as IP Address of data sender.
   * If select DNS as Host. value of host field will set as Domain Name of data sender.
   * If select custom, value of host field will set as given value.
    10. Select the Index name
    11. Click on Review and Click on Submit
   
   ![image](/Docs/screenshots/68.png)   
  
   **Steps for creating UDP input**
                                                                                                
   1. Login to Splunk Enterprises
   2. Go to the Settings dropdown
   3. Click on Data inputs
   4. Click on UDP
   5. Click on New Local UDP
   6. Select TCP and enter the Port number and click on Next
   7. Select value `eclecticiq:er:json` from Source type dropdown 
   8. Select App context as `EclecticIQ Threat Investigator Addon for Splunk` from the dropdown
   9. Select Host
   * If select IP as Host. value of host field will set as IP Address of data sender.
   * If select DNS as Host. value of host field will set as Domain Name of data sender.
   * If select custom, value of host field will set as given value.
   10. Select the Index name
   11. Click on Review and Click on Submit

   ![image](/Docs/screenshots/69.png)   
   
3. Use the created HTTP Event Collector token or TCP or UDP in the EclecticIQ platform to send events to Splunk


### Installation & configuration for search head :

Install the EclecticIQ Intelligence Centre Addon for Splunk and EclecticIQ Intelligence Centre App for Splunk
Setup an account on configuration screen


**Installation for both APP & Addon**

1. Open Splunk Enterprise.
2. Click on Apps and click on Find more Apps.
3. Enter the app name to search for . . . 
4. Check the prerequisites and details.
5. Click on Install.

After installation, we can see the Add-on in Apps dropdown list

![Image](/Docs/screenshots/14.png)



**Installation for both APP & Addon(From File)**

1. Login to Splunk Enterprise
2. Navigate to manage apps and click

![Image](/Docs/screenshots/15.png)

3. Click on Install app from File

![Image](/Docs/screenshots/16.png)

4. Install App From File pop-up window will appear
5. Choose the file and click on checkbox
6. Click on Upload button

![Image](/Docs/screenshots/17.png)

After installation, we can see the Addon and App in Apps dropdown list

![Image](/Docs/screenshots/18.png)

**Configuration :** 
**Account**
After installation of EclecticIQ Intelligence Centre Addon to set up the account follow the below steps. 
1. Navigate to apps and select EclecticIQ Intelligence Centre Addon for Splunk 
2. Click on the Configuration tab
3. In the Accounts Sub tab click on Add
4. Give a unique name to the configuration and add the URL (https://<hostname>/api/<version>) of the product & API key generated from the Product
5. Verify SSL Certificate checkbox(Check the checkbox if the URL has an SSL certificate)
6. Click on Add

![Image](/Docs/screenshots/19.png)

7. Account should be created successfully

![Image](/Docs/screenshots/20.png)

8. Go to Search Tab.Enter index=”<index name>” (Eg:index=”eiq_observables”)

![Image](/Docs/screenshots/21.png)

![Image](/Docs/screenshots/22.png)

### Splunk App

## Create Sighting(From event fields)
1. Navigate to Search Tab.
2. Type the Query to get the Events.(Eg: index=”<index name>”)
3. Click on the event and expand. 
4. Click on the down arrow(right side) of the value(IP/URL/Domain/Hash/Email)
5. Click on EclecticIQ Create Sighting.
6. A pop-up window will appear to ask for the details below. 
Clicking on save will create sightings in the EIQ platform with provided details.
    * Sighting Value: Value which is clicked
    * Sighting description: Description of sighting
    * Sighting title: Title of sighting
    * Sighting tags delimited by a comma: Any tags to attach with sighting
    * Sighting type: Type of sighting. Possible values: ip, domain, url, email, hash,port
    * Sighting confidence: Confidence of sighting. Possible values: low, medium, high,unknown
    
   ![Image](/Docs/screenshots/23.png)
   
7. Go to Search tab and enter | inputlookup eiq_alerts_list. 
8. Verify the created sightings. 

![Image](/Docs/screenshots/24.png)
   
## Lookup Observable

1. Navigate to Search Tab.
2. Type the Query to get the Events.(Eg: index=”<index name>”)
3. Click on the event and expand. 
4. Click on the down arrow(right side) of the value(IP/URL/Domain/Hash/Email).

![Image](/Docs/screenshots/25.png)

5. Click on the EclecticIQ lookup observable.

6. A pop-up window will appear.

![Image](/Docs/screenshots/26.png)

7. Click on Create Sighting button.

8. A pop-up window will appear to ask for the details below. 

Clicking on save will create sightings in the EIQ platform with provided details.

    * Sighting Value: Value which is clicked
    * Sighting description: Description of sighting
    * Sighting title: Title of sighting
    * Sighting tags delimited by a comma: Any tags to attach with sighting
    * Sighting type: Type of sighting. Possible values: ip, domain, url, email, hash,port
    * Sighting confidence: Confidence of sighting. Possible values: low, medium, high,unknown

   ![Image](/Docs/screenshots/27.png)
   
9. Sighting should be created successfully.
10. Go to Search tab and enter | inputlookup eiq_alerts_list. 
   
   ![Image](/Docs/screenshots/28.png)


## Dashboard
App will render the widgets using the SPL queries fired against the splunk lookups for sighting. Sighting details will not be stored in the splunk indexes.Based on macros only the data will populated in dashboards

**Note:** Collection of observable index and entities index should be same in their respective macros. Otherwise edit/add index names in macros

**Steps for Edit/Add macros**
1. Login to Splunk Enterprises
2. Go to the Settings dropdown
3. Click on Advanced search
4. Click on Search macros
5. Click on macro(needs to change/add the index)
6. Respective index pop-up window display
7. Edit the index name or Add the index name by using "OR" condition in Definition field
9. Click on Save button.

**App Dashboards** 
1. Login to Splunk Enterprise.
2. Navigate to apps > EclecticIQ Intelligence Centre App for Splunk
3. Below tabs should be displayed
    * Home
    * Dashboards
        * Matched IP’s
        * Matched Domains and URLs
        * Matched File hashes
        * Matched Emails
        * All Matches
    * Information
        * Observables DB Info
        * Application Logs
    * EIQ Threat Investigator - Intelligence led hunting

**Home Dashboard**
App will render the widgets using the SPL queries fired against the splunk lookups for sighting
In Home Dashboard it shows information about collections of observables and Alerts.
* Total count of observables.
* Shows the details of Alerts: By severity, By Source, By Type.

![Image](/Docs/screenshots/29.png)
* Shows the Top detected Observables by types, Taxonomy/Tag.
* Shows Top detected observables and metadata by sourcetype.

![Image](/Docs/screenshots/30.png)
* Click on table row of top detected observable and metadata by source it will navigate to All Matches Dashboard and show the information.

![Image](/Docs/screenshots/31.png) 


**Matches by IP**
In Matches by IP Dashboard it shows information about Alerts by observable type IP.
* Shows the details of Alerts by severity of ipv4 and ipv6.
* Shows the details of top detected connections by Source observable and Destination observable.

![Image](/Docs/screenshots/32.png)
* Click on any row in the table and it will show more additional information about that row.

![Image](/Docs/screenshots/33.png)
   
**Matches by Domain and URL**
In Matches by Domain and URL Dashboard it shows information about Alerts by observable type Domain and URL.
* Shows the information of severity of Domain and URL.
* Shows the information of URL observable and Domain observable.

![Image](/Docs/screenshots/34.png)
* Clicking on any row in the table. It will show the additional information of that row.

**Matches by File Hashes**
In Matches by File Hashes Dashboard it shows information about Alerts by observable type File hashes.
* Shows the information about the severity of alerts.
* Shows the information of Alerts by Hashes.

![Image](/Docs/screenshots/35.png)
* Clicking on any row in the table. It will show more detailed information about that row.

**Matches by Email**
In Matches by Email Dashboard it shows information about Alerts by observable type Email.
* Shows the information of the Email alerts by severity.
* Shows the information of the alerts by sender observable and receiver observable.

![Image](/Docs/screenshots/36.png)
* Clicking on any row in the more info table. It will show more detailed information about that particular clicked value.(below the table)

**All Matches**

In All Matches Dashboard it shows information about Alerts by all types of observables(IP,Domain,URL,File Hash and Email).
* Shows the information of the severity of all observable types.
* Shows the information of top detected connections by source observables.

![Image](/Docs/screenshots/37.png)

![Image](/Docs/screenshots/38.png)
* Clicking on any row in the table. It will show more detailed information about that clicked value.(below the table)

![Image](/Docs/screenshots/39.png)

**Observables DB Info**

1. Navigate to Information Dropdown in EclecticIQ App for splunk.
2. Select Observable DB Info.

In Observables DB Info Dashboard shows the information of observables stored in the KV store.
* Shows the total count of observables stored in the KV store.
* Shows the information of observables distribution.
* Shows downloaded observables by type & by time and type.

![Image](/Docs/screenshots/40.png)
* Shows the details of count of observables by Type,Tags and Confidence.

![Image](/Docs/screenshots/41.png)
* Clicking on any row of count of observable type in the table will open in another window and show more detailed information of that particular row.

![Image](/Docs/screenshots/42.png)
* Clicking on any row of count of observables by tag in the table will open in another window and show more detailed information of that particular row

![Image](/Docs/screenshots/43.png)
* Clicking on any row of count of observables by Confidence in the table will open in another window and show more detailed information of that particular row.

![Image](/Docs/screenshots/44.png)

**Application Logs**

In Application logs Dashboard shows the information of the log levels,sourcetype and message in the table.

![Image](/Docs/screenshots/45.png)

**EIQ Threat Investigator - Intelligence led hunting**

This dashboard shows the EclecticIQ Endpoint Response events ingested in Splunk. All the data searching queries are SPL queries to populate the data from the indexes[Eg: index = “er_data”].
This dashboard is having the following filters:
* **Time Range:** This filter is used to view the particular events based on the time range by selecting the time from the Time Range dropdown filter( Default:24 hours)
* **Search:** User can filter the events based on keyword present in raw events.(Textbox Default: *).
* **Show ER events with an IC observable match dropdown:**
    * Based on the Yes/No option.
    

This dashboard is having the following panels :
* **Matching EIQ IC Observables table:** This table shows the alerts from the EclecticIQ Intelligence Centre and number of alerts created for that observable value.

![Image](/Docs/screenshots/46.png)
* **ER events matching IC observable types graph:** Whenever there is a match with observable, the matching Observable  type is shown here
    * When click on any observable type in graph, Events by Observable Type table will display and showing the detailed information about the observable type
* **ER events (Top 10) matching IC observables graph:** This graph shows the top 10 matching Observable value of ER data only
    * When click on any observable value in graph, Events by Observable Value table will display and showing the detailed information about the observable value
* **ER events matching IC observable maliciousness graph:** The matching Observable maliciousness will be shown here
    * When click on any maliciousness in graph, Events by Maliciousness table will display and showing the detailed information

**Note:**  Above three graphs are showing based on the Endpoint Response data sourcetype i.e, “eclecticiq:er:json”
 * **All events (Top 10) matching IC observables:** This graph shows the top 10 alerts which are created for Endpoint Response data and other data.

![Image](/Docs/screenshots/47.png)
* **EIQ ER events table:** This is a table containing the events information ingested from the  Endpoint Response device.
    * When selecting “No” from the Show ER events with an IC observable match dropdown this table shows the events information ingested from the Endpoint Response
      
   ![Image](/Docs/screenshots/48.png)
    * When selecting “Yes” from the Show ER events with an IC observable match dropdown this table shows the events which are matched with the data of EclecticIQ Intelligence Centre Addon Observables and which have caused some alerts(Via. Saved Search or Alert action)   
    
   ![Image](/Docs/screenshots/49.png)
* Detailed info table and Raw Splunk Event are displayed when clicking on any row event from the EIQ ER events table
* When clicking on event row in the Detailed info table it will navigate to EIQ ER event correlation Dashboard
   
   ![Image](/Docs/screenshots/50.png)

**EIQ ER event correlation Dashboard** 
This dashboard screen will be displayed whenever a user clicks on any events row in the EIQ Threat Investigator - Intelligence led hunting Dashboard.
**Filter:**
* **Timerange:** This filter is used to view the particular events based on the time range by selecting the time from the Timerange dropdown filter(Default: ±30 minutes)

This dashboard is having the following panels:
* **Event - GUID/PID/Path/Host Name:** This table displays the clicked event of the EIQ Threat Investigator - Intelligence led hunting Dashboard
* **Related events and observables - GUID/PID/Path/Host Name table:** This table displays all the events which are related to the clicked row of the EIQ Threat Investigator - Intelligence led hunting Dashboard
* **Timeline:** This chart will display the count of events as the floated points that are related to clicked events on the main dashboard

    * **Event timeline with GUID/PID/Path/Host Name for which the alert is created timechart:** If the sighting is created for triggered alert/manually then only the events are displayed as floated points.(sighting=1)
    * **Event timeline with GUID/PID/Path/Host Name for which the alert is not created timechart:** In this timechart, only those events which are not created any alert are displayed as floated points.(sighting=0)
   
   ![Image](/Docs/screenshots/51.png)
   
   ![Image](/Docs/screenshots/52.png)
   
   ![Image](/Docs/screenshots/53.png)
     
     
## Saved Searches
App will provide the saved searches which will be helpful for customers to map the data from other log sources with the threat intelligence data collected by the EIQ IC Addon in indexes
   
![Image](/Docs/screenshots/54.png)


**EclecticIQ alert**
To match the data from indexes follow below steps 
* Go to Search, reports, and alerts
* From App dropdown select EclecticIQ Intelligence CentreApp for Splunk
* Go to Owner dropdown and click on All
* Click on EclecticIQ alert
* Adjust the query to match the fields from index data to observable data
    * For example if the data is having field ipaddress which contains the source IP address of attack then in query add the field append it to the list of fields to be matched as given the the screenshot below.
   
   ![Image](/Docs/screenshots/55.png)
    * Then add it to the evaluation field which the field is mapped to. For example: if the ipaddress contains the ip address of the attacker then add it to eval of src field if it is containing destination ip add it to eval of dest field. Example given in below screenshot.
   
   ![Image](/Docs/screenshots/56.png)
* Adjust the schedule of the query.
* Click on Save
* Click on Edit > Enable

To match the data from datamodel follow below steps 
* Go to Search,reports and alerts.
* From App dropdown select EclecticIQ intelligence centre App for Splunk
* Select owner All
* Click on EclecticIQ tstats threat intelligence alert <type>.Type could be Domain,URL,Email,Hash,Source and Destination based upon the fields that should be matched.
* Adjust the schedule of the query.
* Click on Save.
* Click on Edit > Enable
Below Table specifies the Datamodel fields that will be matched with the observable data per alert.

![Image](/Docs/screenshots/62.png)


**EclecticIQ ER alert**

The app will provide the saved searches which will be used to map the data from EclecticIQ Endpoint Response with the threat intelligence data collected by the EclecticIQ Intelligence Center Splunk Addon in indexes.
Follow the below steps to match the data and create an alert 
* Go to Search, reports, and alerts
* From App dropdown select EclecticIQ Intelligence Centre App for Splunk
* Go to Owner dropdown and click on All
* Click on EclecticIQ ER alert
* Click on Edit dropdown and select Edit Schedule
* Check on the "Schedule Report" checkbox in the Edit Schedule popup window
* Select the Schedule and Time Range 
* Click on Save
* Click on Edit > Enable

## Create Sighting(Automatic Based on Saved Searches)
To create the sightings follow below steps
* Go to Search, reports, and alerts
* From App dropdown select EclecticIQ Intelligence Centre App for Splunk
* Go to Owner dropdown and click on All
* Click on EclecticIQ alert Edit dropdown and click on Edit Search

![Image](/Docs/screenshots/57.png)
* Copy the Search query

![Image](/Docs/screenshots/58.png)
* Click on Cancel button 
* Click on New Alert

![Image](/Docs/screenshots/59.png)
* Enter the unique name of the alert
* Paste the copied search in the search query but remove last line (outputlookup command)
* Adjust the schedule and trigger conditions(i.e, For each event)
* Click on Add action 

![Image](/Docs/screenshots/60.png)
* Select ‘Create EclecticIQ Sighting’ action from dropdown
* Enter the fields to send with the sighting(Based on the field name "value" in the observable index, "observable field" should be filled in) 

![Image](/Docs/screenshots/61.png)
* Click on Save
* Click on Edit > Enable

