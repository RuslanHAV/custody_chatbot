from dotenv import load_dotenv
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from langchain import OpenAI, PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory
import os
load_dotenv()

app = FastAPI()

app.mount("/store", StaticFiles(directory="store"), name="store")
# app.mount("/", StaticFiles(directory="static", html=True), name="static")

origins = [os.getenv("CLIENT_URL")]
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

template = """You are a chatbot having a conversation with a human.

Based on the these occurrences, can you provide information about any events that have taken place after January 2019?.

{context}

{chat_history}
Human: {human_input}
Chatbot:"""

prompt = PromptTemplate(
    input_variables=["human_input", "context", "chat_history"],
    template=template
)


@app.get('/')
async def index():
    pass


@app.post('/api')
async def next(msg: str = Body(embed=True)):
    llm = OpenAI(temperature=0)
    memory = ConversationBufferMemory(
        memory_key="chat_history", input_key="human_input")
    chain = load_qa_chain(llm=llm, chain_type="stuff",
                          memory=memory, verbose=True, prompt=prompt)
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.load_local(f"./store", embeddings)
    docs = docsearch.similarity_search(msg)
    completion = chain.run(input_documents=docs, human_input=msg)
    return {'msg': completion}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, port=5000)
