#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test Service module."""

import mock
import pytest

import onapsdk.constants as const
from onapsdk.service import Service
from onapsdk.sdc_resource import SdcResource


def test_init_no_name():
    """Check init with no names."""
    svc = Service()
    assert isinstance(svc, SdcResource)
    assert svc._identifier is None
    assert svc._version is None
    assert svc.name == "ONAP-test-Service"
    assert svc.headers["USER_ID"] == "cs0008"
    assert svc.distribution_status is None
    assert svc._distribution_id is None
    assert isinstance(svc._base_url(), str)


def test_init_with_name():
    """Check init with no names."""
    svc = Service(name="YOLO")
    assert svc._identifier == None
    assert svc._version == None
    assert svc.name == "YOLO"
    assert svc.created() == False
    assert svc.headers["USER_ID"] == "cs0008"
    assert svc.distribution_status is None
    assert svc._distribution_id is None
    assert isinstance(svc._base_url(), str)

def test_init_with_sdc_values():
    """Check init with no names."""
    sdc_values = {'uuid': '12', 'version': '14', 'invariantUUID': '56',
                  'distributionStatus': 'yes', 'lifecycleState': 'state'}
    svc = Service(sdc_values=sdc_values)
    assert svc._identifier == "12"
    assert svc._version == "14"
    assert svc.name == "ONAP-test-Service"
    assert svc.created()
    assert svc.headers["USER_ID"] == "cs0008"
    assert svc.distribution_status == "yes"
    assert svc._distribution_id is None
    assert isinstance(svc._base_url(), str)

def test_equality_really_equals():
    """Check two vfs are equals if name is the same."""
    svc_1 = Service(name="equal")
    svc_1.identifier = "1234"
    svc_2 = Service(name="equal")
    svc_2.identifier = "1235"
    assert svc_1 == svc_2


def test_equality_not_equals():
    """Check two vfs are not equals if name is not the same."""
    svc_1 = Service(name="equal")
    svc_1.identifier = "1234"
    svc_2 = Service(name="not_equal")
    svc_2.identifier = "1234"
    assert svc_1 != svc_2


def test_equality_not_equals_not_same_object():
    """Check a vf and something different are not equals."""
    svc_1 = Service(name="equal")
    svc_1.identifier = "1234"
    svc_2 = SdcResource()
    svc_2.name = "equal"
    assert svc_1 != svc_2

@mock.patch.object(Service, 'load_metadata')
def test_distribution_id_no_load(mock_load):
    svc = Service()
    svc.identifier = "1234"
    svc._distribution_id = "4567"
    assert svc.distribution_id == "4567"
    mock_load.assert_not_called()

@mock.patch.object(Service, 'load_metadata')
def test_distribution_id_load(mock_load):
    svc = Service()
    svc.identifier = "1234"
    assert svc.distribution_id is None
    mock_load.assert_called_once()

def test_distribution_id_setter():
    svc = Service()
    svc.identifier = "1234"
    svc.distribution_id = "4567"
    assert svc._distribution_id == "4567"

@mock.patch.object(Service, '_create')
def test_create(mock_create):
    svc = Service()
    svc.create()
    mock_create.assert_called_once_with("service_create.json.j2", name="ONAP-test-Service")

@mock.patch.object(Service, 'send_message')
def test_add_resource_not_draft(mock_send):
    svc = Service()
    resource = SdcResource()
    svc.add_resource(resource)
    mock_send.assert_not_called()

@mock.patch.object(Service, 'send_message')
def test_add_resource_bad_result(mock_send):
    svc = Service()
    svc.unique_identifier = "45"
    svc.status = const.DRAFT
    mock_send.return_value = {}
    resource = SdcResource()
    resource.unique_identifier = "12"
    resource.version = "40"
    resource.name = "test"
    assert svc.add_resource(resource) is None
    mock_send.assert_called_once_with('POST', 'Add SdcResource to service', 'http://sdc.api.fe.simpledemo.onap.org:30206/sdc1/feProxy/rest/v1/catalog/services/45/resourceInstance', data='{\n  "name": "test",\n  "componentVersion": "40",\n  "posY": 100,\n  "posX": 200,\n  "uniqueId": "12",\n  "originType": "SDCRESOURCE",\n  "componentUid": "12",\n  "icon": "defaulticon"\n}')


@mock.patch.object(Service, 'send_message')
def test_add_resource_OK(mock_send):
    svc = Service()
    svc.unique_identifier = "45"
    svc.status = const.DRAFT
    mock_send.return_value = {'yes': 'indeed'}
    resource = SdcResource()
    resource.unique_identifier = "12"
    resource.version = "40"
    resource.name = "test"
    result = svc.add_resource(resource)
    assert result['yes'] == "indeed"
    mock_send.assert_called_once_with('POST', 'Add SdcResource to service', 'http://sdc.api.fe.simpledemo.onap.org:30206/sdc1/feProxy/rest/v1/catalog/services/45/resourceInstance', data='{\n  "name": "test",\n  "componentVersion": "40",\n  "posY": 100,\n  "posX": 200,\n  "uniqueId": "12",\n  "originType": "SDCRESOURCE",\n  "componentUid": "12",\n  "icon": "defaulticon"\n}')

@mock.patch.object(Service, '_verify_action_to_sdc')
def test_checkin(mock_verify):
    svc = Service()
    svc.checkin()
    mock_verify.assert_called_once_with(const.DRAFT, const.CHECKIN)

@mock.patch.object(Service, '_verify_action_to_sdc')
def test_submit(mock_verify):
    svc = Service()
    svc.submit()
    mock_verify.assert_called_once_with(const.CHECKIN, const.SUBMIT_FOR_TESTING)

@mock.patch.object(Service, '_verify_action_to_sdc')
def test_start_certification(mock_verify):
    svc = Service()
    svc.start_certification()
    mock_verify.assert_called_once_with(const.DRAFT, const.START_CERTIFICATION, headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'USER_ID': 'jm0007', 'Authorization': 'Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazNlSGxjc2UyZ0F3ODR2YW9HR21KdlV5MlU=', 'X-ECOMP-InstanceID': 'onapsdk'})

@mock.patch.object(Service, '_verify_action_to_sdc')
def test_certify(mock_verify):
    svc = Service()
    svc.certify()
    mock_verify.assert_called_once_with(const.DRAFT, const.CERTIFY, headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'USER_ID': 'jm0007', 'Authorization': 'Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazNlSGxjc2UyZ0F3ODR2YW9HR21KdlV5MlU=', 'X-ECOMP-InstanceID': 'onapsdk'})

@mock.patch.object(Service, '_verify_action_to_sdc')
def test_approve(mock_verify):
    svc = Service()
    svc.approve()
    mock_verify.assert_called_once_with(const.DRAFT, const.APPROVE, headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'USER_ID': 'gv0001', 'Authorization': 'Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazNlSGxjc2UyZ0F3ODR2YW9HR21KdlV5MlU=', 'X-ECOMP-InstanceID': 'onapsdk'})

@mock.patch.object(Service, '_verify_action_to_sdc')
def test_distribute(mock_verify):
    svc = Service()
    svc.distribute()
    mock_verify.assert_called_once_with(const.DRAFT, const.DISTRIBUTE, headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'USER_ID': 'op0001', 'Authorization': 'Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazNlSGxjc2UyZ0F3ODR2YW9HR21KdlV5MlU=', 'X-ECOMP-InstanceID': 'onapsdk'})
