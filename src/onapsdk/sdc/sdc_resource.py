#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC Element module."""
import logging
from abc import ABC
from typing import Any, Dict, Iterator, List

from simplejson.errors import JSONDecodeError

import onapsdk.constants as const
from onapsdk.sdc import SDC
from onapsdk.sdc.properties import Input, Property
from onapsdk.utils.headers_creator import (headers_sdc_creator,
                                           headers_sdc_tester)
from onapsdk.utils.jinja import jinja_env


# For an unknown reason, pylint keeps seeing _unique_uuid and
# _unique_identifier as attributes along with unique_uuid and unique_identifier
class SdcResource(SDC, ABC):  # pylint: disable=too-many-instance-attributes
    """Mother Class of all SDC resources."""

    RESOURCE_PATH = 'resources'
    ACTION_TEMPLATE = 'sdc_resource_action.json.j2'
    ACTION_METHOD = 'POST'

    def __init__(self, name: str = None, sdc_values: Dict[str, str] = None,
                 properties: List[Property] = None):
        """Initialize the object."""
        super().__init__()
        self.name: str = name
        self._unique_uuid: str = None
        self._unique_identifier: str = None
        self._resource_type: str = "resources"
        self._properties_to_add: List[Property] = properties or []
        if sdc_values:
            self._logger.debug("SDC values given, using them")
            self.identifier = sdc_values['uuid']
            self.version = sdc_values['version']
            self.unique_uuid = sdc_values['invariantUUID']
            distribitution_state = None
            if 'distributionStatus' in sdc_values:
                distribitution_state = sdc_values['distributionStatus']
            self.status = self._parse_sdc_status(sdc_values['lifecycleState'],
                                                 distribitution_state,
                                                 self._logger)
            self._logger.debug("SDC resource %s status: %s", self.name,
                               self.status)

    def __repr__(self) -> str:
        """SDC resource description.

        Returns:
            str: SDC resource object description

        """
        return f"{self.__class__.__name__.upper()}(name={self.name})"

    @property
    def unique_uuid(self) -> str:
        """Return and lazy load the unique_uuid."""
        if not self._unique_uuid:
            self.load()
        return self._unique_uuid

    @property
    def unique_identifier(self) -> str:
        """Return and lazy load the unique_identifier."""
        if not self._unique_identifier:
            self.deep_load()
        return self._unique_identifier

    @unique_uuid.setter
    def unique_uuid(self, value: str) -> None:
        """Set value for unique_uuid."""
        self._unique_uuid = value

    @unique_identifier.setter
    def unique_identifier(self, value: str) -> None:
        """Set value for unique_identifier."""
        self._unique_identifier = value

    def load(self) -> None:
        """Load Object information from SDC."""
        self.exists()

    def deep_load(self) -> None:
        """Deep load Object informations from SDC."""
        url = (
            f"{self.base_front_url}/sdc1/feProxy/rest/v1/"
            "screen?excludeTypes=VFCMT&excludeTypes=Configuration"
        )
        headers = headers_sdc_creator(SdcResource.headers)
        if self.status == const.UNDER_CERTIFICATION:
            headers = headers_sdc_tester(SdcResource.headers)
        response = self.send_message_json("GET",
                                          "Deep Load {}".format(
                                              type(self).__name__),
                                          url,
                                          headers=headers)
        if response:
            for resource in response[self._sdc_path()]:
                if resource["uuid"] == self.identifier:
                    self._logger.debug("Resource %s found in %s list",
                                       resource["name"], self._sdc_path())
                    self.unique_identifier = resource["uniqueId"]

    def _generate_action_subpath(self, action: str) -> str:
        """

        Generate subpath part of SDC action url.

        Args:
            action (str): the action that will be done

        Returns:
            str: the subpath part

        """
        return action

    def _version_path(self) -> str:
        """
        Give the end of the path for a version.

        Returns:
            str: the end of the path

        """
        return self.unique_identifier

    def _action_url(self,
                    base: str,
                    subpath: str,
                    version_path: str,
                    action_type: str = None) -> str:
        """
        Generate action URL for SDC.

        Args:
            base (str): base part of url
            subpath (str): subpath of url
            version_path (str): version path of the url
            action_type (str, optional): the type of action
                                         ('distribution', 'distribution-state'
                                         or 'lifecycleState'). Default to
                                         'lifecycleState').

        Returns:
            str: the URL to use

        """
        if not action_type:
            action_type = "lifecycleState"
        return "{}/{}/{}/{}/{}".format(base, self._resource_type, version_path,
                                       action_type, subpath)

    @classmethod
    def _base_create_url(cls) -> str:
        """
        Give back the base url of Sdc.

        Returns:
            str: the base url

        """
        return "{}/sdc1/feProxy/rest/v1/catalog".format(cls.base_front_url)

    @classmethod
    def _base_url(cls) -> str:
        """
        Give back the base url of Sdc.

        Returns:
            str: the base url

        """
        return "{}/sdc/v1/catalog".format(cls.base_back_url)

    @classmethod
    def _get_all_url(cls) -> str:
        """
        Get URL for all elements in SDC.

        Returns:
            str: the url

        """
        return "{}/{}?resourceType={}".format(cls._base_url(), cls._sdc_path(),
                                              cls.__name__.upper())

    @classmethod
    def _get_objects_list(cls, result: List[Dict[str, Any]]
                          ) -> List[Dict[str, Any]]:
        """
        Import objects created in SDC.

        Args:
            result (Dict[str, Any]): the result returned by SDC in a Dict

        Return:
            List[Dict[str, Any]]: the list of objects

        """
        return result

    def _get_version_from_sdc(self, sdc_infos: Dict[str, Any]) -> str:
        """
        Get version from SDC results.

        Args:
            sdc_infos (Dict[str, Any]): the result dict from SDC

        Returns:
            str: the version

        """
        return sdc_infos['version']

    def _get_identifier_from_sdc(self, sdc_infos: Dict[str, Any]) -> str:
        """
        Get identifier from SDC results.

        Args:
            sdc_infos (Dict[str, Any]): the result dict from SDC

        Returns:
            str: the identifier

        """
        return sdc_infos['uuid']

    @classmethod
    def import_from_sdc(cls, values: Dict[str, Any]) -> 'SdcResource':
        """
        Import SdcResource from SDC.

        Args:
            values (Dict[str, Any]): dict to parse returned from SDC.

        Return:
            SdcResource: the created resource

        """
        cls._logger.debug("importing SDC Resource %s from SDC", values['name'])
        return cls(name=values['name'], sdc_values=values)

    def _copy_object(self, obj: 'SdcResource') -> None:
        """
        Copy relevant properties from object.

        Args:
            obj (SdcResource): the object to "copy"

        """
        self.identifier = obj.identifier
        self.unique_uuid = obj.unique_uuid
        self.status = obj.status
        self.version = obj.version
        self.unique_identifier = obj.unique_identifier
        self._specific_copy(obj)

    def _specific_copy(self, obj: 'SdcResource') -> None:
        """
        Copy specific properties from object.

        Args:
            obj (SdcResource): the object to "copy"

        """
    def update_informations_from_sdc(self, details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC.

        Args:
            details ([type]): [description]

        """
    def update_informations_from_sdc_creation(self,
                                              details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC after creation.

        Args:
            details ([type]): the details from SDC

        """
        self.unique_uuid = details['invariantUUID']
        distribution_state = None

        if 'distributionStatus' in details:
            distribution_state = details['distributionStatus']
        self.status = self._parse_sdc_status(details['lifecycleState'],
                                             distribution_state, self._logger)
        self.version = details['version']
        self.unique_identifier = details['uniqueId']

    # Not my fault if SDC has so many states...
    # pylint: disable=too-many-return-statements
    @staticmethod
    def _parse_sdc_status(sdc_status: str, distribution_state: str,
                          logger: logging.Logger) -> str:
        """
        Parse  SDC status in order to normalize it.

        Args:
            sdc_status (str): the status found in SDC
            distribution_state (str): the distribution status found in SDC.
                                        Can be None.

        Returns:
            str: the normalized status

        """
        logger.debug("Parse status for SDC Resource")
        if sdc_status.capitalize() == const.CERTIFIED:
            if distribution_state and distribution_state == const.SDC_DISTRIBUTED:
                return const.DISTRIBUTED
            return const.CERTIFIED
        if sdc_status == const.NOT_CERTIFIED_CHECKOUT:
            return const.DRAFT
        if sdc_status == const.NOT_CERTIFIED_CHECKIN:
            return const.CHECKED_IN
        if sdc_status == const.READY_FOR_CERTIFICATION:
            return const.SUBMITTED
        if sdc_status == const.CERTIFICATION_IN_PROGRESS:
            return const.UNDER_CERTIFICATION
        if sdc_status != "":
            return sdc_status
        return None

    def _really_submit(self) -> None:
        """Really submit the SDC Vf in order to enable it."""
        raise NotImplementedError("SDC is an abstract class")

    @classmethod
    def _sdc_path(cls) -> None:
        """Give back the end of SDC path."""
        return cls.RESOURCE_PATH

    @property
    def properties_url(self) -> str:
        """Properties url.

        Returns:
            str: SdcResource properties url

        """
        return (f"{self._base_create_url()}/services/"
                f"{self.unique_identifier}/properties")

    @property
    def properties(self) -> Iterator[Property]:
        """SDC resource properties.

        Iterate resource properties.

        Yields:
            Property: Resource property

        """
        # That's ugly - we should separate `exception`
        # in send_message and send_message_json into
        # two parameters I think: one for API error
        # response and another for invalid response JSON
        # format. In this case if resource has no
        # properties API returns empty response (sic!)
        # instead of eg. empty list. That's of course
        # SDC API issue, but I don't think they will
        # fix that because GUI already works using that.
        response = self.send_message(\
            "GET",
            f"Get {self.name} resource properties",
            self.properties_url,
            exception=AttributeError)
        try:
            response_json = response.json()
        except JSONDecodeError:
            self._logger.exception("API response is empty.")
            response_json = []
        for property_data in response_json:
            yield Property(
                sdc_resource=self,
                unique_id=property_data["uniqueId"],
                name=property_data["name"],
                property_type=property_data["type"],
                parent_unique_id=property_data["parentUniqueId"],
                value=property_data.get("value"),
                description=property_data.get("description"),
                get_input_values=property_data.get("getInputValues"),
            )

    @property
    def resource_inputs_url(self) -> str:
        """Resource inputs url.

        Abstract method which should be implemented by subclasses
            and returns url which point to resource inputs.

        Raises:
            NotImplementedError: Method not implemented by subclass

        Returns:
            str: Resource inputs url

        """
        raise NotImplementedError

    @property
    def inputs(self) -> Iterator[Input]:
        """SDC resource inputs.

        Iterate resource inputs.

        Yields:
            Iterator[Input]: Resource input

        """
        for input_data in self.send_message_json(\
                "GET",
                f"Get {self.name} resource inputs",
                f"{self.resource_inputs_url}/filteredDataByParams?include=inputs",
                exception=AttributeError).get("inputs", []):

            yield Input(
                unique_id=input_data["uniqueId"],
                input_type=input_data["type"],
                name=input_data["name"],
                default_value=input_data.get("defaultValue")
            )

    def declare_input(self, property_to_input_declare: Property) -> None:
        """Declare input for given property.

        Call SDC FE API to declare input for given property.
            It's going to be regular input declared.

        Args:
            property_to_input_declare (Property): Property to declare input

        """
        self._logger.debug("Declare input for created property")
        self.send_message_json("POST",
                               f"Declare new input for {property_to_input_declare.name} property",
                               f"{self.resource_inputs_url}/create/inputs",
                               data=jinja_env().get_template(
                                   "sdc_resource_add_input.json.j2").\
                                       render(
                                           sdc_resource=self,
                                           property=property_to_input_declare
                                       ),
                               exception=ValueError)

    def add_property(self, property_to_add: Property) -> None:
        """Add property to resource.

        Call SDC FE API to add property to resource.

        Args:
            property_to_add (Property): Property object to add to resource.

        Raises:
            AttributeError: Resource has not DRAFT status

        """
        if self.status != const.DRAFT:
            raise AttributeError("Can't add property to resource which is not in DRAFT status")
        self._logger.debug("Add property to sdc resource")
        self.send_message_json("POST",
                               f"Declare new property for {self.name} sdc resource",
                               self.properties_url,
                               data=jinja_env().get_template(
                                   "sdc_resource_add_property.json.j2").\
                                    render(
                                        property=property_to_add
                                    ),
                               exception=ValueError)
        if property_to_add.declare_input:
            self.declare_input(property_to_add)
