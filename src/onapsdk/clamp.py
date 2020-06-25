#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Clamp module."""
import json

from onapsdk.onap_service import OnapService as Onap
from onapsdk.service import Service


class Clamp(Onap):
    """Mother Class of all CLAMP elements."""

    def __init__(self) -> None:
        """Initialize the object."""

    @classmethod
    def base_url(cls) -> str:
        """Give back the base url of Clamp."""
        return "https://clamp.api.simpledemo.onap.org:30258/restservices/clds/v2/"

    @classmethod
    def check_loop_template(cls, service: Service) -> str:
        """Return loop template name if exists."""
        url = "{}/templates/".format(cls.base_url())
        template_list = cls.send_message_json('GET', 'Get Loop Templates', url)
        for template in template_list:
            if template["modelService"]["serviceDetails"]["name"] == service.name:
                return template["name"]
        raise ValueError("Template not found")

    @classmethod
    def check_policies(cls, policy_name: str) -> bool:
        """Ensure that policies are stored in CLAMP."""
        url = "{}/policyToscaModels/".format(cls.base_url())
        policies = cls.send_message_json('GET', 'Get stocked policies', url)
        if len(policies) > 30:
            for policy in policies:
                if policy["policyAcronym"] == policy_name:
                    return True
        raise ValueError("Couldn't load policies from policy engine")


class LoopInstance(Clamp):
    """Control Loop instantiation class."""

    def __init__(self, template: str, name: str, details: dict) -> None:
        """Initialize the object."""
        super().__init__()
        self.template = template
        self.name = name
        self.details = details

    def create(self) -> None:
        """Create instance and load loop details."""
        url = "{}/loop/create/{}?templateName={}".\
              format(self.base_url, self.name, self.template)
        instance_details = self.send_message('POST', 'Add artifact to vf', url)
        if  instance_details:
            self.name = "LOOP_" + self.name
            self.details = json.load(instance_details)
        raise ValueError("Couldn't create the instance")
