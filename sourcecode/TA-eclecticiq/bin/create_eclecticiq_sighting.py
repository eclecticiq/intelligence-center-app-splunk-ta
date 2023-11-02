
# encoding = utf-8
# Always put this line at the beginning of this file
from __future__ import print_function

import os
import sys
import json
import classes.eiq_logger as eiq_logger
import classes.splunk_info as si
import splunklib.binding as bind
import xml.etree.ElementTree as ET

from classes.eiq_api import EclecticIQ_api as eiqlib


current_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload = json.loads(sys.stdin.read())
        sessionKey = str(payload["session_key"])
        splunk_info = si.Splunk_Info(sessionKey)
        splunk_paths = splunk_info.give_splunk_paths(current_dir)
        app_name = splunk_paths['app_name']

        # prepare the logger instance
        log_level = splunk_info.get_config(
            'ta-eclecticiq.conf',
            'main',
            'log_level')
        logger = eiq_logger.Logger()
        script_logger = logger.logger_setup("eiq_sightings_custom_action", level=log_level)

        # Get config params
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

        binding = bind.connect(token=sessionKey, owner="nobody")
        xml_reply_root = ET.fromstring(str(binding.get('/services/server/info')["body"]))
        instance_type_key = xml_reply_root.findall(".//*[@name='instance_type']")
        
        try:
            instance_type = instance_type_key[0].text
        except IndexError:
            instance_type = "on-prem"

        if instance_type == "cloud":
            VERIFYSSL = True
        binding.logout()

        # sign in to the platform
        eiq_api = eiqlib(BASEURL, EIQ_VERSION, "", PASSWORD,
                     VERIFYSSL, PROXY_IP, PROXY_USERNAME,
                     PROXY_PASSWORD, script_logger)

        observable_dict = [{
                            "observable_type": payload["configuration"]["observable_type"], 
                            "observable_value": payload["configuration"]["observable_value"],
                            "observable_maliciousness": payload["configuration"]["observable_confidence"],
                            "observable_classification": "bad"
                            }]

        try:
            reply = eiq_api.create_entity(observable_dict=observable_dict, source_group_name=SOURCEGROUPNAME, entity_title=payload["configuration"]["sighting_title"], entity_description=payload["configuration"]["sighting_description"],
                      entity_confidence=payload["configuration"]["sighting_confidence"], entity_tags=payload["configuration"]["sighting_tags"].split(","))

            script_logger.debug("Entity been created succefully. Sighting id is:" + str(reply))
        except Exception as e:
            script_logger.info("It was an error. Error: " + str(e))

    else:
        if sys.version_info >= (3, 0):
            print("FATAL Unsupported execution mode (expected --execute flag)", file=sys.stderr)
        else:
            print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(2)
