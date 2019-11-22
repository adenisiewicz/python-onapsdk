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
SUBMIT_FOR_TESTING = "certificationRequest"
CHECKOUT = "checkout"
CHECKIN = "checkin"
APPROVE = "approve"
DISTRIBUTE = "PROD/activate"
TOSCA = "toscaModel"
DISTRIBUTION = "distribution"
START_CERTIFICATION = "startCertification"
READY_FOR_CERTIFICATION = "READY_FOR_CERTIFICATION"
CERTIFICATION_IN_PROGRESS = "CERTIFICATION_IN_PROGRESS"
CERTIFIED = "CERTIFIED"
APPROVED = "DISTRIBUTION_APPROVED"
DISTRIBUTED = "DISTRIBUTED"
##
# Distribution States
##
DOWNLOAD_OK = "DOWNLOAD_OK"
