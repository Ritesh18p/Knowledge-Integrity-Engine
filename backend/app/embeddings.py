# Import the Hugging Face embedding class from LangChain.
from langchain_huggingface import HuggingFaceEmbeddings


# Define the Hugging Face model that will run locally.
# This model converts text into 384-dimensional semantic vectors.
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# Create the embedding model once when this module is loaded.
# The model runs locally on the user's computer.
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME
)


def create_embedding(text: str):
    """
    Convert a single piece of text into a semantic embedding vector.

    Args:
        text: Text that needs to be converted into an embedding.

    Returns:
        list: A numerical embedding vector.
    """

    # Convert the supplied text into a numerical vector.
    vector = embeddings.embed_query(text)

    # Return the generated vector.
    return vector