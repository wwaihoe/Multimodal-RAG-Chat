from fastapi import FastAPI, WebSocket, UploadFile, File
from pydantic import BaseModel
import chatModel

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload")
def upload_document(file: UploadFile = File(...)):
    return {"filename": file.filename}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    dialog = []
    while True:
        data = await websocket.receive_text()
        dialog.append(("Human", data))
        output = chatModel.generate(dialog)
        dialog.append(("AI", output))
        await websocket.send_text(output)

if __name__ == '__main__':
    app.run()