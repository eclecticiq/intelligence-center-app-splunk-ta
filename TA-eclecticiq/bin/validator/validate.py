"""Validate Configuration."""
import ta_eclecticiq_declare  # pylint: disable=W0611 # noqa: F401
import requests
import os
import json
import splunk.admin as admin
import splunk.entity as entity

from solnlib import conf_manager
from splunktaucclib.rest_handler.endpoint.validator import Validator
from validator.logger_manager import setup_logging
from constants.eiq_api import EIQ_PERMISSIONS, EIQ_USER_PERMISSIONS
from constants.general import (
    DATA,
    ID,
    MODIFY_EXTRACTS,
    NAME,
    PERMISSIONS,
    READ_ENTITIES,
    READ_EXTRACTS,
    READ_OUTGOING_FEEDS,
    READ_PERMSSIONS,
    REST_REALM,
    API_URL,
    API_KEY,
    GET,
    HTTPS,
    SELF,
    SLASH,
    STATUS_CODE_200,
    STATUS_CODE_201,
    STATUS_CODE_401,
    STATUS_CODE_403,
    STATUS_CODE_404,
)
from constants.conf import (
    PROXY_ENABLED,
    PROXY_PASSWORD,
    PROXY_TYPE_HTTP,
    SETTINGS_CONF,
    PROXY_STANZA,
    PROXY_URL,
    PROXY_USERNAME,
    PROXY_PORT,
    PROXY_CLEAR_PASSWORD,
    PROXY_TYPE_HTTPS,
    ADMIN_ENTITY,
    PASSWORD_ENTITY,
    OWNER_ENTITY,
    USERNAME_ENTITY,
    LOG_FILE_NAME,
)
from constants.messages import (
    ALL_PERMISSIONS_GRANTED_TO_USER,
    CREDENTIALS_GIVEN_ARE_CORRECT,
    ERROR_IN_USER_PERMISSIONS,
    ERROR_OCCURED_IN_PLATFORM_PERMISSIONS,
    GETTING_PLATFORM_PERMISSIONS,
    GETTING_USER_PERMISSIONS,
    JSON_EXCEPTION,
    MISSING_PERMISSIONS,
    MISSING_READ_PERMISSIONS,
    PROXY_FETCHING_ERROR_LOG_MESSAGE,
    API_KEY_REQUIRED_MSG,
    REQUEST_DOES_NOT_EXIST,
    REQUEST_UNAUTHORIZED,
    SSL_ERROR_MSG,
    ERROR_MSG,
    INVALID_CREDS_ERROR_MSG,
    INVALID_CREDS_LOG_ERROR_MSG,
    INVALID_URL_ERROR_MSG,
    SUCCESSFULLY_FETCHED_PLATFORM_PERMISSIONS,
    SUCCESSFULLY_FETCHED_USER_PERMISSIONS,
    USER_MISSING_PERMISSIONS,
    USER_UNAUTHORIZED,
    USER_UNAUTHORIZED_MSG,
)
from constants.general import (
    STR_ONE,
    STR_TILT,
    STR_EMPTY_JSON,
    STR_EMPTY,
    STR_COLON,
    STR_AT_THE_RATE,
    DOMAIN_SEPERATOR,
)


logger = setup_logging(LOG_FILE_NAME)


class GetSessionKey(admin.MConfigHandler):  # type: ignore
    """Inheriting admin.MConfigHandler to get the current user's session key."""

    def __init__(self):
        """Set the session key as parameter to use while getting entities from Splunk REST."""
        self.session_key = self.getSessionKey()


