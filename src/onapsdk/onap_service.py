#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""ONAP Service module."""
from typing import Dict
from typing import Union
from typing import Any

import logging
import requests
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.util.retry import Retry
import simplejson.errors
from jinja2 import Environment, PackageLoader

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OnapService():
    """
    Mother Class of all ONAP sercices.

    Attributes:
        server (str): nickname of the server we send the request.
                      used in logs strings.
        header (Dict[str, str]): the header dictionnary to use
        proxy (Dict[str, str]): the proxy configuration if needed

    """

    __logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        """Initialize the service."""
        self.server: str = None
        self.header: Dict[str, str] = None
        self.proxy: Dict[str, str] = None
        self._jinja_env = Environment(loader=PackageLoader('onapsdk'))

    def send_message(self, method: str, action: str, url: str,
                     **kwargs) -> Union[requests.Request, None]:
        """
        Send a message to an ONAP service.

        Args:
            method (str): which method to use (GET, POST, PUT, PATCH, ...)
            action (str): what action are we doing, used in logs strings.
            url (str): the url to use
            exception (Exception, optional): if an error occurs, raise the
                exception given
            **kwargs: Arbitrary keyword arguments. any arguments used by request
                can be used here.

        Raises:
            exception (Exception): raise the Exception given in args (if given)

        Returns:
            the request response if OK or None if an error occured

        """
        exception = kwargs.pop('exception', None)
        data = kwargs.get('data', None)
        try:
            # build the request with the requested method
            session = self.__requests_retry_session()
            response = session.request(method, url, headers=self.header,
                                       verify=False, proxies=self.proxy,
                                       **kwargs)

            response.raise_for_status()
            self.__logger.info("[%s][%s] response code: %s", self.server,
                               action, response.status_code)
            self.__logger.debug("[%s][%s] sent header: %s",
                                self.server, action, self.header)
            self.__logger.debug("[%s][%s] url used: %s", self.server, action,
                                url)
            self.__logger.debug("[%s][%s] data sent: %s", self.server, action,
                                data)
            self.__logger.debug("[%s][%s] response: %s", self.server, action,
                                response.text)
            return response
        except requests.HTTPError:
            self.__logger.error(
                "[%s][%s] response code: %s", self.server, action,
                response.status_code)
            self.__logger.error("[%s][%s] sent header: %s", self.server, action,
                                self.header)
            self.__logger.error("[%s][%s] url used: %s", self.server, action,
                                url)
            self.__logger.error("[%s][%s] data sent: %s", self.server, action,
                                data)
            self.__logger.error("[%s][%s] response: %s", self.server, action,
                                response.text)
            if exception:
                raise exception
        except requests.RequestException as err:
            self.__logger.error("[%s][%s] Failed to perform: %s", self.server,
                                action, err)
            self.__logger.error("[%s][%s] sent header: %s", self.server, action,
                                self.header)
            self.__logger.error("[%s][%s] url used: %s", self.server, action,
                                url)
            self.__logger.error("[%s][%s] data sent: %s", self.server, action,
                                data)
            if exception:
                raise exception
        return None

    def send_message_json(self, method: str, action: str, url: str,
                          **kwargs) -> Union[Dict[Any, Any], None]:
        """
        Send a message to an ONAP service and parse the response as JSON.

        Args:
            method (str): which method to use (GET, POST, PUT, PATCH, ...)
            action (str): what action are we doing, used in logs strings.
            url (str): the url to use
            exception (Exception, optional): if an error occurs, raise the
                exception given
            **kwargs: Arbitrary keyword arguments. any arguments used by request
                can be used here.

        Raises:
            exception (Exception): raise the Exception given in args (if given)

        Returns:
            the response body in dict format if OK or {}

        """
        exception = kwargs.get('exception', None)
        data = kwargs.get('data', None)
        try:
            response = self.send_message(method, action, url, **kwargs)
            if response:
                return response.json()
        except simplejson.errors.JSONDecodeError as err:
            self.__logger.error("[%s][%s]Failed to decode JSON: %s",
                                self.server, action, err)
            self.__logger.error("[%s][%s] sent header: %s", self.server, action,
                                self.header)
            self.__logger.error("[%s][%s] url used: %s", self.server, action,
                                url)
            self.__logger.error("[%s][%s] data sent: %s", self.server, action,
                                data)
            if exception:
                raise exception
        return {}

    @staticmethod
    def __requests_retry_session(
            retries: int = 10,
            backoff_factor: float = 0.3,
            session: requests.Session = None) -> requests.Session:
        """
        Create a request Session with retries.

        Args:
            retries (int, optional): number of retries. Defaults to 10.
            backoff_factor (float, optional): backoff_factor. Defaults to 0.3.
            session (requests.Session, optional): an existing session to
                enhance. Defaults to None.

        Returns:
            requests.Session: the session with retries set

        """
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
