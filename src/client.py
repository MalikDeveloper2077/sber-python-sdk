import logging
from typing import Union

import requests


class SberBase:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def auth_get_request(self, url: str, headers=None, params=None):
        params, headers = self._prepare_auth_request(params, headers)
        return requests.get(url, headers=headers, params=params)

    def auth_post_request(self, url: str, headers=None, data=None):
        data, headers = self._prepare_auth_request(data, headers)
        return requests.post(url, headers=headers, data=data)

    def _prepare_auth_request(self, data, headers):
        """Form request data and headers

        Returns:
            data (dict): the data with params for authentication
            headers (dict): the headers

        """
        data = self._add_auth_params(get_data_or_dict(data))
        headers = get_data_or_dict(headers)
        return data, headers

    def _add_auth_params(self, data: dict):
        data['userName'] = self.username
        data['password'] = self.password
        return data


class SberController:
    """Utils for working with SBER"""
    logger = None

    def __init__(self, log_path: str, logging_format=None):
        """log_path (str): path to a log file"""
        if log_path:
            if not logging_format:
                logging_format = "%(levelname)s:%(name)s:%(asctime)-15s: %(message)s"
            self.init_logger(log_path, logging_format)

    def init_logger(self, log_path: str, logging_format: str):
        self.logger = logging.getLogger('client.py logger')
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(logging_format)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    @property
    def has_logger(self):
        return bool(self.logger)

    def log_sber_response(self, response_data: dict, log_message: str):
        """
        Error code: '0' - success response
        Else: there's an error
        """
        error_code = response_data.get('errorCode', '0')

        try:
            if error_code == '0':
                self.logger.info(f'{log_message}')
            else:
                self.logger.error(f'{log_message} | ERROR: {response_data.get("errorMessage")}')
        except AttributeError:
            raise AttributeError('You have not initialized a logger')


class SberClient(SberBase):
    """Abstraction for SBER classes"""
    controller = None
    endpoints = {
        'register': 'https://3dsec.sberbank.ru/payment/rest/register.do'
    }

    def __init__(self, order_number: str, log_path=None):
        """
        order_number (str): order number in the store system
        log_path (str): path to a log file. If hasn't determined, there will be no logs
        """
        super().__init__()
        self.order_number = order_number
        self.controller = SberController(log_path)

    def execute(self, *args, **kwargs):
        """Abstract method to do a class main function"""
        raise NotImplementedError


class SberRegistrar(SberClient):
    """Register a SBER order for paying"""
    def __init__(self, order_number, log_path=None):
        super().__init__(order_number, log_path)

    def execute(self, amount: Union[int, float], return_url: str, fail_url: str) -> dict:
        data = {
            'orderNumber': self.order_number,
            'amount': int(amount * 100),
            'returnUrl': return_url,
            'failUrl': fail_url,
            'language': 'ru'
        }
        response = self.auth_post_request(self.endpoints['register'], data=data).json()

        if self.controller.has_logger:
            log_message = f'Регистрация заказа #{self.order_number} на сумму {amount}'
            self.controller.log_sber_response(response, log_message)

        return response
