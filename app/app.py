from datetime import datetime
from fastapi import FastAPI
import joblib
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

# --------------------------
#  LOCAL STORAGE ONLY 🧠
# --------------------------
history_storage = []    # This acts as our database (in RAM)

# Load model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "thirdmodel.joblib")
model = joblib.load(MODEL_PATH)

app = FastAPI(title="Mill Extraction Digital Twin API")

# CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# 🔮 PREDICT — STORE IN MEMORY
# -----------------------------
@app.post("/predict")
def predict(data: dict):
    df = pd.DataFrame([data])
    pred_ext = model.predict(df)[0]

    record = {
        **data,
        "predicted_extraction_pct": float(pred_ext),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # STORE LOCALLY
    history_storage.append(record)

    return {"predicted_extraction_pct": float(pred_ext)}

# -----------------------------
# ⚙️ RECOMMEND WATER
# -----------------------------
@app.post("/recommend")
def recommend_setpoint(data: dict):
    df = pd.DataFrame([data])
    pred_ext = model.predict(df)[0]
    water_optimal = float(data["imbibition_water_pct_fiber"]) * 1.05

    result = {
        "recommended_water_pct_fiber": round(water_optimal, 2),
        "predicted_extraction": round(float(pred_ext), 2)
    }
    return {"recommendation": result}

# -----------------------------
# 📜 HISTORY LIST (RAM ONLY)
# -----------------------------
@app.get("/history")
def get_history():
    return {"history": history_storage}

# -----------------------------
# 🟠 DELETE SINGLE RECORD
# -----------------------------
@app.delete("/delete_record/{timestamp}")
def delete_record(timestamp: str):
    global history_storage
    before = len(history_storage)
    history_storage = [h for h in history_storage if h["timestamp"] != timestamp]
    deleted = before - len(history_storage)
    return {"deleted_count": deleted}

# -----------------------------
# 🔴 DELETE ALL RECORDS
# -----------------------------
@app.delete("/delete_all")
def delete_all_records():
    global history_storage
    history_storage = []
    return {"message": "All records deleted"}

# -----------------------------
# ⬇ DOWNLOAD REPORT AS EXCEL
# -----------------------------
@app.post("/download_report")
def download_report(data: dict):
    history = data.get("history", [])
    if not history:
        return {"error": "No history data to export"}

    df = pd.DataFrame(history)
    file_path = "mill_report.xlsx"
    df.to_excel(file_path, index=False)

    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="mill_report.xlsx"
    )

@app.get("/sample-data")
def get_sample_data():
    df = pd.read_csv("factory_realtime_data.csv")
    return df.to_dict(orient="records")
