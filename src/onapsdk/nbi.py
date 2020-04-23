
import logging
from uuid import uuid4

from onapsdk.aai_element import Customer
from onapsdk.onap_service import OnapService, requests
from onapsdk.utils import get_zulu_time_isoformat
from onapsdk.utils.jinja import jinja_env


class Nbi(OnapService):

    __logger: logging.Logger = logging.getLogger(__name__)

    base_url = "https://nbi.api.simpledemo.onap.org:30274"
    api_version = "/nbi/api/v4"

    @classmethod
    def is_status_ok(cls) -> bool:
        try:
            cls.send_message(
                "GET",
                "Check NBI status",
                f"{cls.base_url}{cls.api_version}/status",
                exception=ValueError
            )
        except ValueError:
            cls.__logger.error("NBI Status check returns error")
            return False
        return True


class ServiceSpecification(Nbi):

    def __init__(self, unique_id: str, name: str, invariant_uuid: str, category: str, distribution_status: str, version: str, lifecycle_status: str) -> None:
        self.unique_id: str = unique_id
        self.name: str = name
        self.invariant_uuid: str = invariant_uuid
        self.category: str = category
        self.distribution_status: str = distribution_status
        self.version: str = version
        self.lifecycle_status: str = lifecycle_status    

    def __repr__(self) -> str:
        return (f"ServiceSpecification(unique_id={self.unique_id}, name={self.name}, invariant_uuid={self.invariant_uuid}, "
                f"category={self.category}, distribution_status={self.distribution_status}, version={self.version}, "
                f"lifecycle_status={self.lifecycle_status}")

    @classmethod
    def get_all(cls):
        for service_specification in cls.send_message_json(
            "GET",
            "Get service specifications from NBI",
            f"{cls.base_url}{cls.api_version}/serviceSpecification"
        ):
            yield ServiceSpecification(
                service_specification.get("id"),
                service_specification.get("name"),
                service_specification.get("invariantUUID"),
                service_specification.get("category"),
                service_specification.get("distributionStatus"),
                service_specification.get("version"),
                service_specification.get("lifecycleStatus"),
            )


class Service(Nbi):

    @classmethod
    def get_all(cls):
        return cls.send_message_json(
            "GET",
            "Get service instances from NBI",
            f"{cls.base_url}{cls.api_version}/service"
        )


class ServiceOrder(Nbi):

    def __init__(self, unique_id: str, href: str, priority: str, description: str, category: str,
                 external_id: str, customer: Customer, service_specification: ServiceSpecification):
        super().__init__()
        self.unique_id: str = unique_id
        self.href: str = href
        self.priority: str = priority
        self.category: str = category
        self.description: str = description
        self.customer: Customer = customer
        self.service_specification: ServiceSpecification = service_specification

    @classmethod
    def get_all(cls):
        return cls.send_message_json(
            "GET",
            "Get all service orders",
            f"{cls.base_url}{cls.api_version}/serviceOrder"
        )

    @classmethod
    def create(cls,
               customer: Customer,
               service_specification: ServiceSpecification,
               name: str = None,
               external_id: str = None) -> "ServiceOrder":
        if external_id is None:
            external_id = str(uuid4())
        if name is None:
            name = str(uuid4())
        response: dict = cls.send_message_json(
            "POST",
            "Add service instance via ServiceOrder API",
            f"{cls.base_url}{cls.api_version}/serviceOrder",
            data=jinja_env()
            .get_template("nbi_service_order_create.json.j2")
            .render(
                customer=customer,
                service_specification=service_specification,
                service_instance_name=name,
                external_id=external_id,
                request_time=get_zulu_time_isoformat()
            )
        )
        return cls(
            unique_id=response.get("id"),
            href=response.get("href"),
            priority=response.get("priority"),
            description=response.get("description"),
            category=response.get("category"),
            external_id=response.get("externalId"),
            customer=customer,
            service_specification=service_specification
        )

    @classmethod
    def get_by_id(cls,
                  unique_id: str) -> "ServiceOrder":
        return cls.send_message_json(
            "GET",
            f"Get service order with {unique_id} ID",
            f"{cls.base_url}{cls.api_version}/serviceOrder/{unique_id}")

    @property
    def completed(self) -> bool:
        pass
