# 🐝 FD Portfolio Optimizer — Powered by Particle Swarm Intelligence

> Built for Blostem AI Builder Hackathon | Open Track / Money Management

A production-grade Fixed Deposit portfolio optimizer that uses **Particle Swarm Optimization (PSO)** to allocate funds across 8 Blostem partner banks — maximizing returns while staying within DICGC insurance limits.

---

## 🏗️ Architecture

```
fd_optimizer/
├── backend/               # FastAPI + PSO Engine
│   ├── main.py            # API routes, auth, endpoints
│   ├── swarm_optimizer.py # PSO algorithm (core logic)
│   ├── fd_data.py         # Bank rates, RBI signals, tax advice
│   ├── auth.py            # JWT authentication
│   ├── models.py          # Pydantic schemas
│   ├── analytics.py       # SQLite portfolio analytics
│   └── requirements.txt
└── frontend/
    └── index.html         # Full dashboard (Chart.js, PSO JS port)
```

---

## 🔬 How Particle Swarm Optimization Works Here

### The Problem
Allocate ₹X across 8 banks to maximize returns, subject to:
- DICGC insurance limit: ₹5L per bank
- Concentration limit: 20% / 35% / 50% per bank (by risk profile)
- Sum of weights = 1.0

This is a **constrained nonlinear optimization problem** — perfect for metaheuristics.

### The PSO Solution

```
Each PARTICLE = a portfolio allocation [w1, w2, ..., w8]
  where wi = fraction invested in bank i, Σwi = 1.0

Each particle has:
  position  → current allocation
  velocity  → how allocation is shifting
  best_pos  → its personal best allocation found so far
  
The SWARM shares:
  global_best → best allocation found by any particle

Velocity Update (each iteration):
  v_new = W * v_old                        ← inertia (momentum)
          + C1 * r1 * (pbest - position)   ← cognitive (personal memory)
          + C2 * r2 * (gbest - position)   ← social (swarm knowledge)

W = 0.729 (inertia), C1 = C2 = 1.494 (cognitive/social balance)
```

### Fitness Function
```python
fitness = normalized_return
         - dicgc_penalty      # heavy if any bank > ₹5L
         - concentration_penalty  # if weight > risk limit
         + diversification_bonus  # entropy-based spread reward
         + credit_rating_bonus    # prefer AAA > AA > A+
```

### Convergence
- **60 particles** × **200 iterations** = 12,000 portfolio evaluations
- Adaptive inertia: W decreases from 0.729 → 0.438 (exploration → exploitation)
- Typically converges within 80–100 iterations

---

## 🔒 Security (RBAC from your previous project)

Borrowed from your Finance Data Processing System:

| Role    | Access |
|---------|--------|
| Admin   | All endpoints + user management |
| Analyst | Optimize + view analytics |  
| Viewer  | Compare rates only |

```python
# Custom FastAPI dependency
def require_role(role: str):
    def _check(current_user = Depends(get_current_user)):
        if current_user.role not in ALLOWED_ROLES[role]:
            raise HTTPException(403, "Insufficient permissions")
    return _check

@app.post("/optimize")
def optimize(req: ..., _=Depends(require_role("analyst"))):
    ...
```

---

## 🚀 Running Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
# API runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
# Open index.html directly in browser
# Or: python -m http.server 3000
```

---

## 📡 Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/token` | Login → JWT token |
| GET | `/banks` | All 8 partner banks + rates |
| POST | `/optimize` | **Run PSO optimization** |
| GET | `/analytics/compare` | Rate comparison table |
| GET | `/analytics/swarm-history` | PSO convergence data |
| GET | `/rbi-prediction` | RBI rate cycle signal |

### Sample Optimize Request
```json
POST /optimize
{
  "total_amount": 1000000,
  "risk_profile": "moderate",
  "tenure_months": 12
}
```

### Sample Response
```json
{
  "allocation": [
    {
      "bank_name": "Bajaj Finance",
      "allocated_amount": 348000,
      "weight_percent": 34.8,
      "interest_rate": 8.35,
      "maturity_amount": 377058,
      "dicgc_insured": true,
      "rating": "AAA"
    }
    // ... 7 more banks
  ],
  "expected_annual_return": 8.21,
  "total_maturity_amount": 1082100,
  "dicgc_compliance": true,
  "optimization_score": 0.0817,
  "ladder_strategy": [...],
  "tax_advice": {...},
  "rbi_signal": {...}
}
```

---

## 🎯 Hackathon Differentiators

1. **Real algorithm** — Not a simple sort. PSO is used in quantitative finance for portfolio optimization
2. **DICGC-aware** — Hard constraint baked into fitness function, not an afterthought
3. **Ladder strategy** — Automatically generates a 3/6/9/12M liquidity ladder from top allocations
4. **RBI signal** — Rate cycle prediction recommends optimal booking window
5. **Tax layer** — Form 15G/15H reminders, TDS threshold calculation
6. **Convergence visualization** — Shows the swarm actually working, not a black box
7. **RBAC integration** — Connects directly to your existing security project

---

## 🔮 Production Extensions

- Replace SQLite with PostgreSQL + Alembic migrations
- Add Account Aggregator (AA) framework for real income/expense data
- Train ML model on historical RBI MPC votes for better rate predictions
- Add WhatsApp notification on FD maturity (via Twilio/MSG91)
- Multi-objective PSO: balance return vs liquidity vs tax efficiency simultaneously

---

*Built with FastAPI · SQLAlchemy · PSO · Chart.js · Blostem SDK*
