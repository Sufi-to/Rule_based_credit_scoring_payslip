from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware


class Indicators(BaseModel):
    net_to_gross_ratio: Optional[float] = None
    deduction_ratio: Optional[float] = None
    allowance_ratio: Optional[float] = None
    overtime_ratio: Optional[float] = None
    bonus_ratio: Optional[float] = None
    loan_to_net_ratio: Optional[float] = None
    estimated_tax_rate: Optional[float] = None
    disposable_income: Optional[float] = None
    savings_potential: Optional[float] = None
    income_stability_flag: Optional[bool] = None
    benefits_value_estimate: Optional[float] = None
    probable_student_flag: Optional[bool] = None

class Features(BaseModel):
    net_salary: Optional[float] = None
    gross_salary: Optional[float] = None
    basic_salary: Optional[float] = None
    employment_start_date: Optional[str] = None
    pension: Optional[float] = None
    garnishments: Optional[float] = None
    indicators: Indicators
    # Add other feature fields if you need them for validation
    
class PayslipData(BaseModel):
    """Defines the structure of the incoming request body."""
    success: bool
    user_id: str
    loan_id: str
    features: Features
    # Add other top-level fields if needed

# --- Pydantic Model for the Output Response ---

class CreditScoreResponse(BaseModel):
    """Defines the structure of the outgoing JSON response."""
    user_id: str
    loan_id: str
    credit_score: int = Field(..., ge=0, le=100, description="The calculated credit score, from 0 to 100.")
    


# Place this function in the same file or import it
def calculate_credit_score(data: dict, requested_loan_amount: float = 100000) -> int:
    """
    Calculates a credit score out of 100 based on payslip data and loan amount.
    Uses percentage-based and ratio-based scoring for better universality.
    """
    score = 0
    features = data.get("features", {})
    indicators = features.get("indicators", {})

    # --- Pillar 1: Income Strength & Stability (Max 35) ---
    net_salary = features.get("net_salary")
    gross_salary = features.get("gross_salary")
    basic_salary = features.get("basic_salary")

    # Income evaluation based on net-to-gross ratio (more universal than fixed amounts)
    if net_salary is not None and gross_salary is not None and gross_salary > 0:
        net_to_gross_ratio = net_salary / gross_salary
        
        # Score based on how much of gross salary is retained (after deductions)
        if net_to_gross_ratio >= 0.85: score += 20  # Excellent (85%+ retention)
        elif net_to_gross_ratio >= 0.75: score += 15  # Good (75-84% retention)
        elif net_to_gross_ratio >= 0.65: score += 10  # Average (65-74% retention)
        else: score += 5  # Poor (<65% retention - high deductions)
    
    # Salary composition analysis (basic salary stability)
    if basic_salary is not None and gross_salary is not None and gross_salary > 0:
        composition_ratio = basic_salary / gross_salary
        if composition_ratio >= 0.8: score += 10  # Stable income (80%+ basic)
        elif composition_ratio >= 0.6: score += 5   # Moderate stability (60-79% basic)

    # Income stability indicator
    if indicators.get("income_stability_flag"):
        score += 5

    # --- Pillar 2: Existing Debt Burden (Max 35) ---
    loan_to_net_ratio = indicators.get("loan_to_net_ratio")
    garnishments = features.get("garnishments")

    # Existing debt burden assessment
    if loan_to_net_ratio is not None:
        if loan_to_net_ratio <= 0.1: score += 25      # Excellent (<10% of income)
        elif loan_to_net_ratio <= 0.25: score += 15   # Good (10-25% of income)
        elif loan_to_net_ratio <= 0.4: score += 5     # Moderate (25-40% of income)
        # No points for >40% debt burden
    
    # No garnishments is positive
    if garnishments is None or garnishments == 0:
        score += 10

    # --- Pillar 3: Financial Discipline (Max 20) ---
    disposable_income = indicators.get("disposable_income")
    pension = features.get("pension")

    # Disposable income as percentage of net salary
    if disposable_income is not None and net_salary is not None and net_salary > 0:
        disposable_ratio = disposable_income / net_salary
        if disposable_ratio > 0.4: score += 15        # Excellent (>40% disposable)
        elif disposable_ratio >= 0.25: score += 10    # Good (25-40% disposable)
        elif disposable_ratio >= 0.15: score += 5     # Moderate (15-24% disposable)
        # No points for <15% disposable income

    # Pension contribution shows financial planning
    if pension is not None and pension > 0 and net_salary is not None and net_salary > 0:
        pension_ratio = pension / net_salary
        if pension_ratio >= 0.05: score += 5  # Contributing 5%+ to pension

    # --- Pillar 4: Employment Stability (Max 10) ---
    start_date_str = features.get("employment_start_date")
    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str.split('T')[0])
            tenure_days = (datetime.now() - start_date).days
            if tenure_days > 3 * 365: score += 10      # >3 years tenure
            elif tenure_days > 1 * 365: score += 5     # >1 year tenure
        except (ValueError, TypeError):
            pass

    # --- Loan Affordability Assessment (Adjusts final score) ---
    if net_salary is not None and net_salary > 0:
        annual_income = net_salary * 12
        loan_affordability_ratio = requested_loan_amount / annual_income
        
        # Loan affordability penalties based on income multiples
        if loan_affordability_ratio > 8:      # Loan > 8x annual income
            score = max(score - 30, 0)
        elif loan_affordability_ratio > 5:    # Loan > 5x annual income
            score = max(score - 20, 0)
        elif loan_affordability_ratio > 3:    # Loan > 3x annual income
            score = max(score - 10, 0)
        elif loan_affordability_ratio > 2:    # Loan > 2x annual income
            score = max(score - 5, 0)
            
        # Additional scrutiny for large loans (100k+)
        if requested_loan_amount >= 100000:
            # Check if monthly income can support large loan payments
            monthly_payment_estimate = requested_loan_amount * 0.01  # Rough 1% monthly payment
            payment_to_income_ratio = monthly_payment_estimate / net_salary
            
            if payment_to_income_ratio > 0.5:  # Payment >50% of income
                score = max(score - 20, 0)
            elif payment_to_income_ratio > 0.35:  # Payment >35% of income
                score = max(score - 10, 0)
            
            # Check disposable income adequacy for large loans
            if disposable_income is not None:
                if disposable_income < monthly_payment_estimate:
                    score = max(score - 15, 0)

    # --- Applying Red Flag Penalties ---
    # Active garnishments are a major red flag
    if garnishments is not None and garnishments > 0:
        score = min(score, 30)

    # High existing debt burden caps the score
    if loan_to_net_ratio is not None and loan_to_net_ratio > 0.5:
        score = min(score, 40)
        
    # Critical information validation
    if net_salary is None or gross_salary is None:
        raise ValueError("Critical salary information is missing. Cannot calculate score.")

    return min(score, 100)



