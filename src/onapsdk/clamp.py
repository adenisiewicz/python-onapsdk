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
    def check_loop_template(cls, service: Service) -> str:
        """Return loop template name if exists."""
        url = "{}/templates/".format(cls.base_url())
        template_list = cls.send_message_json('GET',
                                              'Get Loop Templates',
                                              url)
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
                                         url)
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

    def update_loop_details(self) -> dict:
        """Update loop details."""
        url = "{}/loop/{}".format(self.base_url, self.name)
        loop_details = self.send_message_json('GET',
                                              'Get loop details',
                                              url)
        if loop_details:
            return loop_details
        raise ValueError("Couldn't get the appropriate details")

    def create(self) -> bool:
        """Create instance and load loop details."""
        url = "{}/loop/create/{}?templateName={}".\
              format(self.base_url, self.name, self.template)
        instance_details = self.send_message_json('POST',
                                                  'Create Loop Instance',
                                                  url)
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
                                              url)
        nb_policies = len(self.details["operationalPolicies"])
        if (add_response and (len(add_response["operationalPolicies"]) > nb_policies)):
            self.details = add_response
            return True
        raise ValueError("Couldn't add the op policy")

    def remove_oprational_policy(self, policy_type: str, policy_version: str) -> dict:
        """Remove op policy from the loop instance."""
        url = "{}/loop/removeOperationaPolicy/{}/policyModel/{}/{}".\
              format(self.base_url, self.name, policy_type, policy_version)
        response = self.send_message_json('PUT',
                                          'Remove Operational Policy',
                                          url)
        #must modify loop details depending on response
        return response

    def update_microservice_policy(self) -> None:
        """Add TCA config to microservice."""
        url = "{}/loop/updateMicroservicePolicy/{}".format(self.base_url, self.name)
        template = jinja_env().get_template("clamp_add_tca_config.json.j2")
        data = template.render(LOOP_name=self.name)
        upload_result = self.send_message('POST',
                                          'ADD TCA config',
                                          url,
                                          data=data)
        if upload_result:
            self._logger.info("Files for TCA config %s have been uploaded to loop's microservice",
                              self.name)
        else:
            self._logger.error(("an error occured during file upload for TCA config to loop's"
                                " microservice %s"), self.name)

    def add_drools_conf(self) -> dict:
        """Add drools configuration."""
        url = "{}/loop/updateOperationalPolicies/{}".format(self.base_url, self.name)
        vfmodule_dicts = self.details["modelService"]["resourceDetails"]["VFModule"]
        entity_ids = {}
        #Get the vf module details
        for vfmodule in vfmodule_dicts.values():
            entity_ids["resourceID"] = vfmodule["vfModuleModelName"]
            entity_ids["modelInvariantId"] = vfmodule["vfModuleModelInvariantUUID"]
            entity_ids["modelVersionId"] = vfmodule["vfModuleModelUUID"]
            entity_ids["modelName"] = vfmodule["vfModuleModelName"]
            entity_ids["modelVersion"] = vfmodule["vfModuleModelVersion"]
            entity_ids["modelCustomizationId"] = vfmodule["vfModuleModelCustomizationUUID"]
        template = jinja_env().get_template("clamp_add_drools_policy.json.j2")
        data = template.render(entity_ids=entity_ids, LOOP_name=self.name)
        upload_result = self.send_message('POST',
                                          'ADD drools config',
                                          url,
                                          data=data)
        if upload_result:
            self._logger.info("Files for drools config %s have been uploaded to loop's Op policy",
                              self.name)
        else:
            self._logger.error(("an error occured during file upload for drools config to loop's"
                                " Op policy %s"), self.name)
        return entity_ids

    def add_frequency_limiter(self, limit: int = 1) -> None:
        """Add frequency limiter config."""
        url = "{}/loop/updateOperationalPolicies/{}".format(self.base_url, self.name)
        template = jinja_env().get_template("clamp_add_frequency.json.j2")
        data = template.render(LOOP_name=self.name, limit=limit)
        upload_result = self.send_message('POST',
                                          'ADD frequency limiter config',
                                          url,
                                          data=data)
        if upload_result:
            self._logger.info(("Files for frequency config %s have been uploaded to loop's"
                               "Op policy"), self.name)
        else:
            self._logger.error(("an error occured during file upload for frequency config to loop's"
                                " Op policy %s"), self.name)

    def act_on_loop_policy(self, action: str) -> bool:
        """
        Act on loop's policy.

        Args:
            action : action to be done from (submit, stop, restart)

        Returns:
            action state : failed or done

        """
        url = "{}/loop/{}/{}".format(self.base_url, action, self.name)
        policy_action = self.send_message_json('PUT',
                                               '{} policy'.format(action),
                                               url)
        action_done = False
        if policy_action:
            old_state = self.details["components"]["POLICY"]["componentState"]["stateName"]
            self.details = self.update_loop_details()
            #new_state = "SENT_AND_DEPLOYED"
            new_state = self.details["components"]["POLICY"]["componentState"]["stateName"]
            if new_state != old_state and not(action != "stop" and new_state == "SENT"):
                action_done = True
        return action_done

    def delete(self):
        """Delete the loop instance."""
        self._logger.debug("Delete %s loop instance", self.name)
        url = "{}/loop/delete/{}".format(self.base_url, self.name)
        request = self.send_message_json('PUT',
                                         'Delete loop instance',
                                         url)
        return request
