import time
import requests
import pandas as pd
import io


class OnsApiService:
    def __init__(self):
        self.metadata_cache = {}

    def get_data_and_metadata(self, metadata_url):
        """
        Retrieves the metadata and data file from the provided API endpoint.
        Returns a tuple containing the metadata dictionary and the DataFrame parsed from the CSV data file.
        """
        if metadata_url in self.metadata_cache:
            metadata = self.metadata_cache[metadata_url]
        else:
            try:
                response = requests.get(metadata_url)
                response.raise_for_status()
                metadata = response.json()
                self.metadata_cache[metadata_url] = metadata
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while making the API request: {e}")
                return None, None

        try:
            csv_url = metadata["downloads"]["csv"]["href"]
            csv_data = requests.get(csv_url).content
            data_df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
            return metadata, data_df
        except (KeyError, requests.exceptions.RequestException) as e:
            print(f"An error occurred while retrieving the data file: {e}")
            return metadata, None

    def get_dataset_data(self, limit=20, offset=0):
        url = f"https://api.beta.ons.gov.uk/v1/datasets?limit={limit}&offset={offset}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print("An error occurred while making the API request:", e)
            return None

    def get_dataset_by_endpoint(self, endpoint):
        try:
            response = requests.get(endpoint)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print("An error occurred while making the API request:", e)
            return None

    def get_uk_business_data(self, dimensions=None):
        metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/uk-business-by-enterprises-and-local-units/editions/2022/versions/1"
        metadata, uk_business_data = self.get_data_and_metadata(metadata_url)

        if uk_business_data is not None:
            if dimensions is None:
                dimensions = [dim["name"] for dim in metadata["dimensions"]]

            dimension_labels = {dim["name"]: dim["label"] for dim in metadata["dimensions"]}
            selected_columns = [dim for dim in dimensions if dim in uk_business_data.columns] + ["v4_0"]

            renamed_data = uk_business_data[selected_columns].rename(columns={"v4_0": "Value"})
            return renamed_data.to_dict(orient="records")
        else:
            return None

    def get_wellbeing_quarterly_data(self, dimensions=None):
        metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/wellbeing-quarterly/editions/time-series/versions/9"
        metadata, wellbeing_data = self.get_data_and_metadata(metadata_url)

        if wellbeing_data is not None:
            if dimensions is None:
                dimensions = [dim["name"] for dim in metadata["dimensions"]]

            dimension_labels = {dim["name"]: dim["label"] for dim in metadata["dimensions"]}
            selected_columns = [dim for dim in dimensions if dim in wellbeing_data.columns] + ["v4_2"]

            renamed_data = wellbeing_data[selected_columns].rename(columns={"v4_2": "Value"})
            return renamed_data.to_dict(orient="records")
        else:
            return None

    def get_wellbeing_by_local_authority_data(self, dimensions=None, page=1, page_size=100):
        metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/wellbeing-local-authority/editions/time-series/versions/4"
        metadata, wellbeing_data = self.get_data_and_metadata(metadata_url)

        if wellbeing_data is not None:
            if dimensions is None:
                dimensions = [dim["name"] for dim in metadata["dimensions"]]

            dimension_labels = {dim["name"]: dim["label"] for dim in metadata["dimensions"]}
            value_column = wellbeing_data.columns[-1]  # Assuming the value column is the last column
            selected_columns = [dim for dim in dimensions if dim in wellbeing_data.columns] + [value_column]

            # Apply pagination
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            paginated_data = wellbeing_data[selected_columns][start_index:end_index]

            renamed_data = paginated_data.rename(columns={value_column: "Value"})
            return renamed_data.to_dict(orient="records")
        else:
            return None

    # New method for "Weekly Deaths Region" dataset
    def get_weekly_deaths_region_data(self, page=1, page_size=100, dimensions=None):
        metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/weekly-deaths-region/editions/time-series/versions/14"
        metadata, weekly_deaths_data = self.get_data_and_metadata(metadata_url)

        if weekly_deaths_data is not None:
            if dimensions is None:
                dimensions = [dim["name"] for dim in metadata["dimensions"]]

            dimension_labels = {dim["name"]: dim["label"] for dim in metadata["dimensions"]}
            value_column = weekly_deaths_data.columns[-1]  # Assuming the value column is the last column
            selected_columns = [dim for dim in dimensions if dim in weekly_deaths_data.columns] + [value_column]

            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size
            paginated_data = weekly_deaths_data.iloc[start:end]

            renamed_data = paginated_data[selected_columns].rename(columns={value_column: "Value"})

            # Add pagination metadata
            total_records = len(weekly_deaths_data)
            total_pages = (total_records + page_size - 1) // page_size  # Ceiling division
            has_next = page < total_pages
            has_prev = page > 1

            return {
                'data': renamed_data.to_dict(orient="records"),
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_records': total_records,
                    'total_pages': total_pages,
                    'has_next': has_next,
                    'has_prev': has_prev
                }
            }
        else:
            return None

    def get_weekly_deaths_age_sex_data(self, dimensions=None):
        metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/weekly-deaths-age-sex/editions/time-series/versions/14"
        metadata, weekly_deaths_data = self.get_data_and_metadata(metadata_url)

        if weekly_deaths_data is not None:
            if dimensions is None:
                dimensions = [dim["name"] for dim in metadata["dimensions"]]

            dimension_labels = {dim["name"]: dim["label"] for dim in metadata["dimensions"]}
            value_column = weekly_deaths_data.columns[-1]  # Assuming the value column is the last column
            selected_columns = [dim for dim in dimensions if dim in weekly_deaths_data.columns] + [value_column]

            renamed_data = weekly_deaths_data[selected_columns].rename(columns={value_column: "Value"})
            return renamed_data.to_dict(orient="records")
        else:
            return None

    def get_retail_sales_all_businesses_data(self, dimensions=None):
        metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/retail-sales-index-all-businesses/editions/time-series/versions/24"
        metadata, retail_sales_data = self.get_data_and_metadata(metadata_url)

        if retail_sales_data is not None:
            if dimensions is None:
                dimensions = [dim["name"] for dim in metadata["dimensions"]]

            dimension_labels = {dim["name"]: dim["label"] for dim in metadata["dimensions"]}
            value_column = retail_sales_data.columns[-1]  # Assuming the value column is the last column
            selected_columns = [dim for dim in dimensions if dim in retail_sales_data.columns] + [value_column]

            renamed_data = retail_sales_data[selected_columns].rename(columns={value_column: "Value"})
            return renamed_data.to_dict(orient="records")
        else:
            return None

    def get_tax_benefits_statistics_data(self, dimensions=None):
        metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/tax-benefits-statistics/editions/time-series/versions/3"
        metadata, tax_benefits_data = self.get_data_and_metadata(metadata_url)

        if tax_benefits_data is not None:
            if dimensions is None:
                dimensions = [dim["name"] for dim in metadata["dimensions"]]

            dimension_labels = {dim["name"]: dim["label"] for dim in metadata["dimensions"]}
            value_column = tax_benefits_data.columns[-1]  # Assuming the value column is the last column
            selected_columns = [dim for dim in dimensions if dim in tax_benefits_data.columns] + [value_column]

            renamed_data = tax_benefits_data[selected_columns].rename(columns={value_column: "Value"})
            return renamed_data.to_dict(orient="records")
        else:
            return None

    def get_trade_data(self, dimensions=None):
        metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/trade/editions/time-series/versions/42"
        metadata, trade_data = self.get_data_and_metadata(metadata_url)

        if trade_data is not None:
            if dimensions is None:
                dimensions = [dim["name"] for dim in metadata["dimensions"]]

            dimension_labels = {dim["name"]: dim["label"] for dim in metadata["dimensions"]}
            value_column = trade_data.columns[-1]  # Assuming the value column is the last column
            selected_columns = [dim for dim in dimensions if dim in trade_data.columns] + [value_column]

            renamed_data = trade_data[selected_columns].rename(columns={value_column: "Value"})
            return renamed_data.to_dict(orient="records")
        else:
            return None

    def get_traffic_camera_activity_data(self, dimensions=None):
        metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/traffic-camera-activity/editions/time-series/versions/100"
        metadata, traffic_camera_data = self.get_data_and_metadata(metadata_url)

        if traffic_camera_data is not None:
            if dimensions is None:
                dimensions = [dim["name"] for dim in metadata["dimensions"]]

            dimension_labels = {dim["name"]: dim["label"] for dim in metadata["dimensions"]}
            value_column = traffic_camera_data.columns[-1]  # Assuming the value column is the last column
            selected_columns = [dim for dim in dimensions if dim in traffic_camera_data.columns] + [value_column]

            renamed_data = traffic_camera_data[selected_columns].rename(columns={value_column: "Value"})
            return renamed_data.to_dict(orient="records")
        else:
            return None

    def get_sexual_orientation_by_age_and_sex_data(self, dimensions=None):
        metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/sexual-orientation-by-age-and-sex/editions/time-series/versions/3"
        metadata, sexual_orientation_data = self.get_data_and_metadata(metadata_url)

        if sexual_orientation_data is not None:
            if dimensions is None:
                dimensions = [dim["name"] for dim in metadata["dimensions"]]

            dimension_labels = {dim["name"]: dim["label"] for dim in metadata["dimensions"]}
            value_column = sexual_orientation_data.columns[-1]  # Assuming the value column is the last column
            selected_columns = [dim for dim in dimensions if dim in sexual_orientation_data.columns] + [value_column]

            renamed_data = sexual_orientation_data[selected_columns].rename(columns={value_column: "Value"})
            return renamed_data.to_dict(orient="records")
        else:
            return None

    def get_uk_spending_on_cards_data(self, dimensions=None):
        metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/uk-spending-on-cards/editions/time-series/versions/125"
        metadata, spending_data = self.get_data_and_metadata(metadata_url)

        if spending_data is not None:
            if dimensions is None:
                dimensions = [dim["name"] for dim in metadata["dimensions"]]

            dimension_labels = {dim["name"]: dim["label"] for dim in metadata["dimensions"]}
            value_column = spending_data.columns[-1]  # Assuming the value column is the last column
            selected_columns = [dim for dim in dimensions if dim in spending_data.columns] + [value_column]

            renamed_data = spending_data[selected_columns].rename(columns={value_column: "Value"})
            return renamed_data.to_dict(orient="records")
        else:
            return None


if __name__ == "__main__":
    onsapi_service = OnsApiService()
    print(onsapi_service.get_uk_business_data())
    print(onsapi_service.get_wellbeing_quarterly_data())
    print(onsapi_service.get_weekly_deaths_region_data())
    print(onsapi_service.get_retail_sales_all_businesses_data())
    print(onsapi_service.get_tax_benefits_statistics_data())
    print(onsapi_service.get_trade_data())
    print(onsapi_service.get_traffic_camera_activity_data())
    print(onsapi_service.get_sexual_orientation_by_age_and_sex_data())
    print(onsapi_service.get_wellbeing_by_local_authority_data())
    print(onsapi_service.get_weekly_deaths_age_sex_data())
    print(onsapi_service.get_wellbeing_by_local_authority_data())
    print(onsapi_service.get_sexual_orientation_by_age_and_sex_data())
    print(onsapi_service.get_uk_spending_on_cards_data())
