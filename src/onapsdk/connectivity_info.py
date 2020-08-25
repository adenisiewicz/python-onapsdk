"""Connectivity-Info module."""
from onapsdk.msb import MSB


class ConnectivityInfo(MSB):
    """Connectivity-Info class."""

    api_version = "/api/multicloud-k8s/v1/v1"
    url = f"{MSB.base_url}{api_version}/rb/connectivity-info"

    def __init__(self, cloud_region_id: str,
                 cloud_owner: str,
                 other_connectivity_list: dict) -> None:
        """Connectivity-info object initialization.

        Args:
            cloud_region_id (str): Cloud region ID
            cloud_owner (str): Cloud owner name
            other_connectivity_list (dict): Optional other connectivity list
        """
        super().__init__()
        self.cloud_region_id: str = cloud_region_id
        self.cloud_owner: str = cloud_owner
        self.other_connectivity_list: dict = other_connectivity_list
