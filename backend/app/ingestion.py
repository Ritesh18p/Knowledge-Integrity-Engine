# Import Path so we can work safely with files and folders.
from pathlib import Path

# Import PyPDFLoader to extract text from PDF documents.
from langchain_community.document_loaders import PyPDFLoader

# Import Document so we can create a standard LangChain document
# for plain-text files.
from langchain_core.documents import Document


# Find the main project directory from the current file location.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Define the central folder where knowledge documents are stored.
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"


def load_documents():
    """
    Load supported documents from the data/documents folder.

    Currently supported:
    - PDF files
    - TXT files

    Returns:
        list: A list of LangChain Document objects.
    """

    # Create an empty list to store all loaded documents.
    documents = []

    # Check whether the documents directory exists.
    if not DOCUMENTS_DIR.exists():
        # Create the directory automatically if it doesn't exist.
        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

        # Return an empty list because there are no documents yet.
        return documents

    # Iterate through every file inside the documents directory.
    for file_path in DOCUMENTS_DIR.iterdir():

        # Skip directories and process only files.
        if not file_path.is_file():
            continue

        # Check whether the file is a PDF.
        if file_path.suffix.lower() == ".pdf":

            # Create a PDF loader for the current file.
            loader = PyPDFLoader(str(file_path))

            # Extract the PDF's pages as LangChain Document objects.
            pdf_documents = loader.load()

            # Add the extracted pages to our main document collection.
            documents.extend(pdf_documents)

        # Check whether the file is a plain-text document.
        elif file_path.suffix.lower() == ".txt":

            # Read the complete text file using UTF-8 encoding.
            text = file_path.read_text(encoding="utf-8")

            # Convert the text into a standard LangChain Document.
            document = Document(
                page_content=text,
                metadata={
                    "source": str(file_path)
                }
            )

            # Add the text document to our collection.
            documents.append(document)

    # Return every successfully loaded document.
    return documents