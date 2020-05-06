#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Instantion module."""
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, Iterator
from uuid import uuid4

from onapsdk.aai_element import (
    CloudRegion,
    Customer,
    OwningEntity,
    ServiceInstance as AaiServiceInstance,
    ServiceSubscription,
    Tenant
)
from onapsdk.onap_service import OnapService
from onapsdk.service import Service as SdcService, Vnf, VfModule
from onapsdk.utils.jinja import jinja_env
from onapsdk.utils.headers_creator import headers_so_creator, headers_sdnc_creator
from onapsdk.vid import LineOfBusiness, Platform, Project


@dataclass
class VnfParameter:
    """Class to store vnf parameter used for preload.

    Contains two values: name of vnf parameter and it's value
    """

    name: str
    value: str


class VfModulePreload(OnapService):
    """Class to upload vf module preload."""

    headers: Dict[str, str] = headers_sdnc_creator(OnapService.headers)

    @classmethod
    def upload_vf_module_preload(cls,
                                 vnf_instance: "VnfInstance",
                                 vf_module_instance_name: str,
                                 vf_module: VfModule,
                                 vnf_parameters: Iterable[VnfParameter] = None,
                                 use_vnf_api=False):
        if use_vnf_api:
            url: str = ("https://sdnc.api.simpledemo.onap.org:30267/restconf/operations/"
                        "VNF-API:preload-vnf-topology-operation")
        else:
            url: str = ("https://sdnc.api.simpledemo.onap.org:30267/restconf/operations/"
                        "VNF-API:preload-vnf-topology-operation")
        cls.send_message_json(
            "POST",
            "Upload VF module preload using VNF-API",
            url,
            data=jinja_env().get_template("instantiate_vf_module_ala_carte_upload_preload.json.j2").
            render(
                vnf_instance=vnf_instance,
                vf_module_instance_name=vf_module_instance_name,
                vf_module=vf_module,
                vnf_parameters=vnf_parameters if vnf_parameters else []
            ),
            exception=ValueError
        )

    # @classmethod
    # def upload_vf_module_vnf_api_preload(cls,
    #                                      vnf_instance: "VnfInstance",
    #                                      vf_module_instance_name: str,
    #                                      vf_module: VfModule,
    #                                      vnf_parameters: Iterable[VnfParameter] = None):
    #     """Upload VF module preload using VNF API.

    #     Args:
    #         vnf_instantiation ([type]): VnfInstantiation class object
    #         vf_module_instance_name (str): Name of VF module to upload preload
    #         vf_module (VfModule): VfModule object class
    #         vnf_parameters (Iterable[VnfParameter], optional): VnfParameter iterator to upload.
    #             Defaults to None.

    #     Raises:
    #         ValueError: upload request returns error HTTP code

    #     """
    #     cls.send_message_json(
    #         "POST",
    #         "Upload VF module preload using VNF-API",
    #         ("https://sdnc.api.simpledemo.onap.org:30267/restconf/operations/"
    #          "VNF-API:preload-vnf-topology-operation"),
    #         data=jinja_env().get_template("instantiate_vf_module_ala_carte_upload_preload.json.j2").
    #         render(
    #             vnf_instance=vnf_instance,
    #             vf_module_instance_name=vf_module_instance_name,
    #             vf_module=vf_module,
    #             vnf_parameters=vnf_parameters if vnf_parameters else []
    #         ),
    #         exception=ValueError
    #     )

    # @classmethod
    # def upload_vf_module_gr_api_preload(cls,
    #                                      vnf_instance: "VnfInstance",
    #                                      vf_module_instance_name: str,
    #                                      vf_module: VfModule,
    #                                      vnf_parameters: Iterable[VnfParameter] = None):
    #     """Upload VF module preload using GR API.

    #     Args:
    #         vnf_instantiation ([type]): VnfInstantiation class object
    #         vf_module_instance_name (str): Name of VF module to upload preload
    #         vf_module (VfModule): VfModule object class
    #         vnf_parameters (Iterable[VnfParameter], optional): VnfParameter iterator to upload.
    #             Defaults to None.

    #     Raises:
    #         ValueError: upload request returns error HTTP code

    #     """
    #     cls.send_message_json(
    #         "POST",
    #         "Upload VF module preload using GR-API",
    #         ("https://sdnc.api.simpledemo.onap.org:30267/restconf/operations/"
    #          "GENERIC_RESOURCE_API:preload-vnf-topology-operation"),
    #         data=jinja_env().get_template("instantiate_vf_module_ala_carte_upload_preload.json.j2").
    #         render(
    #             vnf_instance=vnf_instance,
    #             vf_module_instance_name=vf_module_instance_name,
    #             vf_module=vf_module,
    #             vnf_parameters=vnf_parameters if vnf_parameters else []
    #         ),
    #         exception=ValueError
    #     )


