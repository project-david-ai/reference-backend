from backend.app.services.api_service_external.api_public_access.api_network_engineering.ripe.api_ripe_stat_service import \
    RipeStatService
from backend.app.services.logging_service.logger import LoggingUtility


class RipeStatHandler:
    def __init__(self):
        self.ripe_stat_service = RipeStatService()
        self.logging_utility = LoggingUtility()

    def handle_get_abuse_contacts(self, arguments):
        self.logging_utility.info("Retrieving abuse contacts")
        resource = arguments.get("resource", None)
        abuse_contacts_data = self.ripe_stat_service.get_abuse_contact(resource)
        if abuse_contacts_data:
            response = "Abuse Contacts:\n\n"
            abuse_contacts = abuse_contacts_data.get("data", {}).get(
                "abuse_contacts", []
            )
            for contact in abuse_contacts:
                response += f"Contact: {contact}\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve abuse contacts")
            response = "Failed to retrieve abuse contacts."
        return response

    def handle_get_address_space_hierarchy(self, arguments):
        self.logging_utility.info("Retrieving address space hierarchy")
        resource = arguments.get("resource", None)
        hierarchy_data = self.ripe_stat_service.get_address_space_hierarchy(resource)
        if hierarchy_data:
            response = "Address Space Hierarchy:\n\n"
            exact_matches = hierarchy_data.get("data", {}).get("exact", [])
            less_specific = hierarchy_data.get("data", {}).get("less_specific", [])
            more_specific = hierarchy_data.get("data", {}).get("more_specific", [])
            response += "Exact Matches:\n"
            for match in exact_matches:
                response += f"- {match.get('inetnum')}\n"
            response += "\nLess Specific:\n"
            for match in less_specific:
                response += f"- {match.get('inetnum')}\n"
            response += "\nMore Specific:\n"
            for match in more_specific:
                response += f"- {match.get('inetnum')}\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve address space hierarchy")
            response = "Failed to retrieve address space hierarchy."
        return response

    def handle_get_address_space_usage(self, arguments):
        self.logging_utility.info("Retrieving address space usage")
        resource = arguments.get("resource", None)
        all_level_more_specifics = arguments.get("all_level_more_specifics", True)
        usage_data = self.ripe_stat_service.get_address_space_usage(
            resource, all_level_more_specifics
        )
        if usage_data:
            response = "Address Space Usage:\n\n"
            allocations = usage_data.get("data", {}).get("allocations", [])
            assignments = usage_data.get("data", {}).get("assignments", [])
            ip_stats = usage_data.get("data", {}).get("ip_stats", [])
            response += "Allocations:\n"
            for allocation in allocations:
                response += f"- {allocation.get('allocation')}: {allocation.get('asn_name')} (Status: {allocation.get('status')}, Assignments: {allocation.get('assignments')})\n"
            response += "\nAssignments:\n"
            for assignment in assignments:
                response += f"- {assignment.get('address_range')}: {assignment.get('asn_name')} (Status: {assignment.get('status')}, Parent Allocation: {assignment.get('parent_allocation')})\n"
            response += "\nIP Stats:\n"
            for stat in ip_stats:
                response += f"- {stat.get('status')}: {stat.get('ips')} IPs\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve address space usage")
            response = "Failed to retrieve address space usage."
        return response

    def handle_get_announced_prefixes(self, arguments):
        self.logging_utility.info("Retrieving announced prefixes")
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        min_peers_seeing = arguments.get("min_peers_seeing", 10)
        prefixes_data = self.ripe_stat_service.get_announced_prefixes(
            resource, starttime, endtime, min_peers_seeing
        )
        if prefixes_data:
            response = "Announced Prefixes:\n\n"
            prefixes = prefixes_data.get("data", {}).get("prefixes", [])
            for prefix_data in prefixes:
                prefix = prefix_data.get("prefix", "")
                timelines = prefix_data.get("timelines", [])
                response += f"Prefix: {prefix}\n"
                response += "Timelines:\n"
                for timeline in timelines:
                    starttime = timeline.get("starttime", "")
                    endtime = timeline.get("endtime", "")
                    response += f"- Start: {starttime}, End: {endtime}\n"
                response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve announced prefixes")
            response = "Failed to retrieve announced prefixes."
        return response

    def handle_get_allocation_history(self, arguments):
        self.logging_utility.info("Retrieving allocation history")
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        allocation_data = self.ripe_stat_service.get_allocation_history(
            resource, starttime, endtime
        )
        if allocation_data:
            response = "Allocation History:\n\n"
            results = allocation_data.get("data", {}).get("results", {})
            for rir, allocations in results.items():
                response += f"{rir}:\n"
                for allocation in allocations:
                    resource = allocation.get("resource", "")
                    status = allocation.get("status", "")
                    timelines = allocation.get("timelines", [])
                    response += (
                        f"- Resource: {resource}\n  Status: {status}\n  Timelines:\n"
                    )
                    for timeline in timelines:
                        starttime = timeline.get("starttime", "")
                        endtime = timeline.get("endtime", "")
                        response += f"  - Start: {starttime}, End: {endtime}\n"
                response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve allocation history")
            response = "Failed to retrieve allocation history."
        return response

    def handle_get_asn_neighbours(self, arguments):
        self.logging_utility.info("Retrieving ASN neighbours")
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        neighbours_data = self.ripe_stat_service.get_asn_neighbours(resource, starttime)
        if neighbours_data:
            response = "ASN Neighbours:\n\n"
            neighbour_counts = neighbours_data.get("data", {}).get(
                "neighbour_counts", {}
            )
            neighbours = neighbours_data.get("data", {}).get("neighbours", [])
            response += f"Neighbour Counts: Left: {neighbour_counts.get('left', 0)}, Right: {neighbour_counts.get('right', 0)}, Uncertain: {neighbour_counts.get('uncertain', 0)}, Unique: {neighbour_counts.get('unique', 0)}\n\n"
            for neighbour in neighbours:
                asn = neighbour.get("asn", "")
                neighbour_type = neighbour.get("type", "")
                power = neighbour.get("power", "")
                v4_peers = neighbour.get("v4_peers", "")
                v6_peers = neighbour.get("v6_peers", "")
                response += f"ASN: {asn}, Type: {neighbour_type}, Power: {power}, IPv4 Peers: {v4_peers}, IPv6 Peers: {v6_peers}\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve ASN neighbours")
            response = "Failed to retrieve ASN neighbours."
        return response

    def handle_get_atlas_probes(self, arguments):
        self.logging_utility.info("Retrieving Atlas probes")
        resource = arguments.get("resource", None)
        probes_data = self.ripe_stat_service.get_atlas_probes(resource)
        if probes_data:
            response = "Atlas Probes:\n\n"
            probes = probes_data.get("data", {}).get("probes", [])
            for probe in probes:
                probe_id = probe.get("id", "")
                status = probe.get("status_name", "")
                address_v4 = probe.get("address_v4", "")
                address_v6 = probe.get("address_v6", "")
                asn_v4 = probe.get("asn_v4", "")
                asn_v6 = probe.get("asn_v6", "")
                country_code = probe.get("country_code", "")
                response += f"Probe ID: {probe_id}, Status: {status}, IPv4: {address_v4}, IPv6: {address_v6}, ASN v4: {asn_v4}, ASN v6: {asn_v6}, Country: {country_code}\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve Atlas probes")
            response = "Failed to retrieve Atlas probes."
        return response

    def handle_get_bgp_updates(self, arguments):
        self.logging_utility.info("Retrieving BGP updates")
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        rrcs = arguments.get("rrcs", None)
        unix_timestamps = arguments.get("unix_timestamps", False)
        updates_data = self.ripe_stat_service.get_bgp_updates(
            resource, starttime, endtime, rrcs, unix_timestamps
        )
        if updates_data:
            response = "BGP Updates:\n\n"
            updates = updates_data.get("data", {}).get("updates", [])
            for update in updates:
                update_type = update.get("type", "")
                timestamp = update.get("timestamp", "")
                target_prefix = update.get("attrs", {}).get("target_prefix", "")
                path = update.get("attrs", {}).get("path", [])
                community = update.get("attrs", {}).get("community", [])
                source_id = update.get("attrs", {}).get("source_id", "")
                response += f"Type: {update_type}, Timestamp: {timestamp}, Prefix: {target_prefix}, Path: {path}, Community: {community}, Source ID: {source_id}\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve BGP updates")
            response = "Failed to retrieve BGP updates."
        return response

    def handle_get_asn_neighbours_history(self, arguments):
        self.logging_utility.info("Retrieving ASN neighbours history")
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        max_rows = arguments.get("max_rows", 1800)
        history_data = self.ripe_stat_service.get_asn_neighbours_history(
            resource, starttime, endtime, max_rows
        )
        if history_data:
            response = "ASN Neighbours History:\n\n"
            neighbours = history_data.get("data", {}).get("neighbours", [])
            for neighbour in neighbours:
                asn = neighbour.get("neighbour", "")
                timelines = neighbour.get("timelines", [])
                response += f"ASN: {asn}\n"
                for timeline in timelines:
                    starttime = timeline.get("starttime", "")
                    endtime = timeline.get("endtime", "")
                    response += f"  Start: {starttime}, End: {endtime}\n"
                response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve ASN neighbours history")
            response = "Failed to retrieve ASN neighbours history."
        return response

    def handle_get_country_resource_stats(self, arguments):
        self.logging_utility.info("Retrieving country resource stats")
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        resolution = arguments.get("resolution", None)
        stats_data = self.ripe_stat_service.get_country_resource_stats(
            resource, starttime, endtime, resolution
        )
        if stats_data:
            response = "Country Resource Stats:\n\n"
            stats = stats_data.get("data", {}).get("stats", [])
            for stat in stats:
                asns_ris = stat.get("asns_ris", 0)
                asns_stats = stat.get("asns_stats", 0)
                v4_prefixes_ris = stat.get("v4_prefixes_ris", 0)
                v4_prefixes_stats = stat.get("v4_prefixes_stats", 0)
                v6_prefixes_ris = stat.get("v6_prefixes_ris", 0)
                v6_prefixes_stats = stat.get("v6_prefixes_stats", 0)
                timeline = stat.get("timeline", [])
                response += f"ASNs RIS: {asns_ris}, ASNs Stats: {asns_stats}\n"
                response += f"IPv4 Prefixes RIS: {v4_prefixes_ris}, IPv4 Prefixes Stats: {v4_prefixes_stats}\n"
                response += f"IPv6 Prefixes RIS: {v6_prefixes_ris}, IPv6 Prefixes Stats: {v6_prefixes_stats}\n"
                response += "Timeline:\n"
                for item in timeline:
                    starttime = item.get("starttime", "")
                    endtime = item.get("endtime", "")
                    response += f"  Start: {starttime}, End: {endtime}\n"
                response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve country resource stats")
            response = "Failed to retrieve country resource stats."
        return response

    def handle_get_country_resource_list(self, arguments):
        self.logging_utility.info("Retrieving country resource list")
        resource = arguments.get("resource", None)
        time = arguments.get("time", None)
        v4_format = arguments.get("v4_format", None)

        ripe_stat_service = RipeStatService()
        resource_data = ripe_stat_service.get_country_resource_list(
            resource, time, v4_format
        )

        if resource_data:
            response = "Country Resource List:\n\n"
            resources = resource_data.get("data", {}).get("resources", {})

            asn_list = resources.get("asn", [])
            ipv4_list = resources.get("ipv4", [])
            ipv6_list = resources.get("ipv6", [])

            response += "ASNs:\n"
            for asn in asn_list:
                response += f"- {asn}\n"

            response += "\nIPv4:\n"
            for ipv4 in ipv4_list:
                response += f"- {ipv4}\n"

            response += "\nIPv6:\n"
            for ipv6 in ipv6_list:
                response += f"- {ipv6}\n"

            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve country resource list")
            response = "Failed to retrieve country resource list."

        return response

    def handle_get_dns_chain(self, arguments):
        self.logging_utility.info("Retrieving DNS chain")
        resource = arguments.get("resource", None)
        dns_data = self.ripe_stat_service.get_dns_chain(resource)
        if dns_data:
            response = "DNS Chain:\n\n"
            forward_nodes = dns_data.get("data", {}).get("forward_nodes", {})
            reverse_nodes = dns_data.get("data", {}).get("reverse_nodes", {})
            nameservers = dns_data.get("data", {}).get("nameservers", [])
            authoritative_nameservers = dns_data.get("data", {}).get(
                "authoritative_nameservers", []
            )
            response += "Forward Nodes:\n"
            for hostname, ips in forward_nodes.items():
                response += f"{hostname} -> {', '.join(ips)}\n"
            response += "\nReverse Nodes:\n"
            for ip, hostnames in reverse_nodes.items():
                response += f"{ip} -> {', '.join(hostnames)}\n"
            response += "\nNameservers:\n"
            for nameserver in nameservers:
                response += f"- {nameserver}\n"
            response += "\nAuthoritative Nameservers:\n"
            for auth_nameserver in authoritative_nameservers:
                response += f"- {auth_nameserver}\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve DNS chain")
            response = "Failed to retrieve DNS chain."
        return response

    def handle_get_example_resources(self, arguments):
        self.logging_utility.info("Retrieving example resources")
        example_data = self.ripe_stat_service.get_example_resources()
        if example_data:
            response = "Example Resources:\n\n"
            asn = example_data.get("data", {}).get("asn", "")
            ipv4 = example_data.get("data", {}).get("ipv4", "")
            ipv6 = example_data.get("data", {}).get("ipv6", "")
            range4 = example_data.get("data", {}).get("range4", "")
            response += f"ASN: {asn}\n"
            response += f"IPv4: {ipv4}\n"
            response += f"IPv6: {ipv6}\n"
            response += f"IPv4 Range: {range4}\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve example resources")
            response = "Failed to retrieve example resources."
        return response

    def handle_get_historical_whois(self, arguments):
        self.logging_utility.info("Retrieving historical whois")
        resource = arguments.get("resource", None)
        version = arguments.get("version", None)
        whois_data = self.ripe_stat_service.get_historical_whois(resource, version)
        if whois_data:
            response = "Historical Whois:\n\n"
            objects = whois_data.get("data", {}).get("objects", [])
            for obj in objects:
                response += f"Object Type: {obj.get('type', '')}\n"
                response += f"Object Key: {obj.get('key', '')}\n"
                response += "Attributes:\n"
                for attr in obj.get("attributes", []):
                    response += (
                        f"  {attr.get('attribute', '')}: {attr.get('value', '')}\n"
                    )
                response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve historical whois")
            response = "Failed to retrieve historical whois."
        return response

    def handle_get_iana_registry_info(self, arguments):
        self.logging_utility.info("Retrieving IANA registry info")
        resource = arguments.get("resource", None)
        best_match_only = arguments.get("best_match_only", False)
        registry_data = self.ripe_stat_service.get_iana_registry_info(
            resource, best_match_only
        )
        if registry_data:
            response = "IANA Registry Info:\n\n"
            resources = registry_data.get("data", {}).get("resources", [])
            for res in resources:
                resource = res.get("resource", "")
                description = res.get("description", "")
                source_url = res.get("source_url", "")
                source = res.get("source", "")
                details = res.get("details", {})
                response += f"Resource: {resource}\n"
                response += f"Description: {description}\n"
                response += f"Source URL: {source_url}\n"
                response += f"Source: {source}\n"
                response += "Details:\n"
                for key, value in details.items():
                    response += f"  {key}: {value}\n"
                response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve IANA registry info")
            response = "Failed to retrieve IANA registry info."
        return response

    def handle_get_routing_history(self, arguments):
        self.logging_utility.info("Retrieving routing history")
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        min_peers = arguments.get("min_peers", 10)
        history_data = self.ripe_stat_service.get_routing_history(
            resource, starttime, endtime, min_peers
        )
        if history_data:
            response = "Routing History:\n\n"
            by_origin = history_data.get("data", {}).get("by_origin", [])
            for origin_data in by_origin:
                origin = origin_data.get("origin", "")
                prefixes = origin_data.get("prefixes", [])
                response += f"Origin: {origin}\n"
                for prefix_data in prefixes:
                    prefix = prefix_data.get("prefix", "")
                    timelines = prefix_data.get("timelines", [])
                    response += f"Prefix: {prefix}\n"
                    for timeline in timelines:
                        starttime = timeline.get("starttime", "")
                        endtime = timeline.get("endtime", "")
                        response += f"  Start: {starttime}, End: {endtime}\n"
                    response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve routing history")
            response = "Failed to retrieve routing history."
        return response

    def handle_get_routing_status(self, arguments):
        self.logging_utility.info("Retrieving routing status")
        resource = arguments.get("resource", None)
        timestamp = arguments.get("timestamp", None)
        min_peers_seeing = arguments.get("min_peers_seeing", 10)
        status_data = self.ripe_stat_service.get_routing_status(
            resource, timestamp, min_peers_seeing
        )
        if status_data:
            response = "Routing Status:\n\n"
            first_seen = status_data.get("data", {}).get("first_seen", {})
            last_seen = status_data.get("data", {}).get("last_seen", {})
            visibility = status_data.get("data", {}).get("visibility", {})
            announced_space = status_data.get("data", {}).get("announced_space", {})
            response += "First Seen:\n"
            response += f"  Time: {first_seen.get('time', '')}\n"
            response += f"  Origin: {first_seen.get('origin', '')}\n"
            response += f"  Prefix: {first_seen.get('prefix', '')}\n"
            response += "\nLast Seen:\n"
            response += f"  Time: {last_seen.get('time', '')}\n"
            response += f"  Origin: {last_seen.get('origin', '')}\n"
            response += f"  Prefix: {last_seen.get('prefix', '')}\n"
            response += "\nVisibility:\n"
            response += f"  IPv4 Peers Seeing: {visibility.get('v4', {}).get('ris_peers_seeing', 0)}\n"
            response += f"  Total IPv4 Peers: {visibility.get('v4', {}).get('total_ris_peers', 0)}\n"
            response += f"  IPv6 Peers Seeing: {visibility.get('v6', {}).get('ris_peers_seeing', 0)}\n"
            response += f"  Total IPv6 Peers: {visibility.get('v6', {}).get('total_ris_peers', 0)}\n"
            response += "\nAnnounced Space:\n"
            response += (
                f"  IPv4 Prefixes: {announced_space.get('v4', {}).get('prefixes', 0)}\n"
            )
            response += f"  IPv4 IPs: {announced_space.get('v4', {}).get('ips', 0)}\n"
            response += (
                f"  IPv6 Prefixes: {announced_space.get('v6', {}).get('prefixes', 0)}\n"
            )
            response += (
                f"  IPv6 /48s: {announced_space.get('v6', {}).get('slash_48s', 0)}\n"
            )
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve routing status")
            response = "Failed to retrieve routing status."
        return response

    def handle_get_rrc_info(self, arguments):
        self.logging_utility.info("Retrieving RRC info")
        rrc_data = self.ripe_stat_service.get_rrc_info()
        if rrc_data:
            response = "RRC Info:\n\n"
            rrcs = rrc_data.get("data", {}).get("rrcs", [])
            for rrc in rrcs:
                rrc_id = rrc.get("id", "")
                rrc_name = rrc.get("name", "")
                location = rrc.get("location", "")
                response += f"RRC: {rrc_id}\n"
                response += f"  Name: {rrc_name}\n"
                response += f"  Location: {location}\n"
                response += "  Peers:\n"
                for peer in rrc.get("peers", []):
                    response += f"    ASN: {peer.get('asn', '')}\n"
                    response += f"    IP: {peer.get('ip', '')}\n"
                    response += (
                        f"    IPv4 Prefix Count: {peer.get('v4_prefix_count', 0)}\n"
                    )
                    response += (
                        f"    IPv6 Prefix Count: {peer.get('v6_prefix_count', 0)}\n"
                    )
                response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve RRC info")
            response = "Failed to retrieve RRC info."
        return response

    def handle_get_rpki_validation_status(self, arguments):
        self.logging_utility.info("Retrieving RPKI validation status")
        resource = arguments.get("resource", None)
        prefix = arguments.get("prefix", None)
        validation_data = self.ripe_stat_service.get_rpki_validation_status(
            resource, prefix
        )
        if validation_data:
            response = "RPKI Validation Status:\n\n"
            status = validation_data.get("data", {}).get("status", "")
            validating_roas = validation_data.get("data", {}).get("validating_roas", [])
            prefix = validation_data.get("data", {}).get("prefix", "")
            resource = validation_data.get("data", {}).get("resource", "")
            response += f"Status: {status}\n"
            response += f"Prefix: {prefix}\n"
            response += f"Resource: {resource}\n"
            response += "Validating ROAs:\n"
            for roa in validating_roas:
                response += f"  Origin: {roa.get('origin', '')}\n"
                response += f"  Prefix: {roa.get('prefix', '')}\n"
                response += f"  Max Length: {roa.get('max_length', '')}\n"
                response += f"  Validity: {roa.get('validity', '')}\n"
                response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve RPKI validation status")
            response = "Failed to retrieve RPKI validation status."
        return response

    def handle_get_rpki_history(self, arguments):
        self.logging_utility.info("Retrieving RPKI history")
        resource = arguments.get("resource", None)
        family = arguments.get("family", 4)
        resolution = arguments.get("resolution", None)
        delegated = arguments.get("delegated", False)
        history_data = self.ripe_stat_service.get_rpki_history(
            resource, family, resolution, delegated
        )
        if history_data:
            response = "RPKI History:\n\n"
            timeseries = history_data.get("data", {}).get("timeseries", [])
            for data_point in timeseries:
                resource = (
                    data_point.get("prefix", "")
                    or data_point.get("asn", "")
                    or data_point.get("cc", "")
                    or data_point.get("trust_anchor", "")
                )
                family = data_point.get("family", "")
                vrp_count = data_point.get("rpki", {}).get("vrp_count", 0)
                time = data_point.get("time", "")
                response += f"Resource: {resource}\n"
                response += f"Family: {family}\n"
                response += f"VRP Count: {vrp_count}\n"
                response += f"Time: {time}\n"
                if delegated:
                    delegated_data = data_point.get("delegated", {})
                    prefixes_count = delegated_data.get("prefixes", {}).get("count", 0)
                    prefixes_covered_by_rpki = (
                        delegated_data.get("prefixes", {})
                        .get("covered_by_rpki", {})
                        .get("count", 0)
                    )
                    space_count = delegated_data.get("space", {}).get("count", 0)
                    space_covered_by_rpki = (
                        delegated_data.get("space", {})
                        .get("covered_by_rpki", {})
                        .get("count", 0)
                    )
                    response += "Delegated Data:\n"
                    response += f"  Prefixes Count: {prefixes_count}\n"
                    response += (
                        f"  Prefixes Covered by RPKI: {prefixes_covered_by_rpki}\n"
                    )
                    response += f"  Space Count: {space_count}\n"
                    response += f"  Space Covered by RPKI: {space_covered_by_rpki}\n"
                response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve RPKI history")
            response = "Failed to retrieve RPKI history."
        return response

    def handle_get_searchcomplete(self, arguments):
        self.logging_utility.info("Retrieving searchcomplete")
        resource = arguments.get("resource", None)
        limit = arguments.get("limit", 6)

        ripe_stat_service = RipeStatService()
        searchcomplete_data = ripe_stat_service.get_searchcomplete(resource, limit)

        if searchcomplete_data:
            response = "Searchcomplete:\n\n"
            categories = searchcomplete_data.get("data", {}).get("categories", [])

            for category in categories:
                category_name = category.get("category", "")
                suggestions = category.get("suggestions", [])
                response += f"{category_name}:\n"
                for suggestion in suggestions:
                    label = suggestion.get("label", "")
                    value = suggestion.get("value", "")
                    response += f"  Label: {label}\n"
                    response += f"  Value: {value}\n"
                response += "\n"

            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve searchcomplete")
            response = "Failed to retrieve searchcomplete."

        return response

    def handle_get_looking_glass(self, arguments):
        self.logging_utility.info("Retrieving Looking Glass information")
        resource = arguments.get("resource", None)
        looking_glass_data = self.ripe_stat_service.get_looking_glass(resource)
        if looking_glass_data:
            response = "Looking Glass Data:\n\n"
            rrcs = looking_glass_data.get("data", {}).get("rrcs", [])
            for rrc in rrcs:
                response += f"RRC: {rrc.get('rrc', '')}\n"
                response += f"Location: {rrc.get('location', '')}\n"
                response += "Peers:\n"
                for peer in rrc.get("peers", []):
                    response += f"  - ASN: {peer.get('asn', '')}\n"
                    response += f"    IP: {peer.get('ip', '')}\n"
                    response += f"    Origin: {peer.get('origin', '')}\n"
                    response += f"    Prefix: {peer.get('prefix', '')}\n"
                    response += f"    Next Hop: {peer.get('next_hop', '')}\n"
                    response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve Looking Glass data")
            response = "Failed to retrieve Looking Glass data."
        return response

    def handle_get_whats_my_ip(self, arguments):
        self.logging_utility.info("Retrieving What's My IP information")
        whats_my_ip_data = self.ripe_stat_service.get_whats_my_ip()
        if whats_my_ip_data:
            response = "What's My IP Data:\n\n"
            ip = whats_my_ip_data.get("data", {}).get("ip", "")
            response += f"IP Address: {ip}\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve What's My IP data")
            response = "Failed to retrieve What's My IP data."
        return response

    def handle_get_zonemaster_overview(self, arguments):
        self.logging_utility.info("Retrieving Zonemaster overview")
        resource = arguments.get("resource", None)
        zonemaster_overview_data = self.ripe_stat_service.get_zonemaster(resource)
        if zonemaster_overview_data:
            response = "Zonemaster Overview Data:\n\n"
            result = zonemaster_overview_data.get("data", {}).get("result", [])
            for item in result:
                response += f"ID: {item.get('id', '')}\n"
                response += f"Creation Time: {item.get('creation_time', '')}\n"
                response += f"Overall Result: {item.get('overall_result', '')}\n"
                response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve Zonemaster overview data")
            response = "Failed to retrieve Zonemaster overview data."
        return response

    def handle_get_zonemaster_details(self, arguments):
        self.logging_utility.info("Retrieving Zonemaster details")
        resource = arguments.get("resource", None)
        method = "details"
        zonemaster_details_data = self.ripe_stat_service.get_zonemaster(
            resource, method
        )
        if zonemaster_details_data:
            response = "Zonemaster Details Data:\n\n"
            result = zonemaster_details_data.get("data", {}).get("result", {})
            response += f"ID: {result.get('id', '')}\n"
            response += f"Creation Time: {result.get('creation_time', '')}\n"
            response += "Results:\n"
            for item in result.get("results", []):
                response += f"  - Module: {item.get('module', '')}\n"
                response += f"    Level: {item.get('level', '')}\n"
                response += f"    Message: {item.get('message', '')}\n"
                response += "\n"
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve Zonemaster details data")
            response = "Failed to retrieve Zonemaster details data."
        return response

    def handle_get_mlab_bandwidth(self, arguments):
        self.logging_utility.info("Retrieving M-Lab bandwidth measurements")
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        bandwidth_data = self.ripe_stat_service.get_mlab_bandwidth(
            resource, starttime, endtime
        )
        if bandwidth_data:
            response = "M-Lab Bandwidth Measurements:\n\n"
            bandwidths = bandwidth_data.get("data", {}).get("bandwidths", [])
            response += f"Bandwidths (Mbps):\n"
            for bandwidth in bandwidths:
                response += f"- {bandwidth}\n"
            response += f"\nQuery Start Time: {bandwidth_data.get('data', {}).get('query_starttime', '')}\n"
            response += f"Query End Time: {bandwidth_data.get('data', {}).get('query_endtime', '')}\n"
            response += (
                f"Resource: {bandwidth_data.get('data', {}).get('resource', '')}\n"
            )
            response += "---\n"
        else:
            self.logging_utility.warning(
                "Failed to retrieve M-Lab bandwidth measurements"
            )
            response = "Failed to retrieve M-Lab bandwidth measurements."
        return response

    def handle_get_mlab_clients(self, arguments):
        self.logging_utility.info("Retrieving M-Lab client information")
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        clients_data = self.ripe_stat_service.get_mlab_clients(
            resource, starttime, endtime
        )
        if clients_data:
            response = "M-Lab Client Information:\n\n"
            clients = clients_data.get("data", {}).get("clients", {})
            for ip, client_info in clients.items():
                response += f"IP Address: {ip}\n"
                response += f"  Number of Tests: {client_info.get('num_tests', 0)}\n"
                response += f"  Country: {client_info.get('country', '')}\n"
                response += f"  City: {client_info.get('city', '')}\n"
                response += f"  Latitude: {client_info.get('latitude', 0)}\n"
                response += f"  Longitude: {client_info.get('longitude', 0)}\n"
                response += "\n"
            response += f"Number of Clients: {clients_data.get('data', {}).get('nr_clients', 0)}\n"
            response += f"Percentage Coverage: {clients_data.get('data', {}).get('perc_coverage', 0)}\n"
            response += f"Query Start Time: {clients_data.get('data', {}).get('query_starttime', '')}\n"
            response += f"Query End Time: {clients_data.get('data', {}).get('query_endtime', '')}\n"
            response += (
                f"Resource: {clients_data.get('data', {}).get('resource', '')}\n"
            )
            response += "---\n"
        else:
            self.logging_utility.warning("Failed to retrieve M-Lab client information")
            response = "Failed to retrieve M-Lab client information."
        return response
