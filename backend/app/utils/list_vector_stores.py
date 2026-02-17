from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(
    default_headers={"OpenAI-Beta": "assistants=v2"},
    api_key="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",
)


def list_vector_stores_paginated(client, limit=100):
    # Initial request without 'after' parameter
    response = client.beta.vector_stores.list(limit=limit)

    while response:
        # Process the current page of results
        vector_stores = response.dict().get("data", [])

        for store in vector_stores:
            print(f"Vector Store ID: {store['id']} | Created At: {store['created_at']}")

        # Check if there are more results
        if not response.has_more:
            break

        # Prepare for the next iteration by setting 'after' parameter to the last_id of the current page
        after = response.last_id
        response = client.beta.vector_stores.list(limit=limit, after=after)


# Call the function
list_vector_stores_paginated(client, limit=100)