class Instantiation(OnapService, ABC):
    """Abstract class used for instantiation."""

    def __init__(self,  # pylint: disable=R0913
                 name: str,
                 request_id: str,
                 instance_id: str) -> None:
        """Instantiate object initialization.

        Initializator used by classes inherited from this abstract class.

        Args:
            name (str): instantiated object name
            request_id (str): request ID
            instance_id (str): instance ID
        """
        super().__init__()
        self.name: str = name
        self.request_id: str = request_id
        self.instance_id: str = instance_id

    class StatusEnum(Enum):
        """Status enum.

        Store possible statuses for instantiation:
            - IN_PROGRESS,
            - FAILED,
            - COMPLETE.
        If instantiation has status which is not covered by these values
            UNKNOWN value is used.

        """

        IN_PROGRESS = "IN_PROGRESS"
        FAILED = "FAILED"
        COMPLETED = "COMPLETE"
        UNKNOWN = "UNKNOWN"

    @property
    def status(self) -> "StatusEnum":
        """Object instantiation status.

        It's populated by call SO orchestation request endpoint.

        Returns:
            StatusEnum: Instantiation status.

        """
        response: dict = self.send_message_json(
            "GET",
            f"Check {self.name} service instantiation status",
            ("http://so.api.simpledemo.onap.org:30277/onap/so/infra/"
             f"orchestrationRequests/v7/{self.request_id}"),
            headers=headers_so_creator(OnapService.headers)
        )
        try:
            return self.StatusEnum(response["request"]["requestStatus"]["requestState"])
        except ValueError:
            return self.StatusEnum.UNKNOWN

    @property
    def finished(self) -> bool:
        """Store an information if instantion is finished or not.

        Instantiation is finished if it's status is COMPLETED or FAILED.

        Returns:
            bool: True if instantiation is finished, False otherwise.

        """
        return self.status in [self.StatusEnum.COMPLETED, self.StatusEnum.FAILED]


