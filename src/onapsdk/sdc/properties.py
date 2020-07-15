#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Service properties module."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional


@dataclass
class Input:
    """Property input dataclass."""

    unique_id: str
    input_type: str
    name: str
    default_value: Optional[Any] = None


@dataclass
class Property:  # pylint: disable=too-many-instance-attributes
    """Service property dataclass."""

    sdc_resource: "SdcResource"
    unique_id: str
    name: str
    property_type: str
    parent_unique_id: str
    value: Optional[Any] = None
    description: Optional[str] = None
    get_input_values: Optional[List[Dict[str, str]]] = None

    @property
    def input(self) -> Input:
        """Property input.

        Returns property Input object.
            Returns None if property has no associated input.

        Raises:
            AttributeError: Input for given property does not exits.
                It shouldn't ever happen, but it's possible if after you
                get property object someone delete input.

        Returns:
            Input: Property input object.

        """
        if not self.get_input_values:
            return None
        try:
            return next(filter(lambda x: x.unique_id == self.get_input_values[0].get("inputId"),
                               self.sdc_resource.inputs))
        except StopIteration:
            raise AttributeError("Property input does not exist")


class ResourceWithInputsMixin(ABC):
    """Resource with input mixin.

    That mixin can be used by resource class which can have inputs
        for it's properties.

    """

    @property
    @abstractmethod
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
                self.resource_inputs_url,
                exception=AttributeError).get("inputs", []):

            yield Input(
                unique_id=input_data["uniqueId"],
                input_type=input_data["type"],
                name=input_data["name"],
                default_value=input_data.get("defaultValue")
            )
