# Import the function that creates our Knowledge Integrity Engine collection.
from qdrant import create_collection


# Create the collection if it does not already exist.
create_collection()


# Confirm that Qdrant setup completed successfully.
print("\nQdrant setup completed successfully.")