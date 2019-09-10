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
