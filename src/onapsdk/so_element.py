#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SO Element module."""
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Type

import logging

from onapsdk.onap_service import OnapService
import onapsdk.constants as const
from onapsdk.utils.jinja import jinja_env
from onapsdk.utils.tosca_file_handler import get_model_from_tosca
from onapsdk.aai_element import AaiElement

@dataclass
class SoElement(OnapService):
    """Mother Class of all SO elements."""

    name: str = None
    tosca_file_path: str = None
    cloud_region: str = None

    _server: str = "SO"
    # server_aai: str = "AAI"
    _so_url = "http://so.api.simpledemo.onap.org:30277"
    _so_api_version = "v7"
    # aai_url = "https://aai.api.sparky.simpledemo.onap.org:30233"
    # aai_api_version = "/aai/v13"
    _logger: logging.Logger = logging.getLogger(__name__)
    _identifier: str = None
    _status: str = None
    _models: dict = None
    _cloud: dict = None
    _aai = AaiElement()

    def __post_init__(self):
        print("tosca file: {}".format(self.tosca_file_path))
        if (self.tosca_file_path is not None or
                self.cloud_region is not None):
            self.load()


    @property
    def identifier(self) -> str:
        """Return and lazy load the identifier."""
        if not self._identifier:
            self.load()
        return self._identifier

    @identifier.setter
    def identifier(self, value: str) -> None:
        """Set value for identifier."""
        self._identifier = value

    @property
    def models(self) -> str:
        """Return and lazy load the models."""
        if not self._models:
            self.load()
        return self._models

    @models.setter
    def models(self, value: dict) -> None:
        """Set value for models."""
        self._models = value

    @property
    def cloud(self) -> str:
        """Return and lazy load the cloud."""
        if not self._cloud:
            self.load()
        return self._cloud

    @cloud.setter
    def cloud(self, value: dict) -> None:
        """Set value for cloud."""
        self._cloud = value

    def created(self) -> bool:
        """Determine if SoElement is created."""
        return bool(self._identifier)


    def _exists(self, klass) -> bool:
        """
        Check if object created with SO already exists in AAI

        Returns:
            True if exists, False either

        """
        self._logger.debug("check if %s %s exists in SO", type(self).__name__,
                           self.name)
        # TODO
        return False


    def _create(self, template_name: str, **kwargs) -> None:
        """Create the request in SO if not already existing."""
        self._logger.info("attempting to create %s %s in SO",
                          type(self).__name__, self.name)
        # Create only if cloud and tosca model are known
        if (self.models is not None or
                self.cloud is not None):
            self.load()

        if not self.exists():
            url = self._base_create_url()
            template = jinja_env().get_template(template_name)
            data = template.render(**kwargs)
            create_result = self.send_message_json('POST',
                                                   "create {}".format(
                                                       type(self).__name__),
                                                   url, data=data)
            if create_result:
                self._logger.info("%s %s is created in SO",
                                  type(self).__name__, self.name)
                self._status = const.DRAFT
                # self.identifier = self._get_identifier_from_so(create_result)
                # self._version = self._get_version_from_so(create_result)
                # self.update_informations_from_so_creation(create_result)
            else:
                self._logger.error(
                    "an error occured during creation of %s %s in SO",
                    type(self).__name__, self.name)
        else:
            self._logger.warning("%s %s is already created in SO",
                                 type(self).__name__, self.name)

    def load(self) -> None:
        """Load Object information from SDC or AAI."""
        # retrieve models based on Tosca file
        self.models = self._get_models()

        # retrieve cloud info
        if self.cloud_region is not None:
            self.cloud = self._aai.tenants_info(self.cloud_region)
        else:
            self._logger.error("Cloud name not defined")
        # if instance_details:
        #     self._logger.debug("details found, updating")
        #     self.update_informations_from_so(instance_details)
        # else:
        #     # exists() method check if exists AND update indentifier
        #     self.exists()

    def _get_models(self) -> Dict[str, Any]:
        """
        Get models.

        Returns:
            Dict[str, Any]: the description of the item

        """
        try:
            return get_model_from_tosca(self.tosca_file_path)
        except FileNotFoundError:
            self._logger.warning("Tosca file not found")
            return {}

    def _get_cloud(self, cloud_region) -> Dict[str, Any]:
        """
        Get models.

        Returns:
            Dict[str, Any]: the description of the item

        """
        try:
            return self._aai.tenants_info(cloud_region)
        except FileNotFoundError:
            self._logger.warning("No Cloud found")
            return {}


    def _eq(self, klass: Type, other: Any) -> bool:
        """
        Check equality for SOElement and children.

        Args:
            klass (string)
            other: another object

        Returns:
            bool: True if same object, False if not
        """
        if isinstance(other, klass):
            return self.name == other.name
        return False

    @classmethod
    def _base_create_url(cls) -> str:
        """
        Give back the base url of SO.

        Returns:
            str: the base url

        """
        return "{}/onap/so/infra/serviceInstantiation/{}/serviceInstances".format(
            cls._so_url, cls._so_api_version)

    def exists(self):
        """
        Check existence of an object in SO.

        Raises:
            NotImplementedError: this is an abstract method.

        """
        raise NotImplementedError("SoElement is an abstract class")
