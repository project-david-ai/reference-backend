# backend/app/services/function_call_service.py
import requests
from backend.app.services.logging_service.logger import LoggingUtility
from backend.app.services.api_service_external.api_public_access.api_uk_statistics.ons.api_uk_ons import OnsApiService
from backend.app.services.api_service_external.api_public_access.api_network_engineering.ripe.api_ripe_stat_service import RipeStatService
from backend.app.services.api_service_external.api_proprietary_access.api_openai.image_generator_service import ImageGeneratorService
from backend.app.services.api_service_internal.project_david.user_details_service import UserDetailsService


logging_utility = LoggingUtility()


class FunctionCallService:

    def __init__(self):
        self.function_handlers = {
            "getLocationInfo": self.handle_get_location_info,
            "generateImage": self.handle_generate_image,
            "getOnsDataSets": self.handle_get_ons_datasets,
            "getOnsDatasetByEndpoint": self.handle_get_ons_dataset_by_endpoint,
            "getUkBusinessData": self.handle_get_uk_business_data,
            "getWellbeingQuarterlyData": self.handle_get_wellbeing_quarterly_data,
            "getWellbeingByLocalAuthorityData": self.handle_get_wellbeing_by_local_authority_data,
            "getWeeklyDeathsAgeAndSexData": self.handle_get_weekly_deaths_age_and_sex_data,
            "getSexualOrientationByAgeAndSexData": self.handle_get_sexual_orientation_by_age_and_sex_data,
            "getUkSpendingOnCardsData": self.handle_get_uk_spending_on_cards_data,
            "getTradeData": self.handle_get_trade_data,
            "getTaxBenefitsStatisticsData": self.handle_get_tax_benefits_statistics_data,
            "getWeeklyDeathsRegionData": self.handle_get_weekly_deaths_region_data,
            "getRetailSalesAllBusinessesData": self.handle_get_retail_sales_all_businesses_data,
            "getRegionalGdpByYearData": self.handle_get_regional_gdp_by_year_data,
            "getWeeklyDeathsLocalAuthorityData": self.handle_get_weekly_deaths_local_authority_data,
            "getProjectionsOlderPeopleSexRatiosData": self.handle_get_projections_older_people_sex_ratios_data,
            # Network Engineering/Ripe
            "getAbuseContacts": self.handle_get_abuse_contacts,
            "getAddressSpaceHierarchy": self.handle_get_address_space_hierarchy,
            "getAddressSpaceUsage": self.handle_get_address_space_usage,
            "getAnnouncedPrefixes": self.handle_get_announced_prefixes,
            "getAllocationHistory": self.handle_get_allocation_history,
            "getAsnNeighbours": self.handle_get_asn_neighbours,
            "getAtlasProbes": self.handle_get_atlas_probes,
            "getBgpUpdates": self.handle_get_bgp_updates,
            "getAsnNeighboursHistory": self.handle_get_asn_neighbours_history,
            "getCountryResourceStats": self.handle_get_country_resource_stats,
            "getCountryResourceList": self.handle_get_country_resource_list,
            "getDnsChain": self.handle_get_dns_chain,
            "getExampleResources": self.handle_get_example_resources,
            "getHistoricalWhois": self.handle_get_historical_whois,
            "getIanaRegistryInfo": self.handle_get_iana_registry_info,
            "getRoutingHistory": self.handle_get_routing_history,
            "getRoutingStatus": self.handle_get_routing_status,
            "getRrcInfo": self.handle_get_rrc_info,
            "getRpkiValidationStatus": self.handle_get_rpki_validation_status,
            "getRpkiHistory": self.handle_get_rpki_history,
            "getSearchcomplete": self.handle_get_searchcomplete,
            # User services
            "getUserDetailsByFauxIdentity": self.handle_get_user_details_by_faux_identity


        }

    def call_function(self, function_name, arguments):
        if function_name not in self.function_handlers:
            logging_utility.error("Unsupported function: %s", function_name)
            return "Error: Unsupported function"

        return self.function_handlers[function_name](arguments)

    def handle_get_location_info(self, arguments):
        location = arguments["location"]
        location_info = self.fetch_location_info(location)
        return location_info

    def fetch_location_info(self, location):
        logging_utility.info('Fetching location information for: %s', location)
        # For demonstration purposes, let's simulate a successful API call
        return f"Location: {location}, Country: USA, Population: 2,000,000"

    def handle_generate_image(self, arguments):
        image_description = arguments["imageDescription"]
        image_gen_service = ImageGeneratorService()
        try:
            image_url = image_gen_service.generate_image(prompt=image_description)
            if image_url:
                return image_url
            else:
                return "Failed to generate image."
        except Exception as e:
            logging_utility.error("An error occurred while generating the image: %s", str(e))
            return "An error occurred while generating the image."

    def inform_image_capability_under_development(self, image_description):
        logging_utility.info('User requested image generation: %s', image_description)
        response = "I apologize for the inconvenience, but the image generation capability is currently under development. In the meantime, please speak with my brother David for any image-related requests. You can reach him at: https://chat.openai.com/g/g-7oUtFOMf3-david"
        return response

    def handle_get_ons_datasets(self, arguments):
        logging_utility.info('Retrieving ONS datasets')
        limit = arguments.get("limit", 20)
        offset = arguments.get("offset", 0)
        ons_api_service = OnsApiService()
        dataset_data = ons_api_service.get_dataset_data(limit, offset)
        if dataset_data:
            # Access the 'items' key in the JSON response
            dataset_items = dataset_data.get('items', [])
            # Prepare the response string
            response = "Available ONS Datasets:\n\n"
            for item in dataset_items:
                response += f"Dataset ID: {item.get('id')}\n"
                response += f"Dataset Title: {item.get('title')}\n"
                response += f"Dataset Description: {item.get('description')}\n"
                response += f"Dataset URL: {item.get('links', {}).get('latest_version', {}).get('href')}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve ONS dataset data')
            response = "Failed to retrieve dataset data."
        return response

    def handle_get_ons_dataset_by_endpoint(self, arguments):
        endpoint = arguments["endpoint"]

        try:
            response = requests.get(endpoint)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()

            dataset_info = {
                "id": data["id"],
                "title": data["collection_id"],  # Assuming the collection_id represents the dataset title
                "edition": data["edition"],
                "version": data["version"],
                "release_date": data["release_date"],
                "downloads": data["downloads"],
                "dimensions": [dim["label"] for dim in data["dimensions"]],
                "usage_notes": [note["title"] for note in data["usage_notes"]]
            }

            return dataset_info

        except requests.exceptions.RequestException as e:
            logging_utility.error("Error retrieving dataset information: %s", str(e))
            return "Error: Failed to retrieve dataset information"

    def handle_get_uk_business_data(self, arguments):
        logging_utility.info('Retrieving UK business data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        uk_business_data = ons_api_service.get_uk_business_data(dimensions)

        if uk_business_data:
            response = "UK Business Data:\n\n"
            for item in uk_business_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve UK business data')
            response = "Failed to retrieve UK business data."

        return response

    def handle_get_wellbeing_quarterly_data(self, arguments):
        logging_utility.info('Retrieving wellbeing quarterly data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        wellbeing_data = ons_api_service.get_wellbeing_quarterly_data(dimensions)

        if wellbeing_data:
            response = "Wellbeing Quarterly Data:\n\n"
            for item in wellbeing_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve wellbeing quarterly data')
            response = "Failed to retrieve wellbeing quarterly data."

        return response

    def handle_get_wellbeing_by_local_authority_data(self, arguments):
        logging_utility.info('Retrieving wellbeing by local authority data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        wellbeing_data = ons_api_service.get_wellbeing_by_local_authority_data(dimensions)

        if wellbeing_data:
            response = "Wellbeing by Local Authority Data:\n\n"
            for item in wellbeing_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve wellbeing by local authority data')
            response = "Failed to retrieve wellbeing by local authority data."

        return response

    def handle_get_weekly_deaths_age_and_sex_data(self, arguments):
        logging_utility.info('Retrieving weekly deaths by age and sex data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        deaths_data = ons_api_service.get_weekly_deaths_age_sex_data(dimensions)

        if deaths_data:
            response = "Weekly Deaths by Age and Sex Data:\n\n"
            for item in deaths_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve weekly deaths by age and sex data')
            response = "Failed to retrieve weekly deaths by age and sex data."

        return response

    def handle_get_sexual_orientation_by_age_and_sex_data(self, arguments):
        logging_utility.info('Retrieving sexual orientation by age and sex data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        orientation_data = ons_api_service.get_sexual_orientation_by_age_and_sex_data(dimensions)

        if orientation_data:
            response = "Sexual Orientation by Age and Sex Data:\n\n"
            for item in orientation_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve sexual orientation by age and sex data')
            response = "Failed to retrieve sexual orientation by age and sex data."

        return response

    def handle_get_uk_spending_on_cards_data(self, arguments):
        logging_utility.info('Retrieving UK spending on cards data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        spending_data = ons_api_service.get_uk_spending_on_cards_data(dimensions)

        if spending_data:
            response = "UK Spending on Cards Data:\n\n"
            for item in spending_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve UK spending on cards data')
            response = "Failed to retrieve UK spending on cards data."

        return response

    def handle_get_trade_data(self, arguments):
        logging_utility.info('Retrieving trade data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        trade_data = ons_api_service.get_trade_data(dimensions)

        if trade_data:
            response = "Trade Data:\n\n"
            for item in trade_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve trade data')
            response = "Failed to retrieve trade data."

        return response

    def handle_get_tax_benefits_statistics_data(self, arguments):
        logging_utility.info('Retrieving tax benefits statistics data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        tax_benefits_data = ons_api_service.get_tax_benefits_statistics_data(dimensions)

        if tax_benefits_data:
            response = "Tax Benefits Statistics Data:\n\n"
            for item in tax_benefits_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve tax benefits statistics data')
            response = "Failed to retrieve tax benefits statistics data."

        return response

    def handle_get_weekly_deaths_region_data(self, arguments):
        logging_utility.info('Retrieving weekly deaths by region data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        deaths_data = ons_api_service.get_weekly_deaths_region_data(dimensions)

        if deaths_data:
            response = "Weekly Deaths by Region Data:\n\n"
            for item in deaths_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve weekly deaths by region data')
            response = "Failed to retrieve weekly deaths by region data."

        return response

    def handle_get_retail_sales_all_businesses_data(self, arguments):
        logging_utility.info('Retrieving retail sales all businesses data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        sales_data = ons_api_service.get_retail_sales_all_businesses_data(dimensions)

        if sales_data:
            response = "Retail Sales All Businesses Data:\n\n"
            for item in sales_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve retail sales all businesses data')
            response = "Failed to retrieve retail sales all businesses data."

        return response

    def handle_get_regional_gdp_by_year_data(self, arguments):
        logging_utility.info('Retrieving regional GDP by year data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        gdp_data = ons_api_service.get_regional_gdp_by_year_data(dimensions)

        if gdp_data:
            response = "Regional GDP by Year Data:\n\n"
            for item in gdp_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve regional GDP by year data')
            response = "Failed to retrieve regional GDP by year data."

        return response

    def handle_get_weekly_deaths_local_authority_data(self, arguments):
        logging_utility.info('Retrieving weekly deaths by local authority data')
        dimensions = arguments.get("dimensions", None)

        ons_api_service = OnsApiService()
        deaths_data = ons_api_service.get_weekly_deaths_local_authority_data(dimensions)

        if deaths_data:
            response = "Weekly Deaths by Local Authority Data:\n\n"
            for item in deaths_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve weekly deaths by local authority data')
            response = "Failed to retrieve weekly deaths by local authority data."

        return response

    def handle_get_projections_older_people_sex_ratios_data(self, arguments):
           logging_utility.info('Retrieving projections older people sex ratios data')
           dimensions = arguments.get("dimensions", None)

           ons_api_service = OnsApiService()
           sex_ratios_data = ons_api_service.get_projections_older_people_sex_ratios_data(dimensions)

           if sex_ratios_data:
               response = "Projections Older People Sex Ratios Data:\n\n"
               for item in sex_ratios_data:
                   for key, value in item.items():
                       response += f"{key}: {value}\n"
                   response += "---\n"
           else:
               logging_utility.warning('Failed to retrieve projections older people sex ratios data')
               response = "Failed to retrieve projections older people sex ratios data."

           return response

    def handle_get_abuse_contacts(self, arguments):
        logging_utility.info('Retrieving abuse contacts')
        resource = arguments.get("resource", None)

        ripe_stat_service = RipeStatService()
        abuse_contacts_data = ripe_stat_service.get_abuse_contact(resource)

        if abuse_contacts_data:
            response = "Abuse Contacts:\n\n"
            abuse_contacts = abuse_contacts_data.get('data', {}).get('abuse_contacts', [])
            for contact in abuse_contacts:
                response += f"Contact: {contact}\n"
            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve abuse contacts')
            response = "Failed to retrieve abuse contacts."

        return response

    def handle_get_address_space_hierarchy(self, arguments):
        logging_utility.info('Retrieving address space hierarchy')
        resource = arguments.get("resource", None)

        ripe_stat_service = RipeStatService()
        hierarchy_data = ripe_stat_service.get_address_space_hierarchy(resource)

        if hierarchy_data:
            response = "Address Space Hierarchy:\n\n"
            exact_matches = hierarchy_data.get('data', {}).get('exact', [])
            less_specific = hierarchy_data.get('data', {}).get('less_specific', [])
            more_specific = hierarchy_data.get('data', {}).get('more_specific', [])

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
            logging_utility.warning('Failed to retrieve address space hierarchy')
            response = "Failed to retrieve address space hierarchy."

        return response

    def handle_get_address_space_usage(self, arguments):
        logging_utility.info('Retrieving address space usage')
        resource = arguments.get("resource", None)
        all_level_more_specifics = arguments.get("all_level_more_specifics", True)

        ripe_stat_service = RipeStatService()
        usage_data = ripe_stat_service.get_address_space_usage(resource, all_level_more_specifics)

        if usage_data:
            response = "Address Space Usage:\n\n"
            allocations = usage_data.get('data', {}).get('allocations', [])
            assignments = usage_data.get('data', {}).get('assignments', [])
            ip_stats = usage_data.get('data', {}).get('ip_stats', [])

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
            logging_utility.warning('Failed to retrieve address space usage')
            response = "Failed to retrieve address space usage."

        return response

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

    def handle_get_allocation_history(self, arguments):
        logging_utility.info('Retrieving allocation history')
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)

        ripe_stat_service = RipeStatService()
        allocation_data = ripe_stat_service.get_allocation_history(resource, starttime, endtime)

        if allocation_data:
            response = "Allocation History:\n\n"
            results = allocation_data.get('data', {}).get('results', {})

            for rir, allocations in results.items():
                response += f"{rir}:\n"
                for allocation in allocations:
                    resource = allocation.get('resource', '')
                    status = allocation.get('status', '')
                    timelines = allocation.get('timelines', [])
                    response += f"- Resource: {resource}\n  Status: {status}\n  Timelines:\n"
                    for timeline in timelines:
                        starttime = timeline.get('starttime', '')
                        endtime = timeline.get('endtime', '')
                        response += f"  - Start: {starttime}, End: {endtime}\n"
                response += "\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve allocation history')
            response = "Failed to retrieve allocation history."

        return response

    def handle_get_announced_prefixes(self, arguments):
        logging_utility.info('Retrieving announced prefixes')
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        min_peers_seeing = arguments.get("min_peers_seeing", 10)

        ripe_stat_service = RipeStatService()
        prefixes_data = ripe_stat_service.get_announced_prefixes(resource, starttime, endtime, min_peers_seeing)

        if prefixes_data:
            response = "Announced Prefixes:\n\n"
            prefixes = prefixes_data.get('data', {}).get('prefixes', [])

            for prefix_data in prefixes:
                prefix = prefix_data.get('prefix', '')
                timelines = prefix_data.get('timelines', [])
                response += f"Prefix: {prefix}\n"
                response += "Timelines:\n"
                for timeline in timelines:
                    starttime = timeline.get('starttime', '')
                    endtime = timeline.get('endtime', '')
                    response += f"- Start: {starttime}, End: {endtime}\n"
                response += "\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve announced prefixes')
            response = "Failed to retrieve announced prefixes."

        return response

    def handle_get_asn_neighbours(self, arguments):
        logging_utility.info('Retrieving ASN neighbours')
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)

        ripe_stat_service = RipeStatService()
        neighbours_data = ripe_stat_service.get_asn_neighbours(resource, starttime)

        if neighbours_data:
            response = "ASN Neighbours:\n\n"
            neighbour_counts = neighbours_data.get('data', {}).get('neighbour_counts', {})
            neighbours = neighbours_data.get('data', {}).get('neighbours', [])

            response += f"Neighbour Counts: Left: {neighbour_counts.get('left', 0)}, Right: {neighbour_counts.get('right', 0)}, Uncertain: {neighbour_counts.get('uncertain', 0)}, Unique: {neighbour_counts.get('unique', 0)}\n\n"

            for neighbour in neighbours:
                asn = neighbour.get('asn', '')
                neighbour_type = neighbour.get('type', '')
                power = neighbour.get('power', '')
                v4_peers = neighbour.get('v4_peers', '')
                v6_peers = neighbour.get('v6_peers', '')
                response += f"ASN: {asn}, Type: {neighbour_type}, Power: {power}, IPv4 Peers: {v4_peers}, IPv6 Peers: {v6_peers}\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve ASN neighbours')
            response = "Failed to retrieve ASN neighbours."

        return response

    def handle_get_atlas_probes(self, arguments):
        logging_utility.info('Retrieving Atlas probes')
        resource = arguments.get("resource", None)

        ripe_stat_service = RipeStatService()
        probes_data = ripe_stat_service.get_atlas_probes(resource)

        if probes_data:
            response = "Atlas Probes:\n\n"
            probes = probes_data.get('data', {}).get('probes', [])

            for probe in probes:
                probe_id = probe.get('id', '')
                status = probe.get('status_name', '')
                address_v4 = probe.get('address_v4', '')
                address_v6 = probe.get('address_v6', '')
                asn_v4 = probe.get('asn_v4', '')
                asn_v6 = probe.get('asn_v6', '')
                country_code = probe.get('country_code', '')
                response += f"Probe ID: {probe_id}, Status: {status}, IPv4: {address_v4}, IPv6: {address_v6}, ASN v4: {asn_v4}, ASN v6: {asn_v6}, Country: {country_code}\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve Atlas probes')
            response = "Failed to retrieve Atlas probes."

        return response

    def handle_get_bgp_updates(self, arguments):
        logging_utility.info('Retrieving BGP updates')
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        rrcs = arguments.get("rrcs", None)
        unix_timestamps = arguments.get("unix_timestamps", False)

        ripe_stat_service = RipeStatService()
        updates_data = ripe_stat_service.get_bgp_updates(resource, starttime, endtime, rrcs, unix_timestamps)

        if updates_data:
            response = "BGP Updates:\n\n"
            updates = updates_data.get('data', {}).get('updates', [])

            for update in updates:
                update_type = update.get('type', '')
                timestamp = update.get('timestamp', '')
                target_prefix = update.get('attrs', {}).get('target_prefix', '')
                path = update.get('attrs', {}).get('path', [])
                community = update.get('attrs', {}).get('community', [])
                source_id = update.get('attrs', {}).get('source_id', '')
                response += f"Type: {update_type}, Timestamp: {timestamp}, Prefix: {target_prefix}, Path: {path}, Community: {community}, Source ID: {source_id}\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve BGP updates')
            response = "Failed to retrieve BGP updates."

        return response

    def handle_get_asn_neighbours_history(self, arguments):
        logging_utility.info('Retrieving ASN neighbours history')
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        max_rows = arguments.get("max_rows", 1800)

        ripe_stat_service = RipeStatService()
        history_data = ripe_stat_service.get_asn_neighbours_history(resource, starttime, endtime, max_rows)

        if history_data:
            response = "ASN Neighbours History:\n\n"
            neighbours = history_data.get('data', {}).get('neighbours', [])

            for neighbour in neighbours:
                asn = neighbour.get('neighbour', '')
                timelines = neighbour.get('timelines', [])
                response += f"ASN: {asn}\n"
                for timeline in timelines:
                    starttime = timeline.get('starttime', '')
                    endtime = timeline.get('endtime', '')
                    response += f"  Start: {starttime}, End: {endtime}\n"
                response += "\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve ASN neighbours history')
            response = "Failed to retrieve ASN neighbours history."

        return response

    def handle_get_country_resource_stats(self, arguments):
        logging_utility.info('Retrieving country resource stats')
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        resolution = arguments.get("resolution", None)

        ripe_stat_service = RipeStatService()
        stats_data = ripe_stat_service.get_country_resource_stats(resource, starttime, endtime, resolution)

        if stats_data:
            response = "Country Resource Stats:\n\n"
            stats = stats_data.get('data', {}).get('stats', [])

            for stat in stats:
                asns_ris = stat.get('asns_ris', 0)
                asns_stats = stat.get('asns_stats', 0)
                v4_prefixes_ris = stat.get('v4_prefixes_ris', 0)
                v4_prefixes_stats = stat.get('v4_prefixes_stats', 0)
                v6_prefixes_ris = stat.get('v6_prefixes_ris', 0)
                v6_prefixes_stats = stat.get('v6_prefixes_stats', 0)
                timeline = stat.get('timeline', [])

                response += f"ASNs RIS: {asns_ris}, ASNs Stats: {asns_stats}\n"
                response += f"IPv4 Prefixes RIS: {v4_prefixes_ris}, IPv4 Prefixes Stats: {v4_prefixes_stats}\n"
                response += f"IPv6 Prefixes RIS: {v6_prefixes_ris}, IPv6 Prefixes Stats: {v6_prefixes_stats}\n"
                response += "Timeline:\n"
                for item in timeline:
                    starttime = item.get('starttime', '')
                    endtime = item.get('endtime', '')
                    response += f"  Start: {starttime}, End: {endtime}\n"
                response += "\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve country resource stats')
            response = "Failed to retrieve country resource stats."

        return response

    def handle_get_country_resource_list(self, arguments):
        logging_utility.info('Retrieving country resource list')
        resource = arguments.get("resource", None)
        time = arguments.get("time", None)
        v4_format = arguments.get("v4_format", None)

        ripe_stat_service = RipeStatService()
        resource_data = ripe_stat_service.get_country_resource_list(resource, time, v4_format)

        if resource_data:
            response = "Country Resource List:\n\n"
            resources = resource_data.get('data', {}).get('resources', {})

            asn_list = resources.get('asn', [])
            ipv4_list = resources.get('ipv4', [])
            ipv6_list = resources.get('ipv6', [])

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
            logging_utility.warning('Failed to retrieve country resource list')
            response = "Failed to retrieve country resource list."

        return response

    def handle_get_dns_chain(self, arguments):
        logging_utility.info('Retrieving DNS chain')
        resource = arguments.get("resource", None)

        ripe_stat_service = RipeStatService()
        dns_data = ripe_stat_service.get_dns_chain(resource)

        if dns_data:
            response = "DNS Chain:\n\n"
            forward_nodes = dns_data.get('data', {}).get('forward_nodes', {})
            reverse_nodes = dns_data.get('data', {}).get('reverse_nodes', {})
            nameservers = dns_data.get('data', {}).get('nameservers', [])
            authoritative_nameservers = dns_data.get('data', {}).get('authoritative_nameservers', [])

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
            logging_utility.warning('Failed to retrieve DNS chain')
            response = "Failed to retrieve DNS chain."

        return response

    def handle_get_example_resources(self, arguments):
        logging_utility.info('Retrieving example resources')

        ripe_stat_service = RipeStatService()
        example_data = ripe_stat_service.get_example_resources()

        if example_data:
            response = "Example Resources:\n\n"
            asn = example_data.get('data', {}).get('asn', '')
            ipv4 = example_data.get('data', {}).get('ipv4', '')
            ipv6 = example_data.get('data', {}).get('ipv6', '')
            range4 = example_data.get('data', {}).get('range4', '')

            response += f"ASN: {asn}\n"
            response += f"IPv4: {ipv4}\n"
            response += f"IPv6: {ipv6}\n"
            response += f"IPv4 Range: {range4}\n"
            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve example resources')
            response = "Failed to retrieve example resources."

        return response

    def handle_get_historical_whois(self, arguments):
        logging_utility.info('Retrieving historical whois')
        resource = arguments.get("resource", None)
        version = arguments.get("version", None)

        ripe_stat_service = RipeStatService()
        whois_data = ripe_stat_service.get_historical_whois(resource, version)

        if whois_data:
            response = "Historical Whois:\n\n"
            objects = whois_data.get('data', {}).get('objects', [])

            for obj in objects:
                response += f"Object Type: {obj.get('type', '')}\n"
                response += f"Object Key: {obj.get('key', '')}\n"
                response += "Attributes:\n"
                for attr in obj.get('attributes', []):
                    response += f"  {attr.get('attribute', '')}: {attr.get('value', '')}\n"
                response += "\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve historical whois')
            response = "Failed to retrieve historical whois."

        return response

    def handle_get_iana_registry_info(self, arguments):
        logging_utility.info('Retrieving IANA registry info')
        resource = arguments.get("resource", None)
        best_match_only = arguments.get("best_match_only", False)

        ripe_stat_service = RipeStatService()
        registry_data = ripe_stat_service.get_iana_registry_info(resource, best_match_only)

        if registry_data:
            response = "IANA Registry Info:\n\n"
            resources = registry_data.get('data', {}).get('resources', [])

            for res in resources:
                resource = res.get('resource', '')
                description = res.get('description', '')
                source_url = res.get('source_url', '')
                source = res.get('source', '')
                details = res.get('details', {})

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
            logging_utility.warning('Failed to retrieve IANA registry info')
            response = "Failed to retrieve IANA registry info."

        return response

    def handle_get_routing_history(self, arguments):
        logging_utility.info('Retrieving routing history')
        resource = arguments.get("resource", None)
        starttime = arguments.get("starttime", None)
        endtime = arguments.get("endtime", None)
        min_peers = arguments.get("min_peers", 10)

        ripe_stat_service = RipeStatService()
        history_data = ripe_stat_service.get_routing_history(resource, starttime, endtime, min_peers)

        if history_data:
            response = "Routing History:\n\n"
            by_origin = history_data.get('data', {}).get('by_origin', [])

            for origin_data in by_origin:
                origin = origin_data.get('origin', '')
                prefixes = origin_data.get('prefixes', [])

                response += f"Origin: {origin}\n"
                for prefix_data in prefixes:
                    prefix = prefix_data.get('prefix', '')
                    timelines = prefix_data.get('timelines', [])

                    response += f"Prefix: {prefix}\n"
                    for timeline in timelines:
                        starttime = timeline.get('starttime', '')
                        endtime = timeline.get('endtime', '')
                        response += f"  Start: {starttime}, End: {endtime}\n"
                    response += "\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve routing history')
            response = "Failed to retrieve routing history."

        return response

    def handle_get_routing_status(self, arguments):
        logging_utility.info('Retrieving routing status')
        resource = arguments.get("resource", None)
        timestamp = arguments.get("timestamp", None)
        min_peers_seeing = arguments.get("min_peers_seeing", 10)

        ripe_stat_service = RipeStatService()
        status_data = ripe_stat_service.get_routing_status(resource, timestamp, min_peers_seeing)

        if status_data:
            response = "Routing Status:\n\n"
            first_seen = status_data.get('data', {}).get('first_seen', {})
            last_seen = status_data.get('data', {}).get('last_seen', {})
            visibility = status_data.get('data', {}).get('visibility', {})
            announced_space = status_data.get('data', {}).get('announced_space', {})

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
            response += f"  IPv4 Prefixes: {announced_space.get('v4', {}).get('prefixes', 0)}\n"
            response += f"  IPv4 IPs: {announced_space.get('v4', {}).get('ips', 0)}\n"
            response += f"  IPv6 Prefixes: {announced_space.get('v6', {}).get('prefixes', 0)}\n"
            response += f"  IPv6 /48s: {announced_space.get('v6', {}).get('slash_48s', 0)}\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve routing status')
            response = "Failed to retrieve routing status."

        return response

    def handle_get_rrc_info(self, arguments):
        logging_utility.info('Retrieving RRC info')

        ripe_stat_service = RipeStatService()
        rrc_data = ripe_stat_service.get_rrc_info()

        if rrc_data:
            response = "RRC Info:\n\n"
            rrcs = rrc_data.get('data', {}).get('rrcs', [])

            for rrc in rrcs:
                rrc_id = rrc.get('id', '')
                rrc_name = rrc.get('name', '')
                location = rrc.get('location', '')
                response += f"RRC: {rrc_id}\n"
                response += f"  Name: {rrc_name}\n"
                response += f"  Location: {location}\n"
                response += "  Peers:\n"
                for peer in rrc.get('peers', []):
                    response += f"    ASN: {peer.get('asn', '')}\n"
                    response += f"    IP: {peer.get('ip', '')}\n"
                    response += f"    IPv4 Prefix Count: {peer.get('v4_prefix_count', 0)}\n"
                    response += f"    IPv6 Prefix Count: {peer.get('v6_prefix_count', 0)}\n"
                response += "\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve RRC info')
            response = "Failed to retrieve RRC info."

        return response

    def handle_get_rpki_validation_status(self, arguments):
        logging_utility.info('Retrieving RPKI validation status')
        resource = arguments.get("resource", None)
        prefix = arguments.get("prefix", None)

        ripe_stat_service = RipeStatService()
        validation_data = ripe_stat_service.get_rpki_validation_status(resource, prefix)

        if validation_data:
            response = "RPKI Validation Status:\n\n"
            status = validation_data.get('data', {}).get('status', '')
            validating_roas = validation_data.get('data', {}).get('validating_roas', [])
            prefix = validation_data.get('data', {}).get('prefix', '')
            resource = validation_data.get('data', {}).get('resource', '')

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
            logging_utility.warning('Failed to retrieve RPKI validation status')
            response = "Failed to retrieve RPKI validation status."

        return response

    def handle_get_rpki_history(self, arguments):
        logging_utility.info('Retrieving RPKI history')
        resource = arguments.get("resource", None)
        family = arguments.get("family", 4)
        resolution = arguments.get("resolution", None)
        delegated = arguments.get("delegated", False)

        ripe_stat_service = RipeStatService()
        history_data = ripe_stat_service.get_rpki_history(resource, family, resolution, delegated)

        if history_data:
            response = "RPKI History:\n\n"
            timeseries = history_data.get('data', {}).get('timeseries', [])

            for data_point in timeseries:
                resource = data_point.get('prefix', '') or data_point.get('asn', '') or data_point.get('cc',
                                                                                                       '') or data_point.get(
                    'trust_anchor', '')
                family = data_point.get('family', '')
                vrp_count = data_point.get('rpki', {}).get('vrp_count', 0)
                time = data_point.get('time', '')

                response += f"Resource: {resource}\n"
                response += f"Family: {family}\n"
                response += f"VRP Count: {vrp_count}\n"
                response += f"Time: {time}\n"

                if delegated:
                    delegated_data = data_point.get('delegated', {})
                    prefixes_count = delegated_data.get('prefixes', {}).get('count', 0)
                    prefixes_covered_by_rpki = delegated_data.get('prefixes', {}).get('covered_by_rpki', {}).get(
                        'count', 0)
                    space_count = delegated_data.get('space', {}).get('count', 0)
                    space_covered_by_rpki = delegated_data.get('space', {}).get('covered_by_rpki', {}).get('count', 0)

                    response += "Delegated Data:\n"
                    response += f"  Prefixes Count: {prefixes_count}\n"
                    response += f"  Prefixes Covered by RPKI: {prefixes_covered_by_rpki}\n"
                    response += f"  Space Count: {space_count}\n"
                    response += f"  Space Covered by RPKI: {space_covered_by_rpki}\n"

                response += "\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve RPKI history')
            response = "Failed to retrieve RPKI history."

        return response

    def handle_get_searchcomplete(self, arguments):
        logging_utility.info('Retrieving searchcomplete')
        resource = arguments.get("resource", None)
        limit = arguments.get("limit", 6)

        ripe_stat_service = RipeStatService()
        searchcomplete_data = ripe_stat_service.get_searchcomplete(resource, limit)

        if searchcomplete_data:
            response = "Searchcomplete:\n\n"
            categories = searchcomplete_data.get('data', {}).get('categories', [])

            for category in categories:
                category_name = category.get('category', '')
                suggestions = category.get('suggestions', [])
                response += f"{category_name}:\n"
                for suggestion in suggestions:
                    label = suggestion.get('label', '')
                    value = suggestion.get('value', '')
                    response += f"  Label: {label}\n"
                    response += f"  Value: {value}\n"
                response += "\n"

            response += "---\n"
        else:
            logging_utility.warning('Failed to retrieve searchcomplete')
            response = "Failed to retrieve searchcomplete."

        return response

    def handle_get_user_details_by_faux_identity(self, arguments):
        logging_utility.info('Retrieving user details by faux identity')
        faux_identity = arguments.get("faux_identity", None)

        if faux_identity:
            base_url = 'http://localhost:5000'  # Replace with your API base URL
            user_details_service = UserDetailsService(base_url)
            user_details = user_details_service.get_user_details_by_faux_identity(faux_identity)

            if user_details:
                response = "User Details:\n\n"
                response += f"Username: {user_details.get('username', '')}\n"
                response += f"Email: {user_details.get('email', '')}\n"
                response += f"First Name: {user_details.get('first_name', '')}\n"
                response += f"Last Name: {user_details.get('last_name', '')}\n"
                response += f"Role: {user_details.get('role', '')}\n"
                response += f"Internal Role: {user_details.get('internal_role', '')}\n"
                response += f"Faux Identity: {user_details.get('faux_identity', '')}\n"
                response += "---\n"
            else:
                logging_utility.warning('Failed to retrieve user details for faux identity: %s', faux_identity)
                response = f"Failed to retrieve user details for faux identity: {faux_identity}"
        else:
            logging_utility.warning('Faux identity not provided')
            response = "Faux identity not provided."

        return response





