#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Service Instance module."""

import logging

from dataclasses import dataclass

from onapsdk.so_element import SoElement
from onapsdk.utils.headers_creator import headers_so_creator

from onapsdk.utils.tosca_file_handler import random_string_generator

@dataclass
class ServiceInstance(SoElement):
    """
    ONAP ServiceInstance Object used for SO operations.

    Attributes:
    """
    logger: logging.Logger = logging.getLogger(__name__)
    rand_extension: str = ""
    headers: dict = None
    name: str

    def __post_init__(self):
        self.headers = headers_so_creator(SoElement.headers)
        self.name = self.name + "-" + random_string_generator(6)


    def create(self) -> None:
        """Create the Service Instance in SO if models already existing."""
        if self.models['service_instance'] is not None:
            self._create("service_instance_create.json.j2",
                         instance_name=self.name,
                         cloud=self.)

        # url = SO_URL + SO_SERVICE_INSTANTIATION_URL
        # self.__logger.debug("SO request: %s", url)
        # response = self.__send_message('POST', 'create service instance',
        #                                url, data=so_service_payload)
        # self.__logger.info("SO create service request: %s",
        #                    response.text)
        # so_instance_id_response = response.json()
        # self.__logger.debug("so_instance_id_response: %s",
        #                     so_instance_id_response)
        # instance_id = (
        #     so_instance_id_response['requestReferences']['instanceId'])
        # return instance_id

    def exists(self) -> bool:
        pass
