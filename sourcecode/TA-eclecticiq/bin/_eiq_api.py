#!/usr/bin/env python
"""
Copyright 2016 EclecticIQ B.V.
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

import datetime
import json
import requests
import re

import classes.eiq_logger as eiq_logger
import classes.splunk_info as si


APPNAME = 'Eclectic_iq_api'

PATHS = {
    'FC': {
        'auth':         '/feeds/auth',
        'feeds_list':   '/feeds/downloads/',
        'feed_content_blocks': '/feeds/downloads/{0}/runs/latest',
        'groups':       '/api/groups/',
        'entities':     '/api/entities/'
    },
    '2.1': {
        'auth':         '/api/auth',
        'feeds_list':   '/private/outgoing-feed-download/',
        'feed_content_blocks': '/private/outgoing-feed-download/{0}/runs/latest',
        'groups':       '/private/groups/',
        'entities':     '/private/entities/'
    },
    '2.0': {
        'auth':         '/api/auth',
        'feeds_list':   '/api/outgoing-feed-download/',
        'feed_content_blocks': '/api/outgoing-feed-download/{0}/runs/latest',
        'groups':       '/api/groups/',
        'entities':     '/api/entities/'
    }
}

splunk_info = si.Splunk_Info("NA")
log_level = splunk_info.get_config("ta-eclecticiq.conf", 'main', 'log_level')
logger = eiq_logger.Logger()
script_logger = logger.logger_setup("eiq_api", level=log_level)


def format_ts(dt):
    return dt.replace(microsecond=0).isoformat() + 'Z'


class EclecticIQ_api(object):
    def __init__(self,
                 baseurl,
                 eiq_version,
                 username,
                 password,
                 verify_ssl=True,
                 proxy_ip=None,
                 proxy_username=None,
                 proxy_password=None):
        self.verify_ssl = verify_ssl
        self.proxy_ip = proxy_ip
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.baseurl = baseurl
        if eiq_version < '2.1':
            self.eiq_version = '2.0'
        elif eiq_version == 'FC':
            self.eiq_version = 'FC'
        else:
            self.eiq_version = '2.1'
        self.headers = {
            'user-agent': APPNAME + '/' + __version__,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.proxies = None
        if self.proxy_ip and self.proxy_username and self.proxy_password:
            self.proxies = {
                'http': 'http://' + self.proxy_username + ':' + self.proxy_password + '@' + self.proxy_ip + '/',
                'https': 'http://' + self.proxy_username + ':' + self.proxy_password + '@' + self.proxy_ip + '/',
            }
        self.get_outh_token(username, password)

    def send_api_request(self, method, path, params=None, data=None):
        if bool(re.search('^http.', path)):
            url = path
        else:
            url = self.baseurl + path

        r = None
        try:
            if method == 'post':
                r = requests.post(
                    url,
                    headers=self.headers,
                    params=params,
                    data=json.dumps(data),
                    verify=self.verify_ssl,
                    proxies=self.proxies,
                )
            elif method == 'get':
                r = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    data=json.dumps(data),
                    verify=self.verify_ssl,
                    proxies=self.proxies,
                )
            else:
                script_logger.error("Unknown method: " + str(method))
                raise Exception
        except Exception:
            script_logger.exception(
                'Could not perform request to EclecticIQ VA: {}: {}'.format(
                    method, url
                ))

        if r and r.status_code in [100, 200, 201]:
            return r
        else:

            if not r:
                msg = ('Could not perform request to EclecticIQ VA: {}: {}'
                       .format(method, url))
                script_logger.exception(msg)
                raise Exception(msg)

            try:
                err = r.json()
                detail = err['errors'][0]['detail']
                msg = ('EclecticIQ VA returned an error, '
                       'code:[{0}], reason:[{1}], URL: [{2}], details:[{3}]'
                       .format(
                           r.status_code,
                           r.reason,
                           r.url,
                           detail))
            except Exception:
                msg = ('EclecticIQ VA returned an error, '
                       'code:[{0}], reason:[{1}], URL: [{2}]').format(
                    r.status_code,
                    r.reason,
                    r.url)
            raise Exception(msg)

    def get_outh_token(self, username, password):
        script_logger.info('Authenticating using username: ' + str(username))
        try:
            r = self.send_api_request(
                'post',
                path=PATHS[self.eiq_version]['auth'],
                data={
                    'username': username,
                    'password': password
                }
            )
            self.headers['Authorization'] = 'Bearer ' + r.json()['token']
            script_logger.info('Authentication is successful')
        except Exception:
            script_logger.error("Authentication failed")
            raise

    def get_feeds_list(self):
        script_logger.info('Requesting a list of available feeds')
        r = self.send_api_request(
            'get',
            path=PATHS[self.eiq_version]['feeds_list'])
        return r.json()['data']

    def get_feed_content_blocks(self, feed_id):
        script_logger.info('Requesting a list of content-blocks for feed_id='
                           + str(feed_id))

        r = self.send_api_request(
            'get',
            path=PATHS[self.eiq_version]['feed_content_blocks'].format(
                feed_id))
        data = r.json()['data']
        content_blocks_list = data['content_blocks']
        feed_name = data['name']
        script_logger.info('Received list contains {0} blocks. Feed_name=[{1}]'
                           .format(len(content_blocks_list), feed_name))
        return content_blocks_list

    def get_feed_csv(self, cb_url):
        cb_id = cb_url.split('/')[-1]
        script_logger.debug(
            'Requesting a content-block, id=[{0}]'.format(cb_id))
        r = self.send_api_request('get', path=cb_url)
        script_logger.debug('Content-block received')
        return r.text

    def get_source_group_uid(self, group_name):
        script_logger.info(
            "Requesting source id for specified group, "
            "name=[" + str(group_name) + "]")
        r = self.send_api_request(
            'get',
            path=PATHS[self.eiq_version]['groups'],
            params='filter[name]=' + str(group_name))

        if not r.json()['data']:
            script_logger.error(
                'Something went wrong fetching the group id. '
                'Please note the source group name is case sensitive! '
                'Received response:' + str(r.json()))
            return "error_in_fetching_group_id"
        else:
            script_logger.info('Source group id received')
            script_logger.debug(
                'Source group id is: ' + str(r.json()['data'][0]['source']))
            return r.json()['data'][0]['source']

    def create_sighting(self, source, record):
        script_logger.debug("Starting create_sighting from eiq_api.")
        extract_kind = record['type_eiq']
        extract_value = record['value_eiq']
        # first_seen_ts = format_ts(datetime.datetime.fromtimestamp(float(record['event_time'])))  # in UTC !!

        today = datetime.datetime.utcnow().date()

        today_begin = format_ts(datetime.datetime(
            today.year, today.month, today.day, 0, 0, 0))
        today_end = format_ts(datetime.datetime(
            today.year, today.month, today.day, 23, 59, 59))

        ts = format_ts(datetime.datetime.utcnow())

        EIQ_VERSION = splunk_info.get_config('ta-eclecticiq.conf','main','eiq_version')

        try:
            description = record['description']
            if description == "":
                description = 'Automatically generated sighting of {0} {1}'.format(extract_kind, extract_value)
        except KeyError:
            description = 'Automatically generated sighting of {0} {1}'.format(extract_kind, extract_value)

        try:
            title = record['title']
            if title == "":
                title = "Splunk detected {0} {1}".format(extract_kind, extract_value)
        except KeyError:
            title = "Splunk detected {0} {1}".format(extract_kind, extract_value)

        try:
            confidence_value = record['confidence_value']
            if confidence_value == "":
                confidence_value = "Medium"
        except KeyError:
            confidence_value = "Medium"

        try:
            obs_confidence_value = record['observable_confidence']
            if obs_confidence_value == "":
                obs_confidence_value = "medium"
        except KeyError:
            obs_confidence_value = "medium"

        try:
            tags = record['tags']
        except KeyError:
            tags = ["Splunk Alert"]

        script_logger.info("Creating sighting for record {0}:{1}".format(extract_kind, extract_value))

        if float(EIQ_VERSION) >= 2.2:
            sighting = {"data": {
                "data": {
                    "confidence": {
                        "type": "confidence",
                        "value": confidence_value
                    },
                    "description": description,
                    "description_structuring_format": "html",
                    "type": "eclecticiq-sighting",
                    "title": title,
                    "security_control": {
                        "type": "information-source",
                        # "references": [record['splunk_link']],
                        "identity": {
                            "name": "EclecticIQ Platform App for Splunk",
                            "type": "identity"
                        },
                        "time": {
                            "type": "time",
                            "start_time": today_begin,
                            "start_time_precision": "second"
                        }
                    },
                },
                "meta": {
                    "manual_extracts": [
                        {
                            "link_type": "sighted",
                            "classification": "bad",
                            "confidence": obs_confidence_value,
                            "kind": extract_kind,
                            "value": extract_value
                        }
                    ],
                    "taxonomy": [],
                    "estimated_threat_start_time": ts,
                    "tags": tags,
                    "ingest_time": ts
                },
                "sources": [{
                    "source_id": source
                }]
            }}
        else:
            sighting = {"data": {
                "data": {
                    "confidence": {
                        "type": "confidence",
                        "value": "Low"
                    },
                    "description": description,
                    "related_extracts": [
                        {
                            "type": "eclecticiq-extract",
                            "kind": extract_kind,
                            "value": extract_value
                        }
                    ],
                    "description_structuring_format": "html",
                    "type": "eclecticiq-sighting",
                    "title": title,
                    "security_control": {
                        "type": "information-source",
                        # "references": [record['splunk_link']],
                        "identity": {
                            "name": "EclecticIQ Platform App for Splunk",
                            "type": "identity"
                        },
                        "time": {
                            "type": "time",
                            "start_time": today_begin,
                            "start_time_precision": "second" #,
                            # "end_time": today_end,
                            # "end_time_precision": "second"
                        }
                    },
                },
                "meta": {
                    "source": source,
                    "taxonomy": [],
                    "estimated_threat_start_time": ts,
                    # "estimated_observed_time": last_seen_ts,
                    "tags": ["Splunk Alert"],
                    "ingest_time": ts
                }
            }}

        self.send_api_request(
            'post',
            path=PATHS[self.eiq_version]['entities'],
            data=sighting)
