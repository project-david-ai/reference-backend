import requests
from backend.app.services.api_service_external.api_public_access.api_uk_statistics.ons.api_uk_ons import OnsApiService
from backend.app.services.logging_service.logger import LoggingUtility

class OnsDataHandler:
    def __init__(self):
        self.ons_api_service = OnsApiService()
        self.logging_utility = LoggingUtility()

    def handle_get_ons_datasets(self, arguments):
        self.logging_utility.info('Retrieving ONS datasets')
        limit = arguments.get("limit", 20)
        offset = arguments.get("offset", 0)
        dataset_data = self.ons_api_service.get_dataset_data(limit, offset)
        if dataset_data:
            dataset_items = dataset_data.get('items', [])
            response = "Available ONS Datasets:\n\n"
            for item in dataset_items:
                response += f"Dataset ID: {item.get('id')}\n"
                response += f"Dataset Title: {item.get('title')}\n"
                response += f"Dataset Description: {item.get('description')}\n"
                response += f"Dataset URL: {item.get('links', {}).get('latest_version', {}).get('href')}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve ONS dataset data')
            response = "Failed to retrieve dataset data."
        return response

    def handle_get_ons_dataset_by_endpoint(self, arguments):
        endpoint = arguments["endpoint"]
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()
            dataset_info = {
                "id": data["id"],
                "title": data["collection_id"],
                "edition": data["edition"],
                "version": data["version"],
                "release_date": data["release_date"],
                "downloads": data["downloads"],
                "dimensions": [dim["label"] for dim in data["dimensions"]],
                "usage_notes": [note["title"] for note in data["usage_notes"]]
            }
            return dataset_info
        except requests.exceptions.RequestException as e:
            self.logging_utility.error("Error retrieving dataset information: %s", str(e))
            return "Error: Failed to retrieve dataset information"

    def handle_get_uk_business_data(self, arguments):
        self.logging_utility.info('Retrieving UK business data')
        dimensions = arguments.get("dimensions", None)
        uk_business_data = self.ons_api_service.get_uk_business_data(dimensions)
        if uk_business_data:
            response = "UK Business Data:\n\n"
            for item in uk_business_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve UK business data')
            response = "Failed to retrieve UK business data."
        return response

    def handle_get_wellbeing_quarterly_data(self, arguments):
        self.logging_utility.info('Retrieving wellbeing quarterly data')
        dimensions = arguments.get("dimensions", None)
        wellbeing_data = self.ons_api_service.get_wellbeing_quarterly_data(dimensions)
        if wellbeing_data:
            response = "Wellbeing Quarterly Data:\n\n"
            for item in wellbeing_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve wellbeing quarterly data')
            response = "Failed to retrieve wellbeing quarterly data."
        return response

    def handle_get_wellbeing_by_local_authority_data(self, arguments):
        self.logging_utility.info('Retrieving wellbeing by local authority data')
        dimensions = arguments.get("dimensions", None)
        wellbeing_data = self.ons_api_service.get_wellbeing_by_local_authority_data(dimensions)
        if wellbeing_data:
            response = "Wellbeing by Local Authority Data:\n\n"
            for item in wellbeing_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve wellbeing by local authority data')
            response = "Failed to retrieve wellbeing by local authority data."
        return response

    def handle_get_weekly_deaths_age_and_sex_data(self, arguments):
        self.logging_utility.info('Retrieving weekly deaths by age and sex data')
        dimensions = arguments.get("dimensions", None)
        deaths_data = self.ons_api_service.get_weekly_deaths_age_sex_data(dimensions)
        if deaths_data:
            response = "Weekly Deaths by Age and Sex Data:\n\n"
            for item in deaths_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve weekly deaths by age and sex data')
            response = "Failed to retrieve weekly deaths by age and sex data."
        return response

    def handle_get_sexual_orientation_by_age_and_sex_data(self, arguments):
        self.logging_utility.info('Retrieving sexual orientation by age and sex data')
        dimensions = arguments.get("dimensions", None)
        orientation_data = self.ons_api_service.get_sexual_orientation_by_age_and_sex_data(dimensions)
        if orientation_data:
            response = "Sexual Orientation by Age and Sex Data:\n\n"
            for item in orientation_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve sexual orientation by age and sex data')
            response = "Failed to retrieve sexual orientation by age and sex data."
        return response

    def handle_get_uk_spending_on_cards_data(self, arguments):
        self.logging_utility.info('Retrieving UK spending on cards data')
        dimensions = arguments.get("dimensions", None)
        spending_data = self.ons_api_service.get_uk_spending_on_cards_data(dimensions)
        if spending_data:
            response = "UK Spending on Cards Data:\n\n"
            for item in spending_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve UK spending on cards data')
            response = "Failed to retrieve UK spending on cards data."
        return response

    def handle_get_trade_data(self, arguments):
        self.logging_utility.info('Retrieving trade data')
        dimensions = arguments.get("dimensions", None)
        trade_data = self.ons_api_service.get_trade_data(dimensions)
        if trade_data:
            response = "Trade Data:\n\n"
            for item in trade_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve trade data')
            response = "Failed to retrieve trade data."
        return response

    def handle_get_tax_benefits_statistics_data(self, arguments):
        self.logging_utility.info('Retrieving tax benefits statistics data')
        dimensions = arguments.get("dimensions", None)
        tax_benefits_data = self.ons_api_service.get_tax_benefits_statistics_data(dimensions)
        if tax_benefits_data:
            response = "Tax Benefits Statistics Data:\n\n"
            for item in tax_benefits_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve tax benefits statistics data')
            response = "Failed to retrieve tax benefits statistics data."
        return response

    def handle_get_weekly_deaths_region_data(self, arguments):
        self.logging_utility.info('Retrieving weekly deaths by region data')
        dimensions = arguments.get("dimensions", None)
        deaths_data = self.ons_api_service.get_weekly_deaths_region_data(dimensions)
        if deaths_data:
            response = "Weekly Deaths by Region Data:\n\n"
            for item in deaths_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve weekly deaths by region data')
            response = "Failed to retrieve weekly deaths by region data."
        return response

    def handle_get_retail_sales_all_businesses_data(self, arguments):
        self.logging_utility.info('Retrieving retail sales all businesses data')
        dimensions = arguments.get("dimensions", None)
        sales_data = self.ons_api_service.get_retail_sales_all_businesses_data(dimensions)
        if sales_data:
            response = "Retail Sales All Businesses Data:\n\n"
            for item in sales_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve retail sales all businesses data')
            response = "Failed to retrieve retail sales all businesses data."
        return response

    def handle_get_regional_gdp_by_year_data(self, arguments):
        self.logging_utility.info('Retrieving regional GDP by year data')
        dimensions = arguments.get("dimensions", None)
        gdp_data = self.ons_api_service.get_regional_gdp_by_year_data(dimensions)
        if gdp_data:
            response = "Regional GDP by Year Data:\n\n"
            for item in gdp_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve regional GDP by year data')
            response = "Failed to retrieve regional GDP by year data."
        return response

    def handle_get_weekly_deaths_local_authority_data(self, arguments):
        self.logging_utility.info('Retrieving weekly deaths by local authority data')
        dimensions = arguments.get("dimensions", None)
        deaths_data = self.ons_api_service.get_weekly_deaths_local_authority_data(dimensions)
        if deaths_data:
            response = "Weekly Deaths by Local Authority Data:\n\n"
            for item in deaths_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve weekly deaths by local authority data')
            response = "Failed to retrieve weekly deaths by local authority data."
        return response

    def handle_get_projections_older_people_sex_ratios_data(self, arguments):
        self.logging_utility.info('Retrieving projections older people sex ratios data')
        dimensions = arguments.get("dimensions", None)
        sex_ratios_data = self.ons_api_service.get_projections_older_people_sex_ratios_data(dimensions)
        if sex_ratios_data:
            response = "Projections Older People Sex Ratios Data:\n\n"
            for item in sex_ratios_data:
                for key, value in item.items():
                    response += f"{key}: {value}\n"
                response += "---\n"
        else:
            self.logging_utility.warning('Failed to retrieve projections older people sex ratios data')
            response = "Failed to retrieve projections older people sex ratios data."
        return response