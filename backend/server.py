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
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float
    description: str
    category: TransactionCategory
    date: datetime

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
async def get_transactions(current_user: User = Depends(get_current_user)):
    transactions = await db.transactions.find({"user_id": current_user.id}).to_list(1000)
    return [Transaction(**transaction) for transaction in transactions]

@api_router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str, current_user: User = Depends(get_current_user)):
    result = await db.transactions.delete_one({"id": transaction_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

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