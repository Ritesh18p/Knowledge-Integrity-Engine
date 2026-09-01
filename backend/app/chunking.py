from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_document(text: str) -> list[str]:
    """Split knowledge into small, atomic chunks for high-precision retrieval."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=0,
        separators=["\n", ". "],
    )

    return splitter.split_text(text)