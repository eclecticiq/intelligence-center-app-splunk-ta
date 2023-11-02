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
import xml.etree.ElementTree as ET

from splunk.persistconn.application import PersistentServerConnectionApplication

(path, _) = os.path.split(os.path.realpath(__file__))
sys.path.insert(0, path)

import splunklib.binding as bind
import splunklib.client as client
import classes.splunk_info as si
import classes.eiq_logger as eiq_logger

from classes.eiq_api import EclecticIQ_api as eiqlib

class Send(PersistentServerConnectionApplication):
    def __init__(self, command_line, command_arg):
        PersistentServerConnectionApplication.__init__(self)

    def handle(self, in_string):
        """
        Called for a simple synchronous request.
        @param in_string: request data passed in
        @rtype: string or dict
        @return: String to return in response.  If a dict was passed in,
                 it will automatically be JSON encoded before being returned.
        """

        in_string_json = json.loads(in_string)
        splunk_info = si.Splunk_Info(in_string_json["session"]["authtoken"])

        in_string_dict = {}

        for i in in_string_json["form"]:
            in_string_dict[i[0]] = i[1]

        # Prepare the logger
        log_level = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'log_level')

        logger = eiq_logger.Logger()
        script_logger = logger.logger_setup("WorkFlow Action - Create Sighting", level=log_level)

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

        if PASSWORD == "NO_PASSWORD_FOUND_FOR_THIS_USER":
            script_logger.error("No password found for user " + str(USERNAME))
            sys.exit(2)
        if PROXY_PASSWORD == "NO_PASSWORD_FOUND_FOR_THIS_USER":
            PROXY_PASSWORD = None

        # make sure that VERIFYSSL is a boolean True or False
        VERIFYSSL = True if str(VERIFYSSL) == "1" else False

        binding = bind.connect(token=in_string_json["session"]["authtoken"], owner="nobody")
        xml_reply_root = ET.fromstring(str(binding.get('/services/server/info')["body"]))
        instance_type_key = xml_reply_root.findall(".//*[@name='instance_type']")
        
        try:
            instance_type = instance_type_key[0].text
        except IndexError:
            instance_type = "on-prem"

        if instance_type == "cloud":
            VERIFYSSL = True

        binding.logout()

        eiq_api = eiqlib(BASEURL, EIQ_VERSION, "", PASSWORD,
                     VERIFYSSL, PROXY_IP, PROXY_USERNAME,
                     PROXY_PASSWORD, script_logger)

        try:
            reply = eiq_api.search_entity(observable_value=in_string_dict["value"])

            return {"payload": json.dumps(reply)}
        except Exception as e:
            return {"payload": "It was an error. Error: " + str(e)}
