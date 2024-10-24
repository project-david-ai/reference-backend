import requests


class RipeStatService:
    def __init__(self):
        self.base_url = "https://stat.ripe.net/data"
        self.session = requests.Session()

    def get_abuse_contact(self, resource):
        url = f"{self.base_url}/abuse-contact-finder/data.json"
        params = {"resource": resource}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            # Handle any errors that occurred during the request
            print(f"Error: {e}")
            return None

    def get_address_space_hierarchy(self, resource):
        url = f"{self.base_url}/address-space-hierarchy/data.json"
        params = {"resource": resource}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            # Handle any errors that occurred during the request
            print(f"Error: {e}")
            return None

    def get_address_space_usage(self, resource, all_level_more_specifics=True):
        url = f"{self.base_url}/address-space-usage/data.json"
        params = {"resource": resource, "all_level_more_specifics": all_level_more_specifics}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            # Handle any errors that occurred during the request
            print(f"Error: {e}")
            return None

    def get_allocation_history(self, resource, starttime, endtime=None):
        url = f"{self.base_url}/allocation-history/data.json"
        params = {"resource": resource, "starttime": starttime}
        if endtime:
            params["endtime"] = endtime
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_announced_prefixes(self, resource, starttime=None, endtime=None, min_peers_seeing=10):
        url = f"{self.base_url}/announced-prefixes/data.json"
        params = {"resource": resource, "min_peers_seeing": min_peers_seeing}
        if starttime:
            params["starttime"] = starttime
        if endtime:
            params["endtime"] = endtime
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_asn_neighbours(self, resource, starttime=None):
        url = f"{self.base_url}/asn-neighbours/data.json"
        params = {"resource": resource}
        if starttime:
            params["starttime"] = starttime
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_atlas_probes(self, resource):
        url = f"{self.base_url}/atlas-probes/data.json"
        params = {"resource": resource}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_bgp_updates(self, resource, starttime=None, endtime=None, rrcs=None, unix_timestamps=False):
        url = f"{self.base_url}/bgp-updates/data.json"
        params = {"resource": resource, "unix_timestamps": unix_timestamps}
        if starttime:
            params["starttime"] = starttime
        if endtime:
            params["endtime"] = endtime
        if rrcs:
            params["rrcs"] = rrcs
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_asn_neighbours_history(self, resource, starttime=None, endtime=None, max_rows=1800):
        url = f"{self.base_url}/asn-neighbours-history/data.json"
        params = {"resource": resource, "max_rows": max_rows}
        if starttime:
            params["starttime"] = starttime
        if endtime:
            params["endtime"] = endtime
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_country_resource_stats(self, resource, starttime=None, endtime=None, resolution=None):
        url = f"{self.base_url}/country-resource-stats/data.json"
        params = {"resource": resource}
        if starttime:
            params["starttime"] = starttime
        if endtime:
            params["endtime"] = endtime
        if resolution:
            params["resolution"] = resolution
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_country_resource_list(self, resource, time=None, v4_format=None):
        url = f"{self.base_url}/country-resource-list/data.json"
        params = {"resource": resource}
        if time:
            params["time"] = time
        if v4_format:
            params["v4_format"] = v4_format
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_dns_chain(self, resource):
        url = f"{self.base_url}/dns-chain/data.json"
        params = {"resource": resource}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_example_resources(self):
        url = f"{self.base_url}/example-resources/data.json"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_historical_whois(self, resource, version=None):
        url = f"{self.base_url}/historical-whois/data.json"
        params = {"resource": resource}
        if version:
            params["version"] = version
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_iana_registry_info(self, resource=None, best_match_only=False):
        url = f"{self.base_url}/iana-registry-info/data.json"
        params = {}
        if resource:
            params["resource"] = resource
        if best_match_only:
            params["best_match_only"] = best_match_only
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_routing_history(self, resource, starttime=None, endtime=None, min_peers=10):
        url = f"{self.base_url}/routing-history/data.json"
        params = {"resource": resource, "min_peers": min_peers}
        if starttime:
            params["starttime"] = starttime
        if endtime:
            params["endtime"] = endtime
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_routing_status(self, resource, timestamp=None, min_peers_seeing=10):
        url = f"{self.base_url}/routing-status/data.json"
        params = {"resource": resource, "min_peers_seeing": min_peers_seeing}
        if timestamp:
            params["timestamp"] = timestamp
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_rrc_info(self):
        url = f"{self.base_url}/rrc-info/data.json"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_rpki_validation_status(self, resource, prefix):
        url = f"{self.base_url}/rpki-validation/data.json"
        params = {"resource": resource, "prefix": prefix}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_rpki_history(self, resource, family=4, resolution=None, delegated=False):
        url = f"{self.base_url}/rpki-history/data.json"
        params = {"resource": resource, "family": family}
        if resolution:
            params["resolution"] = resolution
        if delegated:
            params["delegated"] = delegated
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_searchcomplete(self, resource, limit=6):
        url = f"{self.base_url}/searchcomplete/data.json"
        params = {"resource": resource, "limit": limit}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_looking_glass(self, resource):
        url = f"{self.base_url}/looking-glass/data.json"
        params = {"resource": resource}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_whats_my_ip(self):
        url = f"{self.base_url}/whats-my-ip/data.json"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_zonemaster(self, resource, method=None):
        url = f"{self.base_url}/zonemaster/data.json"
        params = {"resource": resource}
        if method:
            params["method"] = method
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_mlab_bandwidth(self, resource, starttime=None, endtime=None):
        url = f"{self.base_url}/mlab-bandwidth/data.json"
        params = {"resource": resource}
        if starttime:
            params["starttime"] = starttime
        if endtime:
            params["endtime"] = endtime
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_mlab_clients(self, resource, starttime=None, endtime=None):
        url = f"{self.base_url}/mlab-clients/data.json"
        params = {"resource": resource}
        if starttime:
            params["starttime"] = starttime
        if endtime:
            params["endtime"] = endtime
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None


if __name__ == "__main__":
    service = RipeStatService()

    # Get abuse contact information
    resource = "193.0.0.0/21"
    abuse_contact_data = service.get_abuse_contact(resource)
    print("Abuse Contact Data:")
    print(abuse_contact_data)
    print()

    # Get address space hierarchy
    resource = "193/21"
    address_space_hierarchy_data = service.get_address_space_hierarchy(resource)
    print("Address Space Hierarchy Data:")
    print(address_space_hierarchy_data)
