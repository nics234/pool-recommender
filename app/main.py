from fastapi import FastAPI
app = FastAPI(title="Pool Recommender API")

@app.get("/")
def read_root():
    return {"message": "🏊‍♂️ Pool Recommender API is running!"}
