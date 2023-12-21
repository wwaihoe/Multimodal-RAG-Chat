from fastapi import FastAPI, UploadFile, File, Request, Response
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import json
import retrievalModel

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FileName(BaseModel):
    fileName: str

class RetrievalQuery(BaseModel):
    query: str

class RetrievalDoc(BaseModel):
    doc: str


@app.get("/")
def read_root():
    return {"Server": "On"}

@app.post("/upload")
def uploadDocument(file: UploadFile = File(...)):
    retrievalModel.vectorStore.addToVectorStore(file.file, file.filename)
    print("Uploaded: ", file.filename)
    return 

@app.post("/remove")
def removeDocument(fileName: FileName):
    retrievalModel.vectorStore.removeFromVectorStore(fileName.fileName)
    print("Removed: ", fileName.fileName)
    return

@app.post("/retrieve")
def retrieveDocument(retrievalQuery: RetrievalQuery) -> RetrievalDoc:
    doc = retrievalModel.vectorStore.similarity_search(retrievalQuery.query)
    docText = str(doc[0])
    return RetrievalDoc(doc=docText)

if __name__ == '__main__':
    uvicorn.run(app, port=8002, host='0.0.0.0')