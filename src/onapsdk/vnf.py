#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Vnf module."""
from typing import Any
from typing import Dict

import logging
import json
import yaml

from dataclasses import dataclass
from pathlib import Path

from onapsdk.so_element import SoElement
from onapsdk.utils.tosca_file_handler import get_model_from_tosca

from onapsdk.utils.tosca_file_handler import random_string_generator

@dataclass
class Vnf(SoElement):
    """
    ONAP Vnf Object used for SO operations.

    Attributes:
    """
    logger: logging.Logger = logging.getLogger(__name__)
    rand_extension: str = ""
    headers: dict = None
    name: str

    # def __post_init__(self):
    #     # self.headers = headers_so_creator(SoElement.headers)
    #     self.name = self.name + "-" + random_string_generator(6)

    def __init__(self, name: str = None, tosca_file_path: Path = None):
        """
        Initialize vnf object.

        Args:
            name (optional): the name of the vnf
            package: the csar file

        """
        super().__init__()
        try:
            self.name = name + "-" + str(random_string_generator(6))
        except TypeError:
            raise NameError("VNF Name must be specified")

        try:
            self.tosca_file_path = tosca_file_path or None
            with open(self.tosca_file_path) as f:
                self.model = json.dumps(yaml.safe_load(f))
            if self.model is 'null':
                raise ValueError
        except TypeError:
            raise NameError("Tosca file Path must be specified")
        except (FileNotFoundError, ValueError):
            raise FileNotFoundError("No Tosca file found")

        # self.cloud = Cloud or None

    def instantiate(self) -> None:
        """Instantiate the VNF in SO using Macro."""
        self._instantiate("service_instance_macro.json.j2",
                          vnf_name=self.name,
                          vnf_model=self.model)


    # def _get_model(self) -> Dict[str, Any]:
    #     """
    #     Get models.
    #
    #     Returns:
    #         Dict[str, Any]: the description of the item
    #
    #     """
    #     try:
    #
    #         return get_model_from_tosca(self.tosca_file_path)
    #     except FileNotFoundError:
    #         self._logger.warning("Tosca file not found")
    #         return {}

    # def _get_cloud(self, cloud_region) -> Dict[str, Any]:
    #     """
    #     Get models.
    #
    #     Returns:
    #         Dict[str, Any]: the description of the item
    #
    #     """
    #     try:
    #         return "yo"
    #         # return self._aai.tenants_info(cloud_region)
    #     except FileNotFoundError:
    #         self._logger.warning("No Cloud found")
    #         return {}
