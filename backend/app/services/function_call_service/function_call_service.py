# backend/app/services/function_call_service.py
from backend.app.services.function_call_service.handlers.image_generator_handler import ImageGeneratorHandler
from backend.app.services.function_call_service.handlers.location_handler import LocationHandler
from backend.app.services.function_call_service.handlers.ons_data_handler import OnsDataHandler
from backend.app.services.function_call_service.handlers.ripe_stat_handler import RipeStatHandler
from backend.app.services.function_call_service.handlers.user_details_handler import UserDetailsHandler
from backend.app.services.function_call_service.handlers.user_location_handler import UserLocationHandler
from backend.app.services.function_call_service.handlers.google_geocoding_handler import GoogleGeocodingHandler

from backend.app.services.logging_service.logger import LoggingUtility

logging_utility = LoggingUtility()


class FunctionCallService:
    def __init__(self):
        self.location_handler = LocationHandler()
        self.image_generator_handler = ImageGeneratorHandler()
        self.ons_data_handler = OnsDataHandler()
        self.ripe_stat_handler = RipeStatHandler()
        self.user_details_handler = UserDetailsHandler()
        self.user_location_handler = UserLocationHandler()
        self.google_geocoding_handler = GoogleGeocodingHandler()

        self.function_handlers = {
            "getLocationInfo": self.location_handler.handle_get_location_info,
            "generateImage": self.image_generator_handler.handle_generate_image,
            "getOnsDataSets": self.ons_data_handler.handle_get_ons_datasets,
            "getOnsDatasetByEndpoint": self.ons_data_handler.handle_get_ons_dataset_by_endpoint,
            "getUkBusinessData": self.ons_data_handler.handle_get_uk_business_data,
            "getWellbeingQuarterlyData": self.ons_data_handler.handle_get_wellbeing_quarterly_data,
            "getWellbeingByLocalAuthorityData": self.ons_data_handler.handle_get_wellbeing_by_local_authority_data,
            "getWeeklyDeathsAgeAndSexData": self.ons_data_handler.handle_get_weekly_deaths_age_and_sex_data,
            "getSexualOrientationByAgeAndSexData": self.ons_data_handler.handle_get_sexual_orientation_by_age_and_sex_data,
            "getUkSpendingOnCardsData": self.ons_data_handler.handle_get_uk_spending_on_cards_data,
            "getTradeData": self.ons_data_handler.handle_get_trade_data,
            "getTaxBenefitsStatisticsData": self.ons_data_handler.handle_get_tax_benefits_statistics_data,
            "getWeeklyDeathsRegionData": self.ons_data_handler.handle_get_weekly_deaths_region_data,
            "getRetailSalesAllBusinessesData": self.ons_data_handler.handle_get_retail_sales_all_businesses_data,
            "getRegionalGdpByYearData": self.ons_data_handler.handle_get_regional_gdp_by_year_data,
            "getWeeklyDeathsLocalAuthorityData": self.ons_data_handler.handle_get_weekly_deaths_local_authority_data,
            "getProjectionsOlderPeopleSexRatiosData": self.ons_data_handler.handle_get_projections_older_people_sex_ratios_data,
            "getAbuseContacts": self.ripe_stat_handler.handle_get_abuse_contacts,
            "getAddressSpaceHierarchy": self.ripe_stat_handler.handle_get_address_space_hierarchy,
            "getAddressSpaceUsage": self.ripe_stat_handler.handle_get_address_space_usage,
            "getAnnouncedPrefixes": self.ripe_stat_handler.handle_get_announced_prefixes,
            "getAllocationHistory": self.ripe_stat_handler.handle_get_allocation_history,
            "getAsnNeighbours": self.ripe_stat_handler.handle_get_asn_neighbours,
            "getAtlasProbes": self.ripe_stat_handler.handle_get_atlas_probes,
            "getBgpUpdates": self.ripe_stat_handler.handle_get_bgp_updates,
            "getAsnNeighboursHistory": self.ripe_stat_handler.handle_get_asn_neighbours_history,
            "getCountryResourceStats": self.ripe_stat_handler.handle_get_country_resource_stats,
            "getCountryResourceList": self.ripe_stat_handler.handle_get_country_resource_list,
            "getDnsChain": self.ripe_stat_handler.handle_get_dns_chain,
            "getExampleResources": self.ripe_stat_handler.handle_get_example_resources,
            "getHistoricalWhois": self.ripe_stat_handler.handle_get_historical_whois,
            "getIanaRegistryInfo": self.ripe_stat_handler.handle_get_iana_registry_info,
            "getRoutingHistory": self.ripe_stat_handler.handle_get_routing_history,
            "getRoutingStatus": self.ripe_stat_handler.handle_get_routing_status,
            "getRrcInfo": self.ripe_stat_handler.handle_get_rrc_info,
            "getRpkiValidationStatus": self.ripe_stat_handler.handle_get_rpki_validation_status,
            "getRpkiHistory": self.ripe_stat_handler.handle_get_rpki_history,
            "getSearchcomplete": self.ripe_stat_handler.handle_get_searchcomplete,
            "getLookingGlass": self.ripe_stat_handler.handle_get_looking_glass,
            "getWhatsMyIp": self.ripe_stat_handler.handle_get_whats_my_ip,
            "getZonemasterOverview": self.ripe_stat_handler.handle_get_zonemaster_overview,
            "getZonemasterDetails": self.ripe_stat_handler.handle_get_zonemaster_details,
            # User Services
            "getUserDetailsByFauxIdentity": self.user_details_handler.handle_get_user_details_by_faux_identity,
            "getUserLocations": self.user_location_handler.handle_get_user_locations,
            "getCurrentLocationByGps": self.google_geocoding_handler.handle_get_current_location_by_gps,
            "getPlacesNearByGps": self.google_geocoding_handler.handle_get_places_near_by_gps
        }

    def call_function(self, function_name, arguments):
        if function_name not in self.function_handlers:
            logging_utility.error("Unsupported function: %s", function_name)
            return "Error: Unsupported function"

        return self.function_handlers[function_name](arguments)