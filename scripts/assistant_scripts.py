import os

from dotenv import load_dotenv
from projectdavid import Entity
from projectdavid.synthesis.retriever import retrieve

load_dotenv()

client = Entity(
    base_url=os.getenv("BASE_URL", "http://localhost:9000"),
    api_key=os.getenv("ENTITIES_API_KEY"),
)


# retrieve_user_vector_stores = client.vectors.get_stores_by_user(_user_id="user_a1FWmgox36uy4lif8PrSaN")
# print(retrieve_user_vector_stores)

retrieve_run = client.runs.retrieve_run(run_id="run_ar29rE9odEf9Kq2ciZoq5W")
user_id = retrieve_run.user_id

# ✅ Use the updated, non-deprecated method if available
retrieve_user_vector_stores = client.vectors.list_my_vector_stores()

# Filter by name
file_search_stores = [s for s in retrieve_user_vector_stores if s.name == "file_search"]

# Pick the one with the earliest created_at
if file_search_stores:
    earliest_file_search = min(
        file_search_stores, key=lambda s: s.created_at or float("inf")
    )
    file_search_vector_id = earliest_file_search.id
    print(f"Earliest vector store for 'file_search': {file_search_vector_id}")
else:
    file_search_vector_id = None
    print("No 'file_search' vector store found.")
