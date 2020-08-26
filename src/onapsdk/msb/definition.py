"""Definition module."""
from onapsdk.msb import MSB
from onapsdk.utils.jinja import jinja_env


# pylint: disable=too-many-arguments, too-few-public-methods
class Definition(MSB):
    """Definition class."""

    api_version = "/api/multicloud-k8s/v1/v1"
    base_url = f"{MSB.base_url}{api_version}/rb/definition"

    def __init__(self, rb_name: str,
                 rb_version: str,
                 chart_name: str,
                 description: str,
                 labels: dict) -> None:
        """Definition object initialization.

        Args:
            rb_name (str): Definition name
            rb_version (str): Definition version
            chart_name (str): Chart name, optional field, will be detected if it is not provided
            description (str): Definition description
            labels (str): Labels
        """
        super().__init__()
        self.rb_name: str = rb_name
        self.rb_version: str = rb_version
        self.chart_name: str = chart_name
        self.description: str = description
        self.labels: dict = labels

    @classmethod
    def get_all(cls):
        """Get all definitions.

        Yields:
            Definition: Definition object

        """
        url: str = f"{cls.base_url}"
        for definition in cls.send_message_json("GET",
                                                "Get definitions",
                                                url):
            yield cls(
                definition.get("rb-name"),
                definition.get("rb-version"),
                definition.get("chart-name"),
                definition.get("description"),
                definition.get("labels")
            )

    @classmethod
    def get_definition_by_name_version(cls, rb_name: str, rb_version: str) -> "Definition":
        """Get definition by it's name and version.

        Args:
            rb_name (str): definition name
            rb_version (str): definition version

        Returns:
            Definition: Definition object

        """
        url: str = f"{cls.base_url}/{rb_name}/{rb_version}"
        definition: dict = cls.send_message_json(
            "GET",
            "Get definition",
            url,
            exception=ValueError
        )
        return cls(
            definition.get("rb-name"),
            definition.get("rb-version"),
            definition.get("chart-name"),
            definition.get("description"),
            definition.get("labels")
        )

    def delete_definition(self) -> None:
        """Delete definition."""
        url: str = f"{self.base_url}/{self.rb_name}"
        if self.rb_version is not None:
            url: str = f"{url}/{self.rb_version}"
        self.send_message(
            "DELETE",
            "Delete definition",
            url
        )

    @classmethod
    def create(cls, rb_name: str,
               rb_version: str,
               chart_name: str = '',
               description: str = "",
               labels=None) -> "Definition":
        """Create Definition.

        Args:
            rb_name (str): Definition name
            rb_version (str): Definition version
            chart_name (str): Chart name, optional field, will be detected if it is not provided
            description (str): Definition description
            labels (str): Labels

        Raises:
            ValueError: request response with HTTP error code

        Returns:
            Definition: Created object

        """
        if labels is None:
            labels = {}
        url: str = f"{cls.base_url}"
        cls.send_message(
            "POST",
            "Create definition",
            url,
            data=jinja_env().get_template("multicloud_k8s_add_definition.json.j2").render(
                rb_name=rb_name,
                rb_version=rb_version,
                chart_name=chart_name,
                description=description,
                labels=labels
            ),
            exception=ValueError
        )
        return cls.get_definition_by_name_version(rb_name, rb_version)

    def upload_definition_artifact(self, package: bytes = None):
        """Upload artifact for Definition.

        Args:
            package (bytes): Definition artifact to be uploaded to multicloud-k8s plugin
        Raises:
            ValueError: request response with HTTP error code

        """
        url: str = f"{self.base_url}/{self.rb_name}/{self.rb_version}/content"
        self.send_message(
            "POST",
            "Upload Definition Artifact",
            url,
            data=package,
            headers={},
            exception=ValueError
        )

    def create_profile(self, profile_name: str,
                       namespace: str,
                       kubernetes_version: str,
                       release_name=None) -> "Profile":
        """Create Profile for Definition.

        Args:
            profile_name (str): Name of profile
            namespace (str): Namespace that service is created in
            kubernetes_version (str): Required Kubernetes version
            release_name (str): Release name

        Raises:
            ValueError: request response with HTTP error code

        Returns:
            Profile: Created object

        """
        url: str = f"{self.base_url}{self.api_version}/rb/definition/" \
                   f"{self.rb_name}/{self.rb_version}/profile"
        if release_name is None:
            release_name = profile_name
        self.send_message(
            "POST",
            "Create profile for definition",
            url,
            data=jinja_env().get_template("multicloud_k8s_create_profile_for_definition.json.j2").render(
                rb_name=self.rb_name,
                rb_version=self.rb_version,
                profile_name=profile_name,
                release_name=release_name,
                namespace=namespace,
                kubernetes_version=kubernetes_version
            ),
            exception=ValueError
        )
        return self.get_profile_by_name(profile_name)

    def get_all_profiles(self):
        """Get all profiles.

        Yields:
            Profile: Profile object

        """
        url: str = f"{self.base_url}{self.api_version}/rb/definition/" \
                   f"{self.rb_name}/{self.rb_version}/profile"

        for profile in self.send_message_json("GET",
                                              "Get profiles",
                                              url):
            yield Profile(
                profile.get("rb-name"),
                profile.get("rb-version"),
                profile.get("profile-name"),
                profile.get("namespace"),
                profile.get("kubernetes-version"),
                profile.get("labels"),
                profile.get("release-name")
            )

    def get_profile_by_name(self, profile_name: str) -> "Profile":
        """Get profile by it's name.

        Args:
            profile_name (str): profile name

        Returns:
            Profile: Profile object

        """
        url: str = f"{self.base_url}{self.api_version}/rb/definition/" \
                   f"{self.rb_name}/{self.rb_version}/profile/{profile_name}"

        profile: dict = self.send_message_json(
            "GET",
            "Get profile",
            url,
            exception=ValueError
        )
        return Profile(
            profile.get("rb-name"),
            profile.get("rb-version"),
            profile.get("profile-name"),
            profile.get("namespace"),
            profile.get("kubernetes-version"),
            profile.get("labels"),
            profile.get("release-name")
        )


