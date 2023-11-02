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
import json
import splunklib.client as client
import classes.eiq_logger as eiq_logger
import classes.splunk_info as si
import splunklib.binding as binding
import xml.etree.ElementTree as ET

from classes.eiq_api import EclecticIQ_api as eiqlib

current_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    sessionKey = sys.stdin.readline().strip()
    splunk_info = si.Splunk_Info(sessionKey)

    splunk_paths = splunk_info.give_splunk_paths(current_dir)
    app_name = splunk_paths['app_name']

    # prepare the logger instance
    log_level = splunk_info.get_config(
        'ta-eclecticiq.conf',
        'main',
        'log_level')
    logger = eiq_logger.Logger()
    script_logger = logger.logger_setup("eiq_sightings", level=log_level)

    if len(sessionKey) == 0:
        script_logger.critical(
            "Did not receive a session key from splunkd. "
            "Please enable passAuth in inputs.conf for this script")
        sys.exit(2)

    service = client.connect(token=sessionKey, owner="nobody", app=app_name)
    collection = service.kvstore['eiq_alerts']

    try:
        # Check the searchhead cluster status.
        # If the app is deployed in a searchhead cluster, # only send sightings
        # if the script is running on the cluster captain.
        # This is to prevent that you send the same sighting multiple times.
        shc_status = splunk_info.shcluster_status()
        splunk_paths = splunk_info.give_splunk_paths(current_dir)

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

        SOURCEGROUPNAME = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'sourcegroupname')
        BASEURL = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'eiq_baseurl')
        EIQ_VERSION = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'eiq_version')
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

        # make sure that VERIFYSSL is a boolean True or False
        VERIFYSSL = True if str(VERIFYSSL) == "1" else False

        binding = binding.connect(token=sessionKey, owner="nobody", app=app_name)
        xml_reply_root = ET.fromstring(str(binding.get('/services/server/info')["body"]))
        instance_type_key = xml_reply_root.findall(".//*[@name='instance_type']")
        try:
            instance_type = instance_type_key[0].text
        except IndexError:
            instance_type = "on-prem"

        if instance_type == "cloud":
            VERIFYSSL = True
        binding.logout()

        # create a list with all the sighting types that there can be and
        # create an empty list to populate later with the sightings that were
        # selected to send to the platform.
        type_names_list = [
            'ipv4', 'ipv6', 'domain', 'host', 'uri', 'hash-md5', 'hash-sha1', 'hash-sha256',
            'hash-sha512', 'email']
        filtered_types_list = []

        for type_name in type_names_list:
            val = splunk_info.get_config(
                "ta-eclecticiq.conf",
                'main',
                type_name)
            if val == '1':
                filtered_types_list.append(type_name)

        # sign in to the platform
        eiq_api = eiqlib(BASEURL, EIQ_VERSION, "", PASSWORD,
                     VERIFYSSL, PROXY_IP, PROXY_USERNAME,
                     PROXY_PASSWORD, script_logger)

        query = json.dumps({'sighting': '0'})
        result = collection.data.query(query=query)

        script_logger.debug('In the sightings list to create there are: ' + str(len(result)) + ' records.')

        for k in result:
            sighting_type = str(k['type_eiq'])
            sighting_value = str(k['value_eiq'])
            record = [{
                    'observable_type': sighting_type,
                    'observable_value': sighting_value,
                    'observable_maliciousness': 'medium',
                    'observable_classification': 'bad'
                     }]
            entity_title = 'Splunk detected {0} {1}'.format(sighting_type, sighting_value)
            entity_description = 'Automatically generated sighting of {0} {1}'.format(sighting_type, sighting_value)

            if sighting_type in filtered_types_list:
                eiq_api.create_entity(record, SOURCEGROUPNAME, entity_title, entity_description)
                script_logger.debug('Changing sightings status in Splunk eiq_alerts KV store for record ' +
                                    str(k['_key']) + 'sighting of {0} {1}'.format(sighting_type, sighting_value))
                k['sighting'] = '1'
                id = k['_key']
                upd_query = json.dumps(k)
                collection.data.update(id=id, data=upd_query)
            else:
                script_logger.debug('Sighting of {0} {1}'.format(sighting_type, sighting_value) +
                                    ' has not been created. It is not in the allowed sighting list. Check the App '
                                    'Setup page.')

    except Exception as e:
        script_logger.error('Error occurred: ' + e.message)
        raise
