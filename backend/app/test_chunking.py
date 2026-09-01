# Import the function that splits text into smaller chunks.
from chunking import split_document


# Create sample organizational knowledge for our test.
text = """
Razorpay Knowledge Integrity Policy.

All internal engineering documentation must have a clear owner.
Important technical decisions should include their source and date.
Outdated information must be identified before it is used to answer a question.
Every document should be reviewed periodically to ensure that the information remains accurate.
"""


# Split the sample text into smaller chunks.
chunks = split_document(text)


# Display the total number of chunks created.
print("Total chunks:", len(chunks))


# Display every generated chunk.
for index, chunk in enumerate(chunks, start=1):

    # Print the chunk number.
    print(f"\n--- Chunk {index} ---")

    # Print the actual text contained inside the chunk.
    print(chunk)


# Confirm that the chunking system completed successfully.
print("\nDocument chunking test completed successfully.")