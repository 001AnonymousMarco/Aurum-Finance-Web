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
        self.test_assets_management()
        self.test_liabilities_management()
        self.test_budget_management()
        self.test_savings_goals_management()
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