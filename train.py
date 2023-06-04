from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader, PyPDFLoader
from gdrive import get_files, get_file_path
from dotenv import load_dotenv
from pypdf.errors import PdfStreamError
import os
load_dotenv()

LAW_PATH = f"./files/Virginia Custody Law.txt"
embeddings = OpenAIEmbeddings()

def load_folder(docsearch, folder_id):
    files = get_files(folder_id)
    for file in files:
        path = get_file_path(file["id"], file["name"])
        if path == None:
            continue
        try:
            docsearch.load_local(f"./store", embeddings)
            loader = PyPDFLoader(path)
            pages = loader.load_and_split()
            docsearch.add_documents(pages)
            docsearch.save_local(f"./store")
        except PdfStreamError:
            pass


def main():
    # Load Virginia Custody Law at first

    if os.path.exists(f"./store/index.faiss"):
        docsearch = FAISS.load_local(f"./store", embeddings)
    else:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, length_function=len)
        loader = TextLoader(LAW_PATH)
        texts = loader.load_and_split(text_splitter)
        docsearch = FAISS.from_documents(texts, embeddings)
    docsearch.save_local(f"./store")

    # Load emails and messages from Google Drive

    # load_map()
    load_folder(docsearch, '1iDrAkMoMhZd5orwuGM5d0MB9MQ_wsli5')
    load_folder(docsearch, '1LeUxHZaxXA_D6dkBRFpnUxk2Jd3dU5GO')
    # save_map()


if __name__ == "__main__":
    main()
