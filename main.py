from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from supabase_utils import sync_model_files
from predict import classify_and_describe
from model_loader import get_model, reset_model
from predict import classify_and_describe
from contextlib import asynccontextmanager



# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    sync_model_files()
    yield
    # Shutdown code (optional)
    # e.g., clean up resources

app = FastAPI(title="ERS Image Classifier", lifespan=lifespan)

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
    contents = await file.read()
    result = classify_and_describe(contents)
    return result  # 🔥 Return the full dict directly



