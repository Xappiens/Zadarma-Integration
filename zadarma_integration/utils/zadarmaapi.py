import hashlib
import hmac
import base64
import requests
from hashlib import sha1, md5
from collections import OrderedDict
from urllib.parse import urlencode

class ZadarmaAPI:
    def __init__(self, public_key, private_key, sandbox_mode=False):
        """
        Initializes the Zadarma API Wrapper
        :param public_key: API public key from user settings
        :param private_key: API private key from user settings
        :param sandbox_mode: Boolean to enable or disable sandbox environment
        """
        self.public_key = public_key
        self.private_key = private_key
        self.api_url = 'https://api-sandbox.zadarma.com' if sandbox_mode else 'https://api.zadarma.com'

    def call(self, api_path, parameters=None, http_method='GET', response_type='json', use_auth=True):
        """
        Sends an API request to Zadarma
        :param api_path: The endpoint of the API, including version info
        :param parameters: Parameters for the request
        :param http_method: The HTTP method to use (GET, POST, PUT, DELETE)
        :param response_type: Expected response format ('json' or 'xml')
        :param use_auth: Whether the request requires authentication
        :return: Response from the API
        """
        if parameters is None:
            parameters = {}

        parameters['format'] = response_type
        http_method = http_method.upper()
        if http_method not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise ValueError("Unsupported HTTP method. Choose from 'GET', 'POST', 'PUT', 'DELETE'.")

        encoded_params = self._encode_parameters(parameters)
        auth_header = self._create_auth_header(api_path, encoded_params) if use_auth else None

        headers = {'Authorization': auth_header} if auth_header else {}
        request_url = f"{self.api_url}{api_path}"

        return self._execute_http_request(http_method, request_url, headers, encoded_params)

    def _encode_parameters(self, parameters):
        """
        Encodes parameters for the API request
        :param parameters: Dictionary of parameters
        :return: URL-encoded parameter string
        """
        if any(not isinstance(value, str) for value in parameters.values()):
            return self._encode_nested_parameters(OrderedDict(sorted(parameters.items())))
        return urlencode(OrderedDict(sorted(parameters.items())))

    def _execute_http_request(self, method, url, headers, params):
        """
        Executes an HTTP request
        :param method: HTTP method to use
        :param url: The full request URL
        :param headers: HTTP headers
        :param params: Parameters for the request (GET or request body)
        :return: Response content
        """
        if method == 'GET':
            response = requests.get(f"{url}?{params}", headers=headers)
        else:
            response = requests.request(method, url, headers=headers, data=params)
        return response.text

    def _encode_nested_parameters(self, data):
        """
        Creates a URL-encoded string for nested parameters
        :param data: Dictionary representing the nested data
        :return: URL-encoded string
        """
        parameter_pairs = {}

        def recursive_encoder(item, key_prefix=None):
            if key_prefix is None:
                key_prefix = []

            if isinstance(item, (list, tuple)):
                for idx, element in enumerate(item):
                    key_prefix.append(idx)
                    recursive_encoder(element, key_prefix)
                    key_prefix.pop()
            elif isinstance(item, dict):
                for key, value in item.items():
                    key_prefix.append(key)
                    recursive_encoder(value, key_prefix)
                    key_prefix.pop()
            else:
                key = ''.join(f"[{str(k)}]" if i > 0 else str(k) for i, k in enumerate(key_prefix))
                parameter_pairs[key] = str(item)

        recursive_encoder(data)
        return urlencode(parameter_pairs)

    def _create_auth_header(self, api_path, parameters_string):
        """
        Creates the authentication header for the API request
        :param api_path: API endpoint
        :param parameters_string: URL-encoded parameter string
        :return: Authentication header
        """
        signature_data = api_path + parameters_string + md5(parameters_string.encode('utf-8')).hexdigest()
        hmac_signature = hmac.new(self.private_key.encode('utf-8'), signature_data.encode('utf-8'), sha1).hexdigest()
        auth_header = f"{self.public_key}:{base64.b64encode(hmac_signature.encode('utf-8')).decode()}"
        return auth_header
