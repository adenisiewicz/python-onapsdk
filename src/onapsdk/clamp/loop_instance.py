#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Control Loop module."""
import time
import os
import json
from jsonschema import validate, ValidationError

from onapsdk.clamp.clamp_element import Clamp
from onapsdk.utils.jinja import jinja_env


class LoopInstance(Clamp):
    """Control Loop instantiation class."""

    #class variable
    _loop_schema = None

    def __init__(self, template: str, name: str, details: dict) -> None:
        """Initialize the object."""
        super().__init__()
        self.template = template
        self.name = name
        self._details = details

    @property
    def details(self) -> dict:
        """Return and lazy load the details."""
        if not self._details:
            self._update_loop_details()
        return self._details

    @details.setter
    def details(self, details: dict) -> None:
        """Set value for details."""
        self._details = details

    def _update_loop_details(self) -> dict:
        """Update loop details."""
        url = "{}/loop/{}".format(self.base_url, self.name)
        loop_details = self.send_message_json('GET',
                                              'Get loop details',
                                              url,
                                              cert=self._cert)
        if loop_details:
            return loop_details
        raise ValueError("Couldn't get the appropriate details")

    @property
    def loop_schema(self) -> dict:
        """Return and lazy load the details schema."""
        if not self._loop_schema:
            file = f"{os.path.dirname(os.path.abspath(__file__))}/schema_details.json"
            with open(file, "rb") as plan:
                json_schema = json.load(plan)
                self._loop_schema = json_schema
        return self._loop_schema

    def validate_details(self) -> bool:
        """Validate Loop Instance details."""
        try:
            validate(self.details, self.loop_schema)
        except ValidationError as error:
            self._logger.error(error)
            self._logger.error("---------")
            self._logger.error(error.absolute_path)
            self._logger.error("---------")
            self._logger.error(error.absolute_schema_path)
            return False
        return True

    def create(self) -> bool:
        """Create instance and load loop details."""
        url = "{}/loop/create/{}?templateName={}".\
              format(self.base_url, self.name, self.template)
        instance_details = self.send_message_json('POST',
                                                  'Create Loop Instance',
                                                  url,
                                                  cert=self._cert)
        if  instance_details:
            self.name = "LOOP_" + self.name
            self.details = instance_details
            if len(self.details["microServicePolicies"]) > 0:
                return True
        raise ValueError("Couldn't create the instance")

    def add_operational_policy(self, policy_type: str, policy_version: str) -> bool:
        """Add operational policy to the loop instance."""
        url = "{}/loop/addOperationaPolicy/{}/policyModel/{}/{}".\
              format(self.base_url, self.name, policy_type, policy_version)
        add_response = self.send_message_json('PUT',
                                              'Create Operational Policy',
                                              url,
                                              cert=self._cert)
        nb_policies = len(self.details["operationalPolicies"])
        if (add_response and (len(add_response["operationalPolicies"]) > nb_policies)):
            self.details = add_response
            return True
        raise ValueError("Couldn't add the operational policy")

    def remove_operational_policy(self, policy_type: str, policy_version: str) -> dict:
        """Remove operational policy from the loop instance."""
        url = "{}/loop/removeOperationaPolicy/{}/policyModel/{}/{}".\
              format(self.base_url, self.name, policy_type, policy_version)
        response = self.send_message_json('PUT',
                                          'Remove Operational Policy',
                                          url,
                                          cert=self._cert)
        self.details = self._update_loop_details()
        return response

    def update_microservice_policy(self) -> None:
        """Update microservice policy configuration."""
        url = "{}/loop/updateMicroservicePolicy/{}".format(self.base_url, self.name)
        template = jinja_env().get_template("clamp_add_tca_config.json.j2")
        data = template.render(LOOP_name=self.name)
        upload_result = self.send_message('POST',
                                          'ADD TCA config',
                                          url,
                                          data=data,
                                          cert=self._cert)
        if upload_result:
            self._logger.info("Files for TCA config %s have been uploaded to loop's microservice",
                              self.name)
        else:
            self._logger.error(("an error occured during file upload for TCA config to loop's"
                                " microservice %s"), self.name)

    def add_drools_conf(self) -> dict:
        """Add drools configuration."""
        self.validate_details()
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
        return data

    def add_frequency_limiter(self, limit: int = 1) -> None:
        """Add frequency limiter config."""
        template = jinja_env().get_template("clamp_add_frequency.json.j2")
        data = template.render(LOOP_name=self.name, limit=limit)
        return data

    def add_op_policy_config(self, func, **kwargs) ->None:
        """Add operational policy config."""
        data = func(**kwargs)
        url = "{}/loop/updateOperationalPolicies/{}".format(self.base_url, self.name)
        upload_result = self.send_message('POST',
                                          'ADD operational policy config',
                                          url,
                                          data=data,
                                          cert=self._cert)
        if upload_result:
            self._logger.info(("Files for op policy config %s have been uploaded to loop's"
                               "Op policy"), self.name)
        else:
            self._logger.error(("an error occured during file upload for config to loop's"
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
                                               url,
                                               cert=self._cert)
        action_done = False
        if policy_action:
            self.validate_details()
            old_state = self.details["components"]["POLICY"]["componentState"]["stateName"]
            self.details = self._update_loop_details()
            self.validate_details()
            new_state = self.details["components"]["POLICY"]["componentState"]["stateName"]
            if new_state != old_state and not(action != "stop" and new_state == "SENT"):
                action_done = True
        return action_done

    def deploy_microservice_to_dcae(self) -> bool:
        """Execute the deploy operation on the loop instance."""
        url = "{}/loop/deploy/{}".format(self.base_url, self.name)
        response = self.send_message_json('PUT',
                                          'Deploy microservice to DCAE',
                                          url,
                                          cert=self._cert)
        deploy = False
        if response:
            self.validate_details()
            state = self.details["components"]["DCAE"]["componentState"]["stateName"]
            failure = "MICROSERVICE_INSTALLATION_FAILED"
            success = "MICROSERVICE_INSTALLED_SUCCESSFULLY"
            while state not in (success, failure):
                #modify the time sleep for loop refresh
                time.sleep(0)
                self.details = self._update_loop_details()
                self.validate_details()
                state = self.details["components"]["DCAE"]["componentState"]["stateName"]
            deploy = (state == success)
        return deploy

    def undeploy_microservice_from_dcae(self) -> bool:
        """Stop the deploy operation."""
        url = "{}/loop/stop/{}".format(self.base_url, self.name)
        response = self.send_message_json('PUT',
                                          'Undeploy microservice from DCAE',
                                          url,
                                          cert=self._cert)
        if not response:
            return True
        raise ValueError("Couldn't stop the microservice deploy")

    def delete(self):
        """Delete the loop instance."""
        self._logger.debug("Delete %s loop instance", self.name)
        url = "{}/loop/delete/{}".format(self.base_url, self.name)
        request = self.send_message_json('PUT',
                                         'Delete loop instance',
                                         url,
                                         cert=self._cert)
        return request
