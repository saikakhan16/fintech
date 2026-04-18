"""Portfolio Analytics using SQLAlchemy-style queries on SQLite"""

import sqlite3
import json
from datetime import datetime


def get_portfolio_analytics(user_id: int) -> dict:
    conn = sqlite3.connect("fd_optimizer.db")
    c = conn.cursor()

    c.execute(
        "SELECT allocation, total_amount, expected_return, created_at FROM portfolios WHERE user_id=? ORDER BY created_at DESC LIMIT 20",
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()

    if not rows:
        return {"message": "No portfolios yet", "portfolios": [], "summary": {}}

    portfolios = []
    total_invested = 0
    returns = []

    for row in rows:
        allocation = json.loads(row[0])
        portfolios.append({
            "allocation": allocation,
            "total_amount": row[1],
            "expected_return": row[2],
            "created_at": row[3]
        })
        total_invested += row[1]
        returns.append(row[2])

    return {
        "portfolios": portfolios,
        "summary": {
            "total_portfolios": len(portfolios),
            "total_invested": total_invested,
            "average_return": round(sum(returns) / len(returns), 2) if returns else 0,
            "best_return": max(returns) if returns else 0,
            "latest_portfolio": portfolios[0] if portfolios else None
        }
    }
