
import json
from uuid import uuid4

from onapsdk.aai_element import CloudRegion, Customer, OwningEntity, Tenant
from onapsdk.onap_service import OnapService
from onapsdk.service import Service as SdcService, Vnf
from onapsdk.utils.jinja import jinja_env
from onapsdk.utils.headers_creator import headers_so_creator, headers_sdnc_creator
from onapsdk.vid import LineOfBusiness, Platform, Project


class VnfInstantiation(OnapService):

    def __init__(self,
                 name: str,
                 request_id: str,
                 instance_id: str,
                 service_instantiation: "ServiceInstantiation",
                 line_of_business: LineOfBusiness,
                 platform: Platform,
                 vnf: Vnf) -> None:
        self.name = name
        self.request_id = request_id
        self.instance_id = instance_id
        self.service_instantiation = service_instantiation
        self.line_of_business = line_of_business
        self.platform = platform
        self.vnf = vnf

    @property
    def completed(self) -> bool:
        response: dict = self.send_message_json(
            "GET",
            f"Check {self.name} service instantiation status",
            f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/orchestrationRequests/v7/{self.request_id}",
            headers=headers_so_creator(OnapService.headers)
        )
        return response["request"]["requestStatus"]["requestState"] == "COMPLETE"

    def upload_vf_module_preload(self, vf_module_instance_name: str, vf_module):
        response: dict = self.send_message_json(
            "POST",
            "Upload VF module preload",
            "https://sdnc.api.simpledemo.onap.org:30267/restconf/operations/VNF-API:preload-vnf-topology-operation",
            data=jinja_env().get_template("instantiate_vf_module_ala_carte_upload_preload.json.j2").
                render(
                    vnf_instance=self,
                    vnf=self.vnf,
                    service_instance=self.service_instantiation,
                    vf_module_instance_name=vf_module_instance_name,
                    vf_module=vf_module
                ),
            headers=headers_sdnc_creator(OnapService.headers),
            exception=ValueError
        )

    def instantiate_vf_module(self, vf_module_instance_name_factory: str = None):
        if not self.completed:
            raise AttributeError("VNF is not instantiated")
        if not self.service_instantiation.sdc_service.vf_modules:
            self._logger.info("No vf modules to instantiate")
            return
        if vf_module_instance_name_factory is None:
            vf_module_instance_name_factory = f"Python_ONAP_SDK_vf_module_service_instance_{str(uuid4())}_"
        for index, vf_module in enumerate(self.service_instantiation.sdc_service.vf_modules):
            vf_module_instance_name: str = f"{vf_module_instance_name_factory}{index}"
            self.upload_vf_module_preload(vf_module_instance_name, vf_module)
            response: dict = self.send_message_json(
                "POST",
                f"Instantiate {self.service_instantiation.sdc_service.name} service vf module {vf_module.name}",
                f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/serviceInstantiation/v7/serviceInstances/{self.service_instantiation.instance_id}/vnfs/{self.instance_id}/vfModules",
                data=jinja_env().get_template("instantiate_vf_module_ala_carte.json.j2").
                    render(
                        vf_module_instance_name=vf_module_instance_name,
                        vf_module=vf_module,
                        service=self.service_instantiation.sdc_service,
                        cloud_region=self.service_instantiation.cloud_region,
                        tenant=self.service_instantiation.tenant,
                        customer=self.service_instantiation.customer,
                        service_instance=self.service_instantiation,
                        vnf=self.vnf,
                        vnf_instance=self
                    ),
                headers=headers_so_creator(OnapService.headers),
                exception=ValueError
            )
            print(response)


