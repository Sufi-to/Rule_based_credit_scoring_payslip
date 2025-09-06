# Rule-Based Credit Scoring API

A FastAPI-based credit scoring system that evaluates creditworthiness based on payslip data using a rule-based algorithm.

## Overview

This API analyzes payslip data to generate a credit score (0-100) using a comprehensive rule-based model. The scoring algorithm uses **percentage-based and ratio-based evaluation** to ensure universal applicability across different currencies and economic contexts. The algorithm evaluates multiple financial indicators across four key pillars to determine creditworthiness, with special consideration for large loan amounts (100,000+).

## Features

- **REST API** built with FastAPI
- **Percentage-based scoring algorithm** with universal applicability
- **Ratio-based financial assessment** instead of fixed amount thresholds
- **Large loan evaluation** with payment capacity analysis
- **Comprehensive data validation** using Pydantic models
- **CORS support** for cross-origin requests
- **Detailed error handling** with appropriate HTTP status codes
- **Interactive API documentation** (Swagger/OpenAPI)

## Key Algorithm Improvements

### Universal Design Principles

- **Currency Independent**: Uses percentages and ratios instead of fixed amounts
- **Context Adaptive**: Works across different economic environments
- **Payment Capacity Focus**: Evaluates actual ability to service debt payments
- **Comprehensive Risk Assessment**: Considers multiple financial health indicators

### Scoring Philosophy

The algorithm prioritizes:

1. **Financial Efficiency**: How well income is retained after deductions
2. **Debt Management**: Existing debt burden relative to income capacity
3. **Payment Sustainability**: Ability to handle new loan payments
4. **Financial Planning**: Evidence of long-term financial responsibility

## Scoring Algorithm

The credit scoring model uses **percentage-based and ratio-based evaluation** for universal applicability. It evaluates four main pillars and includes special assessment for large loans (100,000+):

### 1. Income Strength & Stability (Max 35 points)

- **Net-to-Gross Ratio**: Measures income retention efficiency after deductions
  - ≥85% retention: 20 points (excellent financial efficiency)
  - 75-84% retention: 15 points (good)
  - 65-74% retention: 10 points (average)
  - <65% retention: 5 points (high deduction burden)
- **Salary Composition**: Basic salary to gross salary ratio (income stability)
  - ≥80%: 10 points (highly stable income)
  - ≥60%: 5 points (moderately stable)
- **Income Stability Flag**: 5 points if income is flagged as stable

### 2. Existing Debt Burden (Max 35 points)

- **Loan-to-Net Ratio**: Existing debt as percentage of net income
  - ≤10%: 25 points (excellent debt management)
  - ≤25%: 15 points (good debt levels)
  - ≤40%: 5 points (moderate debt burden)
  - >40%: 0 points (high debt burden)
- **Garnishments**: 10 points if no active garnishments

### 3. Financial Discipline (Max 20 points)

- **Disposable Income Ratio**: Available money as percentage of net salary
  - >40% of net salary: 15 points (excellent financial management)
  - 25-40% of net salary: 10 points (good management)
  - 15-24% of net salary: 5 points (moderate management)
  - <15% of net salary: 0 points (poor financial flexibility)
- **Pension Contribution Ratio**: 5 points if contributing ≥5% of salary to pension

### 4. Employment Stability (Max 10 points)

- **Employment Tenure**: Based on employment start date
  - >3 years: 10 points (excellent stability)
  - >1 year: 5 points (good stability)

### Large Loan Assessment (100,000+)

For loans ≥100,000, additional scrutiny is applied:

- **Payment-to-Income Ratio**: Estimated monthly payment vs net salary
  - >50% of income: -20 points (unsustainable payment burden)
  - >35% of income: -10 points (high payment risk)
- **Disposable Income Adequacy**: -15 points if disposable income < estimated payment

### Red Flag Penalties

- **Active Garnishments**: Score capped at 30 (major financial distress indicator)
- **High Existing Debt Ratio** (>50%): Score capped at 40 (unsustainable debt levels)

## API Endpoints

### POST `/evaluate_credit`

Evaluates creditworthiness based on payslip data with consideration for a 100,000 loan amount.

**Request Body:**

```json
{
  "success": true,
  "user_id": "string",
  "loan_id": "string",
  "features": {
    "net_salary": 12000.0,
    "gross_salary": 15000.0,
    "basic_salary": 12000.0,
    "employment_start_date": "2020-01-15",
    "pension": 1200.0,
    "garnishments": 0.0,
    "indicators": {
      "net_to_gross_ratio": 0.8,
      "deduction_ratio": 0.2,
      "allowance_ratio": 0.1,
      "overtime_ratio": 0.05,
      "bonus_ratio": 0.1,
      "loan_to_net_ratio": 0.15,
      "estimated_tax_rate": 0.15,
      "disposable_income": 8000.0,
      "savings_potential": 2000.0,
      "income_stability_flag": true,
      "benefits_value_estimate": 1500.0,
      "probable_student_flag": false
    }
  }
}
```

**Response:**

```json
{
  "user_id": "string",
  "loan_id": "string",
  "credit_score": 85
}
```

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd Rule_based_credit_scoring_payslip
   ```

2. **Create and activate virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic==2.5.0
   ```

## Running the API

### Development Mode

```bash
uvicorn main:app --reload
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at:

- **API**: <http://localhost:8000>
- **Interactive Docs**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## Data Models

### Input Models

**PayslipData**: Main request model containing user/loan IDs and features
**Features**: Financial data from payslip analysis
**Indicators**: Calculated financial health indicators

### Output Models

**CreditScoreResponse**: Contains user ID, loan ID, and calculated credit score (0-100)

## Error Handling

- **422 Unprocessable Entity**: Missing critical salary information
- **500 Internal Server Error**: Unexpected errors during calculation
- **Validation errors**: Automatic Pydantic validation for request data

## Requirements

- Python 3.12+
- FastAPI 0.104.1+
- Pydantic 2.5.0+
- Uvicorn 0.24.0+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
