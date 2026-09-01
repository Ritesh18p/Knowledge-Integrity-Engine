# Import the SentenceTransformer class used to load and run
# Hugging Face sentence-transformer models locally.
from sentence_transformers import SentenceTransformer


# Load the embedding model from Hugging Face.
# The model will be downloaded once and then cached locally.
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# Create sample text representing information that our
# Knowledge Integrity Engine might receive from a document.
text = "Razorpay provides AI-powered tools for internal knowledge management."


# Convert the text into a numerical embedding vector.
# This vector represents the semantic meaning of the text.
embedding = model.encode(text)


# Display the number of dimensions in the generated vector.
print("Embedding dimensions:", len(embedding))


# Display the first five values of the embedding vector.
# We don't need to print the complete 384-dimensional vector.
print("First 5 values:", embedding[:5])


# Confirm that the local embedding model worked successfully.
print("\nLocal Hugging Face embedding test completed successfully.")