# Initialize your FastAPI app
app = FastAPI(
    title="Credit Scoring API",
    description="An API to evaluate creditworthiness based on payslip data."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = "*",
    allow_credentials = False,
    allow_methods = "*",
    allow_headers = "*"
)

@app.post("/evaluate_credit", response_model=CreditScoreResponse, tags=["Credit Scoring"])
async def evaluate_credit_score(payslip_data: PayslipData):
    """
    Receives payslip analysis data and returns a calculated credit score.

    This endpoint uses a rule-based model to evaluate the financial health
    indicators from a payslip and produces a score out of 100.
    The scoring considers a default loan amount of 100,000 for testing purposes.
    """
    try:
        # Pydantic has already validated the incoming data structure.
        # Now we convert the Pydantic model to a dictionary to pass to our scoring function.
        data_dict = payslip_data.model_dump()
        
        # Set the loan amount for testing (100,000 as requested)
        requested_loan_amount = 100000
        
        # Calculate the score with the specified loan amount
        score = calculate_credit_score(data_dict, requested_loan_amount)
        
        # Create and return the response using our response model
        response_data = CreditScoreResponse(
            user_id=payslip_data.user_id,
            loan_id=payslip_data.loan_id,
            credit_score=score,
        )
        return response_data

    except ValueError as e:
        # This catches the specific error we raised for missing salary data
        raise HTTPException(
            status_code=422, # Unprocessable Entity
            detail=str(e)
        )
    except Exception as e:
        # A general catch-all for any other unexpected errors during scoring
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during score calculation: {str(e)}"
        )