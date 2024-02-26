#!/usr/bin/env python

"""
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
import logging

if sys.version_info >= (3, 0):
    import configparser as ConfigParser
else:
    import ConfigParser

import splunklib.client as client
import splunk.entity as entity

class Splunk_Info(object):
    def __init__(self, sessionKey=None, app="-", logger=None):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.splunk_paths = self.give_splunk_paths(self.script_dir)



        custom_conf_file = (
            str(app.lower()) + ".conf" if app is not "-"
            else str(self.splunk_paths['app_name'].lower()) + ".conf")

        # Set the log level based on the value in the config file
        # 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL
        log_level = self.get_config(custom_conf_file, 'main', 'log_level')

        given_sessionKey = sessionKey

        if logger is not None:
            self.logger = logger
        else:
            log_format = logging.Formatter(
                '%(asctime)s loglevel=%(levelname)s file=%(filename)s '
                'line=%(lineno)d function=%(funcName)s message="%(message)s"')

            log_file = os.path.normpath(
                self.splunk_paths['app_root_dir'] +
                os.sep + 'logs' + os.sep + 'splunk_info.log')

            handler = logging.handlers.RotatingFileHandler(
                filename=log_file,
                maxBytes=10485760,
                backupCount=5)
            handler.setFormatter(log_format)

            logger = logging.getLogger("splunk_info")
            logger.propagate = False
            logger.setLevel(log_level)
            logger.addHandler(handler)

            self.logger = logger

        if not given_sessionKey:
            # Get the session_key for the system user for this to work
            # you need to set
            # pass_auth = splunk-system-user
            # in the inputs [script://...] stanza
            sessionKey = sys.stdin.readline().strip()
            logger.debug("Reading sessionKey from stdin")

            if not sessionKey:
                self.logger.critical(
                    "Did not receive a session key from splunkd. "
                    "Please enable passAuth in inputs.conf for this script.")
            else:
                self.logger.debug("sessionKey was received")
                self.connection = client.connect(token=sessionKey, app=app)
        elif given_sessionKey == "NA":
            sessionKey = None
        else:
            sessionKey = given_sessionKey
            logger.debug(
                "sessionKey is passed in with the class call")
            self.connection = client.connect(token=sessionKey, app=app)

        self.app = "-" if not app else app
        self.sessionKey = sessionKey

    def shcluster_status(self):
        if len(self.sessionKey) == 0:
            self.logger.critical(
                "Did not receive a session key from splunkd. "
                "Please enable passAuth in inputs.conf for this script.")
            shc_status = "unknown"
        else:
            self.logger.debug("sessionKey was received")

            # Get the Splunk info, this is mainly the info that is stored in
            # the server.conf
            # info() will return a json with (among other things)
            # the roles this Splunk installation has:
            # 'server_roles': ['indexer','license_master',
            # 'kv_store','shc_captain']
            splunk_info = self.connection.info()
            server_roles = splunk_info['server_roles']

            if 'shc_member' in server_roles:
                self.logger.debug("The script is part of a Searchhead cluster,"
                                  " this system is MEMBER")
                shc_status = "shc_member"
            elif 'shc_captain' in server_roles:
                self.logger.debug("The script is part of a Searchhead cluster,"
                                  " this system is CAPTAIN")
                shc_status = "shc_captain"
            elif 'shc_deployer' in server_roles:
                self.logger.debug("The script is part of a Searchhead cluster,"
                                  " this system is DEPLOYER")
                shc_status = "shc_deployer"
            else:
                self.logger.debug(
                    "The script is not part of a Searchhead cluster, "
                    "or no cluster roles could be determined, current roles: "
                    + str(server_roles))
                shc_status = "shc_none"

        return shc_status

    def give_splunk_paths(self, script_location):
        splunk_home_dir = os.environ['SPLUNK_HOME']
        splunk_apps_dir = os.path.normpath(
            splunk_home_dir + os.sep + "etc" + os.sep + "apps")
        app_name = script_location.replace(
            splunk_apps_dir + os.sep, "").split(os.sep, 1)[0]
        app_root_dir = os.path.normpath(splunk_apps_dir + os.sep + app_name)

        current_dir = script_location
        return {
            'splunk_home_dir': splunk_home_dir,
            'splunk_apps_dir': splunk_apps_dir,
            'app_name': app_name,
            'app_root_dir': app_root_dir,
            'current_dir': current_dir
        }

    def get_config(self, conf_file, stanza=None, option=None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        splunk_paths = self.give_splunk_paths(script_dir)
        app_dir = splunk_paths['app_root_dir']

        if not conf_file.endswith(".conf") and not conf_file.endswith(".meta"):
            conf_file += ".conf"

        if not conf_file.endswith(".meta"):
            default_file = os.path.normpath(
                app_dir + os.sep + "default" + os.sep + conf_file)
            local_file = os.path.normpath(
                app_dir + os.sep + "local" + os.sep + conf_file)
        else:
            default_file = os.path.normpath(
                app_dir + os.sep + "metadata" + os.sep + "default.meta")
            local_file = os.path.normpath(
                app_dir + os.sep + "metadata" + os.sep + "local.meta")

        config = ConfigParser.RawConfigParser()

        # check if the requested config file is in the default dir,
        # if so read the content, else create a empty list to prevent errors
        if os.path.exists(default_file):
            config.read(default_file)
            default_config = (config._sections if not stanza
                              else config._sections[stanza])
        else:
            default_config = []

        # check if the requested config file is in the local dir,
        # if so read the content, else create a empty list to prevent errors
        if os.path.exists(local_file):
            config.read(local_file)
            local_config = (config._sections if not stanza
                            else config._sections[stanza])
        else:
            local_config = []

        # option IS required!
        if option is None:
            return None

        # search for the requested option, first in the local config
        # if it is not found there check the default config.
        if option in local_config:
            active_config = local_config[option]
        elif option in default_config:
            active_config = default_config[option]
        else:
            active_config = None

        # If the log_level is requested
        # make sure to give a value back that can be used
        if option == "log_level":
            # handle unset value by returning default
            if not active_config:
                return 20
            if 0 < int(active_config) < 20:
                active_config = 10
            elif 20 <= int(active_config) < 30:
                active_config = 20
            elif 30 <= int(active_config) < 40:
                active_config = 30
            elif 40 <= int(active_config) < 50:
                active_config = 40
            elif int(active_config) >= 50:
                active_config = 50
            else:
                active_config = 20

        return active_config

    def get_credetials(self, username=None, app="-"):
        if app in [None, '', '-']:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            splunk_paths = self.give_splunk_paths(script_dir)
            app = splunk_paths['app_name']

        try:
            # list all credentials available
            entities = entity.getEntities(
                ['admin', 'passwords'],
                namespace=app,
                owner='nobody',
                sessionKey=self.sessionKey,
                count='-1'
            )
            self.logger.info("entities: " + str(len(entities)))
        except Exception:
            self.logger.exception(
                "Could not get " + str(app) + " credentials from splunk.")
            return "NO_PASSWORD_FOUND_FOR_THIS_USER"

        # return password when the correct info is found
        for i, c in entities.items():
            if c['username'] == username:
                return c['clear_password']

        return "NO_PASSWORD_FOUND_FOR_THIS_USER"

    def write_credentials(self, username, password, app="-"):
        # Rename the username and password
        # to make it clear what is what later on..
        write_username = username
        write_password = password

        try:
            # If the credential already exists, delete it.
            for storage_password in self.service.storage_passwords:
                if storage_password.username == write_username:
                    self.service.storage_passwords.delete(
                        username=storage_password.username)
                    self.logger.info(
                        "The given credentials already exist, "
                        "assuming new password so first "
                        "delete them en then write them again")
                    break

            # Create the credentials
            self.service.storage_passwords.create(
                write_password,
                write_username)

        except Exception:
            self.logger.exception(
                "An error occurred updating credentials. "
                "Please ensure your user account has admin_all_objects "
                "and/or list_storage_passwords capabilities.")

    def create_kv_if_needed(self, collection_name, collection_fields, kwargs):
        service = client.connect(
            token=self.sessionKey,
            owner="nobody",
            app=self.app)

        export_fields_list_kv = []
        export_fields_list_kv.extend(collection_fields.iterkeys())

        if collection_name in service.kvstore:
            return export_fields_list_kv

        # The collection doesn't exist so create it now,
        # and also create the collections.conf file with the correct fields
        self.logger.debug("The KV Store " + str(collection_name) +
                          " doesn't exist so create it")

        # Create and select the KVstore collection
        service.kvstore.create(
            name=collection_name,
            fields=collection_fields,
            **kwargs
        )

        # The kvstore.create command only creates the kvstore but doesn't
        # mean you can use it in a search.
        # To be able to use it a search we need to add a stanza with the
        # definition for the collection in transforms.conf.
        fields_list = ','.join(map(str, export_fields_list_kv))
        self.write_config(
            "transforms.conf",
            collection_name,
            "external_type",
            "kvstore")
        self.write_config(
            "transforms.conf",
            collection_name,
            "collection",
            collection_name)
        self.write_config(
            "transforms.conf",
            collection_name,
            "fields_list",
            fields_list)

        return export_fields_list_kv

    def write_config(self, conf_file, stanza, key, value=""):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        splunk_paths = self.give_splunk_paths(script_dir)
        app_dir = splunk_paths['app_root_dir']

        if not conf_file.endswith(".conf") and not conf_file.endswith(".meta"):
            conf_file += ".conf"

        if not conf_file.endswith(".meta"):
            local_file = os.path.normpath(
                app_dir + os.sep + "local" + os.sep + conf_file)
        else:
            local_file = os.path.normpath(
                app_dir + os.sep + "metadata" + os.sep + "local.meta")

        config = ConfigParser.RawConfigParser()

        if os.path.exists(local_file):
            config.read(local_file)
            if not config.has_section(stanza):
                config.add_section(stanza)
        else:
            config.add_section(stanza)

        config.set(stanza, key, value)

        if not os.path.exists(os.path.dirname(local_file)):
            os.makedirs(os.path.dirname(local_file))

        with open(local_file, 'wb') as configfile:
            config.write(configfile)
