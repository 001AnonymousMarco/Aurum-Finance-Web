#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Aurum Finance MVP
Tests all authentication, CRUD operations, and dashboard analytics
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Backend URL from frontend .env
BASE_URL = "https://0e07d175-cb42-451d-a3b6-9ca51d1b919d.preview.emergentagent.com/api"

class AurumFinanceAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        import time
        self.timestamp = int(time.time())
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    def log_result(self, test_name, success, message=""):
        if success:
            self.test_results["passed"] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED - {message}")
    
    def make_request(self, method, endpoint, data=None, auth_required=True):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if auth_required and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            
            return response
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        print("\n=== Testing User Registration ===")
        
        # Test successful registration with unique email
        user_data = {
            "email": f"sarah.johnson.{self.timestamp}@email.com",
            "password": "SecurePass123!",
            "name": "Sarah Johnson"
        }
        
        response = self.make_request("POST", "/register", user_data, auth_required=False)
        
        if response and response.status_code == 200:
            data = response.json()
            if "id" in data and "email" in data and "name" in data:
                self.log_result("User Registration", True, f"User created with ID: {data['id']}")
                return True
            else:
                self.log_result("User Registration", False, "Missing required fields in response")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("User Registration", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        return False
    
    def test_user_login(self):
        """Test user login endpoint"""
        print("\n=== Testing User Login ===")
        
        # Test successful login
        login_data = {
            "email": f"sarah.johnson.{self.timestamp}@email.com",
            "password": "SecurePass123!"
        }
        
        response = self.make_request("POST", "/login", login_data, auth_required=False)
        
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                self.auth_token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.log_result("User Login", True, f"Token received for user: {data['user']['name']}")
                return True
            else:
                self.log_result("User Login", False, "Missing access_token or user in response")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("User Login", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        return False
    
    def test_get_current_user(self):
        """Test get current user info endpoint"""
        print("\n=== Testing Get Current User ===")
        
        response = self.make_request("GET", "/me")
        
        if response and response.status_code == 200:
            data = response.json()
            if "id" in data and "email" in data and "name" in data:
                self.log_result("Get Current User", True, f"Retrieved user: {data['name']}")
                return True
            else:
                self.log_result("Get Current User", False, "Missing required fields in response")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Get Current User", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        return False
    
    def test_unauthorized_access(self):
        """Test that endpoints require authentication"""
        print("\n=== Testing Unauthorized Access ===")
        
        # Temporarily remove auth token
        temp_token = self.auth_token
        self.auth_token = None
        
        response = self.make_request("GET", "/me")
        
        if response and response.status_code in [401, 403]:
            self.log_result("Unauthorized Access Protection", True, f"Correctly rejected unauthorized request (Status: {response.status_code})")
            success = True
        else:
            self.log_result("Unauthorized Access Protection", False, f"Expected 401/403, got {response.status_code if response else 'None'}")
            success = False
        
        # Restore auth token
        self.auth_token = temp_token
        return success
    
    def test_transaction_management(self):
        """Test transaction CRUD operations"""
        print("\n=== Testing Transaction Management ===")
        
        # Create income transaction
        income_data = {
            "type": "income",
            "amount": 5500.00,
            "description": "Monthly Salary - Software Engineer",
            "category": "salary",
            "date": datetime.now().isoformat()
        }
        
        response = self.make_request("POST", "/transactions", income_data)
        income_id = None
        
        if response and response.status_code == 200:
            data = response.json()
            if "id" in data and data["type"] == "income":
                income_id = data["id"]
                self.log_result("Create Income Transaction", True, f"Created transaction: {data['description']}")
            else:
                self.log_result("Create Income Transaction", False, "Invalid transaction data returned")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Create Income Transaction", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Create expense transaction
        expense_data = {
            "type": "expense",
            "amount": 1200.00,
            "description": "Monthly Rent Payment",
            "category": "housing",
            "date": datetime.now().isoformat()
        }
        
        response = self.make_request("POST", "/transactions", expense_data)
        expense_id = None
        
        if response and response.status_code == 200:
            data = response.json()
            if "id" in data and data["type"] == "expense":
                expense_id = data["id"]
                self.log_result("Create Expense Transaction", True, f"Created transaction: {data['description']}")
            else:
                self.log_result("Create Expense Transaction", False, "Invalid transaction data returned")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Create Expense Transaction", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Get all transactions
        response = self.make_request("GET", "/transactions")
        
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) >= 2:
                self.log_result("Get All Transactions", True, f"Retrieved {len(data)} transactions")
            else:
                self.log_result("Get All Transactions", False, f"Expected list with 2+ items, got {type(data)} with {len(data) if isinstance(data, list) else 'unknown'} items")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Get All Transactions", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Delete transaction
        if expense_id:
            response = self.make_request("DELETE", f"/transactions/{expense_id}")
            
            if response and response.status_code == 200:
                self.log_result("Delete Transaction", True, "Transaction deleted successfully")
            else:
                error_msg = response.text if response else "No response"
                self.log_result("Delete Transaction", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_assets_management(self):
        """Test assets CRUD operations"""
        print("\n=== Testing Assets Management ===")
        
        # Create asset
        asset_data = {
            "description": "Primary Checking Account - Chase Bank",
            "current_value": 15000.00
        }
        
        response = self.make_request("POST", "/assets", asset_data)
        asset_id = None
        
        if response and response.status_code == 200:
            data = response.json()
            if "id" in data and "current_value" in data:
                asset_id = data["id"]
                self.log_result("Create Asset", True, f"Created asset: {data['description']}")
            else:
                self.log_result("Create Asset", False, "Invalid asset data returned")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Create Asset", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Get all assets
        response = self.make_request("GET", "/assets")
        
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) >= 1:
                self.log_result("Get All Assets", True, f"Retrieved {len(data)} assets")
            else:
                self.log_result("Get All Assets", False, f"Expected list with 1+ items, got {type(data)} with {len(data) if isinstance(data, list) else 'unknown'} items")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Get All Assets", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Update asset
        if asset_id:
            update_data = {
                "description": "Primary Checking Account - Chase Bank (Updated)",
                "current_value": 16500.00
            }
            
            response = self.make_request("PUT", f"/assets/{asset_id}", update_data)
            
            if response and response.status_code == 200:
                data = response.json()
                if data["current_value"] == 16500.00:
                    self.log_result("Update Asset", True, f"Asset updated to value: ${data['current_value']}")
                else:
                    self.log_result("Update Asset", False, "Asset value not updated correctly")
            else:
                error_msg = response.text if response else "No response"
                self.log_result("Update Asset", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Delete asset
        if asset_id:
            response = self.make_request("DELETE", f"/assets/{asset_id}")
            
            if response and response.status_code == 200:
                self.log_result("Delete Asset", True, "Asset deleted successfully")
            else:
                error_msg = response.text if response else "No response"
                self.log_result("Delete Asset", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_liabilities_management(self):
        """Test liabilities CRUD operations"""
        print("\n=== Testing Liabilities Management ===")
        
        # Create liability
        liability_data = {
            "description": "Student Loan - Federal Direct",
            "amount_owed": 25000.00
        }
        
        response = self.make_request("POST", "/liabilities", liability_data)
        liability_id = None
        
        if response and response.status_code == 200:
            data = response.json()
            if "id" in data and "amount_owed" in data:
                liability_id = data["id"]
                self.log_result("Create Liability", True, f"Created liability: {data['description']}")
            else:
                self.log_result("Create Liability", False, "Invalid liability data returned")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Create Liability", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Get all liabilities
        response = self.make_request("GET", "/liabilities")
        
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) >= 1:
                self.log_result("Get All Liabilities", True, f"Retrieved {len(data)} liabilities")
            else:
                self.log_result("Get All Liabilities", False, f"Expected list with 1+ items, got {type(data)} with {len(data) if isinstance(data, list) else 'unknown'} items")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Get All Liabilities", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Update liability
        if liability_id:
            update_data = {
                "description": "Student Loan - Federal Direct (Updated)",
                "amount_owed": 23500.00
            }
            
            response = self.make_request("PUT", f"/liabilities/{liability_id}", update_data)
            
            if response and response.status_code == 200:
                data = response.json()
                if data["amount_owed"] == 23500.00:
                    self.log_result("Update Liability", True, f"Liability updated to amount: ${data['amount_owed']}")
                else:
                    self.log_result("Update Liability", False, "Liability amount not updated correctly")
            else:
                error_msg = response.text if response else "No response"
                self.log_result("Update Liability", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Delete liability
        if liability_id:
            response = self.make_request("DELETE", f"/liabilities/{liability_id}")
            
            if response and response.status_code == 200:
                self.log_result("Delete Liability", True, "Liability deleted successfully")
            else:
                error_msg = response.text if response else "No response"
                self.log_result("Delete Liability", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_budget_management(self):
        """Test budget management"""
        print("\n=== Testing Budget Management ===")
        
        # Create budget
        budget_data = {
            "month": datetime.now().month,
            "year": datetime.now().year,
            "category": "food",
            "budget_amount": 800.00
        }
        
        response = self.make_request("POST", "/budgets", budget_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if "id" in data and "budget_amount" in data:
                self.log_result("Create Budget", True, f"Created budget for {data['category']}: ${data['budget_amount']}")
            else:
                self.log_result("Create Budget", False, "Invalid budget data returned")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Create Budget", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Get all budgets
        response = self.make_request("GET", "/budgets")
        
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) >= 1:
                self.log_result("Get All Budgets", True, f"Retrieved {len(data)} budgets")
            else:
                self.log_result("Get All Budgets", False, f"Expected list with 1+ items, got {type(data)} with {len(data) if isinstance(data, list) else 'unknown'} items")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Get All Budgets", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_savings_goals_management(self):
        """Test savings goals CRUD operations"""
        print("\n=== Testing Savings Goals Management ===")
        
        # Create savings goal
        goal_data = {
            "goal_name": "Emergency Fund",
            "target_amount": 10000.00,
            "current_amount": 2500.00
        }
        
        response = self.make_request("POST", "/savings-goals", goal_data)
        goal_id = None
        
        if response and response.status_code == 200:
            data = response.json()
            if "id" in data and "target_amount" in data:
                goal_id = data["id"]
                self.log_result("Create Savings Goal", True, f"Created goal: {data['goal_name']} (${data['current_amount']}/${data['target_amount']})")
            else:
                self.log_result("Create Savings Goal", False, "Invalid savings goal data returned")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Create Savings Goal", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Get all savings goals
        response = self.make_request("GET", "/savings-goals")
        
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) >= 1:
                self.log_result("Get All Savings Goals", True, f"Retrieved {len(data)} savings goals")
            else:
                self.log_result("Get All Savings Goals", False, f"Expected list with 1+ items, got {type(data)} with {len(data) if isinstance(data, list) else 'unknown'} items")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Get All Savings Goals", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Update savings goal
        if goal_id:
            update_data = {
                "goal_name": "Emergency Fund (Updated)",
                "target_amount": 12000.00,
                "current_amount": 3000.00
            }
            
            response = self.make_request("PUT", f"/savings-goals/{goal_id}", update_data)
            
            if response and response.status_code == 200:
                data = response.json()
                if data["current_amount"] == 3000.00 and data["target_amount"] == 12000.00:
                    self.log_result("Update Savings Goal", True, f"Goal updated: ${data['current_amount']}/${data['target_amount']}")
                else:
                    self.log_result("Update Savings Goal", False, "Savings goal not updated correctly")
            else:
                error_msg = response.text if response else "No response"
                self.log_result("Update Savings Goal", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_enhanced_transaction_features(self):
        """Test enhanced transaction features: filtering, recurring transactions"""
        print("\n=== Testing Enhanced Transaction Features ===")
        
        # Create test transactions with different dates and categories
        test_transactions = [
            {
                "type": "income",
                "amount": 3000.00,
                "description": "Freelance Project Payment",
                "category": "freelance",
                "date": (datetime.now() - timedelta(days=30)).isoformat()
            },
            {
                "type": "expense",
                "amount": 150.00,
                "description": "Grocery Shopping",
                "category": "food",
                "date": (datetime.now() - timedelta(days=15)).isoformat()
            },
            {
                "type": "expense",
                "amount": 80.00,
                "description": "Gas Station",
                "category": "transport",
                "date": datetime.now().isoformat()
            }
        ]
        
        # Create test transactions
        created_ids = []
        for transaction_data in test_transactions:
            response = self.make_request("POST", "/transactions", transaction_data)
            if response and response.status_code == 200:
                created_ids.append(response.json()["id"])
        
        # Test date range filtering
        start_date = (datetime.now() - timedelta(days=20)).isoformat()
        end_date = datetime.now().isoformat()
        
        response = self.make_request("GET", f"/transactions?start_date={start_date}&end_date={end_date}")
        
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                # Should get transactions from last 20 days (2 transactions)
                filtered_count = len([t for t in data if t["category"] in ["food", "transport"]])
                if filtered_count >= 2:
                    self.log_result("Transaction Date Range Filtering", True, f"Retrieved {filtered_count} transactions in date range")
                else:
                    self.log_result("Transaction Date Range Filtering", False, f"Expected 2+ transactions, got {filtered_count}")
            else:
                self.log_result("Transaction Date Range Filtering", False, "Expected list response")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Transaction Date Range Filtering", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Test category filtering
        response = self.make_request("GET", "/transactions?category=food")
        
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                food_transactions = [t for t in data if t["category"] == "food"]
                if len(food_transactions) >= 1:
                    self.log_result("Transaction Category Filtering", True, f"Retrieved {len(food_transactions)} food transactions")
                else:
                    self.log_result("Transaction Category Filtering", False, "No food transactions found")
            else:
                self.log_result("Transaction Category Filtering", False, "Expected list response")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Transaction Category Filtering", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Test search query filtering
        response = self.make_request("GET", "/transactions?search_query=Grocery")
        
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                grocery_transactions = [t for t in data if "Grocery" in t["description"]]
                if len(grocery_transactions) >= 1:
                    self.log_result("Transaction Search Query Filtering", True, f"Found {len(grocery_transactions)} transactions matching 'Grocery'")
                else:
                    self.log_result("Transaction Search Query Filtering", False, "No transactions found matching 'Grocery'")
            else:
                self.log_result("Transaction Search Query Filtering", False, "Expected list response")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Transaction Search Query Filtering", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Test recurring transaction creation
        recurring_data = {
            "type": "expense",
            "amount": 1200.00,
            "description": "Monthly Rent Payment",
            "category": "housing",
            "date": datetime.now().isoformat(),
            "is_recurring": True,
            "frequency": "monthly",
            "recurring_start_date": datetime.now().isoformat()
        }
        
        response = self.make_request("POST", "/transactions", recurring_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("is_recurring") == True and data.get("frequency") == "monthly":
                self.log_result("Create Recurring Transaction", True, f"Created recurring transaction: {data['description']}")
            else:
                self.log_result("Create Recurring Transaction", False, "Recurring transaction fields not set correctly")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Create Recurring Transaction", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Test process recurring transactions endpoint
        response = self.make_request("POST", "/transactions/process-recurring", auth_required=False)
        
        if response and response.status_code == 200:
            data = response.json()
            if "message" in data and "Processed" in data["message"]:
                self.log_result("Process Recurring Transactions", True, data["message"])
            else:
                self.log_result("Process Recurring Transactions", False, "Invalid response format")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Process Recurring Transactions", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_debt_management(self):
        """Test debt management CRUD operations"""
        print("\n=== Testing Debt Management ===")
        
        # Create debt
        debt_data = {
            "debt_name": "Credit Card - Chase Sapphire",
            "total_balance": 4500.00,
            "interest_rate": 18.99,
            "minimum_payment": 150.00
        }
        
        response = self.make_request("POST", "/debts", debt_data)
        debt_id = None
        
        if response and response.status_code == 200:
            data = response.json()
            if "id" in data and "debt_name" in data and "total_balance" in data:
                debt_id = data["id"]
                self.log_result("Create Debt", True, f"Created debt: {data['debt_name']} - ${data['total_balance']}")
            else:
                self.log_result("Create Debt", False, "Invalid debt data returned")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Create Debt", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Get all debts
        response = self.make_request("GET", "/debts")
        
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) >= 1:
                self.log_result("Get All Debts", True, f"Retrieved {len(data)} debts")
            else:
                self.log_result("Get All Debts", False, f"Expected list with 1+ items, got {type(data)} with {len(data) if isinstance(data, list) else 'unknown'} items")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Get All Debts", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Update debt
        if debt_id:
            update_data = {
                "debt_name": "Credit Card - Chase Sapphire (Updated)",
                "total_balance": 4200.00,
                "interest_rate": 18.99,
                "minimum_payment": 140.00
            }
            
            response = self.make_request("PUT", f"/debts/{debt_id}", update_data)
            
            if response and response.status_code == 200:
                data = response.json()
                if data["total_balance"] == 4200.00 and data["minimum_payment"] == 140.00:
                    self.log_result("Update Debt", True, f"Debt updated: ${data['total_balance']} balance, ${data['minimum_payment']} minimum payment")
                else:
                    self.log_result("Update Debt", False, "Debt not updated correctly")
            else:
                error_msg = response.text if response else "No response"
                self.log_result("Update Debt", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Delete debt
        if debt_id:
            response = self.make_request("DELETE", f"/debts/{debt_id}")
            
            if response and response.status_code == 200:
                self.log_result("Delete Debt", True, "Debt deleted successfully")
            else:
                error_msg = response.text if response else "No response"
                self.log_result("Delete Debt", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_reports_endpoints(self):
        """Test reports endpoints: cashflow and spending"""
        print("\n=== Testing Reports Endpoints ===")
        
        # Create some test data for reports
        # Create transactions across different months
        test_data = [
            {
                "type": "income",
                "amount": 5000.00,
                "description": "Salary - Current Month",
                "category": "salary",
                "date": datetime.now().isoformat()
            },
            {
                "type": "expense",
                "amount": 1200.00,
                "description": "Rent - Current Month",
                "category": "housing",
                "date": datetime.now().isoformat()
            },
            {
                "type": "expense",
                "amount": 300.00,
                "description": "Groceries - Current Month",
                "category": "food",
                "date": datetime.now().isoformat()
            },
            {
                "type": "income",
                "amount": 4800.00,
                "description": "Salary - Last Month",
                "category": "salary",
                "date": (datetime.now() - timedelta(days=35)).isoformat()
            },
            {
                "type": "expense",
                "amount": 1200.00,
                "description": "Rent - Last Month",
                "category": "housing",
                "date": (datetime.now() - timedelta(days=35)).isoformat()
            }
        ]
        
        # Create test transactions
        for transaction_data in test_data:
            self.make_request("POST", "/transactions", transaction_data)
        
        # Test cashflow report
        response = self.make_request("GET", "/reports/cashflow")
        
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) == 12:
                # Check if we have proper structure
                first_month = data[0]
                required_fields = ["month", "month_name", "income", "expenses", "net"]
                
                if all(field in first_month for field in required_fields):
                    self.log_result("Cashflow Report", True, f"Retrieved 12 months of cashflow data")
                else:
                    self.log_result("Cashflow Report", False, f"Missing required fields in cashflow data")
            else:
                self.log_result("Cashflow Report", False, f"Expected list with 12 items, got {len(data) if isinstance(data, list) else 'not a list'}")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Cashflow Report", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Test spending report with date range
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
        end_date = datetime.now().isoformat()
        
        response = self.make_request("GET", f"/reports/spending?start_date={start_date}&end_date={end_date}")
        
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["total_spent", "categories", "date_range"]
            
            if all(field in data for field in required_fields):
                if isinstance(data["categories"], list) and len(data["categories"]) > 0:
                    # Check category structure
                    first_category = data["categories"][0]
                    category_fields = ["category", "amount", "percentage"]
                    
                    if all(field in first_category for field in category_fields):
                        self.log_result("Spending Report", True, f"Retrieved spending data: ${data['total_spent']} total, {len(data['categories'])} categories")
                    else:
                        self.log_result("Spending Report", False, "Invalid category structure in spending report")
                else:
                    self.log_result("Spending Report", False, "No categories found in spending report")
            else:
                self.log_result("Spending Report", False, f"Missing required fields in spending report")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Spending Report", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Test spending report without date parameters (should default to current month)
        response = self.make_request("GET", "/reports/spending")
        
        if response and response.status_code == 200:
            data = response.json()
            if "total_spent" in data and "categories" in data:
                self.log_result("Spending Report (Default Date Range)", True, f"Retrieved default spending data: ${data['total_spent']} total")
            else:
                self.log_result("Spending Report (Default Date Range)", False, "Invalid response structure")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Spending Report (Default Date Range)", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")

    def test_dashboard_analytics(self):
        """Test dashboard analytics endpoint"""
        print("\n=== Testing Dashboard Analytics ===")
        
        # First create some test data for analytics
        # Create an asset
        asset_data = {
            "description": "Savings Account",
            "current_value": 20000.00
        }
        self.make_request("POST", "/assets", asset_data)
        
        # Create a liability
        liability_data = {
            "description": "Credit Card Debt",
            "amount_owed": 3000.00
        }
        self.make_request("POST", "/liabilities", liability_data)
        
        # Create some transactions for current month
        income_data = {
            "type": "income",
            "amount": 6000.00,
            "description": "Monthly Salary",
            "category": "salary",
            "date": datetime.now().isoformat()
        }
        self.make_request("POST", "/transactions", income_data)
        
        expense_data = {
            "type": "expense",
            "amount": 1500.00,
            "description": "Rent Payment",
            "category": "housing",
            "date": datetime.now().isoformat()
        }
        self.make_request("POST", "/transactions", expense_data)
        
        # Now test dashboard summary
        response = self.make_request("GET", "/dashboard/summary")
        
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["net_worth", "monthly_income", "monthly_expenses", "cash_flow", 
                             "total_assets", "total_liabilities", "expense_breakdown"]
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                # Verify calculations
                expected_net_worth = data["total_assets"] - data["total_liabilities"]
                expected_cash_flow = data["monthly_income"] - data["monthly_expenses"]
                
                if (abs(data["net_worth"] - expected_net_worth) < 0.01 and 
                    abs(data["cash_flow"] - expected_cash_flow) < 0.01):
                    self.log_result("Dashboard Analytics", True, 
                                  f"Net Worth: ${data['net_worth']}, Cash Flow: ${data['cash_flow']}")
                else:
                    self.log_result("Dashboard Analytics", False, 
                                  f"Calculation errors - Net Worth: {data['net_worth']} vs {expected_net_worth}, Cash Flow: {data['cash_flow']} vs {expected_cash_flow}")
            else:
                self.log_result("Dashboard Analytics", False, f"Missing fields: {missing_fields}")
        else:
            error_msg = response.text if response else "No response"
            self.log_result("Dashboard Analytics", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Aurum Finance Backend API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Authentication flow tests
        if not self.test_user_registration():
            print("❌ Registration failed - cannot continue with other tests")
            return False
        
        if not self.test_user_login():
            print("❌ Login failed - cannot continue with authenticated tests")
            return False
        
        # Test authenticated endpoints
        self.test_get_current_user()
        self.test_unauthorized_access()
        
        # Core functionality tests
        self.test_transaction_management()
        self.test_enhanced_transaction_features()
        self.test_assets_management()
        self.test_liabilities_management()
        self.test_budget_management()
        self.test_savings_goals_management()
        self.test_debt_management()
        self.test_reports_endpoints()
        self.test_dashboard_analytics()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.test_results['passed'] / 
                       (self.test_results['passed'] + self.test_results['failed'])) * 100
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = AurumFinanceAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)