class ServiceInstantiation(OnapService):

    def __init__(self,
                 name: str,
                 request_id: str,
                 instance_id: str,
                 sdc_service: SdcService,
                 cloud_region: CloudRegion,
                 tenant: Tenant,
                 customer: Customer,
                 owning_entity: OwningEntity,
                 project: Project) -> None:
        self.name = name
        self.request_id = request_id
        self.instance_id = instance_id
        self.sdc_service = sdc_service
        self.cloud_region = cloud_region
        self.tenant = tenant
        self.customer = customer
        self.owning_entity = owning_entity
        self.project = project

        self._completed: bool = False

    @classmethod
    def get_by_service_instance_name(cls, service_instance_name: str) -> "ServiceInstantiation":
        response: dict = cls.send_message_json(
            "GET",
            f"Check {service_instance_name} service instantiation status",
            f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/orchestrationRequests/v7?filter=serviceInstanceName:EQUALS:{service_instance_name}",
            headers=headers_so_creator(OnapService.headers)
        )
        if not len(response.get("requestList", [])):
            raise AttributeError("Service instance doesn't exist")
        request_details = response["requestList"][-1]
        cloud_region = CloudRegion.get_by_region_id(request_details["request"]["requestDetails"]["cloudConfiguration"]["lcpCloudRegionId"])
        return ServiceInstantiation(
            name = service_instance_name,
            sdc_service = SdcService(request_details["request"]["requestDetails"]["modelInfo"]["modelName"]),
            cloud_region=cloud_region,
            tenant = cloud_region.get_tenant(request_details["request"]["requestDetails"]["cloudConfiguration"]["tenantId"]),
            customer = Customer.get_by_global_customer_id(request_details["request"]["requestDetails"]["subscriberInfo"]["globalSubscriberId"]),
            owning_entity = OwningEntity.get_by_owning_entity_id(request_details["request"]["requestDetails"]["owningEntity"]["owningEntityId"]),
            project = Project.create(request_details["request"]["requestDetails"]["project"]["projectName"]),
            request_id = request_details["request"]["requestId"],
            instance_id = request_details["request"]["instanceReferences"]["serviceInstanceId"]
        )

    @classmethod
    def instantiate_so_ala_carte(cls,
                                 sdc_service: SdcService,
                                 cloud_region: CloudRegion,
                                 tenant: Tenant,
                                 customer: Customer,
                                 owning_entity: OwningEntity,
                                 project: Project,
                                 service_instance_name: str = None):
        if not sdc_service.distributed:
            raise ValueError("Service is not distributed")
        if service_instance_name is None:
            service_instance_name = f"Python_ONAP_SDK_service_instance_{str(uuid4())}"
        response: dict = cls.send_message_json(
            "POST",
            f"Instantiate {sdc_service.name} service",
            "http://so.api.simpledemo.onap.org:30277/onap/so/infra/serviceInstantiation/v7/serviceInstances",
            data=jinja_env().get_template("instantiate_so_ala_carte.json.j2").
            render(
                sdc_service=sdc_service,
                cloud_region=cloud_region,
                tenant=tenant,
                customer=customer,
                owning_entity=owning_entity,
                service_instance_name=service_instance_name,
                project=project
            ),
            headers=headers_so_creator(OnapService.headers),
            exception=ValueError
        )
        return ServiceInstantiation(
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

    @property
    def completed(self) -> bool:
        response: dict = self.send_message_json(
            "GET",
            f"Check {self.name} service instantiation status",
            f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/orchestrationRequests/v7/{self.request_id}",
            headers=headers_so_creator(OnapService.headers)
        )
        return response["request"]["requestStatus"]["requestState"] == "COMPLETE"
    
    def instantiate_vnf(self, line_of_business: LineOfBusiness, platform: Platform, vnf_service_instance_name_factory: str = None):
        if not self.completed:
            raise AttributeError("Service is not instantiated")
        if not self.sdc_service.vnfs:
            self._logger.info("No vnfs to instantiate")
            return
        if vnf_service_instance_name_factory is None:
            vnf_service_instance_name_factory = f"Python_ONAP_SDK_vnf_service_instance_{str(uuid4())}_"
        for index, vnf in enumerate(self.sdc_service.vnfs):
            vnf_instance_name: str = f"{vnf_service_instance_name_factory}{index}"
            response: dict = self.send_message_json(
                "POST",
                f"Instantiate {self.sdc_service.name} service vnf {vnf.name}",
                f"http://so.api.simpledemo.onap.org:30277/onap/so/infra/serviceInstantiation/v7/serviceInstances/{self.instance_id}/vnfs",
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
                        service_instance=self
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
