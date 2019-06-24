#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test AaiElement module."""
import mock
import pytest

from onapsdk.aai_element import AaiElement
from onapsdk.onap_service import OnapService

def test_init():
    """Test the initialization."""
    element = AaiElement()
    assert isinstance(element, OnapService)

def test_class_variables():
    """Test the class variables."""
    assert AaiElement.server == "AAI"
    assert AaiElement.base_url == "https://aai.api.sparky.simpledemo.onap.org:30233"
    assert AaiElement.api_version == "/aai/v13"
    assert AaiElement.headers == {
            "Content-Type": "application/json",
            "Accept": "application/json"}

@mock.patch.object(AaiElement, 'send_message_json')
def test_customers(mock_send):
    """Test get_customer function of A&AI."""
    mock_send.return_value = {'results':[
        {"customer":[
            {"global-customer-id":"generic",
             "subscriber-name":"generic",
             "subscriber-type":"INFRA",
             "resource-version":"1561218640404"}]}]}
    assert len(AaiElement.customers()) == 1
    aai_customer_1 = AaiElement.customers()["results"][0]['customer'][0]
    assert aai_customer_1['global-customer-id'] == "generic"
    assert aai_customer_1['subscriber-name'] == "generic"
    assert aai_customer_1['subscriber-type'] == "INFRA"
    assert aai_customer_1['resource-version'] == "1561218640404"
    mock_send.assert_called_with("GET", 'get customers', mock.ANY)

@mock.patch.object(AaiElement, 'send_message_json')
def test_customers_no_resources(mock_send):
    """Test get_customer function with no customer declared in A&AI."""
    mock_send.return_value = {"requestError":
            {"serviceException":
                {"messageId":"SVC3001",
                "text": ("Resource not found for %1 using id "+
                         "%2 (msg=%3) +(ec=%4)"),
                "variables":[
                    "GET",
                    "business/customers",
                    ("Node Not Found:No Node of type customer found at: " +
                     "business/customers"),
                    "ERR.5.4.6114"]}}}
    assert len(AaiElement.customers()) == 1
    aai_customer_1 = AaiElement.customers()
    assert "ERR.5.4.6114" in str(aai_customer_1)
    mock_send.assert_called_with("GET", 'get customers', mock.ANY)

@mock.patch.object(AaiElement, 'send_message_json')
def test_subscription_type_list(mock_send):
    """Test the getter of subscription types in A&AI."""
    mock_send.return_value = {'service': [
        {
            "service-id": "f4bcf0b0-b44e-423a-8357-5758afc14e88",
            "service-description": "ubuntu16",
            "resource-version": "1561218639393"},
        {
            "service-id": "2e812e77-e437-46c4-8e8e-908fbc7e176c",
            "service-description": "freeradius",
            "resource-version": "1561219163076"},
        {
            "service-id": "f208de57-0e02-4505-a0fa-375b13ad24ac",
            "service-description": "ims",
            "resource-version": "1561219799684"}]}

    assert len(AaiElement.subscription_types()["service"]) == 3
    aai_service_1 = AaiElement.subscription_types()["service"][0]
    aai_service_2 = AaiElement.subscription_types()["service"][1]
    aai_service_3 = AaiElement.subscription_types()["service"][2]
    assert aai_service_1['service-id'] == "f4bcf0b0-b44e-423a-8357-5758afc14e88"
    assert aai_service_1['service-description'] == "ubuntu16"
    assert aai_service_1['resource-version'] == "1561218639393"
    assert aai_service_2['service-id'] == "2e812e77-e437-46c4-8e8e-908fbc7e176c"
    assert aai_service_2['service-description'] == "freeradius"
    assert aai_service_2['resource-version'] == "1561219163076"
    assert aai_service_3['service-id'] == "f208de57-0e02-4505-a0fa-375b13ad24ac"
    assert aai_service_3['service-description'] == "ims"
    assert aai_service_3['resource-version'] == "1561219799684"
    mock_send.assert_called_with("GET", 'get subscriptions', mock.ANY)

