from langchain_community.document_loaders import PyPDFLoader  
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

loader = PyPDFLoader("ltv-repair-procedures.pdf") #loading the pdf file using PyPDFLoader
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents) 
#splitting the documents into smaller 1000 character chunks /w an overlap of 200 characters between chunks

embeddings = HuggingFaceEmbeddings() #generate embeddings for the text chunks
vectorstore = FAISS.from_documents(texts, embeddings)

def FAISSearch(query): #take in a query and return the most relevant document chunk
    docs = vectorstore.similarity_search(query, k=1)
    for doc in docs:
        print("page:", doc.metadata.get("page"))
        print(doc.page_content)
        print("-" * 80)
# query = "Err. c"
# docs = vectorstore.similarity_search(query, k=1)

# for doc in docs:
#     print("page:", doc.metadata.get("page"))
#     print(doc.page_content)
#     print("-" * 80)