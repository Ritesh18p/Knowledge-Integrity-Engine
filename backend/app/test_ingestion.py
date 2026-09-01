# Import the document loader we created for the Knowledge Integrity Engine.
from ingestion import load_documents


# Load all supported documents from the central documents folder.
documents = load_documents()


# Display the total number of documents/pages that were loaded.
print("Documents loaded:", len(documents))


# Display the extracted content from every loaded document.
for index, document in enumerate(documents, start=1):

    # Print the document number for easier debugging.
    print(f"\n--- Document {index} ---")

    # Print the source file stored in the document metadata.
    print("Source:", document.metadata.get("source"))

    # Print the extracted text.
    print("Content:")
    print(document.page_content)


# Confirm that document ingestion completed successfully.
print("\nDocument ingestion test completed successfully.")