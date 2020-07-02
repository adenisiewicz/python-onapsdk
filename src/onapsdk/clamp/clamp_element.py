#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Clamp module."""
import json
import os
from OpenSSL.crypto import load_pkcs12, dump_privatekey, dump_certificate, FILETYPE_PEM

from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService as Onap
from onapsdk.service import Service
from onapsdk.utils.jinja import jinja_env


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
    def create_cert(cls, key: str) -> None:
        """Create certificate tuple."""
        #Must modify key from parameters to hide it
        _root_path = os.getcwd().rsplit('/onapsdk')[0]
        file = _root_path +"/src/onapsdk/clamp/aaf_certificate.p12"
        with open(file, 'rb') as pkcs12_file:
            pkcs12_data = pkcs12_file.read()
        pkcs12_password_bytes = key.encode('utf8')
        pyo_pk = load_pkcs12(pkcs12_data, pkcs12_password_bytes)
        cert = dump_certificate(FILETYPE_PEM, pyo_pk.get_certificate())
        private_key = dump_privatekey(FILETYPE_PEM, pyo_pk.get_privatekey(),
                                      "aes256", pkcs12_password_bytes)
        with open('cert.pem', 'wb') as pem_file:
            pem_file.write(cert)
        with open('cert.key', 'wb') as key_file:
            key_file.write(private_key)
        cls._cert = ('cert.pem', 'cert.key')

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
        if len(policies) >= req_policies:
            for policy in policies:
                if policy["policyAcronym"] == policy_name:
                    return True
        raise ValueError("Couldn't load policies from policy engine")
