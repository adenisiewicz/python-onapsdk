#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Vendor module."""
from typing import List

import logging

from onapsdk.sdc_element import SdcElement
import onapsdk.constants as const

class Vendor(SdcElement):
    """
    ONAP Vendor Object used for SDC operations.

    Attributes:
        name (str): the name of the vendor. Defaults to "Generic-Vendor".
        identifier (str): the unique ID of the vendor from SDC.
        status (str): the status of the vendor from SDC.
        version (str): the version ID of the vendor from SDC.
        created (bool): allows to know if the vendor is already created in SDC.

    """

    __logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self, name: str = None):
        """
        Initialize vendor object.

        Args:
            name (optional): the name of the vendor
        """
        super().__init__()
        self.identifier: str = None
        self.version: str = None
        self.status: str = None
        self.created: bool = False
        self.name: str = name or "Generic-Vendor"
        self.header["USER_ID"] = "cs0008"
        self.base_url = "{}/sdc1/feProxy/onboarding-api/v1.0".format(
            self.base_front_url)

    def get_all(self) -> List['Vendor']:
        """
        Get the vendors list created in SDC.

        Returns:
            the list of the vendors

        """
        self.__logger.debug("retrieving all vendors from SDC")
        url = "{}/vendor-license-models".format(self.base_url)
        vendor_lists = self.send_message_json('GET', 'get vendors', url)
        vendors = []
        if vendor_lists:
            for vendor_info in vendor_lists['results']:
                vendor = Vendor(vendor_info['name'])
                vendor.identifier = vendor_info['id']
                vendor.created = True
                vendors.append(vendor)
        self.__logger.debug("number of vendors returned: %s", len(vendors))
        return vendors

    def exists(self) -> bool:
        """
        Check if vendor already exists in SDC and update infos.

        Returns:
            True if exists, False either

        """
        self.__logger.debug("check if vendor %s exists in SDC", self.name)
        vendors = self.get_all()
        for vendor in vendors:
            self.__logger.debug("checking if %s is the same", vendor.name)
            if vendor == self:
                self.__logger.info("Vendor found, updating information")
                self.identifier = vendor.identifier
                self.created = True
                url = "{}/items/{}/versions".format(self.base_url,
                                                    self.identifier)
                vendor_details = self.send_message_json('GET', 'get vendors',
                                                        url)
                if vendor_details:
                    self.__logger.debug("details found, updating")
                    self.status = vendor_details['results'][-1]['status']
                    self.version = vendor_details['results'][-1]['id']
                return True
        self.__logger.info("vendor %s doesn't exists in SDC", self.name)
        return False

    def create(self) -> None:
        """Create the vendor in SDC if not already existing."""
        if not self.exists():
            url = "{}/vendor-license-models".format(self.base_url)
            template = self.__jinja_env.get_template('vendor_create.json.j2')
            data = template.render(name=self.name)
            create_result = self.send_message_json('POST', 'create vendor',
                                                   url, data=data)
            if create_result:
                self.created = True
                self.status = create_result['version']['status']
                self.identifier = create_result['itemId']
                self.version = create_result['version']['id']

    def submit(self) -> None:
        """Submit the SDC vendor in order to have it."""
        if self.status != const.CERTIFIED:
            url = "{}/vendor-license-models/{}/versions/{}/actions".format(
                self.base_url, self.identifier, self.version)
            template = self.__jinja_env.get_template('vendor_submit.json')
            data = template.render()
            submitted = self.send_message('PUT', 'submit vendor', url,
                                          data=data)
            if submitted:
                self.status = const.CERTIFIED

    def __eq__(self, other: 'Vendor') -> bool:
        """
        Check equality for Vendor.

        Args:
            other: another object

        Returns:
            bool: True if same object, False if not

        """
        if isinstance(other, Vendor):
            return self.name == other.name
        return False
