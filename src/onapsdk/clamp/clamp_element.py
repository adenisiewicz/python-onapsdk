#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Clamp module."""
import os
from zipfile import ZipFile 

from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService as Onap
from onapsdk.service import Service


class Clamp(Onap):
    """Mother Class of all CLAMP elements."""

    #class variable
    base_back_url = settings.CLAMP_URL
    _cert: tuple = None

    @classmethod
    def base_url(cls) -> str:
        """Give back the base url of Clamp."""
        return "{}/restservices/clds/v2".format(cls.base_back_url)

    @classmethod
    def create_cert(cls) -> None:
        """Create certificate tuple."""
        #Must modify key from parameters to hide it
        _root_path = os.getcwd().rsplit('/onapsdk')[0]
        clamp_dir = _root_path +"/src/onapsdk/clamp/"
        zip_path = _root_path +"/src/onapsdk/clamp/cert.zip"
        with ZipFile(zip_path, 'r') as zf: 
            zf.extract('cert.pem', clamp_dir)
            zf.extract('cert.key', clamp_dir)
            cls._cert = (clamp_dir+'cert.cert', clamp_dir+'cert.key')

    @classmethod
    def check_loop_template(cls, service: Service) -> str:
        """Return loop template name if exists."""
        url = "{}/templates/".format(cls.base_url())
        template_list = cls.send_message_json('GET',
                                              'Get Loop Templates',
                                              url,
                                              cert=cls._cert)
        for template in template_list:
            if template["modelService"]["serviceDetails"]["name"] == service.name:
                return template["name"]
        raise ValueError("Template not found")

    @classmethod
    def check_policies(cls, policy_name: str, req_policies: int = 30) -> bool:
        """Ensure that a policy is stored in CLAMP."""
        url = "{}/policyToscaModels/".format(cls.base_url())
        policies = cls.send_message_json('GET',
                                         'Get stocked policies',
                                         url,
                                         cert=cls._cert)
        exist_policy = False
        for policy in policies:
            if policy["policyAcronym"] == policy_name:
                exist_policy = True
        return (len(policies) >= req_policies) and exist_policy
