from fastapi import FastAPI, UploadFile, File, Request, Response
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import chatModel
import asyncio

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Server": "On"}

@app.post("/chat", response_class=PlainTextResponse)
async def getResponse(request: Request):
    input = await request.json()
    output = chatModel.QAChainModel.generate(input)
    return PlainTextResponse(output)   

if __name__ == '__main__':
    uvicorn.run(app, port=8001, host='0.0.0.0')