class ValidateAccount(Validator):  # type: ignore
    """Inheriting the Validator Class for creating custom validations."""

    def __init__(self, *args, **kwargs):  # pylint: disable=W0613
        """Create instance of ValidateAccount class along with Super class parameters .Setting the my_app parameter as main TA directory name."""
        super().__init__()
        self.my_app = __file__.split(os.sep)[-4]

    def get_proxy(self):
        """Fetch the information of proxy from Splunk REST Service.

        :return: dictionary having proxy information
        """
        session_key = GetSessionKey().session_key

        # Getting the entites for getting the clear password from passwords.conf
        entities = entity.getEntities(
            [ADMIN_ENTITY, PASSWORD_ENTITY],
            namespace=self.my_app,
            owner=OWNER_ENTITY,
            sessionKey=session_key,
            search=self.my_app,
        )
        proxy_data = {}
        # Getting the proxy info from rest
        proxy_file_obj = (
            conf_manager.ConfManager(
                session_key,
                self.my_app,
                realm=REST_REALM.format(app=self.my_app, conf=SETTINGS_CONF),
            )
            .get_conf(SETTINGS_CONF)
            .get(PROXY_STANZA)
        )
        try:
            # If proxy is enabled get all the info else pass
            if proxy_file_obj.get(PROXY_ENABLED) == STR_ONE:
                proxy_url = proxy_file_obj.get(PROXY_URL)
                proxy_port = proxy_file_obj.get(PROXY_PORT)
                if proxy_file_obj.get(PROXY_USERNAME) and proxy_file_obj.get(
                    PROXY_PASSWORD
                ):

                    for _, value in entities.items():
                        # Checking if stanza  in passwords.conf is matching with username
                        if value[USERNAME_ENTITY].partition(STR_TILT)[
                            0
                        ] == PROXY_STANZA and not value[
                            PROXY_CLEAR_PASSWORD
                        ].startswith(
                            STR_TILT
                        ):
                            cred = json.loads(
                                value.get(PROXY_CLEAR_PASSWORD, STR_EMPTY_JSON)
                            )
                            proxy_password = cred.get(PROXY_PASSWORD, STR_EMPTY)
                            break
                    # Creating as proxy string for setting in proxy dict
                    proxy_username = proxy_file_obj.get(PROXY_USERNAME)
                    proxy_username = requests.compat.quote_plus(proxy_username)
                    proxy_password = requests.compat.quote_plus(proxy_password)
                    proxy_https = (
                        PROXY_TYPE_HTTP
                        + DOMAIN_SEPERATOR
                        + proxy_username
                        + STR_COLON
                        + proxy_password
                        + STR_AT_THE_RATE
                        + proxy_url
                        + STR_COLON
                        + proxy_port
                    )
                else:
                    proxy_https = f"{proxy_url}{STR_COLON}{proxy_port}"
                proxy_data = {PROXY_TYPE_HTTPS: f"{proxy_https}"}
        except conf_manager.ConfManagerException:
            pass
        return proxy_data

    @staticmethod
    def get_response_content(response):
        """Get the response content from the response.

        :param response: Response to retrieve content
        :type response: Response
        :return: Response content
        :rtype: dict / None
        """
        content = {}
        try:
            content = json.loads(response.content)
        except json.decoder.JSONDecodeError as error:
            logger.info(JSON_EXCEPTION.format(error))

        return content

    @staticmethod
    def get_platform_permission_ids(permissions_data):
        """Get permission ids required for user to authenticate.

        :param feeds: permissions_data
        :type response: list
            [{"id": 1, "name": "read history-events"},{"id": 2,"name": "read discovery-rules"}...]
        :return: List of permission ids
            [33, 59, 66,78]
        :rtype: list
        """
        wanted_permissions = [
            READ_ENTITIES,
            MODIFY_EXTRACTS,
            READ_EXTRACTS,
            READ_OUTGOING_FEEDS,
        ]
        ids_required_for_user = []
        for value in permissions_data:
            if value[NAME] in wanted_permissions:
                ids_required_for_user.append(value[ID])

        return ids_required_for_user

    def get_platform_permissions(self, url, api_token, verify_ssl, proxy_settings):
        """Get all platform permissions .

        :return: List of permission data ids and name
            [{"id": 1, "name": "read history-events"},{"id": 2,"name": "read discovery-rules"}]
        :rtype: list
        """
        permissions_data = []
        logger.info(GETTING_PLATFORM_PERMISSIONS)

        url = url + EIQ_PERMISSIONS

        response = self.send_request(url, api_token, verify_ssl, proxy_settings)
        if not response:
            return permissions_data
        if response.status_code == STATUS_CODE_401:
            logger.info(REQUEST_UNAUTHORIZED)
        elif response.status_code == STATUS_CODE_403:
            logger.info(USER_MISSING_PERMISSIONS)
        elif response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            logger.error(
                ERROR_OCCURED_IN_PLATFORM_PERMISSIONS.format(
                    response.status_code, response.content
                )
            )
        else:
            logger.info(SUCCESSFULLY_FETCHED_PLATFORM_PERMISSIONS)
            content = ValidateAccount.get_response_content(response)
            permissions_data = content.get(DATA)
        return permissions_data

    @staticmethod
    def get_permssion_ids(permissions):
        """Get permission ids granted to user.

        :param feeds: permissions
            ["https://ic-playground.eclecticiq.com/api/beta/permissions/1",
            "https://ic-playground.eclecticiq.com/api/beta/permissions/2"....]

        :type response: list
        :return: List of permission ids
            [1,2,...]
        :rtype: list
        """
        permission_ids = []
        for permission in permissions:
            permission_ids.append(int(permission.split(SLASH)[-1]))
        return permission_ids

    @staticmethod
    def authenticate_user(ids_of_user, ids_required_for_user):
        """Get user authentication and missing permission ids .

        :param ids_of_user: permission ids user have
        :type ids_of_user: list
        :param ids_required_for_user: permission ids required for user to authenticate
        :type ids_required_for_user: list
        :return: is user authenticated , missing permissions ids
        :rtype: boolean,set
        """
        user_authenticated = False
        value = set(ids_required_for_user).difference(ids_of_user)

        if not value:
            logger.info(ALL_PERMISSIONS_GRANTED_TO_USER.format(value))
            user_authenticated = True
        return user_authenticated, value

    @staticmethod
    def get_permission_name_from_id(permission_data, permission_ids):
        """Get permission name from permission ids.

        :return: permission names
        :rtype: list of str
        """
        permissions_name = []
        for data in permission_data:
            for permission_id in permission_ids:
                if data[ID] == permission_id:
                    permissions_name.append(data[NAME])
        return permissions_name

    def get_user_granted_permissions(self, url, api_token, verify_ssl, proxy_settings):
        """Get all permissions granted to user.

        :return: List of permissions
        :rtype: list
        """
        permissions = []
        logger.info(GETTING_USER_PERMISSIONS)
        # configs_user_permissions = configs
        # configs_user_permissions[TIMEOUT]= DEFAULT_TIMEOUT_USER_PERMISSIONS
        # configs_user_permissions[RETRY_INTERVAL] = DEFAULT_MAX_RETRY_USER_PERMISSIONS
        # request = self.auth_config.get_eiq_request(configs=configs_user_permissions)
        url = url + EIQ_USER_PERMISSIONS + SLASH + SELF

        response = self.send_request(url, api_token, verify_ssl, proxy_settings)

        if not response:
            return permissions, 404

        logger.info(response.status_code)
        if response.status_code == STATUS_CODE_401:
            logger.info(REQUEST_UNAUTHORIZED)
        elif response.status_code == STATUS_CODE_403:
            logger.info(MISSING_PERMISSIONS)
        elif response.status_code == STATUS_CODE_404:
            logger.info(REQUEST_DOES_NOT_EXIST)
        elif response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            logger.info(
                ERROR_IN_USER_PERMISSIONS.format(response.status_code, response.content)
            )
        else:
            logger.info(SUCCESSFULLY_FETCHED_USER_PERMISSIONS)
            content = ValidateAccount.get_response_content(response)
            if content:
                permissions = content.get(DATA).get(PERMISSIONS)
            else:
                response.status_code = STATUS_CODE_401

        return permissions, response.status_code

    def validate_user_permissions(self, url, api_token, verify_ssl, proxy_settings):
        """Get permission ids granted to user.

        :return: missing_permissions
        :rtype: set
        """
        permissions_of_user, status_code = self.get_user_granted_permissions(
            url, api_token, verify_ssl, proxy_settings
        )
        missing_permissions = []
        if status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            logger.error(USER_UNAUTHORIZED)
        elif not permissions_of_user and status_code in [
            STATUS_CODE_200,
            STATUS_CODE_201,
        ]:
            logger.error(MISSING_READ_PERMISSIONS)
            missing_permissions = READ_PERMSSIONS
        else:
            ids_of_user = ValidateAccount.get_permssion_ids(
                permissions_of_user
            )  # permission ids possesed by user
            permissions_data = self.get_platform_permissions(
                url, api_token, verify_ssl, proxy_settings
            )
            if permissions_data:
                ids_required_for_user = ValidateAccount.get_platform_permission_ids(
                    permissions_data
                )
                user_authenticated, permission_ids = ValidateAccount.authenticate_user(
                    ids_of_user, ids_required_for_user
                )

                if not user_authenticated:
                    # check for missing permissions
                    permissions_data = self.get_platform_permissions(
                        url, api_token, verify_ssl, proxy_settings
                    )
                    missing_permissions = ValidateAccount.get_permission_name_from_id(
                        permissions_data, permission_ids
                    )
            else:
                missing_permissions = READ_PERMSSIONS
                status_code = STATUS_CODE_401
        return missing_permissions, status_code

    def send_request(self, url, api_token, verify_ssl, proxy_settings):
        """Send an API request to the URL provided with api token and proxy .sets the error message in UI and Log.

        :param url: API URL to send request
        :type url: str
        :param api_token: API token for authentication
        :type params: str
        :param proxy_settings: proxy details to be included in the request
        :type proxy: dict
        :return: response if True else {}
        :rtype: Response else dict
        """
        try:

            headers = {"Authorization": f"Bearer {api_token}"}
            response = requests.request(
                GET,
                url,
                headers=headers,
                verify=verify_ssl,
                proxies=proxy_settings,
                timeout=40,
            )

            response.raise_for_status()
            return response
        except requests.exceptions.SSLError as error:
            logger.error(SSL_ERROR_MSG.format(error_msg_prefix=ERROR_MSG))
            self.put_msg(error)
            return {}
        except Exception as error:
            logger.error(INVALID_CREDS_LOG_ERROR_MSG.format(msg=ERROR_MSG, err=error))
            self.put_msg(INVALID_CREDS_ERROR_MSG.format(error_msg_prefix=ERROR_MSG))
            return {}

    def validate(self, value, data):  # pylint: disable=W0613
        """
        Check if the url and api token provided by user is valid or not.

        :param value: value given in the Name field of configuration page/account.
        (Not required but only keeping as this method will be called with it by rest module.)
        :type value: str
        :param data: all the inputs provided by user in configuration page/account tab while saving.
        :type proxy: dict
        :return True or False
        """
        # Get proxy settings information
        try:
            proxy_settings = self.get_proxy()
        except Exception as exception:
            logger.exception(PROXY_FETCHING_ERROR_LOG_MESSAGE.format(msg=exception))
            self.put_msg(PROXY_FETCHING_ERROR_LOG_MESSAGE.format(msg=exception))
            return False

        verify_ssl = False
        # Set parameters
        url = data[API_URL]
        logger.info(data)

        if not url.startswith(HTTPS):
            self.put_msg(INVALID_URL_ERROR_MSG)
            return False
        api_token = data.get(API_KEY)

        if data.get("certificate_validation") == "1":
            verify_ssl = True

        # Check if API token is there
        if not api_token:
            logger.error(API_KEY_REQUIRED_MSG)
            self.put_msg(API_KEY_REQUIRED_MSG)
            return False

        missing_permissions, eiq_api_status_code = self.validate_user_permissions(
            url, api_token, verify_ssl, proxy_settings
        )

        if eiq_api_status_code not in [200, 201]:
            self.put_msg(USER_UNAUTHORIZED_MSG)
            logger.info(USER_UNAUTHORIZED)
        elif not missing_permissions and eiq_api_status_code in [200, 201]:
            logger.info(CREDENTIALS_GIVEN_ARE_CORRECT)
            return True
        else:
            logger.info(MISSING_PERMISSIONS.format(missing_permissions))
        return False
