"""
FD Portfolio Optimizer - Main FastAPI Application
Uses Particle Swarm Optimization (PSO) for portfolio allocation
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import uvicorn

from auth import create_token, verify_token, hash_password, verify_password
from models import UserProfile, OptimizationRequest, OptimizationResult
from swarm_optimizer import SwarmOptimizer
from fd_data import FD_BANKS, get_rbi_rate_prediction, get_tax_optimization
from analytics import get_portfolio_analytics
import sqlite3
import json
from datetime import datetime

app = FastAPI(
    title="FD Portfolio Optimizer",
    description="AI-Powered Fixed Deposit Portfolio Optimizer with Swarm Intelligence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ─── DB SETUP ────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect("fd_optimizer.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            profile TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            allocation TEXT NOT NULL,
            total_amount REAL,
            expected_return REAL,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    # Insert demo user
    try:
        c.execute(
            "INSERT INTO users (username, hashed_password, created_at) VALUES (?, ?, ?)",
            ("demo", hash_password("demo123"), datetime.now().isoformat())
        )
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()

init_db()

# ─── AUTH HELPERS ─────────────────────────────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]

def get_db_user(username: str):
    conn = sqlite3.connect("fd_optimizer.db")
    c = conn.cursor()
    c.execute("SELECT id, username, hashed_password, profile FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row

# ─── AUTH ENDPOINTS ───────────────────────────────────────────────────────────

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_db_user(form_data.username)
    if not user or not verify_password(form_data.password, user[2]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token({"sub": form_data.username, "user_id": user[0]})
    return {"access_token": token, "token_type": "bearer"}

class RegisterRequest(BaseModel):
    username: str
    password: str

@app.post("/register")
def register(req: RegisterRequest):
    conn = sqlite3.connect("fd_optimizer.db")
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, hashed_password, created_at) VALUES (?, ?, ?)",
            (req.username, hash_password(req.password), datetime.now().isoformat())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()
    return {"message": "User registered successfully"}

# ─── BANK DATA ENDPOINTS ──────────────────────────────────────────────────────

@app.get("/banks")
def get_banks():
    """Get all Blostem partner banks with current FD rates"""
    return {"banks": FD_BANKS}

@app.get("/rbi-prediction")
def rbi_prediction():
    """Get AI prediction on RBI rate cycle"""
    return get_rbi_rate_prediction()

# ─── OPTIMIZATION ENDPOINT ────────────────────────────────────────────────────

@app.post("/optimize", response_model=dict)
def optimize_portfolio(req: OptimizationRequest, username: str = Depends(get_current_user)):
    """
    Core endpoint: Runs Particle Swarm Optimization to allocate FD portfolio.
    Maximizes returns while respecting DICGC insurance limits (₹5L/bank).
    """
    optimizer = SwarmOptimizer(
        total_amount=req.total_amount,
        risk_profile=req.risk_profile,
        tenure_months=req.tenure_months,
        banks=FD_BANKS,
        dicgc_limit=500000,
        num_particles=60,
        max_iterations=200
    )
    result = optimizer.optimize()

    # Save to DB
    user = get_db_user(username)
    if user:
        conn = sqlite3.connect("fd_optimizer.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO portfolios (user_id, allocation, total_amount, expected_return, created_at) VALUES (?,?,?,?,?)",
            (user[0], json.dumps(result["allocation"]), req.total_amount, result["expected_annual_return"], datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    # Append tax optimization advice
    result["tax_advice"] = get_tax_optimization(req.total_amount, result["expected_annual_return"])
    result["rbi_signal"] = get_rbi_rate_prediction()
    result["ladder_strategy"] = optimizer.build_ladder_strategy(result["allocation"])

    return result

# ─── ANALYTICS ENDPOINTS ─────────────────────────────────────────────────────

@app.get("/analytics/portfolio")
def portfolio_analytics(username: str = Depends(get_current_user)):
    """Get historical portfolio performance analytics"""
    user = get_db_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return get_portfolio_analytics(user[0])

@app.get("/analytics/compare")
def compare_banks(amount: float = 100000, tenure: int = 12):
    """Compare returns across all banks for a given amount and tenure"""
    comparisons = []
    for bank in FD_BANKS:
        rate = bank["rates"].get(str(tenure), bank["rates"].get("12", 7.0))
        interest = amount * (rate / 100) * (tenure / 12)
        comparisons.append({
            "bank": bank["name"],
            "rate": rate,
            "interest_earned": round(interest, 2),
            "maturity_amount": round(amount + interest, 2),
            "dicgc_insured": amount <= 500000,
            "rating": bank["rating"]
        })
    comparisons.sort(key=lambda x: x["rate"], reverse=True)
    return {"comparisons": comparisons, "amount": amount, "tenure_months": tenure}

@app.get("/analytics/swarm-history")
def swarm_history():
    """Returns swarm convergence data for visualization"""
    optimizer = SwarmOptimizer(
        total_amount=1000000, risk_profile="moderate",
        tenure_months=12, banks=FD_BANKS,
        num_particles=30, max_iterations=50
    )
    optimizer.optimize()
    return {"convergence": optimizer.convergence_history, "particles": optimizer.particle_history}

@app.get("/")
def root():
    return {"status": "FD Portfolio Optimizer API Running", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
