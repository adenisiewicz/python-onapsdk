#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""AAI Element module."""
from dataclasses import dataclass
import logging

from onapsdk.onap_service import OnapService
from onapsdk.utils.headers_creator import headers_aai_creator

class AaiElement(OnapService):
    """Mother Class of all A&AI elements."""

    __logger: logging.Logger = logging.getLogger(__name__)

    name: str = "AAI"
    server: str = "AAI"
    base_url = "https://aai.api.sparky.simpledemo.onap.org:30233"
    api_version = "/aai/v16"
    headers = headers_aai_creator(OnapService.headers)

    def __init__(self):
        """Initialize the object."""
        super().__init__()

    @classmethod
    def customers(cls):
        """Get the list of subscription types in A&AI."""
        url = cls.base_url + cls.api_version + "/business/customers"
        return cls.send_message_json('GET', 'get customers', url)

    @classmethod
    def subscriptions(cls):
        """Get the list of subscriptions in A&AI."""
        url = (cls.base_url + cls.api_version +
               "/service-design-and-creation/services")
        return cls.send_message_json('GET', 'get subscriptions', url)

    @classmethod
    def customer_service_tenant_relations(cls, customer_name):
        """Get the list of customer/service/tenant relations in A&AI."""
        url = (cls.base_url + cls.api_version +
               "/business/customers/customer/" +
               customer_name + "/service-subscriptions?depth=all")
        return cls.send_message_json('GET', 'get relations', url)

    @classmethod
    def cloud_regions(cls):
        """Get the list of subscription types in AAI."""
        url = (cls.base_url + cls.api_version +
               "/cloud-infrastructure/cloud-regions")
        return cls.send_message_json('GET', 'get cloud regions', url)

    @classmethod
    def tenants_info(cls, cloud_name):
        """Get the Cloud info of one cloud region."""
        cloud_regions = cls.cloud_regions()
        cloud_owner = ""
        cloud_region_id = ""
        for cloud_region in cloud_regions['cloud-region']:
            cloud_region_id = cloud_region["cloud-region-id"]
            if cloud_region_id in cloud_name:
                cloud_owner = cloud_region["cloud-owner"]
                cloud_region_id = cloud_region["cloud-region-id"]
                url = (cls.base_url + cls.api_version +
                       "/cloud-infrastructure/cloud-regions/cloud-region/" +
                       cloud_owner + "/" + cloud_region_id + "/tenants")
            else:
                raise Exception("Region not found")
        return cls.send_message_json('GET', 'get tenants', url)

    @classmethod
    def get_cloud_info(cls):
        clouds = cls.cloud_regions()
        cloud_info = {}
        cloud_info['cloud_owner']=clouds['cloud-region'][0]['cloud-owner']
        cloud_info['cloud_region_id']=clouds['cloud-region'][0]['cloud-region-id']
        cloud_details=cls.tenants_info(cloud_info['cloud_region_id'])
        cloud_info['tenant_id']=cloud_details['tenant'][0]['tenant-id']
        return cloud_info
