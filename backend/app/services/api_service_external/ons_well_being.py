import requests
import pandas as pd
import io


def get_wellbeing_data_by_area(agg_func='mean', groupby_cols=['administrative-geography', 'measure-of-wellbeing'], value_col='v4_3', top_n=None):
    # Make the initial API call to get the metadata
    metadata_url = "https://api.beta.ons.gov.uk/v1/datasets/wellbeing-local-authority/editions/time-series/versions/4"
    response = requests.get(metadata_url)
    metadata = response.json()

    # Get the URL for the CSV data file
    csv_url = metadata["downloads"]["csv"]["href"]

    # Download the CSV data file
    csv_data = requests.get(csv_url).content

    # Parse the CSV data into a Pandas DataFrame
    well_being_data = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))

    # Group the data and apply the aggregation function
    well_being_by_area = well_being_data.groupby(groupby_cols)[value_col].agg(agg_func).reset_index()

    # Filter for top N rows if specified
    if top_n is not None:
        well_being_by_area = well_being_by_area.nlargest(top_n, value_col)

    return well_being_by_area


# Get the mean well-being values (default)
well_being_data = get_wellbeing_data_by_area()

# Get the maximum well-being values
well_being_data = get_wellbeing_data_by_area(agg_func='max')
print(well_being_data)

# Get the sum of well-being values, grouped only by geography
well_being_data = get_wellbeing_data_by_area(agg_func='sum', groupby_cols=['administrative-geography'])
print(well_being_data)

# Get the top 10 rows with the highest well-being values
well_being_data = get_wellbeing_data_by_area(top_n=10)
print(well_being_data)