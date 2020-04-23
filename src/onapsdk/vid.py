
import logging
from dataclasses import dataclass

from onapsdk.onap_service import OnapService
from onapsdk.utils.jinja import jinja_env


class Vid(OnapService):

    __logger: logging.Logger = logging.getLogger(__name__)

    base_url = "https://vid.api.simpledemo.onap.org:30200"
    api_version = "/vid"


@dataclass
class OwningEntity(Vid):

    name: str

    @classmethod
    def create(cls, name: str) -> "OwningEntity":
        cls.send_message(
            "POST",
            "Declare owning entity in VID",
            f"{cls.base_url}{cls.api_version}/maintenance/category_parameter/owningEntity",
            data=jinja_env().get_template("vid_declare_owning_entity.json.j2").render(
                owning_entity_name=name
            )
        )
        return cls(name)


@dataclass
class Project(Vid):

    name: str

    @classmethod
    def create(cls, name: str) -> "Project":
        cls.send_message(
            "POST",
            "Declare VID project",
            f"{cls.base_url}{cls.api_version}/maintenance/category_parameter/project",
            data=jinja_env().get_template("vid_declare_project.json.j2").render(
                project=name
            )
        )
        return cls(name)


@dataclass
class LineOfBusiness(Vid):

    name: str

    @classmethod
    def create(cls, name: str) -> "LineOfBusiness":
        cls.send_message(
            "POST",
            "Declare VID line of business",
            f"{cls.base_url}{cls.api_version}/maintenance/category_parameter/lineOfBusiness",
            data=jinja_env().get_template("vid_declare_line_of_business.json.j2").render(
                line_of_business=name
            )
        )
        return cls(name)


@dataclass
class Platform(Vid):
    
    name: str

    @classmethod
    def create(cls, name: str) -> "Platform":
        cls.send_message(
            "POST",
            "Declare VID platform",
            f"{cls.base_url}{cls.api_version}/maintenance/category_parameter/platform",
            data=jinja_env().get_template("vid_declare_platform.json.j2").render(
                platform=name
            )
        )
        return cls(name)
