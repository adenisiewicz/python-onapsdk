#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""AAI Element module."""
import logging

from onapsdk.onap_service import OnapService
from onapsdk.utils.headers_creator import headers_aai_creator

class AaiElement(OnapService):
    """Mother Class of all A&AI elements."""

    __logger: logging.Logger = logging.getLogger(__name__)

    server: str = "AAI"
    base_url = "https://aai.api.sparky.simpledemo.onap.org:30233"
    api_version = "/aai/v13"

    def __init__(self, name: str = None):
        """
        Initialize AaiElement object.

        Args:
            name (optional): the name of the AaiElement
        """
        super().__init__()
        self.name: str = name or "AAI"
        self.headers = headers_aai_creator(OnapService.headers)

    @classmethod
    def customers(cls):
        """Get the list of subscription types in A&AI."""
        url = cls.base_url + cls.api_version + "/business/customers"
        return cls.send_message_json('GET', 'get customers', url)

    @classmethod
    def subscription_types(cls):
        """Get the list of subscription types in A&AI."""
        url = (cls.base_url + cls.api_version +
               "/service-design-and-creation/services")
        return cls.send_message_json('GET', 'get subscriptions', url)

    @classmethod
    def cloud_regions(cls):
        """Get the list of subscription types in AAI."""
        url = (cls.base_url + cls.api_version +
               "/cloud-infrastructure/cloud-regions")
        return cls.send_message_json('GET', 'get cloud regions', url)
