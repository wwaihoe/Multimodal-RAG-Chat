from fastapi import FastAPI, WebSocket, UploadFile, File
import chatModel, retrieverModel

app = FastAPI()


@app.get("/")
def read_root():
    return {"Server": "On"}

@app.post("/upload")
def upload_document(file: UploadFile = File(...)):
    chatModel.addToVectorStore(file)
    return

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