class Profile(MSB):
    """Profile class."""

    api_version = "/api/multicloud-k8s/v1/v1"

    @property
    def url(self) -> str:
        """URL address for Profile calls.

        Returns:
            str: URL to Profile in Multicloud-k8s API.

        """
        return f"{self.base_url}{self.api_version}/rb/definition/" \
               f"{self.rb_name}/{self.rb_version}/profile/"

    def __init__(self, rb_name: str,
                 rb_version: str,
                 profile_name: str,
                 namespace: str,
                 kubernetes_version: str,
                 labels=None,
                 release_name=None) -> None:
        """Profile object initialization.

        Args:
            rb_name (str): Definition name
            rb_version (str): Definition version
            profile_name (str): Name of profile
            release_name (str): Release name, if release_name is not provided,
            profile-name will be used
            namespace (str): Namespace that service is created in
            kubernetes_version (str): Required Kubernetes version
            labels (str): Labels
        """
        super().__init__()
        if release_name is None:
            release_name = profile_name
        self.rb_name: str = rb_name
        self.rb_version: str = rb_version
        self.profile_name: str = profile_name
        self.release_name: str = release_name
        self.namespace: str = namespace
        self.kubernetes_version: str = kubernetes_version
        self.labels: str = labels

    def upload_profile_artifact(self, package: bytes = None):
        """Upload artifact for Profile.

        Args:

        Raises:
            ValueError: request response with HTTP error code

        """
        url: str = f"{self.url}/{self.profile_name}/content"
        self.send_message(
            "POST",
            "Upload Profile Artifact",
            url,
            data=package,
            headers={},
            exception=ValueError
        )
