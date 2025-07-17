from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import bcrypt
import jwt
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Configuration
SECRET_KEY = "aurum-finance-secret-key-2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Enums
class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCategory(str, Enum):
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT = "investment"
    HOUSING = "housing"
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    SHOPPING = "shopping"
    UTILITIES = "utilities"
    OTHER = "other"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: TransactionType
    amount: float
    description: str
    category: TransactionCategory
    date: datetime
    is_recurring: bool = False
    frequency: Optional[str] = None  # 'weekly', 'monthly', 'yearly'
    recurring_start_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float
    description: str
    category: TransactionCategory
    date: datetime
    is_recurring: bool = False
    frequency: Optional[str] = None
    recurring_start_date: Optional[datetime] = None

class Asset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    description: str
    current_value: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AssetCreate(BaseModel):
    description: str
    current_value: float

class Liability(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    description: str
    amount_owed: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LiabilityCreate(BaseModel):
    description: str
    amount_owed: float

class Budget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    month: int
    year: int
    category: TransactionCategory
    budget_amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BudgetCreate(BaseModel):
    month: int
    year: int
    category: TransactionCategory
    budget_amount: float

class SavingsGoal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    goal_name: str
    target_amount: float
    current_amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SavingsGoalCreate(BaseModel):
    goal_name: str
    target_amount: float
    current_amount: float = 0

class Debt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    debt_name: str
    total_balance: float
    interest_rate: float  # APR as percentage
    minimum_payment: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DebtCreate(BaseModel):
    debt_name: str
    total_balance: float
    interest_rate: float
    minimum_payment: float

class NetWorthSnapshot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    date: datetime
    total_assets: float
    total_liabilities: float
    net_worth: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise credentials_exception
    return User(**user)

# Auth routes
@api_router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name
    )
    
    await db.users.insert_one(user.dict())
    return UserResponse(**user.dict())

@api_router.post("/login")
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@api_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

