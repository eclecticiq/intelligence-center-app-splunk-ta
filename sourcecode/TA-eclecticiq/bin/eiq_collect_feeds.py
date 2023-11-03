#!/usr/bin/env python

"""
Copyright 2023 EclecticIQ B.V.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
import hashlib  # to create content for the KV-store _key field
import csv
import json
import time
import re
import splunklib.client as client
import splunklib.binding as binding
import classes.splunk_info as si
import classes.eiq_logger as eiq_logger
import xml.etree.ElementTree as ET

from classes.eiq_api import EclecticIQ_api as eiqlib


if sys.version_info >= (3, 0):
    import io
else:
    import StringIO

current_dir = os.path.dirname(os.path.abspath(__file__))

# List with all the fields that are in the feed and we want in Splunk
EXPORT_FIELDS_LIST = [
    'value', 'type', 'value_url', 'timestamp',
    'entity.id', 'entity.type', 'entity.title', 'meta.tlp', 'meta.ingest_time',
    'meta.estimated_observed_time', 'meta.estimated_threat_start_time',
    'meta.estimated_threat_end_time', 'meta.relevancy', 'meta.tags', 'meta.taxonomy',
    'meta.source_reliability', 'meta.entity_url', 'meta.classification', 'meta.confidence'
]


def add_feeds_info_to_meta_kv(feeds_info, feeds_list, last_ingested={}):
    global app_name, sessionKey, splunk_info

    collection_name = "eiq_feeds_list"
    service = client.connect(token=sessionKey, owner="nobody", app=app_name)
    collection = service.kvstore[collection_name]
    add_data = {}

    for feed_dict in feeds_info:
        if str(feed_dict["id"]) in feeds_list:
            if sys.version_info >= (3, 0):
                kv_key = hashlib.sha224(str(feed_dict['id']).encode()).hexdigest()
            else:
                kv_key = hashlib.sha224(str(feed_dict['id'])).hexdigest()
            add_data["_key"] = kv_key
            add_data["feed_id"] = str(feed_dict['id'])
            add_data["feed_name"] = str(feed_dict['name'])
            add_data["created_at"] = str(feed_dict['created_at'])
            if not last_ingested:
                add_data["last_ingested"] = "None"
            else:
                try:
                    add_data["last_ingested"] = last_ingested[str(feed_dict["id"])]
                except:
                    add_data["last_ingested"] = "None"

            add_data["update_strategy"] = str(feed_dict['update_strategy'])
            collection.data.insert(json.dumps(add_data))


def update_meta_kv_if_need(feeds_info):
    global app_name, sessionKey, splunk_info

    collection_name = 'eiq_feeds_list'
    service = client.connect(token=sessionKey, owner='nobody', app=app_name)
    collection = service.kvstore[collection_name]
    old_kv = collection.data.query()
    old_feeds_list = []
    new_feeds_list = splunk_info.get_config(
        'ta-eclecticiq.conf',
        'main',
        'feedslist'
    ).replace(' ', '').split(',')

    if not old_kv:  # if KV is empty, will add new data using list from .conf file
        add_feeds_info_to_meta_kv(feeds_info, new_feeds_list)

    else:  # if not empty find the diff with .conf and update old kv and safe last_ingest field
        for item in old_kv:
            old_feeds_list.append(item['feed_id'])

        if set(old_feeds_list) != set(new_feeds_list):  # check diff between KV and .conf file
            old_useful_ids = list(set(new_feeds_list).intersection(set(old_feeds_list)))
            old_unuseful_ids = list(set(old_feeds_list).difference(set(new_feeds_list)))
            old_states = {}

            for item in old_kv:
                if str(item['feed_id']) in old_useful_ids:
                    old_states[item['feed_id']] = item['last_ingested']

            collection.data.delete()
            add_feeds_info_to_meta_kv(feeds_info, new_feeds_list, old_states)

            if old_unuseful_ids:
                collection_name = 'eiq_ioc_list'
                service = client.connect(token=sessionKey, owner='nobody', app=app_name)
                collection = service.kvstore[collection_name]
                for feed in old_unuseful_ids:
                    query = json.dumps({'feed_id_eiq': str(feed)})
                    collection.data.delete(query)


def update_state_meta_kv(id, state, field):
    global app_name, sessionKey, splunk_info

    service = client.connect(token=sessionKey, owner="nobody", app=app_name)
    collection_name = "eiq_feeds_list"
    collection = service.kvstore[collection_name]

    try:  # try to find raw with id and then get data from this raw
        query = json.dumps({"feed_id": str(id)})
        feed_state_dict, = collection.data.query(query=query)
    except:
        script_logger.debug(
            "No information with feed id=" + str(id) + " in KV store eiq_feed_list")
        return

    feed_state_dict[field] = str(state)
    collection.data.update(feed_state_dict["_key"], json.dumps(feed_state_dict))


def format_to_kv(data_to_add, field_name, value):
    if re.match("\w+\.", field_name):
        path = re.search("\w+\.", field_name).group(0)[:-1]
        new_field_name = re.sub("\w+\.", "", field_name) + "_eiq"

        try:
            data_to_add[path][new_field_name] = value
        except KeyError:
            data_to_add[path] = {new_field_name: value}
    else:
        data_to_add[field_name + "_eiq"] = value

    return data_to_add


def check_state_from_meta_kv(feed_id):
    global app_name, sessionKey

    service = client.connect(token=sessionKey, owner="nobody", app=app_name)
    collection_name = "eiq_feeds_list"
    collection = service.kvstore[collection_name]

    try:
        query = json.dumps({"feed_id": str(feed_id)})
        feed_state_dict, = collection.data.query(query=query)
    except:
        script_logger.debug(
            "No information with feed_id" + str(feed_id) + "in KV store")

        feed_state_dict = {
            'feed_id': str(feed_id),
            'created_at': None,
            'last_ingested': None}

    if feed_state_dict["last_ingested"] == "None":
        feed_state_dict["last_ingested"] = None

    if feed_state_dict["created_at"] == "None":
        feed_state_dict["created_at"] = None

    return feed_state_dict

def es_ti_batches_prepare(list_to_add):
    result = {
        "ip":[],
        "file":[],
        "http":[],
        "email":[]
    }

    for i in list_to_add:
        if i['type_eiq'] == "ipv4":
            result["ip"].append({"ip":i["value_eiq"], "_key": i["_key"]})
        elif i['type_eiq'] in ["hash-md5", "hash-sha1", "hash-sha256", "hash-sha512"]:
            result["file"].append({"file_hash":i["value_eiq"], "_key": i["_key"]})
        elif i['type_eiq'] == "uri":
            result["http"].append({"url":i["value_eiq"], "_key": i["_key"]})
        elif i['type_eiq'] == "domain":
            result["ip"].append({"domain":i["value_eiq"], "_key": i["_key"]})
        elif i['type_eiq'] == "email":
            result["email"].append({"src_user":i["value_eiq"], "_key": i["_key"]})

    return result

def es_ti_add(service, es_list_to_add):
    endpoints = {
        "ip":"ip_intel",
        "file":"file_intel",
        "http":"http_intel",
        "email":"email_intel"
    }
    result = ""

    for i in es_list_to_add:
        if (len(es_list_to_add[i])) > 0:
            try:
                result = service.post("/services/data/threat_intel/item/" + endpoints[i], body={"item": json.dumps(es_list_to_add[i])})
            except Exception as e:
                script_logger.error("Adding IOC to ES failed, value: " + str(i) + ". Exception: " + str(e))                


    return result

def es_ti_batches_prepare_remove(list_to_remove):
    result = {
        "ip":[],
        "file":[],
        "http":[],
        "email":[]
    }

    for i in list_to_remove:
        if i['type_eiq'] == "ipv4":
            result["ip"].append({"_key": i["_key"]})
        elif i['type_eiq'] in ["hash-md5", "hash-sha1", "hash-sha256", "hash-sha512"]:
            result["file"].append({"_key": i["_key"]})
        elif i['type_eiq'] == "uri":
            result["http"].append({"_key": i["_key"]})
        elif i['type_eiq'] == "domain":
            result["ip"].append({"_key": i["_key"]})
        elif i['type_eiq'] == "email":
            result["email"].append({"_key": i["_key"]})

    return result

def es_ti_remove(service, es_list_to_remove):
    endpoints = {
        "ip":"ip_intel",
        "file":"file_intel",
        "http":"http_intel",
        "email":"email_intel"
    }
    result = ""

    for i in es_list_to_remove:
        if (len(es_list_to_remove[i])) > 0:
            for k in es_list_to_remove[i]:
                try:
                    result = service.delete("/services/data/threat_intel/item/" + endpoints[i] + "/" + str(k["_key"]))
                except Exception as e:
                    script_logger.error("Remove of IOC " + str(k) + " failed. Exception: " + str(e))

    return result

def export_csv_to_kv(feed_id, text, count=0, diff_flag=False, es_ingest=False):
    global app_name, sessionKey, splunk_info
    service = client.connect(token=sessionKey, owner="nobody", app=app_name)
    #bind = binding.connect(token=sessionKey, owner="nobody", app=app_name)
    collection_name = "eiq_ioc_list"
    collection = service.kvstore[collection_name]

    if sys.version_info >= (3, 0):
        text = io.StringIO(text)
    else:
        text = StringIO.StringIO(text)

    csvreader = csv.DictReader(text)

    list_to_add = []

    if 'diff' not in csvreader.fieldnames:
        # If there is no "diff" column in the CSV
        # So the update method is set to "replace", this means we
        # delete everything from this feed and then recreate it.

        if count == 0:
            # we delete data from KV only before first block is downloaded

            script_logger.debug(
                "Update method is 'replace' and feed id=" + str(feed_id) + ", so delete current "
                                                                           "content of " + str(
                    collection_name) + " and then add "
                                       "everything again")
            collection.data.delete(json.dumps({"feed_id_eiq": str(feed_id)}))

        # For performance monitoring
        start_time = time.time()

        for row in csvreader:
            # Loop through the rows in the CSV
            # Make a hash from the combo of feed_id type and
            # value to use as _key field
            if sys.version_info >= (3, 0):
                kv_key = hashlib.sha224((str(feed_id) + row['type'] + row['value']).encode()).hexdigest()
            else:
                kv_key = hashlib.sha224(str(feed_id) + row['type'] + row['value']).hexdigest()
            data_to_add = {"_key": kv_key, "feed_id_eiq": str(feed_id)}
            format_to_kv(data_to_add, "source.name", row["source.names"])

            for field_name in EXPORT_FIELDS_LIST:
                # Loop through the fields that need to be in the collection
                format_to_kv(data_to_add, field_name, row[field_name])

            list_to_add.append(data_to_add)

        if es_ingest == "1":
            es_ti_ingestion_status = es_ti_add(service, es_ti_batches_prepare(list_to_add))

        for item in list_to_add:
            collection.data.batch_save(item)

        time_taken = time.time() - start_time
        script_logger.debug(
            "Feed id=" + str(feed_id) + ", block number " + str(count + 1) + " contained " + str(
                len(list_to_add)) + " rows and took " + str(
                time_taken) + " seconds")

    else:
        # There is a diff column so we need
        # to change existing rows
        # delete or add new rows
        script_logger.debug(
            "Update method is 'diff', so check for changes and update " +
            str(collection_name))

        # For performance monitoring
        start_time = time.time()

        list_to_add = []
        list_to_delete = []
        list_to_delete_es = []

        if diff_flag:
            # if crated_at field was changed, we need to delete all data and
            # ingest all blocks again
            collection.data.delete(json.dumps({"feed_id_eiq": str(feed_id)}))

        for row in csvreader:
            # Loop through the rows and see what must be done
            if sys.version_info >= (3, 0):
                kv_key = hashlib.sha224((str(feed_id) + row['type'] + row['value']).encode()).hexdigest()
            else:
                kv_key = hashlib.sha224(str(feed_id) + row['type'] + row['value']).hexdigest()
            data_to_add = {}

            if row['diff'] == 'add':

                # write new entry
                data_to_add["_key"] = kv_key
                data_to_add["feed_id_eiq"] = str(feed_id)
                data_to_add["source"] = {"name_iq": row["source.names"]}

                # Loop through the fields that need to be in the collection
                for field_name in EXPORT_FIELDS_LIST:
                    format_to_kv(data_to_add, field_name, row[field_name])

                list_to_add.append(data_to_add)

            elif row['diff'] == 'del':
                list_to_delete.append({"_key": kv_key, "type_eiq": "DELETE_RAW"})
                list_to_delete_es.append({"_key": kv_key, "type_eiq": row['type']})


        if list_to_add:
            for item in list_to_add:
                collection.data.batch_save(item)

            if es_ingest == "1":
                es_ti_ingestion_status = es_ti_add(service, es_ti_batches_prepare(list_to_add))

        if list_to_delete:
            for item in list_to_delete:
                collection.data.batch_save(item)
            collection.data.delete(json.dumps({"type_eiq": "DELETE_RAW"}))

            if es_ingest == "1":
                es_ti_ingestion_status = es_ti_remove(service, es_ti_batches_prepare_remove(list_to_delete_es))

        time_taken = time.time() - start_time
        script_logger.debug(
            "Feed id=" + str(feed_id) + ", block number " + str(count + 1) + " contained " + str(
                len(list_to_add)) + " rows to add and " + str(
                len(list_to_delete)) + " rows to delete" + " and took " + str(
                time_taken) + " seconds")


if __name__ == '__main__':    

    sessionKey = sys.stdin.readline().strip()
    splunk_info = si.Splunk_Info(sessionKey)

    # Prepare the logger
    log_level = splunk_info.get_config(
        'ta-eclecticiq.conf',
        'main',
        'log_level')
    logger = eiq_logger.Logger()
    script_logger = logger.logger_setup("eiq_collect_feeds", level=log_level)

    if len(sessionKey) == 0:
        script_logger.critical(
            "Did not receive a session key from splunkd. "
            "Please enable passAuth in inputs.conf for this script")
        sys.exit(2)

    try:
        # Check the search head cluster status. If the app is deployed in a
        # searchhead cluster only collect the feed if the script is running on
        # the cluster captain. This is to prevent that the EclecticIQ appliance
        # is getting a "DDOS" with feed requests from Splunk, especially in
        # big cluster environments. Also this prevents unnecessary network
        # traffic, Splunk wil replicate the data within the cluster anyway.
        shc_status = splunk_info.shcluster_status()
        splunk_paths = splunk_info.give_splunk_paths(current_dir)
        app_name = splunk_paths['app_name']

        # Only continue if
        # - this is the SHC captain
        # - this is a standalone installation
        if shc_status != "shc_captain" and shc_status != "shc_none":
            if shc_status == "shc_deployer" or shc_status == "shc_member":
                script_logger.info(
                    "Script is running in a cluster but this is not the "
                    "captain, searchhead cluster role: " + str(shc_status))
            else:
                script_logger.warning(
                    "Could not determine a valid system status to run the "
                    "download, a valid status is shc_captain OR shc_none, "
                    "got status: " + str(shc_status))
            sys.exit(2)

        # Get the config from the ta-eclecticiq.conf file and
        # get the password from the Splunk password store
        BASEURL = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'eiq_baseurl')
        EIQ_VERSION = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'eiq_version')
        ES_TI_INGEST = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'es_ti_ingest')
        FEEDSLIST = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'feedslist'
        ).replace(' ', '').split(',')
        VERIFYSSL = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'verify-ssl')
        PROXY_IP = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'proxy_ip')
        PROXY_USERNAME = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'proxy_username')
        PASSWORD = splunk_info.get_credetials("eiq_user")
        PROXY_PASSWORD = splunk_info.get_credetials(PROXY_USERNAME)

        # make sure we have a username and a password
        # before we try to authenticate

        if PASSWORD == "NO_PASSWORD_FOUND_FOR_THIS_USER":
            script_logger.error("No password found.")
            sys.exit(2)
        if PROXY_PASSWORD == "NO_PASSWORD_FOUND_FOR_THIS_USER":
            PROXY_PASSWORD = None

        # make sure that VERIFYSSL is a boolean True or False
        VERIFYSSL = True if str(VERIFYSSL) == "1" else False

        LOOKUPS_PATH = os.path.normpath(
            splunk_paths['app_root_dir'] + os.sep + "lookups")

        binding = binding.connect(token=sessionKey, owner="nobody", app=app_name)
        xml_reply_root = ET.fromstring(str(binding.get('/services/server/info')["body"]))
        instance_type_key = xml_reply_root.findall(".//*[@name='instance_type']")
        try:
            instance_type = instance_type_key[0].text
        except IndexError:
            instance_type = "on-prem"

        if instance_type == "cloud":
            VERIFYSSL = True

        api = eiqlib(BASEURL, EIQ_VERSION, "", PASSWORD,
                     VERIFYSSL, PROXY_IP, PROXY_USERNAME,
                     PROXY_PASSWORD, script_logger)

        feeds_info = api.get_feed_info(','.join(FEEDSLIST))

        update_meta_kv_if_need(feeds_info)

        for item in feeds_info:
            # Loop through all received feeds

            state = check_state_from_meta_kv(item['id'])

            if item['created_at'] != state['created_at']:
                # check created_at field between platform and splunk meta KV information
                # if they are different
                # delete all from this feed from Splunk KV and ingest in again from ground up
                # update meta KV info about this feed to default

                script_logger.error("Feed id=" + str(item[
                                                         'id']) + "was changed in EIQ Platform, starting to delete "
                                                                  "all data from feed id=" + str(
                    item['id']) + " and ingest it again from EIQ Platform")
                flag = True
                update_state_meta_kv(item['id'], item['created_at'], "created_at")
                update_state_meta_kv(item['id'], "None", "last_ingested")
                state = check_state_from_meta_kv(item['id'])
            else:
                flag = False

            blocks = api.get_feed_content_blocks(item, state)
            if blocks:
                counter = 0
                for block in blocks:
                    # Loop through all received blocks
                    # download data from link
                    # export it to KV
                    # update last_ingested field in meta KV

                    data_from_block = api.download_block_list(block)
                    export_csv_to_kv(item['id'], data_from_block, counter, flag, ES_TI_INGEST)
                    counter += 1
                    flag = False
                    update_state_meta_kv(item['id'], block, "last_ingested")
                script_logger.info(
                    "Feed id=" + str(item['id']) + " name='" + str(item['name']) + "' was updated, " + str(
                        counter) + " blocks were used")
            elif blocks is not None:
                script_logger.info(
                    "Feed id=" + str(item['id']) + " name='" + str(item['name']) + "' up-to-date, nothing to download")
                continue
            else:
                continue

    except Exception as e:
        script_logger.exception('Error occurred: ' + str(e) + '. Exit')
        raise