class VfModuleInstantiation(Instantiation):
    """VF module instantiation class."""

    headers = headers_so_creator(OnapService.headers)

    def __init__(self,  # pylint: disable=R0913
                 name: str,
                 request_id: str,
                 instance_id: str,
                 vf_module: VfModule) -> None:
        """Initialize class object.

        Args:
            name (str): vf module name
            request_id (str): request ID
            instance_id (str): instance ID
            vnf_instantiation (VnfInstantiation): VNF instantiation class object
            vf_module (VfModule): VF module used for instantiation
        """
        super().__init__(name, request_id, instance_id)
        self.vf_module: VfModule = vf_module

    @classmethod
    def instantiate_ala_carte(cls,
                              vf_module,
                              vnf_instance,
                              vf_module_instance_name: str = None,
                              use_vnf_api=False,
                              vnf_parameters: Iterable[VnfParameter] = None
                              ) -> "VfModuleInstantiation":
        """Instantiate VF module.

        Iterate throught vf modules from service Tosca file and instantiate vf modules.

        Args:
            vf_module_instance_name_factory (str, optional): Factory to create VF module names.
                It's going to be a prefix of name. Index of vf module in Tosca file will be
                added to it.
                If no value is provided it's going to be
                "Python_ONAP_SDK_vf_module_service_instance_{str(uuid4())}".
                Defaults to None.
            use_vnf_api (bool, optional): Flague which determines if VNF_API or
                GR_API should be used.
                Defaults to False.
            vnf_parameters (Iterable[VnfParameter], optional): Parameters which are
                going to be used in preload upload for vf modules. Defaults to None.

        Raises:
            AttributeError: VNF is not successfully instantiated.
            ValueError: VF module instnatiation request returns HTTP error code.

        Yields:
            Iterator[VfModuleInstantiation]: VfModuleInstantiation class object.

        """
        sdc_service: SdcService = vnf_instance.service_instance.service_subscription.sdc_service
        if vf_module_instance_name is None:
            vf_module_instance_name = \
                f"Python_ONAP_SDK_vf_module_instance_{str(uuid4())}"
        VfModulePreload.upload_vf_module_preload(
            vnf_instance,
            vf_module_instance_name,
            vf_module,
            vnf_parameters,
            use_vnf_api=use_vnf_api
        )
        response: dict = cls.send_message_json(
            "POST",
            (f"Instantiate {sdc_service.name} "
                f"service vf module {vf_module.name}"),
            (f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/serviceInstantiation/v7/"
                f"serviceInstances/{vnf_instance.service_instance.instance_id}/vnfs/"
                f"{vnf_instance.vnf_id}/vfModules"),
            data=jinja_env().get_template("instantiate_vf_module_ala_carte.json.j2").
            render(
                vf_module_instance_name=vf_module_instance_name,
                vf_module=vf_module,
                service=sdc_service,
                cloud_region=vnf_instance.service_instance.service_subscription.cloud_region,
                tenant=vnf_instance.service_instance.service_subscription.tenant,
                vnf_instance=vnf_instance,
                use_vnf_api=use_vnf_api
            ),
            exception=ValueError
        )
        return VfModuleInstantiation(
            name=vf_module_instance_name,
            request_id=response["requestReferences"].get("requestId"),
            instance_id=response["requestReferences"].get("instanceId"),
            vf_module=vf_module
        )


