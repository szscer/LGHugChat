from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA,  ConversationalRetrievalChain
from langchain_huggingface import HuggingFaceEndpoint

def load_db(file_list, chain_type, k):
    # load documents
    loaders=[]
    documents = []
    for filename in file_list:
        ext = filename.split('.')[1]
        if ext == 'pdf':
            loaders.append(PyPDFLoader(filename, extract_images=True))
        if ext == 'csv':
            loaders.append(CSVLoader(filename))
        if ext == 'txt':
            loaders.append(TextLoader(filename))

    for loader in loaders:
        documents.extend(loader.load())

    #documents = loader.load()
    # split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)
    # define embedding
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    embedding = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    # create vector database from data
    db = DocArrayInMemorySearch.from_documents(docs, embedding)
    # define retriever
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})
    # create a chatbot chain. Memory is managed externally.
    qa = ConversationalRetrievalChain.from_llm(
        llm=HuggingFaceEndpoint(
    #repo_id="HuggingFaceH4/zephyr-7b-beta",
    #repo_id="meta-llama/Llama-2-7b-chat-hf",
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    # task="text-generation",
    max_new_tokens=2048,
    # do_sample=False,
    # repetition_penalty=1.03,
    temperature=0.1,
        ),
        chain_type=chain_type,
        retriever=retriever,
        return_source_documents=True,
        return_generated_question=True,
    )
    return qa