#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC Component module."""
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Component:  # pylint: disable=too-many-instance-attributes
    """Component dataclass."""

    created_from_csar: bool
    actual_component_uid: str
    unique_id: str
    normalized_name: str
    name: str
    origin_type: str
    customization_uuid: str
    component_uid: str
    component_version: str
    tosca_component_name: str
    component_name: str
    sdc_resource: "SdcResource"

    @classmethod
    def create_from_api_response(cls,
                                 api_response: Dict[str, Any],
                                 sdc_resource: "SdcResource") -> "Component":
        """Create component from api response.

        Args:
            api_response (Dict[str, Any]): component API response
            sdc_resource (SdcResource): component's SDC resource

        Returns:
            Component: Component created using api_response and SDC resource

        """
        return cls(created_from_csar=api_response["createdFromCsar"],
                   actual_component_uid=api_response["actualComponentUid"],
                   unique_id=api_response["uniqueId"],
                   normalized_name=api_response["normalizedName"],
                   name=api_response["name"],
                   origin_type=api_response["originType"],
                   customization_uuid=api_response["customizationUUID"],
                   component_uid=api_response["componentUid"],
                   component_version=api_response["componentVersion"],
                   tosca_component_name=api_response["toscaComponentName"],
                   component_name=api_response["componentName"],
                   sdc_resource=sdc_resource)
