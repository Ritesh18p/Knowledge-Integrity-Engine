# Import the Qdrant client used to communicate with our local database.
from qdrant import client


# Ask Qdrant for all collections currently available.
collections = client.get_collections()


# Display the collections returned by our local Qdrant server.
print("Qdrant connection successful.")

# Display the names of the existing collections.
print("Existing collections:")

for collection in collections.collections:
    print("-", collection.name)