@mock.patch.object(AaiElement, 'send_message_json')
def test_subscription_types_no_resources(mock_send):
    """Test get_customer function with no customer declared in A&AI."""
    mock_send.return_value = {
        "requestError":
            {"serviceException":
                {"messageId":"SVC3001",
                "text": ("Resource not found for %1 using id "+
                         "%2 (msg=%3) +(ec=%4)"),
                "variables":[
                    "GET",
                    "service-design-and-creation/services",
                    ("Node Not Found:No Node of type service found at: " +
                     "/service-design-and-creation/services"),
                    "ERR.5.4.6114"]}}}
    assert len(AaiElement.subscription_types()) == 1
    aai_subscription_list = AaiElement.subscription_types()
    assert "ERR.5.4.6114" in str(aai_subscription_list)
    mock_send.assert_called_with("GET", 'get subscriptions', mock.ANY)

def test_get_vnfid_from_instance_id():
    """Test the retrieval of VNF_ID based on instance-id."""
    pass

def test_get_vnfid_from_bad_instance_id():
    """Test the retrieval of VNF_ID based on instance-id."""
    pass

def test_get_vfmoduleid_from_vnf_id():
    """Get the retrival of vfmodule id(s) based on vnf-id."""
    pass

def test_get_vfmoduleid_from_bad_vnf_id():
    """Get the retrival of vfmodule id(s) based on vnf-id."""
    pass

def test_get_infos_from_instance_id():
    """Test the retrieval of infos from instance-id."""
    pass

def test_get_infos_from_bad_instance_id():
    """Test the retrieval of infos from instance-id."""
    pass

def test_put_custom_query_from_instance_id():
    """Test put custom query."""
    pass

def test_put_custom_query_from_bad_instance_id():
    """Test put custom query."""
    pass

def test_put_custom_bad_query():
    """Test put custom query."""
    pass

@mock.patch.object(AaiElement, 'send_message_json')
def test_cloud_regions(mock_send):
    """Test get cloud regions from A&AI."""
    mock_send.return_value = {
      "cloud-region": [
        {
          "cloud-owner": "OPNFV",
          "cloud-region-id": "RegionOne",
          "cloud-type": "openstack",
          "owner-defined-type": "N/A",
          "cloud-region-version": "pike",
          "identity-url": "http://msb-iag.onap:80/api/multicloud-pike/v0/OPNFV_RegionOne/identity/v2.0",
          "cloud-zone": "OPNFV LaaS",
          "complex-name": "Cruguil",
          "resource-version": "1561217827955",
          "relationship-list": {
            "relationship": [
              {
                "related-to": "complex",
                "relationship-label": "org.onap.relationships.inventory.LocatedIn",
                "related-link": "/aai/v13/cloud-infrastructure/complexes/complex/cruguil",
                "relationship-data": [
                  {
                    "relationship-key": "complex.physical-location-id",
                    "relationship-value": "cruguil"}]}]}}]}
    assert len(AaiElement.cloud_regions()["cloud-region"]) == 1
    cloud_region = AaiElement.cloud_regions()["cloud-region"][0]
    assert cloud_region['cloud-owner'] == "OPNFV"
    assert cloud_region['cloud-type'] == "openstack"
    assert cloud_region['complex-name'] == "Cruguil"

def test_check_aai_resource_service():
    """Test that a given service instance is in A&AI."""
    pass

def test_check_aai_resource_service_not_found():
    """Test that a given service instance is not in A&AI (cleaned)."""
    pass

def test_check_aai_resource_vnf():
    """Test that a given vnf is in A&AI."""
    pass

def test_check_aai_resource_vnf_not_found():
    """Test that a given vnf is not in A&AI (cleaned)."""
    pass

def test_check_aai_resource_module():
    """Test that a given module is in A&AI."""
    pass

def test_check_aai_resource_module_not_found():
    """Test that a given module is not in A&AI (cleaned)."""
    pass

def test_check_aai_net_module():
    """Test that a given net is in A&AI."""
    pass

def test_check_aai_resource_net_not_found():
    """Test that a given net is not in A&AI (cleaned)."""
    pass
