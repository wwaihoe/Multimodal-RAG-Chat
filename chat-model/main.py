from fastapi import FastAPI, UploadFile, File, Request, Response
from fastapi.responses import PlainTextResponse
import uvicorn
from pydantic import BaseModel
import json
import chatModel, retrieverModel

app = FastAPI()


class FileName(BaseModel):
    fileName: str


@app.get("/")
def read_root():
    return {"Server": "On"}

@app.post("/upload")
def uploadDocument(response: Response, file: UploadFile = File(...)):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, PUT"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    chatModel.vectorStore.addToVectorStore(file.file, file.filename)
    print("Uploaded: ", file.filename)
    return 

@app.post("/remove")
def removeDocument(fileName: str):
    chatModel.vectorStore.removeFromVectorStore(fileName)
    return

@app.post("/chat", response_class=PlainTextResponse)
async def getResponse(request: Request):
    input = await request.json()
    output = await chatModel.QAChainModel.generate(input)
    print(output)
    return output

if __name__ == '__main__':
    uvicorn.run(app, port=8080, host='0.0.0.0')