class VnfInstantiation(Instantiation):
    """VNF instantiation class."""

    headers = headers_so_creator(OnapService.headers)

    def __init__(self,  # pylint: disable=R0913
                 name: str,
                 request_id: str,
                 instance_id: str,
                 line_of_business: LineOfBusiness,
                 platform: Platform,
                 vnf: Vnf) -> None:
        """Class VnfInstantion object initialization.

        Args:
            name (str): VNF name
            request_id (str): request ID
            instance_id (str): instance ID
            service_instantiation ([type]): ServiceInstantiation class object
            line_of_business (LineOfBusiness): LineOfBusiness class object
            platform (Platform): Platform class object
            vnf (Vnf): Vnf class object
        """
        super().__init__(name, request_id, instance_id)
        self.line_of_business = line_of_business
        self.platform = platform
        self.vnf = vnf

    @classmethod
    def create_from_request_response(cls, request_response: dict) -> "VnfInstantiation":
        """Create VNF instantiation object based on request details.

        Raises:
            ValueError: Service related with given object doesn't exist
            ValueError: No ServiceInstantiation related with given VNF instantiation
            ValueError: VNF related with given object doesn't exist
            ValueError: Invalid dictionary - couldn't create VnfInstantiation object

        Returns:
            VnfInstantiation: VnfInstantiation object

        """
        if request_response.get("request", {}).get("requestScope") == "vnf" and \
            request_response.get("request", {}).get("requestType") == "createInstance":
            service: SdcService = None
            service_instantiation: "ServiceInstantiation" = None
            for related_instance in request_response.get("request", {}).get("requestDetails", {})\
                    .get("relatedInstanceList", []):
                if related_instance.get("relatedInstance", {}).get("modelInfo", {})\
                        .get("modelType") == "service":
                    service = SdcService(related_instance.get("relatedInstance", {})\
                        .get("modelInfo", {}).get("modelName"))
                    service_instantiation = ServiceInstantiation.get_by_service_instance_id(\
                        related_instance.get("relatedInstance", {}).get("instanceId"))
            if not service:
                raise ValueError("No related service in Vnf instance details response")
            if not service_instantiation:
                raise ValueError("No related service instantiation in Vnf details response")
            vnf: Vnf = None
            for service_vnf in service.vnfs:
                if service_vnf.name == request_response.get("request", {})\
                    .get("requestDetails", {}).get("modelInfo", {}).get("modelCustomizationName"):
                    vnf = service_vnf
            if not vnf:
                raise ValueError("No vnf in service vnfs list")
            return cls(
                name=request_response.get("request", {}).get("requestDetails", {})\
                    .get("instanceReferences", {}).get("vnfInstanceName"),
                request_id=request_response.get("request", {}).get("requestId"),
                instance_id=request_response.get("request", {}).get("requestDetails", {})\
                    .get("instanceReferences", {}).get("vnfInstanceId"),
                line_of_business=LineOfBusiness.create(request_response.get("request", {})\
                    .get("requestDetails", {}).get("lineOfBusiness", {}).get("lineOfBusinessName")),
                platform=Platform.create(request_response.get("request", {})\
                    .get("requestDetails", {}).get("platform", {}).get("platformName")),
                vnf=vnf
            )
        raise ValueError("Invalid vnf instantions request dictionary")

    @classmethod
    def get_by_vnf_instance_name(cls, vnf_instance_name: str) -> "VnfInstantiation":
        """Get VNF instantiation request by instance name.

        Raises:
            ValueError: Vnf instance with given name doesn't exist

        Returns:
            VnfInstantiation: Vnf instantiation request object

        """
        response: dict = cls.send_message_json(
            "GET",
            f"Check {vnf_instance_name} service instantiation status",
            (f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/orchestrationRequests/v7?"
             f"filter=vnfInstanceName:EQUALS:{vnf_instance_name}"),
            headers=headers_so_creator(OnapService.headers)
        )
        if not response.get("requestList", []):
            raise ValueError("Vnf instance doesn't exist")
        for details in response["requestList"]:
            return cls.create_from_request_response(details)
        raise ValueError("No createInstance request found")

    # def instantiate_vf_module(self,
    #                           vf_module_instance_name_factory: str = None,
    #                           use_vnf_api=True,
    #                           vnf_parameters: Iterable[VnfParameter] = None
    #                           ) -> Iterator[VfModuleInstantiation]:
    #     """Instantiate VF modules.

    #     Iterate throught vf modules from service Tosca file and instantiate vf modules.

    #     Args:
    #         vf_module_instance_name_factory (str, optional): Factory to create VF module names.
    #             It's going to be a prefix of name. Index of vf module in Tosca file will be
    #             added to it.
    #             If no value is provided it's going to be
    #             "Python_ONAP_SDK_vf_module_service_instance_{str(uuid4())}".
    #             Defaults to None.
    #         use_vnf_api (bool, optional): Flague which determines if VNF_API or
    #             GR_API should be used.
    #             Defaults to True.
    #         vnf_parameters (Iterable[VnfParameter], optional): Parameters which are
    #             going to be used in preload upload for vf modules. Defaults to None.

    #     Raises:
    #         AttributeError: VNF is not successfully instantiated.
    #         ValueError: VF module instnatiation request returns HTTP error code.

    #     Yields:
    #         Iterator[VfModuleInstantiation]: VfModuleInstantiation class object.

    #     """
    #     if self.status != self.StatusEnum.COMPLETED:
    #         raise AttributeError("VNF is successfully instantiated")
    #     if not self.service_instantiation.sdc_service.vf_modules:
    #         self._logger.info("No vf modules to instantiate")
    #         return
    #     if vf_module_instance_name_factory is None:
    #         vf_module_instance_name_factory = \
    #             f"Python_ONAP_SDK_vf_module_service_instance_{str(uuid4())}_"
    #     for index, vf_module in enumerate(self.service_instantiation.sdc_service.vf_modules):
    #         vf_module_instance_name: str = f"{vf_module_instance_name_factory}{index}"
    #         if use_vnf_api:
    #             VfModulePreload.upload_vf_module_vnf_api_preload(
    #                 self,
    #                 vf_module_instance_name,
    #                 vf_module,
    #                 vnf_parameters
    #             )
    #         else:
    #             VfModulePreload.upload_vf_module_gr_api_preload(
    #                 self,
    #                 vf_module_instance_name,
    #                 vf_module,
    #                 vnf_parameters
    #             )
    #         response: dict = self.send_message_json(
    #             "POST",
    #             (f"Instantiate {self.service_instantiation.sdc_service.name} "
    #              f"service vf module {vf_module.name}"),
    #             (f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/serviceInstantiation/v7/"
    #              f"serviceInstances/{self.service_instantiation.instance_id}/vnfs/"
    #              f"{self.instance_id}/vfModules"),
    #             data=jinja_env().get_template("instantiate_vf_module_ala_carte.json.j2").
    #             render(
    #                 vf_module_instance_name=vf_module_instance_name,
    #                 vf_module=vf_module,
    #                 service=self.service_instantiation.sdc_service,
    #                 cloud_region=self.service_instantiation.cloud_region,
    #                 tenant=self.service_instantiation.tenant,
    #                 customer=self.service_instantiation.customer,
    #                 service_instance=self.service_instantiation,
    #                 vnf=self.vnf,
    #                 vnf_instance=self,
    #                 use_vnf_api=use_vnf_api
    #             ),
    #             exception=ValueError
    #         )
    #         yield VfModuleInstantiation(
    #             name=vf_module_instance_name,
    #             request_id=response["requestReferences"].get("requestId"),
    #             instance_id=response["requestReferences"].get("instanceId"),
    #             vnf_instantiation=self,
    #             vf_module=vf_module
    #         )

    @classmethod
    def instantiate_ala_carte(cls,
                              aai_service_instance: AaiServiceInstance,
                              vnf: Vnf,
                              line_of_business: LineOfBusiness,
                              platform: Platform,
                              vnf_instance_name: str = None,
                              use_vnf_api: bool = True):
        sdc_service: SdcService = aai_service_instance.service_subscription.sdc_service
        if vnf_instance_name is None:
            vnf_instance_name = \
                f"Python_ONAP_SDK_vnf_instance_{str(uuid4())}"
        response: dict = cls.send_message_json(
            "POST",
            f"Instantiate {aai_service_instance.service_subscription.sdc_service.name} service vnf {vnf.name}",
            (f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/serviceInstantiation/v7/"
                f"serviceInstances/{aai_service_instance.instance_id}/vnfs"),
            data=jinja_env().get_template("instantiate_vnf_ala_carte.json.j2").
            render(
                vnf_service_instance_name=vnf_instance_name,
                vnf=vnf,
                service=sdc_service,
                cloud_region=aai_service_instance.service_subscription.cloud_region,
                tenant=aai_service_instance.service_subscription.tenant,
                line_of_business=line_of_business,
                platform=platform,
                service_instance=aai_service_instance,
                use_vnf_api=use_vnf_api
            ),
            headers=headers_so_creator(OnapService.headers),
            exception=ValueError
        )
        return VnfInstantiation(
            name=vnf_instance_name,
            request_id=response["requestReferences"]["requestId"],
            instance_id=response["requestReferences"]["instanceId"],
            line_of_business=line_of_business,
            platform=platform,
            vnf=vnf
        )

