import tempfile

from langchain_community.document_loaders import PyPDFLoader


def load_cv(uploaded_file):
    suffix = ".pdf"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as tmp:
        tmp.write(uploaded_file.getvalue())
        temp_path = tmp.name

    loader = PyPDFLoader(temp_path)

    documents = loader.load()

    return documents


def documents_to_text(documents):
    return "\n\n".join(
        document.page_content
        for document in documents
    )
