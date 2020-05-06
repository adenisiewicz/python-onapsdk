#!/usr/bin/env python3  pylint: disable=C0302
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""AAI Element module."""
import logging
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional

from onapsdk.onap_service import OnapService
from onapsdk.utils.headers_creator import headers_aai_creator
from onapsdk.utils.jinja import jinja_env


@dataclass
class Relationship:
    """Relationship class.

    A&AI elements could have relationship with other A&AI elements.
    Relationships are represented by this class objects.
    """

    related_to: str
    related_link: str
    relationship_data: List[Dict[str, str]]
    relationship_label: str = ""
    related_to_property: List[Dict[str, str]] = field(default_factory=list)


class AaiElement(OnapService):
    """Mother Class of all A&AI elements."""

    __logger: logging.Logger = logging.getLogger(__name__)

    name: str = "AAI"
    server: str = "AAI"
    base_url = "https://aai.api.sparky.simpledemo.onap.org:30233"
    api_version = "/aai/v16"
    headers = headers_aai_creator(OnapService.headers)

    @classmethod
    def filter_none_key_values(cls, dict_to_filter: Dict[str, Optional[str]]) -> Dict[str, str]:
        """Filter out None key values from dictionary.

        Iterate throught given dictionary and filter None values.

        Args:
            dict_to_filter (Dict): Dictionary to filter out None

        Returns:
            Dict[str, str]: Filtered dictionary

        """
        return dict(
            filter(lambda key_value_tuple: key_value_tuple[1] is not None, dict_to_filter.items(),)
        )

    # @classmethod
    # def customers(cls):
    #     """Get the list of subscription types in A&AI."""
    #     return Customer.get_all()

    # @classmethod
    # def subscriptions(cls):
    #     """Get the list of subscriptions in A&AI."""
    #     return Service.get_all()

    # @classmethod
    # def customer_service_tenant_relations(cls, customer_name):
    #     """Get the list of customer/service/tenant relations in A&AI."""
    #     url = (
    #         cls.base_url
    #         + cls.api_version
    #         + "/business/customers/customer/"
    #         + customer_name
    #         + "/service-subscriptions?depth=all"
    #     )
    #     return cls.send_message_json("GET", "get relations", url)

    # @classmethod
    # def cloud_regions(cls) -> Iterator["CloudRegion"]:
    #     """Get the list of subscription types in AAI."""
    #     return CloudRegion.get_all()

    # @classmethod
    # def get_customers(cls):
    #     """Get the list of  in A&AI."""
    #     return Customer.get_all()

    # @classmethod
    # def get_subscription_type_list(cls):
    #     """Get the list of subscription types in A&AI."""
    #     return Service.get_all()

    # @classmethod
    # def tenants_info(cls, cloud_owner, region_name):
    #     """Get the Cloud info of one cloud region."""
    #     try:
    #         cloud_region: CloudRegion = CloudRegion.get_by_id(cloud_owner, region_name)
    #         return cloud_region.tenants
    #     except ValueError as exc:
    #         cls.__logger.exception(str(exc))
    #         raise Exception("CloudRegion not found")

    # @classmethod
    # def get_cloud_info(cls):
    #     """Get the preformatted Cloud info for SO instantiation."""
    #     try:
    #         return next(cls.cloud_regions())
    #     except StopIteration:
    #         cls.__logger.error("No cloud regions defined in A&AI")
    #         raise

    @property
    def url(self) -> str:
        """Resource's url.

        Returns:
            str: Resource's url

        """
        raise NotImplementedError

    @property
    def relationships(self) -> Iterator[Relationship]:
        """Resource relationships iterator.

        Yields:
            Relationship: resource relationship
        """
        for relationship in self.send_message_json("GET",
                                                   f"Get object relationships",
                                                   f"{self.url}/relationship-list")\
                                                       .get("relationship", []):
            yield Relationship(
                related_to=relationship.get("related-to"),
                relationship_label=relationship.get("relationship-label"),
                related_link=relationship.get("related-link"),
                relationship_data=relationship.get("relationship-data"),
            )

    def add_relationship(self, relationship: Relationship) -> None:
        """Add relationship to aai resource.

        Add relationship to resource using A&AI API

        Args:
            relationship (Relationship): Relationship to add

        """
        self.send_message(
            "PUT",
            "add relationship to cloud region",
            f"{self.url}/relationship-list/relationship",
            data=jinja_env()
            .get_template("aai_add_relationship.json.j2")
            .render(relationship=relationship),
        )
