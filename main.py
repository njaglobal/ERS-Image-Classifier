from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from supabase_utils import sync_model_files
from predict import classify_and_describe

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["https://yourfrontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Model API is live"}

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    sync_model_files()
    contents = await file.read()
    result = classify_and_describe(contents)
    return result  # 🔥 Return the full dict directly



