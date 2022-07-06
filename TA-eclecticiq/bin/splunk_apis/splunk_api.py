"""Splunk APIs for KV store."""

import json

import splunklib.client as client
from constants.general import _KEY, APP_NAME, NOBODY, SESSION_KEY
from splunklib.binding import HTTPError


class SplunkApi:
    """Splunk APIs for KV Store."""

    def __init__(self, helper, event_writer):
        self.helper = helper
        self.event_writer = event_writer

    def insert_record_in_collection(self, data, collection_name):
        """Insert record in  splunk kv store.

        :param data: data to insert in collection
        :type data: dict
        :param collection_name: collection name to insert the data
        :type collection_name: str

        :return: response
        :rtype: boolean
        """
        insertion = True
        session_key = self.helper.context_meta[SESSION_KEY]

        service = client.connect(token=session_key, owner=NOBODY, app=APP_NAME)

        collection = service.kvstore[collection_name]
        try:
            response = collection.data.insert(json.dumps(data))
            self.helper.log_info(response)
        except HTTPError as error:
            self.helper.log_info(error)
            insertion = False
        return insertion

    def update_record_in_collection(self, data, collection_name, key):
        """Update record in  splunk kv store.

        :param data: data to insert in collection
        :type data: dict
        :param collection_name: collection name to insert the data
        :type collection_name: str
        :param key: key id to update the record
        :type key: str

        :return: updation response
        :rtype: boolean
        """
        updation = True
        session_key = self.helper.context_meta[SESSION_KEY]

        service = client.connect(token=session_key, owner=NOBODY, app=APP_NAME)

        collection = service.kvstore[collection_name]
        try:
            response = collection.data.update(key, json.dumps(data))
            self.helper.log_info(response)
        except HTTPError as error:
            self.helper.log_info(error)
            updation = False

        return updation

    def get_record_in_collection(self, collection_name, key):
        """Get a record from splunk kv store.

        :param collection_name: collection name to get the data
        :type collection_name: str
        :param key: key id to update the record
        :type key: str

        :return: response
        :rtype: boolean
        """
        response = []
        session_key = self.helper.context_meta[SESSION_KEY]

        service = client.connect(token=session_key, owner=NOBODY, app=APP_NAME)

        collection = service.kvstore[collection_name]
        try:
            query = json.dumps({_KEY: str(key)})
            response = collection.data.query(query=query)

        except HTTPError as error:
            self.helper.log_info(error)

        return response

    def get_all_records_in_collection(self, collection_name):
        """Get all record from splunk kv store.

        :param collection_name: collection name to get the data
        :type collection_name: str

        :return: response
        :rtype: boolean
        """
        response = []
        session_key = self.helper.context_meta[SESSION_KEY]

        service = client.connect(token=session_key, owner=NOBODY, app=APP_NAME)

        collection = service.kvstore[collection_name]
        try:

            response = collection.data.query()
        except HTTPError as error:
            self.helper.log_info(error)

        return response

    def delete_record_from_collection(self, collection_name, key):
        """Delete record from splunk kv store.

        :param collection_name: collection name to get the data
        :type collection_name: str
        :param key: key id to update the record
        :type key: str

        :return: response
        :rtype: boolean
        """
        deletion = True
        session_key = self.helper.context_meta[SESSION_KEY]

        service = client.connect(token=session_key, owner=NOBODY, app=APP_NAME)

        collection = service.kvstore[collection_name]
        try:
            query = json.dumps({_KEY: str(key)})
            collection.data.delete(query)

        except HTTPError as error:
            self.helper.log_info(error)
            deletion = False

        return deletion
