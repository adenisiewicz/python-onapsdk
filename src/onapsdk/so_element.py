#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SO Element module."""
from dataclasses import dataclass

import logging

from onapsdk.onap_service import OnapService
import onapsdk.constants as const
from onapsdk.utils.jinja import jinja_env

@dataclass
class SoElement(OnapService):
    """Mother Class of all SO elements."""

    name: str = None
    _server: str = "SO"
    _so_url = "http://so.api.simpledemo.onap.org:30277"
    _so_api_version = "v7"
    # aai_url = "https://aai.api.sparky.simpledemo.onap.org:30233"
    # aai_api_version = "/aai/v13"
    _logger: logging.Logger = logging.getLogger(__name__)
    _status: str = None

    def _instantiate(self, template_name: str, **kwargs) -> None:
        """Create the request in SO if not already existing."""
        self._logger.info("attempting to create %s %s in SO",
                          type(self).__name__, self.name)

        url = self._base_create_url()
        template = jinja_env().get_template("service_instance_macro.json.j2")
        print(url)
        print(kwargs)
        print(template)
        # data = template.render(**kwargs)
        # create_result = self.send_message_json('POST',
        #                                        "create {}".format(
        #                                            type(self).__name__),
        #                                        url, data=data)
        # if create_result:
        #     self._logger.info("%s %s is created in SO",
        #                       type(self).__name__, self.name)
        #     self._status = const.DRAFT
            # self.identifier = self._get_identifier_from_so(create_result)
            # self._version = self._get_version_from_so(create_result)
            # self.update_informations_from_so_creation(create_result)
        # else:
        #     self._logger.error(
        #         "an error occured during creation of %s %s in SO",
        #         type(self).__name__, self.name)



    @classmethod
    def _base_create_url(cls) -> str:
        """
        Give back the base url of SO.

        Returns:
            str: the base url

        """
        return "{}/onap/so/infra/serviceInstantiation/{}/serviceInstances".format(
            cls._so_url, cls._so_api_version)
