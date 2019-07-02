#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Constant package."""

##
# State Machines
# Vendor: DRAFT --> CERTIFIED
# VSP: DRAFT --> UPLOADED --> VALIDATED --> COMMITED --> CERTIFIED
##

##
# States
##
DRAFT = "Draft"
CERTIFIED = "Certified"
COMMITED = "Commited"
UPLOADED = "Uploaded"
VALIDATED = "Validated"

##
# Actions
##
CERTIFY = "Certify"
COMMIT = "Commit"
CREATE_PACKAGE = "Create_Package"
SUBMIT = "Submit"
SUBMIT_FOR_TESTING = "CertificationRequest"
CHECKOUT = "Checkout"
CHECKIN = "Checkin"
APPROVE = "Approve"
DISTRIBUTE = "PROD/activate"
TOSCA = "ToscaModel"
DISTRIBUTION = "Distribution"
START_CERTIFICATION = "StartCertification"

##
# Distribution States
##
DOWNLOAD_OK = "DOWNLOAD_OK"