class ServiceInstantiation(Instantiation):  # pylint: disable=R0913, R0902
    """Service instantiation class."""

    def __init__(self,  # pylint: disable=R0913
                 name: str,
                 request_id: str,
                 instance_id: str,
                 sdc_service: SdcService,
                 cloud_region: CloudRegion,
                 tenant: Tenant,
                 customer: Customer,
                 owning_entity: OwningEntity,
                 project: Project) -> None:
        """Class ServiceInstantiation object initialization.

        Args:
            name (str): service instance name
            request_id (str): service instantiation request ID
            instance_id (str): service instantiation ID
            sdc_service (SdcService): SdcService class object
            cloud_region (CloudRegion): CloudRegion class object
            tenant (Tenant): Tenant class object
            customer (Customer): Customer class object
            owning_entity (OwningEntity): OwningEntity class object
            project (Project): Project class object

        """
        super().__init__(name, request_id, instance_id)
        self.sdc_service = sdc_service
        self.cloud_region = cloud_region
        self.tenant = tenant
        self.customer = customer
        self.owning_entity = owning_entity
        self.project = project

    @classmethod
    def get_by_service_instance_id(cls, service_instance_id: str) -> "ServiceInstantiation":
        """Get service instancy by it's instance ID.

        It uses SO API to get orchestration request for service with provided instance ID.

        Raises:
            ValueError: No service instance with given ID

        Returns:
            ServiceInstantiation: Service instantiation request

        """
        response: dict = cls.send_message_json(
            "GET",
            f"Check {service_instance_id} service instantiation status",
            (f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/orchestrationRequests/v7?"
             f"filter=serviceInstanceId:EQUALS:{service_instance_id}"),
            headers=headers_so_creator(OnapService.headers)
        )
        if not response.get("requestList", []):
            raise ValueError("Service instance doesn't exist")
        for details in response["requestList"]:
            if details.get("request", {}).get("requestScope") == "service" and \
                details.get("request", {}).get("requestType") == "createInstance":
                cloud_region = CloudRegion.get_by_region_id(
                    details["request"]["requestDetails"]["cloudConfiguration"]["lcpCloudRegionId"]
                )
                return cls(
                    name=details["request"]["instanceReferences"]["serviceInstanceName"],
                    sdc_service=SdcService(
                        details["request"]["requestDetails"]["modelInfo"]["modelName"]
                    ),
                    cloud_region=cloud_region,
                    tenant=cloud_region.get_tenant(
                        details["request"]["requestDetails"]["cloudConfiguration"]["tenantId"]
                    ),
                    customer=Customer.get_by_global_customer_id(
                        details["request"]["requestDetails"]["subscriberInfo"]\
                            ["globalSubscriberId"]),
                    owning_entity=OwningEntity.get_by_owning_entity_id(
                        details["request"]["requestDetails"]["owningEntity"]["owningEntityId"]
                    ),
                    project=Project.create(
                        details["request"]["requestDetails"]["project"]["projectName"]
                    ),
                    request_id=details["request"]["requestId"],
                    instance_id=service_instance_id
                )
        raise ValueError("No createInstance request found")

    @classmethod
    def get_by_service_instance_name(cls, service_instance_name: str) -> "ServiceInstantiation":
        """Get service instancy by it's name.

        It uses SO API to get orchestration request for service with provided name.

        Raises:
            ValueError: No service instance with given name

        Returns:
            ServiceInstantiation: Service instantiation request

        """
        response: dict = cls.send_message_json(
            "GET",
            f"Check {service_instance_name} service instantiation status",
            (f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/orchestrationRequests/v7?"
             f"filter=serviceInstanceName:EQUALS:{service_instance_name}"),
            headers=headers_so_creator(OnapService.headers)
        )
        if not response.get("requestList", []):
            raise ValueError("Service instance doesn't exist")
        for details in response["requestList"]:
            if details.get("request", {}).get("requestScope") == "service" and \
                details.get("request", {}).get("requestType") == "createInstance":
                cloud_region = CloudRegion.get_by_region_id(
                    details["request"]["requestDetails"]["cloudConfiguration"]["lcpCloudRegionId"]
                )
                return cls(
                    name=service_instance_name,
                    sdc_service=SdcService(
                        details["request"]["requestDetails"]["modelInfo"]["modelName"]
                    ),
                    cloud_region=cloud_region,
                    tenant=cloud_region.get_tenant(
                        details["request"]["requestDetails"]["cloudConfiguration"]["tenantId"]
                    ),
                    customer=Customer.get_by_global_customer_id(
                        details["request"]["requestDetails"]["subscriberInfo"]\
                            ["globalSubscriberId"]),
                    owning_entity=OwningEntity.get_by_owning_entity_id(
                        details["request"]["requestDetails"]["owningEntity"]["owningEntityId"]
                    ),
                    project=Project.create(
                        details["request"]["requestDetails"]["project"]["projectName"]
                    ),
                    request_id=details["request"]["requestId"],
                    instance_id=details["request"]["instanceReferences"]["serviceInstanceId"]
                )
        raise ValueError("No createInstance request found")

    @classmethod
    def instantiate_so_ala_carte(cls,  # pylint: disable=R0913
                                 sdc_service: SdcService,
                                 cloud_region: CloudRegion,
                                 tenant: Tenant,
                                 customer: Customer,
                                 owning_entity: OwningEntity,
                                 project: Project,
                                 service_instance_name: str = None,
                                 use_vnf_api: bool = False) -> "ServiceInstantiationc":
        """Instantiate service using SO a'la carte request.

        Args:
            sdc_service (SdcService): Service to instantiate
            cloud_region (CloudRegion): Cloud region to use in instantiation request
            tenant (Tenant): Tenant to use in instantiation request
            customer (Customer): Customer to use in instantiation request
            owning_entity (OwningEntity): Owning entity to use in instantiation request
            project (Project): Project to use in instantiation request
            service_instance_name (str, optional): Service instance name. Defaults to None.
            use_vnf_api (bool, optional): Flague to determine if VNF_API or GR_API
                should be used to instantiate. Defaults to False.

        Raises:
            ValueError: Instantiation request returns HTTP error code.

        Returns:
            ServiceInstantiation: instantiation request object

        """
        if not sdc_service.distributed:
            raise ValueError("Service is not distributed")
        if service_instance_name is None:
            service_instance_name = f"Python_ONAP_SDK_service_instance_{str(uuid4())}"
        response: dict = cls.send_message_json(
            "POST",
            f"Instantiate {sdc_service.name} service a'la carte",
            ("http://so.api.simpledemo.onap.org:30277/onap/so/infra/"
             "serviceInstantiation/v7/serviceInstances"),
            data=jinja_env().get_template("instantiate_so_ala_carte.json.j2").
            render(
                sdc_service=sdc_service,
                cloud_region=cloud_region,
                tenant=tenant,
                customer=customer,
                owning_entity=owning_entity,
                service_instance_name=service_instance_name,
                project=project,
                use_vnf_api=use_vnf_api
            ),
            headers=headers_so_creator(OnapService.headers),
            exception=ValueError
        )
        return cls(
            name=service_instance_name,
            request_id=response["requestReferences"].get("requestId"),
            instance_id=response["requestReferences"].get("instanceId"),
            sdc_service=sdc_service,
            cloud_region=cloud_region,
            tenant=tenant,
            customer=customer,
            owning_entity=owning_entity,
            project=project
        )

    # @property
    # def vnf_instances(self) -> Iterator[VnfInstantiation]:
    #     """Vnf instances correlated with service.

    #     Yields:
    #         Iterator[VnfInstantiation]: VNF instance.

    #     """
    #     response: dict = self.send_message_json(
    #         "GET",
    #         f"Check {self.name} service instantiation status",
    #         (f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/orchestrationRequests/v7?"
    #          f"filter=serviceInstanceId:EQUALS:{self.instance_id}"),
    #         headers=headers_so_creator(OnapService.headers)
    #     )
    #     for request in response.get("requestList", []):
    #         if request.get("request", {}).get("requestScope") == "vnf" \
    #             and request.get("request", {}).get("requestType") == "createInstance":
    #             yield VnfInstantiation.create_from_request_response(request)

    @property
    def aai_service_instance(self) -> AaiServiceInstance:
        if self.status != self.StatusEnum.COMPLETED:
            raise AttributeError("Service not instantiated")
        try:
            service_subscription: ServiceSubscription = \
                self.customer.get_service_subscription_by_service_type(self.sdc_service.name)
            return service_subscription.get_service_instance_by_name(self.name)
        except ValueError:
            self._logger.error("A&AI resources not created properly")
            raise AttributeError


    def instantiate_vnf(self,
                        line_of_business: LineOfBusiness,
                        platform: Platform,
                        vnf_service_instance_name_factory: str = None,
                        use_vnf_api: bool = True) -> Iterator[VnfInstantiation]:
        """Instantiate VNF for Service.

        Get VNF for Service from it's Tosca and call instantiation requests.

        Args:
            line_of_business (LineOfBusiness): LineOfBusiness to use in instantiation request
            platform (Platform): Platform to use in instantiation request
            vnf_service_instance_name_factory (str, optional): Factory to create VNF names.
                It's going to be a prefix of name. Index of vnf in Tosca file will be
                added to it.
                If no value is provided it's going to be
                "Python_ONAP_SDK_vnf_service_instance_{str(uuid4())}".
                Defaults to None.
            use_vnf_api (bool, optional): Flague to determine if VNF_API or GR_API
                should be used to instantiate. Defaults to True.

        Raises:
            AttributeError: Service is not instantiated.

        Yields:
            Iterator[VnfInstantiation]: VnfInstantion class object

        """
        if self.status != self.StatusEnum.COMPLETED:
            raise AttributeError("Service is not instantiated")
        if not self.sdc_service.vnfs:
            self._logger.info("No vnfs to instantiate")
            return
        if vnf_service_instance_name_factory is None:
            vnf_service_instance_name_factory = \
                f"Python_ONAP_SDK_vnf_service_instance_{str(uuid4())}_"
        for index, vnf in enumerate(self.sdc_service.vnfs):
            vnf_instance_name: str = f"{vnf_service_instance_name_factory}{index}"
            response: dict = self.send_message_json(
                "POST",
                f"Instantiate {self.sdc_service.name} service vnf {vnf.name}",
                (f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/serviceInstantiation/v7/"
                 f"serviceInstances/{self.instance_id}/vnfs"),
                data=jinja_env().get_template("instantiate_vnf_ala_carte.json.j2").
                render(
                    vnf_service_instance_name=vnf_instance_name,
                    vnf=vnf,
                    service=self.sdc_service,
                    cloud_region=self.cloud_region,
                    tenant=self.tenant,
                    customer=self.customer,
                    line_of_business=line_of_business,
                    platform=platform,
                    service_instance=self,
                    use_vnf_api=use_vnf_api
                ),
                headers=headers_so_creator(OnapService.headers),
                exception=ValueError
            )
            yield VnfInstantiation(
                name=vnf_instance_name,
                request_id=response["requestReferences"]["requestId"],
                instance_id=response["requestReferences"]["instanceId"],
                service_instantiation=self,
                line_of_business=line_of_business,
                platform=platform,
                vnf=vnf
            )
