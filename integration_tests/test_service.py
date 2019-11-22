#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Integration test Vendor module."""
import os

import pytest

import requests

from onapsdk.vendor import Vendor
from onapsdk.vsp import Vsp
from onapsdk.vf import Vf
from onapsdk.service import Service
import onapsdk.constants as const


@pytest.mark.integration
def test_service_unknown():
    """Integration tests for Service."""
    response = requests.post("{}/reset".format(Vendor.base_front_url))
    response.raise_for_status()
    Vf.base_back_url = Vf.base_front_url
    vendor = Vendor(name="test")
    vendor.create()
    vendor.submit()
    vsp = Vsp(name="test")
    vsp.vendor = vendor
    vsp.create()
    vsp.upload_files(open("{}/ubuntu16.zip".format(
        os.path.dirname(os.path.abspath(__file__))), 'rb'))
    vsp.validate()
    vsp.commit()
    vsp.submit()
    vsp.create_csar()
    vf = Vf(name='test')
    vf.vsp = vsp
    vf.create()
    vf.submit()
    vf.load()
    svc = Service(name='test')
    assert svc.identifier is None
    assert svc.status is None
    svc.create()
    assert svc.identifier is not None
    assert svc.status == const.DRAFT
    svc.add_resource(vf)
    svc.checkin()
    assert svc.status == const.CHECKIN
    svc.submit()
    assert svc.status == const.DRAFT
    svc.start_certification()
    assert svc.status == const.DRAFT
    svc.certify()
    assert svc.status == const.CERTIFIED
    svc.approve()
    assert svc.status == const.DRAFT
    svc.distribute()
    assert svc.status == const.DRAFT
    assert svc.distributed