# Transaction routes
@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction_data: TransactionCreate, current_user: User = Depends(get_current_user)):
    transaction = Transaction(
        user_id=current_user.id,
        **transaction_data.dict()
    )
    await db.transactions.insert_one(transaction.dict())
    return transaction

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    search_query: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    # Build query filters
    query_filter = {"user_id": current_user.id}
    
    # Date range filter
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            date_filter["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        query_filter["date"] = date_filter
    
    # Category filter
    if category:
        query_filter["category"] = category
    
    # Search query filter (searches in description)
    if search_query:
        query_filter["description"] = {"$regex": search_query, "$options": "i"}
    
    transactions = await db.transactions.find(query_filter).sort("date", -1).to_list(1000)
    return [Transaction(**transaction) for transaction in transactions]

@api_router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str, current_user: User = Depends(get_current_user)):
    result = await db.transactions.delete_one({"id": transaction_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

@api_router.post("/transactions/process-recurring")
async def process_recurring_transactions():
    """Process recurring transactions - typically called by a cron job"""
    today = datetime.now().date()
    
    # Get all recurring transactions
    recurring_transactions = await db.transactions.find({"is_recurring": True}).to_list(1000)
    
    processed_count = 0
    for recurring_transaction in recurring_transactions:
        transaction = Transaction(**recurring_transaction)
        
        # Calculate next due date based on frequency
        if not transaction.recurring_start_date:
            continue
            
        start_date = transaction.recurring_start_date.date()
        
        # Check if we need to create a new instance
        should_create = False
        next_date = None
        
        if transaction.frequency == "weekly":
            days_diff = (today - start_date).days
            if days_diff >= 0 and days_diff % 7 == 0:
                should_create = True
                next_date = today
        elif transaction.frequency == "monthly":
            # Simple monthly check - same day of month
            if today.day == start_date.day and today > start_date:
                # Check if we already created this month's transaction
                existing = await db.transactions.find_one({
                    "user_id": transaction.user_id,
                    "description": transaction.description,
                    "amount": transaction.amount,
                    "date": {
                        "$gte": datetime(today.year, today.month, 1),
                        "$lte": datetime(today.year, today.month, today.day)
                    },
                    "is_recurring": False
                })
                
                if not existing:
                    should_create = True
                    next_date = today
        elif transaction.frequency == "yearly":
            if today.month == start_date.month and today.day == start_date.day and today.year > start_date.year:
                # Check if we already created this year's transaction
                existing = await db.transactions.find_one({
                    "user_id": transaction.user_id,
                    "description": transaction.description,
                    "amount": transaction.amount,
                    "date": {
                        "$gte": datetime(today.year, 1, 1),
                        "$lte": datetime(today.year, 12, 31)
                    },
                    "is_recurring": False
                })
                
                if not existing:
                    should_create = True
                    next_date = today
        
        if should_create and next_date:
            # Create new transaction instance
            new_transaction = Transaction(
                user_id=transaction.user_id,
                type=transaction.type,
                amount=transaction.amount,
                description=f"{transaction.description} (Recurring)",
                category=transaction.category,
                date=datetime.combine(next_date, datetime.min.time()),
                is_recurring=False  # This is an instance, not the recurring template
            )
            
            await db.transactions.insert_one(new_transaction.dict())
            processed_count += 1
    
    return {"message": f"Processed {processed_count} recurring transactions"}

# Asset routes
@api_router.post("/assets", response_model=Asset)
async def create_asset(asset_data: AssetCreate, current_user: User = Depends(get_current_user)):
    asset = Asset(
        user_id=current_user.id,
        **asset_data.dict()
    )
    await db.assets.insert_one(asset.dict())
    return asset

@api_router.get("/assets", response_model=List[Asset])
async def get_assets(current_user: User = Depends(get_current_user)):
    assets = await db.assets.find({"user_id": current_user.id}).to_list(1000)
    return [Asset(**asset) for asset in assets]

@api_router.put("/assets/{asset_id}", response_model=Asset)
async def update_asset(asset_id: str, asset_data: AssetCreate, current_user: User = Depends(get_current_user)):
    update_data = asset_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.assets.update_one(
        {"id": asset_id, "user_id": current_user.id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    updated_asset = await db.assets.find_one({"id": asset_id, "user_id": current_user.id})
    return Asset(**updated_asset)

@api_router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str, current_user: User = Depends(get_current_user)):
    result = await db.assets.delete_one({"id": asset_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"message": "Asset deleted successfully"}

# Liability routes
@api_router.post("/liabilities", response_model=Liability)
async def create_liability(liability_data: LiabilityCreate, current_user: User = Depends(get_current_user)):
    liability = Liability(
        user_id=current_user.id,
        **liability_data.dict()
    )
    await db.liabilities.insert_one(liability.dict())
    return liability

@api_router.get("/liabilities", response_model=List[Liability])
async def get_liabilities(current_user: User = Depends(get_current_user)):
    liabilities = await db.liabilities.find({"user_id": current_user.id}).to_list(1000)
    return [Liability(**liability) for liability in liabilities]

@api_router.put("/liabilities/{liability_id}", response_model=Liability)
async def update_liability(liability_id: str, liability_data: LiabilityCreate, current_user: User = Depends(get_current_user)):
    update_data = liability_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.liabilities.update_one(
        {"id": liability_id, "user_id": current_user.id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Liability not found")
    
    updated_liability = await db.liabilities.find_one({"id": liability_id, "user_id": current_user.id})
    return Liability(**updated_liability)

@api_router.delete("/liabilities/{liability_id}")
async def delete_liability(liability_id: str, current_user: User = Depends(get_current_user)):
    result = await db.liabilities.delete_one({"id": liability_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Liability not found")
    return {"message": "Liability deleted successfully"}

# Budget routes
@api_router.post("/budgets", response_model=Budget)
async def create_budget(budget_data: BudgetCreate, current_user: User = Depends(get_current_user)):
    budget = Budget(
        user_id=current_user.id,
        **budget_data.dict()
    )
    await db.budgets.insert_one(budget.dict())
    return budget

@api_router.get("/budgets", response_model=List[Budget])
async def get_budgets(current_user: User = Depends(get_current_user)):
    budgets = await db.budgets.find({"user_id": current_user.id}).to_list(1000)
    return [Budget(**budget) for budget in budgets]

# Savings Goal routes
@api_router.post("/savings-goals", response_model=SavingsGoal)
async def create_savings_goal(goal_data: SavingsGoalCreate, current_user: User = Depends(get_current_user)):
    goal = SavingsGoal(
        user_id=current_user.id,
        **goal_data.dict()
    )
    await db.savings_goals.insert_one(goal.dict())
    return goal

@api_router.get("/savings-goals", response_model=List[SavingsGoal])
async def get_savings_goals(current_user: User = Depends(get_current_user)):
    goals = await db.savings_goals.find({"user_id": current_user.id}).to_list(1000)
    return [SavingsGoal(**goal) for goal in goals]

@api_router.put("/savings-goals/{goal_id}", response_model=SavingsGoal)
async def update_savings_goal(goal_id: str, goal_data: SavingsGoalCreate, current_user: User = Depends(get_current_user)):
    update_data = goal_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.savings_goals.update_one(
        {"id": goal_id, "user_id": current_user.id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    
    updated_goal = await db.savings_goals.find_one({"id": goal_id, "user_id": current_user.id})
    return SavingsGoal(**updated_goal)

# Dashboard analytics
@api_router.get("/dashboard/summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_user)):
    # Get current month's transactions
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get all transactions for current month
    transactions = await db.transactions.find({
        "user_id": current_user.id,
        "$expr": {
            "$and": [
                {"$eq": [{"$month": "$date"}, current_month]},
                {"$eq": [{"$year": "$date"}, current_year]}
            ]
        }
    }).to_list(1000)
    
    # Calculate monthly income and expenses
    monthly_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    monthly_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    
    # Get assets and liabilities
    assets = await db.assets.find({"user_id": current_user.id}).to_list(1000)
    liabilities = await db.liabilities.find({"user_id": current_user.id}).to_list(1000)
    
    total_assets = sum(asset["current_value"] for asset in assets)
    total_liabilities = sum(liability["amount_owed"] for liability in liabilities)
    net_worth = total_assets - total_liabilities
    
    # Expense breakdown by category
    expense_breakdown = {}
    for transaction in transactions:
        if transaction["type"] == "expense":
            category = transaction["category"]
            expense_breakdown[category] = expense_breakdown.get(category, 0) + transaction["amount"]
    
    return {
        "net_worth": net_worth,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "cash_flow": monthly_income - monthly_expenses,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "expense_breakdown": expense_breakdown
    }

# Reports endpoints
@api_router.get("/reports/cashflow")
async def get_cashflow_report(current_user: User = Depends(get_current_user)):
    """Get cash flow data for the last 12 months"""
    results = []
    
    for i in range(12):
        # Calculate the target month/year
        target_date = datetime.now().replace(day=1) - timedelta(days=i*30)
        target_month = target_date.month
        target_year = target_date.year
        
        # Get transactions for this month
        transactions = await db.transactions.find({
            "user_id": current_user.id,
            "$expr": {
                "$and": [
                    {"$eq": [{"$month": "$date"}, target_month]},
                    {"$eq": [{"$year": "$date"}, target_year]}
                ]
            }
        }).to_list(1000)
        
        # Calculate totals
        income = sum(t["amount"] for t in transactions if t["type"] == "income")
        expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
        
        results.append({
            "month": target_date.strftime("%Y-%m"),
            "month_name": target_date.strftime("%B %Y"),
            "income": income,
            "expenses": expenses,
            "net": income - expenses
        })
    
    return list(reversed(results))

@api_router.get("/reports/spending")
async def get_spending_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get spending breakdown by category for a date range"""
    # Default to current month if no dates provided
    if not start_date:
        start_date = datetime.now().replace(day=1).isoformat()
    if not end_date:
        end_date = datetime.now().isoformat()
    
    # Build query
    query = {
        "user_id": current_user.id,
        "type": "expense",
        "date": {
            "$gte": datetime.fromisoformat(start_date.replace('Z', '+00:00')),
            "$lte": datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        }
    }
    
    transactions = await db.transactions.find(query).to_list(1000)
    
    # Group by category
    category_totals = {}
    for transaction in transactions:
        category = transaction["category"]
        category_totals[category] = category_totals.get(category, 0) + transaction["amount"]
    
    # Format for frontend
    results = [
        {
            "category": category,
            "amount": amount,
            "percentage": (amount / sum(category_totals.values()) * 100) if category_totals else 0
        }
        for category, amount in category_totals.items()
    ]
    
    return {
        "total_spent": sum(category_totals.values()),
        "categories": sorted(results, key=lambda x: x["amount"], reverse=True),
        "date_range": {"start": start_date, "end": end_date}
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()