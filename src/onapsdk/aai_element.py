#!/usr/bin/env python3  pylint: disable=C0302
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""AAI Element module."""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urlencode
from uuid import uuid4

from onapsdk.multicloud import Multicloud
from onapsdk.onap_service import OnapService
from onapsdk.service import Service as SdcService
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

    @classmethod
    def customers(cls):
        """Get the list of subscription types in A&AI."""
        return Customer.get_all()

    @classmethod
    def subscriptions(cls):
        """Get the list of subscriptions in A&AI."""
        return Service.get_all()

    @classmethod
    def customer_service_tenant_relations(cls, customer_name):
        """Get the list of customer/service/tenant relations in A&AI."""
        url = (
            cls.base_url
            + cls.api_version
            + "/business/customers/customer/"
            + customer_name
            + "/service-subscriptions?depth=all"
        )
        return cls.send_message_json("GET", "get relations", url)

    @classmethod
    def cloud_regions(cls) -> Iterator["CloudRegion"]:
        """Get the list of subscription types in AAI."""
        return CloudRegion.get_all()

    @classmethod
    def get_customers(cls):
        """Get the list of  in A&AI."""
        return Customer.get_all()

    @classmethod
    def get_subscription_type_list(cls):
        """Get the list of subscription types in A&AI."""
        return Service.get_all()

    @classmethod
    def tenants_info(cls, cloud_name):
        """Get the Cloud info of one cloud region."""
        try:
            cloud_region: CloudRegion = CloudRegion.get_by_region_id(cloud_name)
            return cloud_region.tenants
        except ValueError as exc:
            cls.__logger.exception(str(exc))
            raise Exception("Region not found")

    @classmethod
    def get_cloud_info(cls):
        """Get the preformatted Cloud info for SO instantiation."""
        try:
            return next(cls.cloud_regions())
        except StopIteration:
            cls.__logger.error("No cloud regions defined in A&AI")
            raise

    @property
    def url(self) -> str:
        """Resource's url.

        Returns:
            str: Resource's url

        """
        raise NotImplementedError

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


class Complex(AaiElement):  # pylint: disable=R0902
    """Complex class.

    Collection of physical locations that can house cloud-regions.
    """

    def __init__(self,  # pylint: disable=R0914
                 name: str,
                 physical_location_id: str,
                 *,
                 data_center_code: str = "",
                 identity_url: str = "",
                 resource_version: str = "",
                 physical_location_type: str = "",
                 street1: str = "",
                 street2: str = "",
                 city: str = "",
                 state: str = "",
                 postal_code: str = "",
                 country: str = "",
                 region: str = "",
                 latitude: str = "",
                 longitude: str = "",
                 elevation: str = "",
                 lata: str = "") -> None:
        """Complex object initialization.

        Args:
            name (str): complex name
            physical_location_id (str): complex ID
            data_center_code (str, optional): complex data center code. Defaults to "".
            identity_url (str, optional): complex identity url. Defaults to "".
            resource_version (str, optional): complex resource version. Defaults to "".
            physical_location_type (str, optional): complex physical location type. Defaults to "".
            street1 (str, optional): complex address street part one. Defaults to "".
            street2 (str, optional): complex address street part two. Defaults to "".
            city (str, optional): complex address city. Defaults to "".
            state (str, optional): complex address state. Defaults to "".
            postal_code (str, optional): complex address postal code. Defaults to "".
            country (str, optional): complex address country. Defaults to "".
            region (str, optional): complex address region. Defaults to "".
            latitude (str, optional): complex geographical location latitude. Defaults to "".
            longitude (str, optional): complex geographical location longitude. Defaults to "".
            elevation (str, optional): complex elevation. Defaults to "".
            lata (str, optional): complex lata. Defaults to "".

        """
        super().__init__()
        self.name: str = name
        self.physical_location_id: str = physical_location_id
        self.data_center_code: str = data_center_code
        self.identity_url: str = identity_url
        self.resource_version: str = resource_version
        self.physical_location_type: str = physical_location_type
        self.street1: str = street1
        self.street2: str = street2
        self.city: str = city
        self.state: str = state
        self.postal_code: str = postal_code
        self.country: str = country
        self.region: str = region
        self.latitude: str = latitude
        self.longitude: str = longitude
        self.elevation: str = elevation
        self.lata: str = lata

    def __repr__(self) -> str:
        """Complex object description.

        Returns:
            str: Complex object description

        """
        return (f"Complex(name={self.name}, physical_location_id={self.physical_location_id}, "
                f"resource_version={self.resource_version})")

    @property
    def url(self) -> str:
        """Complex url.

        Returns:
            str: Complex url

        """
        return (f"{self.base_url}{self.api_version}/cloud-infrastructure/complexes/complex/"
                f"{self.physical_location_id}?resource-version={self.resource_version}")

    @classmethod
    def create(cls,  # pylint: disable=R0914
               name: str,
               physical_location_id: str,
               *,
               data_center_code: str = "",
               identity_url: str = "",
               resource_version: str = "",
               physical_location_type: str = "",
               street1: str = "",
               street2: str = "",
               city: str = "",
               state: str = "",
               postal_code: str = "",
               country: str = "",
               region: str = "",
               latitude: str = "",
               longitude: str = "",
               elevation: str = "",
               lata: str = "") -> "Complex":
        """Create complex.

        Create complex object by calling A&AI API.
        If API request doesn't fail it returns Complex object.

        Returns:
            Complex: Created complex object

        """
        complex_object: Complex = Complex(
            name=name,
            physical_location_id=physical_location_id,
            data_center_code=data_center_code,
            identity_url=identity_url,
            resource_version=resource_version,
            physical_location_type=physical_location_type,
            street1=street1,
            street2=street2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            region=region,
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
            lata=lata,
        )
        payload: str = jinja_env().get_template("complex_create.json.j2").render(
            complex=complex_object)
        url: str = (
            f"{cls.base_url}{cls.api_version}/cloud-infrastructure/complexes/complex/"
            f"{complex_object.physical_location_id}"
        )
        cls.send_message("PUT", "create complex", url, data=payload)
        return complex_object

    @classmethod
    def get_all(cls,
                physical_location_id: str = None,
                data_center_code: str = None,
                complex_name: str = None,
                identity_url: str = None) -> Iterator["Complex"]:
        """Get all complexes from A&AI.

        Call A&AI API to get all complex objects.

        Args:
            physical_location_id (str, optional): Unique identifier for physical location,
                e.g., CLLI. Defaults to None.
            data_center_code (str, optional): Data center code which can be an alternate way
                to identify a complex. Defaults to None.
            complex_name (str, optional): Gamma complex name for LCP instance. Defaults to None.
            identity_url (str, optional): URL of the keystone identity service. Defaults to None.

        Yields:
            Complex -- Complex object. Can not yield anything if any complex with given filter
                parameters doesn't exist

        """
        filter_parameters: dict = cls.filter_none_key_values(
            {
                "physical-location-id": physical_location_id,
                "data-center-code": data_center_code,
                "complex-name": complex_name,
                "identity-url": identity_url,
            }
        )
        url: str = (f"{cls.base_url}{cls.api_version}/cloud-infrastructure/"
                    f"complexes?{urlencode(filter_parameters)}")
        for complex_json in cls.send_message_json("GET",
                                                  "get cloud regions",
                                                  url).get("complex", []):
            yield Complex(
                name=complex_json["complex-name"],
                physical_location_id=complex_json["physical-location-id"],
                data_center_code=complex_json.get("data-center-code"),
                identity_url=complex_json.get("identity-url"),
                resource_version=complex_json.get("resource-version"),
                physical_location_type=complex_json.get("physical-location-type"),
                street1=complex_json.get("street1"),
                street2=complex_json.get("street2"),
                city=complex_json.get("city"),
                state=complex_json.get("state"),
                postal_code=complex_json.get("postal-code"),
                country=complex_json.get("country"),
                region=complex_json.get("region"),
                latitude=complex_json.get("latitude"),
                longitude=complex_json.get("longitude"),
                elevation=complex_json.get("elevation"),
                lata=complex_json.get("lata"),
            )


class Service(AaiElement):
    """SDC service class."""

    def __init__(self, service_id: str, service_description: str, resource_version: str) -> None:
        """Service model initialization.

        Args:
            service_id (str): This gets defined by others to provide a unique ID for the service.
            service_description (str): Description of the service.
            resource_version (str): Used for optimistic concurrency.

        """
        super().__init__()
        self.service_id = service_id
        self.service_description = service_description
        self.resource_version = resource_version

    def __repr__(self) -> str:
        """Service object description.

        Returns:
            str: Service object description

        """
        return (
            f"Service(service_id={self.service_id}, "
            f"service_description={self.service_description}, "
            f"resource_version={self.resource_version})"
        )

    @property
    def url(self) -> str:
        """Service object url.

        Returns:
            str: Service object url address

        """
        return (f"{self.base_url}{self.api_version}/service-design-and-creation/services/service/"
                f"{self.service_id}?resource-version={self.resource_version}")

    @classmethod
    def get_all(cls,
                service_id: str = None,
                service_description: str = None) -> Iterator["Service"]:
        """Services iterator.

        Stand-in for service model definitions.

        Returns:
            Iterator[Service]: Service

        """
        filter_parameters: dict = cls.filter_none_key_values(
            {"service-id": service_id, "service-description": service_description}
        )
        url: str = (f"{cls.base_url}{cls.api_version}/service-design-and-creation/"
                    f"services?{urlencode(filter_parameters)}")
        for service in cls.send_message_json("GET", "get subscriptions", url).get("service", []):
            yield Service(
                service_id=service["service-id"],
                service_description=service["service-description"],
                resource_version=service["resource-version"],
            )

    @classmethod
    def create(cls,
               service_id: str,
               service_description: str) -> None:
        """Create service.

        Args:
            service_id (str): service ID
            service_description (str): service description

        Raises:
            ValueError: Creation request returns HTTP error code

        """
        cls.send_message(
            "PUT",
            "Create A&AI service",
            f"{cls.base_url}{cls.api_version}/service-design-and-creation/"
            f"services/service/{service_id}",
            data=jinja_env()
            .get_template("aai_service_create.json.j2")
            .render(
                service_id=service_id,
                service_description=service_description
            ),
            exception=ValueError
        )


class Tenant(AaiElement):
    """Tenant class."""

    def __init__(self,  # pylint: disable=R0913
                 cloud_region: "CloudRegion",
                 tenant_id: str,
                 tenant_name: str,
                 tenant_context: str = None,
                 resource_version: str = None):
        """Tenant object initialization.

        Tenant object represents A&AI Tenant resource.

        Args:
            cloud_region (str): Cloud region object
            tenant_id (str): Unique Tenant ID
            tenant_name (str): Tenant name
            tenant_context (str, optional): Tenant context. Defaults to None.
            resource_version (str, optional): Tenant resource version. Defaults to None.

        """
        super().__init__()
        self.cloud_region: "CloudRegion" = cloud_region
        self.tenant_id: str = tenant_id
        self.name: str = tenant_name
        self.context: str = tenant_context
        self.resource_version: str = resource_version

    def __repr__(self) -> str:
        """Tenant repr.

        Returns:
            str: Human readable Tenant object description

        """
        return (
            f"Tenant(tenant_id={self.tenant_id}, tenant_name={self.name}, "
            f"tenant_context={self.context}, "
            f"resource_version={self.resource_version}, "
            f"cloud_region={self.cloud_region.cloud_region_id})"
        )

    @property
    def url(self) -> str:
        """Tenant url.

        Returns:
            str: Url which can be used to update or delete tenant.

        """
        return (
            f"{self.base_url}{self.api_version}/cloud-infrastructure/cloud-regions/cloud-region/"
            f"{self.cloud_region.cloud_owner}/{self.cloud_region.cloud_region_id}"
            f"/tenants/tenant/{self.tenant_id}?"
            f"resource-version={self.resource_version}"
        )

    def delete(self) -> None:
        """Delete tenant.

        Remove tenant from cloud region.

        """
        return self.send_message(
            "DELETE",
            f"Remove tenant {self.name} from {self.cloud_region.cloud_region_id} cloud region",
            url=self.url,
        )


@dataclass
class AvailabilityZone:
    """Availability zone.

    A collection of compute hosts/pservers
    """

    name: str
    hypervisor_type: str
    operational_status: str = None
    resource_version: str = None


@dataclass
class EsrSystemInfo:  # pylint: disable=R0902
    """Persist common address information of external systems."""

    esr_system_info_id: str
    user_name: str
    password: str
    system_type: str
    resource_version: str
    system_name: str = None
    esr_type: str = None
    vendor: str = None
    version: str = None
    service_url: str = None
    protocol: str = None
    ssl_cacert: str = None
    ssl_insecure: Optional[bool] = None
    ip_address: str = None
    port: str = None
    cloud_domain: str = None
    default_tenant: str = None
    passive: Optional[bool] = None
    remote_path: str = None
    system_status: str = None
    openstack_region_id: str = None


class ServiceInstance(AaiElement):  # pylint: disable=R0902
    """Service instanve class."""

    def __init__(self,  # pylint: disable=R0913, R0914
                 service_subscription: "ServiceSubscription",
                 instance_id: str,
                 instance_name: str = None,
                 service_type: str = None,
                 service_role: str = None,
                 environment_context: str = None,
                 workload_context: str = None,
                 created_at: str = None,
                 updated_at: str = None,
                 description: str = None,
                 model_invariant_id: str = None,
                 model_version_id: str = None,
                 persona_model_version: str = None,
                 widget_model_id: str = None,
                 widget_model_version: str = None,
                 bandwith_total: str = None,
                 vhn_portal_url: str = None,
                 service_instance_location_id: str = None,
                 resource_version: str = None,
                 selflink: str = None,
                 orchestration_status: str = None,
                 input_parameters: str = None) -> None:
        """Service instance object initialization.

        Args:
            service_subscription (ServiceSubscription): service subscription which is belongs to
            instance_id (str): Uniquely identifies this instance of a service
            instance_name (str, optional): This field will store a name assigned to
                the service-instance. Defaults to None.
            service_type (str, optional): String capturing type of service. Defaults to None.
            service_role (str, optional): String capturing the service role. Defaults to None.
            environment_context (str, optional): This field will store the environment context
                assigned to the service-instance. Defaults to None.
            workload_context (str, optional): This field will store the workload context assigned to
                the service-instance. Defaults to None.
            created_at (str, optional): Create time of Network Service. Defaults to None.
            updated_at (str, optional): Last update of Network Service. Defaults to None.
            description (str, optional): Short description for service-instance. Defaults to None.
            model_invariant_id (str, optional): The ASDC model id for this resource or
                service model. Defaults to None.
            model_version_id (str, optional): The ASDC model version for this resource or
                service model. Defaults to None.
            persona_model_version (str, optional): The ASDC model version for this resource or
                service model. Defaults to None.
            widget_model_id (str, optional): he ASDC data dictionary widget model. This maps
                directly to the A&AI widget. Defaults to None.
            widget_model_version (str, optional): The ASDC data dictionary version of the widget
                model. This maps directly to the A&AI version of the widget. Defaults to None.
            bandwith_total (str, optional): Indicates the total bandwidth to be used for this
                service. Defaults to None.
            vhn_portal_url (str, optional): URL customers will use to access the vHN Portal.
                Defaults to None.
            service_instance_location_id (str, optional): An identifier that customers assign to
                the location where this service is being used. Defaults to None.
            resource_version (str, optional): Used for optimistic concurrency. Must be empty on
                create, valid on update and delete. Defaults to None.
            selflink (str, optional): Path to the controller object. Defaults to None.
            orchestration_status (str, optional): Orchestration status of this service.
                Defaults to None.
            input_parameters (str, optional): String capturing request parameters from SO to
                pass to Closed Loop. Defaults to None.
        """
        super().__init__()
        self.service_subscription: "ServiceSubscription" = service_subscription
        self.instance_id: str = instance_id
        self.instance_name: str = instance_name
        self.service_type: str = service_type
        self.service_role: str = service_role
        self.environment_context: str = environment_context
        self.workload_context: str = workload_context
        self.created_at: str = created_at
        self.updated_at: str = updated_at
        self.description: str = description
        self.model_invariant_id: str = model_invariant_id
        self.model_version_id: str = model_version_id
        self.persona_model_version: str = persona_model_version
        self.widget_model_id: str = widget_model_id
        self.widget_model_version: str = widget_model_version
        self.bandwith_total: str = bandwith_total
        self.vhn_portal_url: str = vhn_portal_url
        self.service_instance_location_id: str = service_instance_location_id
        self.resource_version: str = resource_version
        self.selflink: str = selflink
        self.orchestration_status: str = orchestration_status
        self.input_parameters: str = input_parameters

    def __repr__(self) -> str:
        """Service instance object representation.

        Returns:
            str: Human readable service instance representation

        """
        return (f"ServiceInstance(instance_id={self.instance_id}, "
                f"instance_name={self.instance_name})")

    @property
    def url(self) -> str:
        """Service instance resource URL.

        Returns:
            str: Service instance url

        """
        return (
            f"{self.service_subscription.url}/service-instances/service-instance/{self.instance_id}"
        )


@dataclass
class ServiceSubscription(AaiElement):
    """Service subscription class."""

    service_type: str
    resource_version: str
    customer: "Customer"

    def __init__(self, customer: "Customer", service_type: str, resource_version: str) -> None:
        """Service subscription object initialization.

        Args:
            customer (Customer): Customer object
            service_type (str): Service type
            resource_version (str): Service subscription resource version
        """
        super().__init__()
        self.customer: "Customer" = customer
        self.service_type: str = service_type
        self.resource_version: str = resource_version

    def _get_service_instance_by_filter_parameter(self,
                                                  filter_parameter_name: str,
                                                  filter_parameter_value: str) -> ServiceInstance:
        """Call a request to get service instance with given filter parameter and value.

        Args:
            filter_parameter_name (str): Name of parameter to filter
            filter_parameter_value (str): Value of filter parameter

        Raises:
            ValueError: Service instance with given filter parameters
                doesn't exist

        Returns:
            ServiceInstance: ServiceInstance object

        """
        service_instance: dict = self.send_message_json(
            "GET",
            f"Get service instance with {filter_parameter_value} {filter_parameter_name}",
            f"{self.url}/service-instances?{filter_parameter_name}={filter_parameter_value}",
            exception=ValueError
        )["service-instance"][0]
        return ServiceInstance(
            service_subscription=self,
            instance_id=service_instance.get("service-instance-id"),
            instance_name=service_instance.get("service-instance-name"),
            service_type=service_instance.get("service-type"),
            service_role=service_instance.get("service-role"),
            environment_context=service_instance.get("environment-context"),
            workload_context=service_instance.get("workload-context"),
            created_at=service_instance.get("created-at"),
            updated_at=service_instance.get("updated-at"),
            description=service_instance.get("description"),
            model_invariant_id=service_instance.get("model-invariant-id"),
            model_version_id=service_instance.get("model-version-id"),
            persona_model_version=service_instance.get("persona-model-version"),
            widget_model_id=service_instance.get("widget-model-id"),
            widget_model_version=service_instance.get("widget-model-version"),
            bandwith_total=service_instance.get("bandwidth-total"),
            vhn_portal_url=service_instance.get("vhn-portal-url"),
            service_instance_location_id=service_instance.get("service-instance-location-id"),
            resource_version=service_instance.get("resource-version"),
            selflink=service_instance.get("selflink"),
            orchestration_status=service_instance.get("orchestration-status"),
            input_parameters=service_instance.get("input-parameters")
        )

    @property
    def url(self) -> str:
        """Cloud region object url.

        URL used to call CloudRegion A&AI API

        Returns:
            str: CloudRegion object url

        """
        return (
            f"{self.base_url}{self.api_version}/business/customers/"
            f"customer/{self.customer.global_customer_id}/service-subscriptions/"
            f"service-subscription/{self.service_type}"
        )

    @property
    def relationships(self) -> Iterator[Relationship]:
        """Cloud region relationships.

        Iterate over CloudRegion relationships. Relationship list is given using A&AI API call.

        Returns:
            Iterator[Relationship]: CloudRegion relationship

        """
        response: dict = self.send_message_json(
            "GET", "get service subscription relationships", f"{self.url}/relationship-list"
        )
        return (
            Relationship(
                related_to=relationship.get("related-to"),
                relationship_label=relationship.get("relationship-label"),
                related_link=relationship.get("related-link"),
                relationship_data=relationship.get("relationship-data"),
            )
            for relationship in response.get("relationship", [])
        )

    @property
    def service_instances(self) -> Iterator[ServiceInstance]:
        """Service instances.

        Yields:
            Iterator[ServiceInstance]: Service instance

        """
        for service_instance in \
            self.send_message_json("GET",
                                   (f"Get all service instances for {self.service_type} service "
                                    f"subscription"),
                                   f"{self.url}/service-instances").get("service-instance", []):
            yield ServiceInstance(
                service_subscription=self,
                instance_id=service_instance.get("service-instance-id"),
                instance_name=service_instance.get("service-instance-name"),
                service_type=service_instance.get("service-type"),
                service_role=service_instance.get("service-role"),
                environment_context=service_instance.get("environment-context"),
                workload_context=service_instance.get("workload-context"),
                created_at=service_instance.get("created-at"),
                updated_at=service_instance.get("updated-at"),
                description=service_instance.get("description"),
                model_invariant_id=service_instance.get("model-invariant-id"),
                model_version_id=service_instance.get("model-version-id"),
                persona_model_version=service_instance.get("persona-model-version"),
                widget_model_id=service_instance.get("widget-model-id"),
                widget_model_version=service_instance.get("widget-model-version"),
                bandwith_total=service_instance.get("bandwidth-total"),
                vhn_portal_url=service_instance.get("vhn-portal-url"),
                service_instance_location_id=service_instance.get("service-instance-location-id"),
                resource_version=service_instance.get("resource-version"),
                selflink=service_instance.get("selflink"),
                orchestration_status=service_instance.get("orchestration-status"),
                input_parameters=service_instance.get("input-parameters")
            )

    def get_service_instance_by_id(self, service_instance_id) -> ServiceInstance:
        """Get service instance using it's ID.

        Args:
            service_instance_id (str): ID of the service instance

        Raises:
            ValueError: service subscription has no related service instance with given ID

        Returns:
            ServiceInstance: ServiceInstance object

        """
        return self._get_service_instance_by_filter_parameter(
            "service-instance-id",
            service_instance_id
        )

    def get_service_instance_by_name(self, service_instance_name: str) -> ServiceInstance:
        """Get service instance using it's name.

        Args:
            service_instance_name (str): Name of the service instance

        Raises:
            ValueError: service subscription has no related service instance with given name

        Returns:
            ServiceInstance: ServiceInstance object

        """
        return self._get_service_instance_by_filter_parameter(
            "service-instance-name",
            service_instance_name
        )

    def link_to_cloud_region_and_tenant(self,
                                        cloud_region: "CloudRegion",
                                        tenant: "Tenant") -> None:
        """Create relationship between object and cloud region with tenant.

        Args:
            cloud_region (CloudRegion): Cloud region to link to
            tenant (Tenant): Cloud region tenant to link to
        """
        relationship: Relationship = Relationship(
            related_to="tenant",
            related_link=tenant.url,
            relationship_data=[
                {
                    "relationship-key": "cloud-region.cloud-owner",
                    "relationship-value": cloud_region.cloud_owner,
                },
                {
                    "relationship-key": "cloud-region.cloud-region-id",
                    "relationship-value": cloud_region.cloud_region_id,
                },
                {
                    "relationship-key": "tenant.tenant-id",
                    "relationship-value": tenant.tenant_id,
                },
            ],
            related_to_property=[
                {"property-key": "tenant.tenant-name", "property-value": tenant.name}
            ],
        )
        self.add_relationship(relationship)


class CloudRegion(AaiElement):  # pylint: disable=R0902
    """Cloud region class.

    Represents A&AI cloud region object.
    """

    def __init__(self,
                 cloud_owner: str,
                 cloud_region_id: str,
                 orchestration_disabled: bool,
                 in_maint: bool,
                 *,  # rest of parameters are keyword
                 cloud_type: str = "",
                 owner_defined_type: str = "",
                 cloud_region_version: str = "",
                 identity_url: str = "",
                 cloud_zone: str = "",
                 complex_name: str = "",
                 sriov_automation: str = "",
                 cloud_extra_info: str = "",
                 upgrade_cycle: str = "",
                 resource_version: str = "") -> None:
        """Cloud region object initialization.

        Args:
            cloud_owner (str): Identifies the vendor and cloud name.
            cloud_region_id (str): Identifier used by the vendor for the region.
            orchestration_disabled (bool): Used to indicate whether orchestration is
                enabled for this cloud-region.
            in_maint (bool): Used to indicate whether or not cloud-region object
                is in maintenance mode.
            owner_defined_type (str, optional): Cloud-owner defined type
                indicator (e.g., dcp, lcp). Defaults to "".
            cloud_region_version (str, optional): Software version employed at the site.
                Defaults to "".
            identity_url (str, optional): URL of the keystone identity service. Defaults to "".
            cloud_zone (str, optional): Zone where the cloud is homed. Defaults to "".
            complex_name (str, optional): Complex name for cloud-region instance. Defaults to "".
            sriov_automation (str, optional): Whether the cloud region supports (true) or does
                not support (false) SR-IOV automation. Defaults to "".
            cloud_extra_info (str, optional): ESR inputs extra information about the VIM or Cloud
                which will be decoded by MultiVIM. Defaults to "".
            upgrade_cycle (str, optional): Upgrade cycle for the cloud region.
                For AIC regions upgrade cycle is designated by A,B,C etc. Defaults to "".
            resource_version (str, optional): Used for optimistic concurrency.
                Must be empty on create, valid on update and delete. Defaults to "".

        """
        super().__init__()
        self.cloud_owner = cloud_owner
        self.cloud_region_id = cloud_region_id
        self.orchestration_disabled = orchestration_disabled
        self.in_maint = in_maint
        self.cloud_type = cloud_type
        self.owner_defined_type = owner_defined_type
        self.cloud_region_version = cloud_region_version
        self.identity_url = identity_url
        self.cloud_zone = cloud_zone
        self.complex_name = complex_name
        self.sriov_automation = sriov_automation
        self.cloud_extra_info = cloud_extra_info
        self.upgrade_cycle = upgrade_cycle
        self.resource_version = resource_version

    def __repr__(self) -> str:
        """Cloud region object representation.

        Returns:
            str: Human readable string contains most important information about cloud region.

        """
        return (
            f"CloudRegion(cloud_owner={self.cloud_owner}, cloud_region_id={self.cloud_region_id})"
        )

    @classmethod
    def get_all(cls,
                cloud_owner: str = None,
                cloud_region_id: str = None,
                cloud_type: str = None,
                owner_defined_type: str = None) -> Iterator["CloudRegion"]:
        """Get all A&AI cloud regions.

        Cloud regions can be filtered by 4 parameters: cloud-owner,
        cloud-region-id, cloud-type and owner-defined-type.

        Yields:
            CloudRegion -- CloudRegion object. Can not yield anything
                if cloud region with given filter parameters doesn't exist

        """
        # Filter request parameters - use only these which are not None
        filter_parameters: dict = cls.filter_none_key_values(
            {
                "cloud-owner": cloud_owner,
                "cloud-region-id": cloud_region_id,
                "cloud-type": cloud_type,
                "owner-defined-type": owner_defined_type,
            }
        )
        url: str = (f"{cls.base_url}{cls.api_version}/cloud-infrastructure/"
                    f"cloud-regions?{urlencode(filter_parameters)}")
        response_json: Dict[str, List[Dict[str, Any]]] = cls.send_message_json(
            "GET", "get cloud regions", url
        )
        for cloud_region in response_json.get("cloud-region", []):  # typing: dict
            yield CloudRegion(
                cloud_owner=cloud_region["cloud-owner"],  # required
                cloud_region_id=cloud_region["cloud-region-id"],  # required
                cloud_type=cloud_region.get("cloud-type"),
                owner_defined_type=cloud_region.get("owner-defined-type"),
                cloud_region_version=cloud_region.get("cloud-region-version"),
                identity_url=cloud_region.get("identity_url"),
                cloud_zone=cloud_region.get("cloud-zone"),
                complex_name=cloud_region.get("complex-name"),
                sriov_automation=cloud_region.get("sriov-automation"),
                cloud_extra_info=cloud_region.get("cloud-extra-info"),
                upgrade_cycle=cloud_region.get("upgrade-cycle"),
                orchestration_disabled=cloud_region["orchestration-disabled"],  # required
                in_maint=cloud_region["in-maint"],  # required
                resource_version=cloud_region.get("resource-version"),
            )

    @classmethod
    def get_by_region_id(cls, cloud_region_id: str) -> "CloudRegion":
        """Get CloudRegion object by cloud-region-id field value.

        This method calls A&AI cloud region API filtering them by cloud-region-id field value.

        Raises:
            ValueError: Cloud region with given id does not exist.

        Returns:
            CloudRegion: CloudRegion object with given cloud-region-id.

        """
        try:
            return next(cls.get_all(cloud_region_id=cloud_region_id))
        except StopIteration:
            raise ValueError(f"CloudRegion with {cloud_region_id} cloud-region-id not found")

    @classmethod
    def create(cls,  # pylint: disable=R0914
               cloud_owner: str,
               cloud_region_id: str,
               orchestration_disabled: bool,
               in_maint: bool,
               *,  # rest of parameters are keyword
               cloud_type: str = "",
               owner_defined_type: str = "",
               cloud_region_version: str = "",
               identity_url: str = "",
               cloud_zone: str = "",
               complex_name: str = "",
               sriov_automation: str = "",
               cloud_extra_info: str = "",
               upgrade_cycle: str = "") -> "CloudRegion":
        """Create CloudRegion object.

        Create cloud region with given values.

        Returns:
            CloudRegion: Created cloud region.

        """
        cloud_region: "CloudRegion" = CloudRegion(
            cloud_owner=cloud_owner,
            cloud_region_id=cloud_region_id,
            orchestration_disabled=orchestration_disabled,
            in_maint=in_maint,
            cloud_type=cloud_type,
            owner_defined_type=owner_defined_type,
            cloud_region_version=cloud_region_version,
            identity_url=identity_url,
            cloud_zone=cloud_zone,
            complex_name=complex_name,
            sriov_automation=sriov_automation,
            cloud_extra_info=cloud_extra_info,
            upgrade_cycle=upgrade_cycle,
        )
        url: str = (
            f"{cls.base_url}{cls.api_version}/cloud-infrastructure/cloud-regions/cloud-region/"
            f"{cloud_region.cloud_owner}/{cloud_region.cloud_region_id}"
        )
        cls.send_message(
            "PUT",
            "Create cloud region",
            url,
            data=jinja_env()
            .get_template("cloud_region_create.json.j2")
            .render(cloud_region=cloud_region),
        )
        return cloud_region

    @property
    def url(self) -> str:
        """Cloud region object url.

        URL used to call CloudRegion A&AI API

        Returns:
            str: CloudRegion object url

        """
        return (
            f"{self.base_url}{self.api_version}/cloud-infrastructure/cloud-regions/cloud-region/"
            f"{self.cloud_owner}/{self.cloud_region_id}"
        )

    @property
    def tenants(self) -> Iterator[Tenant]:
        """Tenants iterator.

        Cloud region tenants iterator.

        Returns:
            Iterator[Tenant]: Iterate through cloud region tenants

        """
        response: dict = self.send_message_json("GET", "get tenants", f"{self.url}/tenants")
        return (
            Tenant(
                cloud_region=self,
                tenant_id=tenant["tenant-id"],
                tenant_name=tenant["tenant-name"],
                tenant_context=tenant.get("tenant-context"),
                resource_version=tenant.get("resource-version"),
            )
            for tenant in response.get("tenant", [])
        )

    @property
    def relationships(self) -> Iterator[Relationship]:
        """Cloud region relationships.

        Iterate over CloudRegion relationships. Relationship list is given using A&AI API call.

        Returns:
            Iterator[Relationship]: CloudRegion relationship

        """
        response: dict = self.send_message_json(
            "GET", "get cloud region relationships", f"{self.url}/relationship-list"
        )
        return (
            Relationship(
                related_to=relationship.get("related-to"),
                relationship_label=relationship.get("relationship-label"),
                related_link=relationship.get("related-link"),
                relationship_data=relationship.get("relationship-data"),
            )
            for relationship in response.get("relationship", [])
        )

    @property
    def availability_zones(self) -> Iterator[AvailabilityZone]:
        """Cloud region availability zones.

        Iterate over CloudRegion availability zones. Relationship list is given using A&AI API call.

        Returns:
            Iterator[AvailabilityZone]: CloudRegion availability zone

        """
        response: dict = self.send_message_json(
            "GET", "get cloud region availability zones", f"{self.url}/availability-zones"
        )
        return (
            AvailabilityZone(
                name=availability_zone.get("availability-zone-name"),
                hypervisor_type=availability_zone.get("hypervisor-type"),
                operational_status=availability_zone.get("operational-status"),
                resource_version=availability_zone.get("resource-version")
            )
            for availability_zone in response.get("availability-zone", [])
        )

    @property
    def esr_system_infos(self) -> Iterator[EsrSystemInfo]:
        """Cloud region collection of persistent block-level external system auth info.

        Returns:
            Iterator[EsrSystemInfo]: Cloud region external system address information.

        """
        response: dict = self.send_message_json(
            "GET", "get cloud region external systems info list", f"{self.url}/esr-system-info-list"
        )
        return (
            EsrSystemInfo(
                esr_system_info_id=esr_system_info.get("esr-system-info-id"),
                user_name=esr_system_info.get("user-name"),
                password=esr_system_info.get("password"),
                system_type=esr_system_info.get("system-type"),
                system_name=esr_system_info.get("system-name"),
                esr_type=esr_system_info.get("type"),
                vendor=esr_system_info.get("vendor"),
                version=esr_system_info.get("version"),
                service_url=esr_system_info.get("service-url"),
                protocol=esr_system_info.get("protocol"),
                ssl_cacert=esr_system_info.get("ssl-cacert"),
                ssl_insecure=esr_system_info.get("ssl-insecure"),
                ip_address=esr_system_info.get("ip-address"),
                port=esr_system_info.get("port"),
                cloud_domain=esr_system_info.get("cloud-domain"),
                default_tenant=esr_system_info.get("default-tenant"),
                passive=esr_system_info.get("passive"),
                remote_path=esr_system_info.get("remote-path"),
                system_status=esr_system_info.get("system-status"),
                openstack_region_id=esr_system_info.get("openstack-region-id"),
                resource_version=esr_system_info.get("resource-version"),
            )
            for esr_system_info in response.get("esr-system-info", [])
        )

    def add_tenant(self, tenant_id: str, tenant_name: str, tenant_context: str = None) -> None:
        """Add tenant to cloud region.

        Args:
            tenant_id (str): Unique id relative to the cloud-region.
            tenant_name (str): Readable name of tenant
            tenant_context (str, optional): This field will store
                the tenant context.. Defaults to None.

        """
        self.send_message(
            "PUT",
            "add tenant to cloud region",
            f"{self.url}/tenants/tenant/{tenant_id}",
            data=jinja_env()
            .get_template("cloud_region_add_tenant.json.j2")
            .render(tenant_id=tenant_id, tenant_name=tenant_name, tenant_context=tenant_context),
        )

    def get_tenant(self, tenant_id: str) -> Tenant:
        """Get tenant with provided ID.

        Args:
            tenant_id (str): Tenant ID

        Returns:
            Tenant: Tenant object

        Raises:
            ValueError: Tenant with provided ID doesn't exist

        """
        response: dict = self.send_message_json(
            "GET",
            "get tenants",
            f"{self.url}/tenants/tenant/{tenant_id}",
            exception=ValueError
        )
        return Tenant(
            cloud_region=self,
            tenant_id=response["tenant-id"],
            tenant_name=response["tenant-name"],
            tenant_context=response.get("tenant-context"),
            resource_version=response.get("resource-version"),
        )

    def add_availability_zone(self,
                              availability_zone_name: str,
                              availability_zone_hypervisor_type: str,
                              availability_zone_operational_status: str = None) -> None:
        """Add avaiability zone to cloud region.

        Args:
            availability_zone_name (str): Name of the availability zone.
                Unique across a cloud region
            availability_zone_hypervisor_type (str): Type of hypervisor
            availability_zone_operational_status (str, optional): State that indicates whether
                the availability zone should be used. Defaults to None.
        """
        self.send_message(
            "PUT",
            "Add availability zone to cloud region",
            f"{self.url}/availability-zones/availability-zone/{availability_zone_name}",
            data=jinja_env()
            .get_template("cloud_region_add_availability_zone.json.j2")
            .render(availability_zone_name=availability_zone_name,
                    availability_zone_hypervisor_type=availability_zone_hypervisor_type,
                    availability_zone_operational_status=availability_zone_operational_status)
        )

    def add_esr_system_info(self,  # pylint: disable=R0913, R0914
                            esr_system_info_id: str,
                            user_name: str,
                            password: str,
                            system_type: str,
                            system_name: str = None,
                            esr_type: str = None,
                            vendor: str = None,
                            version: str = None,
                            service_url: str = None,
                            protocol: str = None,
                            ssl_cacert: str = None,
                            ssl_insecure: Optional[bool] = None,
                            ip_address: str = None,
                            port: str = None,
                            cloud_domain: str = None,
                            default_tenant: str = None,
                            passive: Optional[bool] = None,
                            remote_path: str = None,
                            system_status: str = None,
                            openstack_region_id: str = None,
                            resource_version: str = None) -> None:
        """Add external system info to cloud region.

        Args:
            esr_system_info_id (str): Unique ID of esr system info
            user_name (str): username used to access external system
            password (str): password used to access external system
            system_type (str): it could be vim/vnfm/thirdparty-sdnc/
                ems-resource/ems-performance/ems-alarm
            system_name (str, optional): name of external system. Defaults to None.
            esr_type (str, optional): type of external system. Defaults to None.
            vendor (str, optional): vendor of external system. Defaults to None.
            version (str, optional): version of external system. Defaults to None.
            service_url (str, optional): url used to access external system. Defaults to None.
            protocol (str, optional): protocol of third party SDNC,
                for example netconf/snmp. Defaults to None.
            ssl_cacert (str, optional): ca file content if enabled ssl on auth-url.
                Defaults to None.
            ssl_insecure (bool, optional): Whether to verify VIM's certificate. Defaults to True.
            ip_address (str, optional): service IP of ftp server. Defaults to None.
            port (str, optional): service port of ftp server. Defaults to None.
            cloud_domain (str, optional): domain info for authentication. Defaults to None.
            default_tenant (str, optional): default tenant of VIM. Defaults to None.
            passive (bool, optional): ftp passive mode or not. Defaults to False.
            remote_path (str, optional): resource or performance data file path. Defaults to None.
            system_status (str, optional): he status of external system. Defaults to None.
            openstack_region_id (str, optional): OpenStack region ID used by MultiCloud plugin to
                interact with an OpenStack instance. Defaults to None.
        """
        self.send_message(
            "PUT",
            "Add external system info to cloud region",
            f"{self.url}/esr-system-info-list/esr-system-info/{esr_system_info_id}",
            data=jinja_env()
            .get_template("cloud_region_add_esr_system_info.json.j2")
            .render(esr_system_info_id=esr_system_info_id,
                    user_name=user_name,
                    password=password,
                    system_type=system_type,
                    system_name=system_name,
                    esr_type=esr_type,
                    vendor=vendor,
                    version=version,
                    service_url=service_url,
                    protocol=protocol,
                    ssl_cacert=ssl_cacert,
                    ssl_insecure=ssl_insecure,
                    ip_address=ip_address,
                    port=port,
                    cloud_domain=cloud_domain,
                    default_tenant=default_tenant,
                    passive=passive,
                    remote_path=remote_path,
                    system_status=system_status,
                    openstack_region_id=openstack_region_id,
                    resource_version=resource_version)
        )

    def register_to_multicloud(self, default_tenant: str = None) -> None:
        """Register cloud to multicloud using MSB API.

        Args:
            default_tenant (str, optional): Default tenant. Defaults to None.
        """
        Multicloud.register_vim(self.cloud_owner, self.cloud_region_id, default_tenant)

    def unregister_from_multicloud(self) -> None:
        """Unregister cloud from mutlicloud."""
        Multicloud.unregister_vim(self.cloud_owner, self.cloud_region_id)

    def delete(self) -> None:
        """Delete cloud region."""
        self.send_message(
            "DELETE",
            f"Delete cloud region {self.cloud_region_id}",
            self.url,
            params={"resource-version": self.resource_version}
        )

    def link_to_complex(self, complex_object: Complex) -> None:
        """Link cloud region to comples.

        It creates relationhip object and add it into cloud region.
        """
        relationship = Relationship(
            related_to="complex",
            related_link=(f"aai/v13/cloud-infrastructure/complexes/"
                          f"complex/{complex_object.physical_location_id}"),
            relationship_data={
                "relationship-key": "complex.physical-location-id",
                "relationship-value": f"{complex_object.physical_location_id}",
            },
            relationship_label="org.onap.relationships.inventory.LocatedIn",
        )
        self.add_relationship(relationship)


class Customer(AaiElement):
    """Customer class."""

    def __init__(self,
                 global_customer_id: str,
                 subscriber_name: str,
                 subscriber_type: str,
                 resource_version: str = None) -> None:
        """Initialize Customer class object.

        Args:
            global_customer_id (str): Global customer id used across ONAP to
                uniquely identify customer.
            subscriber_name (str): Subscriber name, an alternate way to retrieve a customer.
            subscriber_type (str): Subscriber type, a way to provide VID with
                only the INFRA customers.
            resource_version (str, optional): Used for optimistic concurrency.
                Must be empty on create, valid on update
                and delete. Defaults to None.

        """
        super().__init__()
        self.global_customer_id: str = global_customer_id
        self.subscriber_name: str = subscriber_name
        self.subscriber_type: str = subscriber_type
        self.resource_version: str = resource_version

    def __repr__(self) -> str:  # noqa
        """Customer description.

        Returns:
            str: Customer object description

        """
        return (f"Customer(global_customer_id={self.global_customer_id}, "
                f"subscriber_name={self.subscriber_name}, "
                f"subscriber_type={self.subscriber_type}, "
                f"resource_version={self.resource_version})")

    @classmethod
    def get_all(cls,
                global_customer_id: str = None,
                subscriber_name: str = None,
                subscriber_type: str = None) -> Iterator["Customer"]:
        """Get all customers.

        Call an API to retrieve all customers. It can be filtered
            by global-customer-id, subscriber-name and/or subsriber-type.

        Args:
            global_customer_id (str): global-customer-id to filer customers by. Defaults to None.
            subscriber_name (str): subscriber-name to filter customers by. Defaults to None.
            subscriber_type (str): subscriber-type to filter customers by. Defaults to None.

        """
        filter_parameters: dict = cls.filter_none_key_values(
            {
                "global-customer-id": global_customer_id,
                "subscriber-name": subscriber_name,
                "subscriber-type": subscriber_type,
            }
        )
        url: str = (f"{cls.base_url}{cls.api_version}/business/customers?"
                    f"{urlencode(filter_parameters)}")
        for customer in cls.send_message_json("GET", "get customers", url).get("customer", []):
            yield Customer(
                global_customer_id=customer["global-customer-id"],
                subscriber_name=customer["subscriber-name"],
                subscriber_type=customer["subscriber-type"],
                resource_version=customer["resource-version"],
            )

    @classmethod
    def get_by_global_customer_id(cls, global_customer_id: str) -> "Customer":
        """Get customer by it's global customer id.

        Args:
            global_customer_id (str): global customer ID

        Returns:
            Customer: Customer with given global_customer_id

        Raises:
            ValueError: Customer with given global_customer_id doesn't exist

        """
        response: dict = cls.send_message_json(
            "GET",
            f"Get {global_customer_id} customer",
            f"{cls.base_url}{cls.api_version}/business/customers/customer/{global_customer_id}",
            exception=ValueError
        )
        return Customer(
            global_customer_id=response["global-customer-id"],
            subscriber_name=response["subscriber-name"],
            subscriber_type=response["subscriber-type"],
            resource_version=response["resource-version"],
        )

    @classmethod
    def create(cls,
               global_customer_id: str,
               subscriber_name: str,
               subscriber_type: str) -> "Customer":
        """Create customer.

        Args:
            global_customer_id (str): Global customer id used across ONAP
                to uniquely identify customer.
            subscriber_name (str): Subscriber name, an alternate way
                to retrieve a customer.
            subscriber_type (str): Subscriber type, a way to provide
                VID with only the INFRA customers.

        Returns:
            Customer: Customer object.

        """
        url: str = (
            f"{cls.base_url}{cls.api_version}/business/customers/"
            f"customer/{global_customer_id}"
        )
        cls.send_message(
            "PUT",
            "declare customer",
            url,
            data=jinja_env()
            .get_template("customer_create.json.j2")
            .render(
                global_customer_id=global_customer_id,
                subscriber_name=subscriber_name,
                subscriber_type=subscriber_type,
            ),
        )
        response: dict = cls.send_message_json(
            "GET", "get created customer", url
        )  # Call API one more time to get Customer's resource version
        return Customer(
            global_customer_id=response["global-customer-id"],
            subscriber_name=response["subscriber-name"],
            subscriber_type=response["subscriber-type"],
            resource_version=response["resource-version"],
        )

    @property
    def url(self) -> str:
        """Return customer object url.

        Unique url address to get customer's data.

        Returns:
            str: Customer object url

        """
        return (
            f"{self.base_url}{self.api_version}/business/customers/customer/"
            f"{self.global_customer_id}?resource-version={self.resource_version}"
        )

    @property
    def service_subscriptions(self) -> Iterator[ServiceSubscription]:
        """Service subscriptions of customer resource.

        Yields:
            ServiceSubscription: ServiceSubscription object

        """
        response: dict = self.send_message_json(
            "GET",
            "get customer service subscriptions",
            f"{self.base_url}{self.api_version}/business/customers/"
            f"customer/{self.global_customer_id}/service-subscriptions"
        )
        for service_subscription in response.get("service-subscription", []):
            yield ServiceSubscription(
                service_type=service_subscription.get("service-type"),
                resource_version=service_subscription.get("resource-version"),
                customer=self
            )

    def subscribe_service(self, service: SdcService):
        """Create SDC Service subscription.

        Args:
            service (SdcService): SdcService object to subscribe.

        Raises:
            ValueError: Request response with HTTP error code

        """
        self.send_message(
            "PUT",
            "Create service subscription",
            (f"{self.base_url}{self.api_version}/business/customers/"
             f"customer/{self.global_customer_id}/service-subscriptions/"
             f"service-subscription/{service.name}"),
            data=jinja_env()
            .get_template("customer_service_subscription_create.json.j2")
            .render(
                service_id=service.unique_uuid,
            ),
            exception=ValueError
        )


class OwningEntity(AaiElement):
    """Owning entity class."""

    def __init__(self, name: str, owning_entity_id: str, resource_version: str) -> None:
        """Owning entity object initialization.

        Args:
            name (str): Owning entity name
            owning_entity_id (str): owning entity ID
            resource_version (str): resource version
        """
        super().__init__()
        self.name: str = name
        self.owning_entity_id: str = owning_entity_id
        self.resource_version: str = resource_version

    def __repr__(self) -> str:
        """Owning entity object representation.

        Returns:
            str: Owning entity object representation

        """
        return f"OwningEntity(name={self.name}, owning_entity_id={self.owning_entity_id})"

    @property
    def url(self) -> str:
        """Owning entity object url.

        Returns:
            str: Url

        """
        return (f"{self.base_url}{self.api_version}/business/owning-entities/owning-entity/"
                f"{self.owning_entity_id}?resource-version={self.resource_version}")

    @classmethod
    def get_all(cls) -> Iterator["OwningEntity"]:
        """Get all owning entities.

        Yields:
            OwningEntity: OwningEntity object

        """
        url: str = f"{cls.base_url}{cls.api_version}/business/owning-entities"
        for owning_entity in cls.send_message_json("GET",
                                                   "Get A&AI owning entities",
                                                   url).get("owning-entity", []):
            yield cls(
                owning_entity.get("owning-entity-name"),
                owning_entity.get("owning-entity-id"),
                owning_entity.get("resource-version")
            )

    @classmethod
    def get_by_owning_entity_id(cls, owning_entity_id: str) -> "OwningEntity":
        """Get owning entity by it's ID.

        Args:
            owning_entity_id (str): owning entity object id

        Returns:
            OwningEntity: OwningEntity object

        """
        response: dict = cls.send_message_json(
            "GET",
            "Get A&AI owning entity",
            (f"{cls.base_url}{cls.api_version}/business/owning-entities/"
             f"owning-entity/{owning_entity_id}"),
            exception=ValueError
        )
        return cls(
            response.get("owning-entity-name"),
            response.get("owning-entity-id"),
            response.get("resource-version")
        )

    @classmethod
    def get_by_owning_entity_name(cls, owning_entity_name: str) -> "OwningEntity":
        """Get owning entity resource by it's name.

        Raises:
            ValueError: Owning entity with given name doesn't exist

        Returns:
            OwningEntity: Owning entity with given name

        """
        for owning_entity in cls.get_all():
            if owning_entity.name == owning_entity_name:
                return owning_entity
        raise ValueError

    @classmethod
    def create(cls, name: str, owning_entity_id: str = None) -> "OwningEntity":
        """Create owning entity A&AI resource.

        Args:
            name (str): owning entity name
            owning_entity_id (str): owning entity ID. Defaults to None.

        Raises:
            ValueError: request response with HTTP error code

        Returns:
            OwningEntity: Created OwningEntity object

        """
        if not owning_entity_id:
            owning_entity_id = str(uuid4())
        cls.send_message(
            "PUT",
            "Declare A&AI owning entity",
            (f"{cls.base_url}{cls.api_version}/business/owning-entities/"
             f"owning-entity/{owning_entity_id}"),
            data=jinja_env().get_template("aai_owning_entity_create.json.j2").render(
                owning_entity_name=name,
                owning_entity_id=owning_entity_id
            ),
            exception=ValueError
        )
        return cls.get_by_owning_entity_id(owning_entity_id)


class Model(AaiElement):
    """Model resource class."""

    def __init__(self, invariant_id: str, model_type: str, resource_version: str) -> None:
        """Model object initialization.

        Args:
            invariant_id (str): invariant id
            model_type (str): model type
            resource_version (str): resource version

        """
        super().__init__()
        self.invariant_id: str = invariant_id
        self.model_type: str = model_type
        self.resource_version: str = resource_version

    def __repr__(self) -> str:
        """Model object representation.

        Returns:
            str: model object representation

        """
        return (f"Model(invatiant_id={self.invariant_id}, "
                f"model_type={self.model_type}, "
                f"resource_version={self.resource_version}")

    @property
    def url(self) -> str:
        """Model instance url.

        Returns:
            str: Model's url

        """
        return (f"{self.base_url}{self.api_version}/service-design-and-creation/models/"
                f"model/{self.invariant_id}?resource-version={self.resource_version}")

    @classmethod
    def get_all(cls) -> Iterator["Model"]:
        """Get all models.

        Yields:
            Model: Model object

        """
        for model in cls.send_message_json("GET",
                                           "Get A&AI sdc models",
                                           (f"{cls.base_url}{cls.api_version}/"
                                            "service-design-and-creation/models")).get("model",
                                                                                       []):
            yield Model(
                invariant_id=model.get("model-invariant-id"),
                model_type=model.get("model-type"),
                resource_version=model.get("resource-version")
            )
