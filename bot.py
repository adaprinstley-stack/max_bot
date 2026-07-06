from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def test():
    return {"status": "ok"}
