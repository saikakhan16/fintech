"""Pydantic Models for Request/Response validation"""

from pydantic import BaseModel, Field
from typing import Optional, List


class UserProfile(BaseModel):
    age: Optional[int] = None
    monthly_income: Optional[float] = None
    risk_tolerance: Optional[str] = "moderate"
    is_senior_citizen: Optional[bool] = False


class OptimizationRequest(BaseModel):
    total_amount: float = Field(..., gt=0, description="Total investment amount in INR")
    risk_profile: str = Field("moderate", description="conservative | moderate | aggressive")
    tenure_months: int = Field(12, description="Investment tenure in months")
    preferred_banks: Optional[List[str]] = None
    exclude_nbfc: Optional[bool] = False
    prioritize_dicgc: Optional[bool] = True


class OptimizationResult(BaseModel):
    total_investment: float
    total_interest_earned: float
    total_maturity_amount: float
    expected_annual_return: float
    tenure_months: int
    risk_profile: str
    dicgc_compliance: bool
    num_banks_used: int
