#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""NS module."""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import logging
import json
import yaml

from onapsdk.so_element import SoElement
from onapsdk.utils.jinja import jinja_env
from onapsdk.utils.tosca_file_handler import get_parameter_from_yaml, random_string_generator


@dataclass
class NetworkService(SoElement):
    """Network Service Object used for SO operations."""

    logger: logging.Logger = logging.getLogger(__name__)
    rand_extension: str = ""
    name: str
    random_string_length = 6

    # def __post_init__(self):
    #     # self.headers = headers_so_creator(SoElement.headers)
    #     self.name = self.name + "-" + random_string_generator(6)

    def __init__(self, name: str, tosca_file_path: str):
        """
        Initialize vnf object.

        Args:
            name (optional): the name of the vnf
            package: the csar file

        """
        super().__init__()
        try:
            self.name = name + "-" + str(random_string_generator(self.random_string_length))
        except TypeError:
            raise NameError("VNF Name must be specified")

        self.tosca_file_path = tosca_file_path
        try:
            with open(self.tosca_file_path) as my_file:
                self.model = json.dumps(yaml.safe_load(my_file))
            if self.model == "null":
                raise ValueError
        except TypeError:
            raise NameError("Tosca file Path must be specified")
        except (FileNotFoundError, ValueError):
            raise FileNotFoundError("No Tosca file found")

        # self.cloud = Cloud or None

    @property
    def service_name(self) -> str:
        """Returns service name. It's object name without random string.

        :return: Service name
        """
        return get_parameter_from_yaml("metadata.name", self.model)

    def instantiate(self, service_file_path: Path, instantiation_mode: str = "macro") -> None:
        """Instantiate the VNF in SO using Macro."""
        self._logger.info("attempting to create %s %s in SO", type(self).__name__, self.name)

        # Get subscribed ID
        global_subscriber_id = self.get_subscriber_info()
        self._logger.debug("Global subscriber retrieved: %s", global_subscriber_id)
        # subscription_service_type
        subscription_service_type = self.get_subscription_service_type(self.name)
        self._logger.debug("Subscription service type found: %s", subscription_service_type)

        # Get Service model
        service_model = self.get_service_model_info(self.service_name)

        # Get instance parameters
        vnf_instance_params, vf_instance_params = self.get_instance_params(service_file_path)

        # get vf
        vnf_instances = self.get_vnfs(
            ns_name=self.name,
            ns_model=self.model,
            ns_vnf_instance_params=vnf_instance_params,
            ns_vf_instance_params=vf_instance_params,
        )

        # Generate Cloud INFO
        cloud_info = self.get_cloud_info()

        # Create Service Instance payloadData
        if instantiation_mode == "macro":
            template_macro = jinja_env().get_template("service_instance_macro.json.j2")
            macro_payload = template_macro.render(
                global_subscriber_id=global_subscriber_id,
                ns_instance_name=self.name,
                cloud_configuration=cloud_info,
                subscription_service_type=subscription_service_type,
                vnf_instances=vnf_instances,
                service_model=service_model,
            )
            response = self.send_message_json(
                "POST", "Instantiate service", self._base_create_url(), data=macro_payload, headers=self.headers
            )
            # TODO: Parse response - there is an information about orchestration request, which can be useful
            print(response)
        else:
            raise ValueError("Not supported instantiation mode")

    def get_instance_params(self, service_file_path: Path) -> Tuple[Dict, Dict]:
        """Load instance config file and read service parameters from it.

        :param service_file_path: YAML file path which has to have "vnfs" section
        :return: Two dictionaries tuple. First dictionary contains vnf_instance_params and the second one
            is vf_instance_params dictionary.
        :raises:
            FileNotFoundError: service_file_path doesn't exist
            KeyError: invalid YAML file format, section from exception is missed
        """
        vnf_instance_params: dict = {}
        vf_instance_params: dict = {}  # Always empty
        with service_file_path.open() as service_file:  # type: TextIOWrapper
            yaml_service_file: dict = yaml.safe_load(service_file)
            for vnf_parameter in (
                parameter
                for service in yaml_service_file
                for vnf in yaml_service_file[service]["vnfs"]
                for parameter in vnf["vnf_parameters"]
            ):
                vnf_instance_params.update({vnf_parameter["vnf-parameter-name"]: vnf_parameter["vnf-parameter-value"]})
        return vnf_instance_params, vf_instance_params

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
