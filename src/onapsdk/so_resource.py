#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SO Resource module."""
from dataclasses import dataclass

import logging
import json
import yaml

from onapsdk.utils.jinja import jinja_env
from onapsdk.utils.tosca_file_handler import get_parameter_from_yaml

@dataclass
class SoResource():
    """Mother Class of all SO resource."""

    model: str = None
    service_model_info = None

    _logger: logging.Logger = logging.getLogger(__name__)
    if model is not None:
        service_model_info = self.set_service_model_info()
        # _vf_model_info = self.set_vf_model_info(model)
        # _vnf_model_info = self.set_vnf_model_info(model)

    def set_model(model: str):
        self.model = model

    def set_service_module(self):
        template_service = jinja_env().get_template(
            'service_instance_model_info.json.j2')
        # Get service instance model
        return json.loads(template_service.render(
            model_invariant_id=get_parameter_from_yaml("metadata.invariantUUID",
                                                       self.model),
        model_name_version_id=get_parameter_from_yaml("metadata.UUID",
                                                      self.model),
        model_name=get_parameter_from_yaml("metadata.name", self.model),
        model_version="1.0"))
