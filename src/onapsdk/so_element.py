#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SO Element module."""
from dataclasses import dataclass
from typing import Dict

import logging
import json

from onapsdk.service import Service
from onapsdk.vf import Vf
from onapsdk.onap_service import OnapService

from onapsdk.utils.headers_creator import headers_so_creator
from onapsdk.utils.jinja import jinja_env
from onapsdk.utils.tosca_file_handler import get_modules_list_from_tosca_file, get_vf_list_from_tosca_file
from onapsdk.aai_element import AaiElement


@dataclass
class SoElement(OnapService):
    """Mother Class of all SO elements."""

    name: str = None
    _server: str = "SO"
    _so_url = "http://so.api.simpledemo.onap.org:30277"
    _so_api_version = "v7"
    _logger: logging.Logger = logging.getLogger(__name__)
    _status: str = None

    @property
    def headers(self):
        """Create headers for SO request.

        It is used as a property because x-transactionid header should be unique for each request.
        """
        return headers_so_creator(OnapService.headers)

    def instantiate(self, **kwargs) -> None:
        """Create the request in SO if not already existing.

        Implement that method on each subclass.
        """
        raise NotImplementedError

    @classmethod
    def get_cloud_info(cls):
        """Retrieve Cloud info."""
        # on pourrait imaginer de préciser le cloud ici en cas de Multicloud
        # en attendant on prendra le premier cloud venu..
        aai = AaiElement()
        aai_info = aai.get_cloud_info()
        template_cloud = jinja_env().get_template("cloud_configuration.json.j2")
        parsed = json.loads(
            template_cloud.render(
                cloud_region_id=aai_info["cloud_region_id"],
                tenant_id=aai_info["tenant_id"],
                cloud_owner=aai_info["cloud_owner"],
            )
        )
        return json.dumps(parsed, indent=4)

    @classmethod
    def get_subscriber_info(cls):
        """Get subscriber Info."""
        aai = AaiElement()
        aai_info = aai.get_customers()
        return aai_info["customer"][0]["global-customer-id"]

    @classmethod
    def get_subscription_service_type(cls, vf_name):
        """Retrieve the model info of the VFs."""
        vf_object = Vf(name=vf_name)
        return vf_object.name

    @classmethod
    def get_service_model_info(cls, service_name):
        """Retrieve Service Model info."""
        service = Service(name=service_name)
        template_service = jinja_env().get_template("service_instance_model_info.json.j2")
        # Get service instance model
        parsed = json.loads(
            template_service.render(
                model_invariant_id=service.unique_uuid,
                model_name_version_id=service.identifier,
                model_name=service.name,
                model_version=service.version,
            )
        )
        return json.dumps(parsed, indent=4)

    @classmethod
    def get_vnf_model_info(cls, vf_name):
        """Retrieve the model info of the VFs."""
        vf_object = Vf(name=vf_name)
        template_service = jinja_env().get_template("vnf_model_info.json.j2")
        parsed = json.loads(
            template_service.render(
                vnf_model_invariant_uuid=vf_object.unique_uuid,
                vnf_model_customization_id="????",
                vnf_model_version_id=vf_object.identifier,
                vnf_model_name=vf_object.name,
                vnf_model_version=vf_object.version,
                vnf_model_instance_name=(vf_object.name + " 0"),
            )
        )
        # we need also a vnf instance Name
        # Usually it is found like that
        # name: toto
        # instance name: toto 0
        # it can be retrieved from the tosca
        return json.dumps(parsed, indent=4)

    @classmethod
    def get_vf_model_info(cls, vf_name: str, vf_model: str) -> str:
        """Retrieve the VF model info From Tosca?."""
        modules: Dict = get_modules_list_from_tosca_file(vf_model)
        template_service = jinja_env().get_template("vf_model_info.json.j2")
        parsed = json.loads(template_service.render(modules=modules))
        return json.dumps(parsed, indent=4)

    def get_vnfs(self, **kwargs):
        """Get VNFs description for macro instantiation."""
        vf_names = get_vf_list_from_tosca_file(kwargs["ns_model"])

        for vf_name in vf_names:
            template_vnf = jinja_env().get_template("vnf_instance_macro.json.j2")

            self._logger.debug(kwargs["ns_name"])
            self._logger.debug("----------------------> 1")
            self._logger.debug(self.get_vnf_model_info(vf_name))
            self._logger.debug("----------------------> 2")
            self._logger.debug(self.get_cloud_info())
            self._logger.debug("----------------------> 3")
            self._logger.debug("vnf_%s", vf_name)
            self._logger.debug("----------------------> 4")
            self._logger.debug(self.get_vf_model_info(vf_name, kwargs["ns_model"]))
            self._logger.debug("----------------------> 5")
            self._logger.debug("vf_%s", vf_name)

            vnfs_macro = json.loads(
                template_vnf.render(
                    vnf_model_info=self.get_vnf_model_info(vf_name),
                    cloud_configuration=self.get_cloud_info(),
                    vnf_instance_name="vnf_" + vf_name,
                    vnf_instance_param=kwargs["ns_vnf_instance_params"],
                    vf_modules=self.get_vf_model_info(vf_name, kwargs["ns_model"]),
                    vnf_model_instance_name="vnf_" + kwargs["ns_name"],
                    vnf_instance_params=kwargs["ns_vf_instance_params"],
                )
            )
        self._logger.info("vnfs payload part built: %s", vnfs_macro)
        return json.dumps(vnfs_macro, indent=4)

    @classmethod
    def _base_create_url(cls) -> str:
        """
        Give back the base url of SO.

        Returns:
            str: the base url

        """
        return "{}/onap/so/infra/serviceInstantiation/{}/serviceInstances".format(cls._so_url, cls._so_api_version)
