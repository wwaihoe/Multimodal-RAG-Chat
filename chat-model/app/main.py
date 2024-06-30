from fastapi import FastAPI, UploadFile, File, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import chatModel


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatResponse(BaseModel):
    output: str
    file_names: list[str]


@app.get("/")
def read_root():
    return {"Server": "On"}

@app.post("/chat")
async def getResponse(request: Request):
    input = await request.json()
    response = chatModel.QAChainModel.generate(input)
    return ChatResponse(output=response["output"], file_names=response["file_names"])   

if __name__ == '__main__':
    uvicorn.run(app, port=8001, host='0.0.0.0')