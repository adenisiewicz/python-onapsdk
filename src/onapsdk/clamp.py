#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Clamp module."""
from onapsdk.onap_service import OnapService as Onap
from onapsdk.service import Service
from onapsdk.utils.jinja import jinja_env


class Clamp(Onap):
    """Mother Class of all CLAMP elements."""

    @classmethod
    def base_url(cls) -> str:
        """Give back the base url of Clamp."""
        return "https://clamp.api.simpledemo.onap.org:30258/restservices/clds/v2"

    @classmethod
    def pkcs12_filename(cls) -> str:
        """Give back the certificate name for Clamp."""
        return ("https://gerrit.onap.org/r/gitweb?p=clamp.git;a=blob;f=src/main/resources/"
                "clds/aaf/org.onap.clamp.p12;h=268aa1a3ce56e01448f8043cc0b05b5fceb5a47d;hb=HEAD")
    
    @classmethod
    def pkcs12_password(cls) -> str:
        """Give back the certificate password for Clamp."""
        return "China in the Spring"

    @classmethod
    def check_loop_template(cls, service: Service) -> str:
        """Return loop template name if exists."""
        url = "{}/templates/".format(cls.base_url())
        template_list = cls.send_message_json('GET',
                                              'Get Loop Templates',
                                              url,
                                              cls.pkcs12_filename,
                                              cls.pkcs12_password)
        for template in template_list:
            if template["modelService"]["serviceDetails"]["name"] == service.name:
                return template["name"]
        raise ValueError("Template not found")

    @classmethod
    def check_policies(cls, policy_name: str) -> bool:
        """Ensure that policies are stored in CLAMP."""
        url = "{}/policyToscaModels/".format(cls.base_url())
        policies = cls.send_message_json('GET',
                                         'Get stocked policies',
                                         url,
                                         cls.pkcs12_filename,
                                         cls.pkcs12_password)
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

    def create(self) -> bool:
        """Create instance and load loop details."""
        url = "{}/loop/create/{}?templateName={}".\
              format(self.base_url, self.name, self.template)
        instance_details = self.send_message_json('POST',
                                                  'Create Loop Instance',
                                                  url,
                                                  self.pkcs12_filename,
                                                  self.pkcs12_password)
        if  instance_details:
            self.name = "LOOP_" + self.name
            self.details = instance_details
            if len(self.details["microServicePolicies"]) > 0:
                return True
        raise ValueError("Couldn't create the instance")

    def add_oprational_policy(self, policy_type: str, policy_version: str) -> bool:
        """Add op policy to the loop instance."""
        url = "{}/loop/addOperationaPolicy/{}/policyModel/{}/{}".\
              format(self.base_url, self.name, policy_type, policy_version)
        add_response = self.send_message_json('PUT',
                                              'Create Operational Policy',
                                              url,
                                              self.pkcs12_filename,
                                              self.pkcs12_password)
        nb_policies = len(self.details["operationalPolicies"])
        if (add_response and (len(add_response["operationalPolicies"]) > nb_policies)):
            self.details = add_response
            return True
        raise ValueError("Couldn't add the op policy")

    def update_microservice_policy(self) -> None:
        """Add TCA config to microservice."""
        url = "{}/loop/updateMicroservicePolicy/{}".format(self.base_url, self.name)
        template = jinja_env().get_template("clamp_add_tca_config.json.j2")
        data = template.render(LOOP_name=self.name)
        upload_result = self.send_message('POST',
                                          'ADD TCA config',
                                          url,
                                          self.pkcs12_filename,
                                          self.pkcs12_password,
                                          data=data)
        if upload_result:
            self._logger.info("Files for TCA config %s have been uploaded to loop's microservice",
                              self.name)
        else:
            self._logger.error(("an error occured during file upload for TCA config to loop's"
                                " microservice %s"), self.name)
