"""Connectivity-Info module."""
from onapsdk.msb import MSB


class ConnectivityInfo(MSB):
    """Connectivity-Info class."""

    api_version = "/api/multicloud-k8s/v1/v1"
    url = f"{MSB.base_url}{api_version}/connectivity-info"

    def __init__(self, cloud_region_id: str,
                 cloud_owner: str,
                 other_connectivity_list: dict,
                 kubeconfig: str) -> None:
        """Connectivity-info object initialization.

        Args:
            cloud_region_id (str): Cloud region ID
            cloud_owner (str): Cloud owner name
            other_connectivity_list (dict): Optional other connectivity list
            kubeconfig (str): kubernetes cluster kubeconfig
        """
        super().__init__()
        self.cloud_region_id: str = cloud_region_id
        self.cloud_owner: str = cloud_owner
        self.other_connectivity_list: dict = other_connectivity_list
        self.kubeconfig: str = kubeconfig

    @classmethod
    def get_connectivity_info(cls, cloud_region_id: str) -> "ConnectivityInfo":
        """Get connectivity-info by its name (cloud region id).

        Args:
            cloud_region_id (str): Cloud region ID

        Returns:
            ConnectivityInfo: Connectivity-Info object

        """
        url: str = f"{cls.url}/{cloud_region_id}"
        connectivity_info: dict = cls.send_message_json(
            "GET",
            "Get Connectivity Info",
            url,
            exception=ValueError
        )
        return cls(
            connectivity_info["cloud-region"],
            connectivity_info["cloud-owner"],
            connectivity_info.get("other-connectivity-list"),
            connectivity_info["kubeconfig"]
        )

    def delete_connectivity_info(self) -> None:
        """Delete connectivity info."""
        url: str = f"{self.url}/{self.cloud_region_id}"
        self.send_message(
            "DELETE",
            "Delete Connectivity Info",
            url
        )
