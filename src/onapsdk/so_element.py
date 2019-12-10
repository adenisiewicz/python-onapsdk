#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SO Element module."""
from dataclasses import dataclass

import logging
import json

from onapsdk.service import Service
from onapsdk.vf import Vf
from onapsdk.onap_service import OnapService
import onapsdk.constants as const
from onapsdk.utils.jinja import jinja_env
from onapsdk.utils.tosca_file_handler import get_vf_list_from_tosca_file
from onapsdk.aai_element import AaiElement

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

    def _instantiate(self, **kwargs) -> None:
        """Create the request in SO if not already existing."""
        self._logger.info("attempting to create %s %s in SO",
                          type(self).__name__, self.name)

        url = self._base_create_url()

        # Generate VF model INFO
        service_model = self.set_service_model_info(kwargs['ns_name'])
        print(service_model)
        vf_names = get_vf_list_from_tosca_file(kwargs['ns_model'])
        vf_models_info = {}
        for vf_name in vf_names:
            vf_models_info[vf_name] = self.set_vf_model_info(vf_name)
        print(vf_models_info)
        # Generate Cloud INFO
        cloud_info = self.set_cloud_info()
        print(cloud_info)

        # Create Service Instance payloadData
        if kwargs['ns_instantiation_mode'] is 'macro':
            template = jinja_env().get_template("service_instance_macro.json.j2")


    def set_service_model_info(self, service_name):
        service = Service(name=service_name)
        template_service = jinja_env().get_template(
            'service_instance_model_info.json.j2')
        # Get service instance model
        return json.loads(template_service.render(
            model_invariant_id=service.unique_uuid,
            model_name_version_id=service.identifier,
            model_name=service.name,
            model_version=service.version))

    def set_vf_model_info(self, vf_name):
        vf = Vf(name=vf_name)
        template_service = jinja_env().get_template(
            'vf_model_info.json.j2')
        return json.loads(template_service.render(
            vf_model_invariant_uuid=vf.unique_uuid,
            vf_model_customization_id="????",
            vf_model_version_id=vf.identifier,
            vf_model_name=vf.name,
            vf_model_version=vf.version))

    def set_cloud_info(self):
        # on pourrait imaginer de préciser le cloud ici en cas de Multicloud
        # en attendant on prendra le premier cloud venu..
        aai = AaiElement()
        aai_info=aai.get_cloud_info()
        template_cloud = jinja_env().get_template(
            'cloud_configuration.json.j2')
        return json.loads(template_cloud.render(
            cloud_region_id=aai_info['cloud_region_id'],
            tenant_id=aai_info['tenant_id'],
            cloud_owner=aai_info['cloud_owner']))

    @classmethod
    def _base_create_url(cls) -> str:
        """
        Give back the base url of SO.

        Returns:
            str: the base url

        """
        return "{}/onap/so/infra/serviceInstantiation/{}/serviceInstances".format(
            cls._so_url, cls._so_api_version)
