###############################################################################################
##########################################CLAMP################################################
import json

from onapsdk.onap_service import OnapService as Onap
from onapsdk.service import Service
#base_url = "https://clamp.api.simpledemo.onap.org:30258/restservices/clds/v2/"


class Clamp(Onap):
    """Mother Class of all CLAMP elements."""
    def __init__(self):
        super().__init__()
    
    @classmethod
    def base_url(cls) -> str:
        return "https://clamp.api.simpledemo.onap.org:30258/restservices/clds/v2/"
        
    @classmethod
    def check_loop_template(cls, service: Service):
        url = "{}/templates/".format(cls.base_url())
        template_list = cls.send_message_json('GET', 'Get Loop Templates', url)
        for template in template_list:
            if template["modelService"]["serviceDetails"]["name"] == service.name:
                return template["name"]
        raise ValueError("Template not found")

    @classmethod
    def check_policies(cls, policy_name: str):
        url = "{}/policyToscaModels/".format(cls.base_url())
        policies = cls.send_message_json('GET', 'Get stocked policies', url)
        if len(policies)>30:
            for policy in policies:
                if policy["policyAcronym"] == policy_name:
                    return True
        raise ValueError("Couldn't load policies from policy engine")


class LoopInstance(Clamp):
    """Control Loop instantiation class."""
    def __init__(template: str, name: str, details: dict):
        self.template = template
        self.name = name
        self.details = details

    def create(self):
        url = "{}/loop/create/{}?templateName={}".\
              format(self.base_url, self.name, self.template)
        instance_details = self.send_message('POST', 'Add artifact to vf', url)
        if  instance_details:
            self.name = "LOOP_" + self.name
            self.details = json.load(instance_details)
        raise ValueError("Couldn't create the instance")
