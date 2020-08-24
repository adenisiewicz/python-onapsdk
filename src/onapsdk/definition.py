from onapsdk.msb import MSB
from onapsdk.utils.jinja import jinja_env


class Definition(MSB):
    """Definition class."""
    api_version = "/api/multicloud-k8s/v1/v1"

    @property
    def url(self) -> str:
        pass

    def __init__(self, rb_name: str, rb_version: str, chart_name: str, description: str, labels: dict) -> None:
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
        url: str = f"{cls.base_url}{cls.api_version}/rb/definition"

        for definition in cls.send_message_json("GET",
                                                "Get definitions",
                                                url):
            yield cls(
                definition.get("rb-name"),
                definition.get("rb-version"),
                definition.get("chart-name"),
                definition.get("chart-name"),
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
        url: str = f"{cls.base_url}{cls.api_version}/rb/definition/{rb_name}/{rb_version}"

        definition: dict = cls.send_message_json(
            "GET",
            "Get definition",
            url
        )
        return cls(
            definition.get("rb-name"),
            definition.get("rb-version"),
            definition.get("chart-name"),
            definition.get("chart-name"),
            definition.get("labels")
        )

    @classmethod
    def delete_definition(cls, rb_name: str, rb_version: str = None) -> None:
        """Delete definition.

        Args:
            rb_name (str): Definition name
            rb_version (str): Definition version, if not provided al versions of
             definition will be deleted

        """
        url: str = f"{cls.base_url}{cls.api_version}/rb/definition/{rb_name}"
        if rb_version is not None:
            url: str = f"{cls.base_url}{cls.api_version}/rb/definition/{rb_name}/{rb_version}"
        cls.send_message(
            "DELETE",
            "Delete definition",
            url
        )

    @classmethod
    def create(cls, rb_name: str, rb_version: str, chart_name: str = '',
               description: str = "", labels: dict = {}) -> "Definition":
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
        url: str = f"{cls.base_url}{cls.api_version}/rb/definition"
        cls.send_message(
            "POST",
            "Create definition",
            url,
            data=jinja_env().get_template("add_definition.json.j2").render(
                rb_name=rb_name,
                rb_version=rb_version,
                chart_name=chart_name,
                description=description,
                labels=labels
            ),
            exception=ValueError
        )
        return cls.get_definition_by_name_version(rb_name, rb_version)
