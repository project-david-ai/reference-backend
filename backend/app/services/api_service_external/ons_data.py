import requests


def get_dataset_data():
    url = "https://api.beta.ons.gov.uk/v1/datasets"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("An error occurred while making the API request:", e)
        return None


# Call the function to retrieve the dataset data
dataset_data = get_dataset_data()

# Process the dataset data
if dataset_data:
    # Access the 'items' key in the JSON response
    dataset_items = dataset_data.get('items', [])

    # Iterate over each dataset item and print its details
    for item in dataset_items:
        print("Dataset ID:", item.get('id'))
        print("Dataset Title:", item.get('title'))
        print("Dataset Description:", item.get('description'))
        print("Dataset URL:", item.get('links', {}).get('latest_version', {}).get('href'))
        print("---")
else:
    print("Failed to retrieve dataset data.")