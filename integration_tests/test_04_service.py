#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Integration test Vendor module."""
import os

import pytest
from unittest import mock

import requests

from onapsdk.sdc import SDC
from onapsdk.vendor import Vendor
from onapsdk.vsp import Vsp
from onapsdk.vf import Vf
from onapsdk.service import Service, Vnf
import onapsdk.constants as const


@pytest.mark.integration
def test_service_unknown():
    """Integration tests for Service."""
    response = requests.post("{}/reset".format(SDC.base_front_url))
    response.raise_for_status()
    vendor = Vendor(name="test")
    vendor.onboard()
    vsp = Vsp(name="test", package=open("{}/ubuntu16.zip".format(
        os.path.dirname(os.path.abspath(__file__))), 'rb'))
    vsp.vendor = vendor
    vsp.onboard()
    vf = Vf(name='test', vsp=vsp)
    vf.onboard()
    svc = Service(name='test')
    assert svc.identifier is None
    assert svc.status is None
    svc.create()
    assert svc.identifier is not None
    assert svc.status == const.DRAFT
    svc.add_resource(vf)
    svc.checkin()
    assert svc.status == const.CHECKED_IN
    svc.certify()
    assert svc.status == const.CERTIFIED
    svc.distribute()
    assert svc.status == const.DISTRIBUTED
    assert svc.distributed

@pytest.mark.integration
def test_service_onboard_unknown():
    """Integration tests for Service."""
    response = requests.post("{}/reset".format(SDC.base_front_url))
    response.raise_for_status()
    vendor = Vendor(name="test")
    vendor.onboard()
    vsp = Vsp(name="test", package=open("{}/ubuntu16.zip".format(
        os.path.dirname(os.path.abspath(__file__))), 'rb'))
    vsp.vendor = vendor
    vsp.onboard()
    vf = Vf(name='test', vsp=vsp)
    vf.onboard()
    svc = Service(name='test', resources=[vf])
    svc.onboard()
    assert svc.distributed

@mock.patch.object(Service, 'add_vnf_uid_to_metadata')
@pytest.mark.integration
def test_service_upload_tca_artifact(mock_add):
    """Integration tests for Service."""
    #requests.get("{}/reset".format(SDC.base_front_url))
    response = requests.post("{}/reset".format(SDC.base_front_url))
    response.raise_for_status()
    svc = Service(name="test")
    svc.create()
    file = open("{}/tca_clampnode.yaml".format(os.path.dirname(os.path.abspath(__file__))), 'rb')
    data = file.read()
    #mock
    mock_add.return_value = "test"
    svc.add_artifact_to_vf(vnf_name="test", 
                           artifact_type="DCAE_INVENTORY_BLUEPRINT",
                           artifact_name="tca_clampnode.yaml",
                           artifact=data)
