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
import re
import io

import splunk.admin as admin
import splunklib.client as client

import classes.eiq_logger as eiq_logger

script_log_level = 30  # 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL

splunk_home_dir = os.environ['SPLUNK_HOME']
splunk_apps_dir = os.path.normpath(
    splunk_home_dir + os.sep + "etc" + os.sep + "apps")
script_dir = os.path.dirname(os.path.abspath(__file__))
app_name = script_dir.replace(splunk_apps_dir + os.sep, "").split(os.sep, 1)[0]
app_root_dir = os.path.normpath(splunk_apps_dir + os.sep + app_name)
log_root_dir = os.path.normpath(app_root_dir + os.sep + "logs")
script_log_file = os.path.normpath(log_root_dir + os.sep + "eiq_app_setup.log")

logger = eiq_logger.Logger()
script_logger = logger.logger_setup(
    name="eiq_config",
    log_file=script_log_file,
    level=script_log_level
)


class ConfigApp(admin.MConfigHandler):
    # setup the supported arguments,
    # the fields that are defined on the setup page
    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in [
                'feedslist', 'eiq_baseurl', 'eiq_version', 'sourcegroupname',
                'es_ti_ingest', 'eiq_password', 'ipv4', 'ipv6', 'domain', 'uri',
                'hash-md5', 'hash-sha1', 'hash-sha256', 'hash-sha512',
                'email', 'sightings_query', 'verify-ssl', 'log_level',
                'proxy_ip', 'proxy_username', 'proxy_password'
            ]:
                self.supportedArgs.addOptArg(arg)

    # Read the inital values of the options from the file ta-eclecticiq.conf
    # and place them in the setup page.
    # If no setup has been done before read from the app default file
    # If the setup has been done before read from the app local file first
    # and if a field has no value there, fallback to the default values
    def handleList(self, confInfo):
        # Connect to Splunk to update or read some values if needed, like:
        # username
        # password
        # macros.conf
        session_key = self.getSessionKey()
        if len(session_key) == 0:
            script_logger.critical(
                "Did not receive a session key from splunkd. "
                "Please enable passAuth in inputs.conf for this script.")
            return

        try:
            service = client.connect(token=session_key, app="TA-eclecticiq")
        except Exception:
            script_logger.exception("An error occurred connecting to splunkd")
            return

        conf_dict = self.readConf("ta-eclecticiq")
        if conf_dict is None:
            return

        keys_list1 = [
            'feedslist', 'eiq_baseurl', 'eiq_version', 'sourcegroupname',
            'es_ti_ingest', 'eiq_password', 'proxy_ip', 'proxy_username',
            'proxy_password']
        keys_list2 = [
            'ipv4', 'ipv6', 'domain', 'uri', 'hash-md5', 'hash-sha1',
            'hash-sha256', 'hash-sha512', 'email', 'verify-ssl']
        for stanza, settings in conf_dict.items():
            for key, val in settings.items():
                if key in keys_list1 and val in [None, '', 'configured']:
                    val = ''

                if key in keys_list2:
                    if int(val) == 1:
                        val = '1'
                    else:
                        val = '0'

                if key == 'sightings_query':
                    # get the content from the macro "eiq_sightings_search",
                    # don't trust the config file because the
                    # macro could have been edited via the GUI
                    macro_content = service.get(
                        "properties/macros/eiq_sightings_search/definition")[
                        "body"]
                    val = str(macro_content)

                if key == 'log_level':
                    # make sure we have a valid value for log_level
                    if 0 < int(val) < 20:
                        val = '10'
                    elif 20 <= int(val) < 30:
                        val = '20'
                    elif 30 <= int(val) < 40:
                        val = '30'
                    elif 40 <= int(val) < 50:
                        val = '40'
                    elif int(val) >= 50:
                        val = '50'
                    else:
                        val = '20'

                confInfo[stanza].append(key, val)

    # After the user clicks the "SAVE" button, take the updated settings,
    # normalize them and then save them.
    def handleEdit(self, confInfo):
        # Connect to Splunk to update or read some values if needed, like:
        # username
        # password
        # macros.conf
        session_key = self.getSessionKey()
        if len(session_key) == 0:
            script_logger.critical(
                "Did not receive a session key from splunkd. "
                "Please enable passAuth in inputs.conf for this script.")
            return

        try:
            service = client.connect(token=session_key, app="TA-eclecticiq")
        except Exception:
            script_logger.exception("An error occurred connecting to splunkd")
            return

        # Make two lists with field names,
        # one with the text fields, minus the username and password fields,
        # one with the boolean fields.
        # this is so we don't have to make a if else loop for each field.
        text_fields_list = [
            'feedslist', 'eiq_baseurl', 'eiq_version', 'sourcegroupname',
            'sightings_query'
        ]
        boolean_sightings_fields_list = [
            'ipv4', 'ipv6', 'domain', 'uri', 'hash-md5', 'hash-sha1', 'hash-sha256',
            'hash-sha512', 'email', 'es_ti_ingest'
        ]

        args_data = self.callerArgs.data

        # Loop through the text fields
        # if the field is None or empty make it empty
        for field_name in text_fields_list:
            if args_data[field_name][0] in [None, '']:
                args_data[field_name][0] = ''

        # loop through the boolean sightings fields if one of them is enabled
        # set a variable to later enable the datamodel acceleration
        enable_dm_acc = "0"
        for field_name in boolean_sightings_fields_list:
            if int(args_data[field_name][0]) == 1:
                args_data[field_name][0] = '1'
                enable_dm_acc = '1'
            else:
                args_data[field_name][0] = '0'

        if int(args_data['verify-ssl'][0]) == 1:
            args_data['verify-ssl'][0] = '1'
        else:
            args_data['verify-ssl'][0] = '0'

        if args_data['proxy_ip'][0] in [None, '']:
            proxy_ip = 0
            args_data['proxy_ip'][0] = ''
        else:
            proxy_ip = args_data['proxy_ip'][0]

        # Check the user name and password fields if they are None or empty
        # set a variable so we know we don't have to store them in the Splunk
        # credential store later.
        if args_data['proxy_username'][0] in [None, '']:
            proxy_name = 0
            args_data['proxy_username'][0] = ''
        else:
            proxy_name = args_data['proxy_username'][0]

        if args_data['eiq_password'][0] in [None, '', 'configured']:
            eiq_pass = 0
            args_data['eiq_password'][0] = ''
        else:
            eiq_pass = args_data['eiq_password'][0]
            args_data['eiq_password'][0] = 'configured'

        if args_data['proxy_password'][0] in [None, '', 'configured']:
            proxy_pass = 0
            args_data['proxy_password'][0] = ''
        else:
            proxy_pass = args_data['proxy_password'][0]
            args_data['proxy_password'][0] = 'configured'

        # Make sure the log_level is set to a valid value before we save it.
        if 0 < int(args_data['log_level'][0]) < 20:
            args_data['log_level'][0] = '10'
        elif 20 <= int(args_data['log_level'][0]) < 30:
            args_data['log_level'][0] = '20'
        elif 30 <= int(args_data['log_level'][0]) < 40:
            args_data['log_level'][0] = '30'
        elif 40 <= int(args_data['log_level'][0]) < 50:
            args_data['log_level'][0] = '40'
        elif int(args_data['log_level'][0]) >= 50:
            args_data['log_level'][0] = '50'
        else:
            args_data['log_level'][0] = '20'

        args_data['eiq_baseurl'][0] = re.sub(r"(https?\:\/\/[^\/]+)(.*)", r"\1", args_data['eiq_baseurl'][0])
        args_data['eiq_version'][0] = re.sub(r"(\d+\.*\d*)(.*)", r"\1", args_data['eiq_version'][0])

        # write everything to the eclecticiq config file
        self.writeConf('ta-eclecticiq', 'main', args_data)

        # cahnge encoding for local config file for windows
        local_config = os.path.normpath(os.environ['SPLUNK_HOME'] + os.sep + "etc" + os.sep + "apps" + os.sep + "TA-eclecticiq" + os.sep + "local" + os.sep + "ta-eclecticiq.conf")
        with io.open(local_config, mode="r", encoding="utf-8-sig") as fd:
            content = fd.read()
        with io.open(local_config, mode="w", encoding="utf-8") as fd:
            fd.write(content)

        # Store the username and password if they are not empty
        if eiq_name != 0 and eiq_pass != 0:
            try:
                # If the credential already exists, delete it.
                for storage_password in service.storage_passwords:
                    if storage_password.username == eiq_name:
                        service.storage_passwords.delete(
                            username=storage_password.username)
                        break
                # Create the credentials
                service.storage_passwords.create(eiq_pass, eiq_name)
            except Exception:
                script_logger.exception(
                    "An error occurred updating credentials. "
                    "Please ensure your user account has admin_all_objects "
                    "and/or list_storage_passwords capabilities.")

        # Store the proxy username and password if they are not empty
        if proxy_name != 0 and proxy_pass != 0:
            try:
                # If the credential already exists, delete it.
                for storage_password in service.storage_passwords:
                    if storage_password.username == proxy_name:
                        service.storage_passwords.delete(
                            username=storage_password.username)
                        break
                # Create the credentials
                service.storage_passwords.create(proxy_pass, proxy_name)
            except Exception:
                script_logger.exception(
                    "An error occurred updating proxy credentials. "
                    "Please ensure your user account has admin_all_objects "
                    "and/or list_storage_passwords capabilities.")

        current_macro_content = service.get(
            "properties/macros/eiq_sightings_search/definition")["body"]

        if (args_data['sightings_query'][0] not in [None, '']
            and
                str(args_data['sightings_query'][0])
                !=
                str(current_macro_content)):
            try:
                # update the macro named "eiq_sightings_search" in the app
                service.post("properties/macros/eiq_sightings_search",
                             definition=args_data['sightings_query'][0])
            except Exception:
                script_logger.exception(
                    "An error occurred with the update of the "
                    "'eiq_sightings_search' macro")

        if args_data['eiq_baseurl'][0] not in [None, '']:
            try:
                # update the workflow action named EclecticIQ_entity_lookup in the app
                workflow_action_update = str(args_data['eiq_baseurl'][0]) + '/search/observable?q=$@field_value$'
                service.post("properties/workflow_actions/EclecticIQ_entity_lookup/disabled", value = '0')
                service.post("properties/workflow_actions/EclecticIQ_entity_lookup/link.uri", value = workflow_action_update)
            except Exception:
                script_logger.exception(
                    "An error occurred with the update of the Workflow action")


admin.init(ConfigApp, admin.CONTEXT_NONE)
