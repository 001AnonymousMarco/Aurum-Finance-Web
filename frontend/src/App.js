import React, { useState, useEffect, createContext, useContext } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { 
  PieChart, 
  Pie, 
  Cell, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import { 
  Plus, 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  Wallet, 
  PiggyBank, 
  Target,
  Home,
  CreditCard,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
  Search,
  Filter,
  FileText,
  Calendar,
  Repeat,
  Calculator,
  Edit,
  Trash2
} from 'lucide-react';
import { Dialog, Transition } from '@headlessui/react';
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      checkAuth();
    } else {
      setLoading(false);
    }
  }, [token]);

  const checkAuth = async () => {
    try {
      const response = await axios.get(`${API}/me`);
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('token');
      setToken(null);
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/login`, { email, password });
      const { access_token, user } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(user);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (name, email, password) => {
    try {
      await axios.post(`${API}/register`, { name, email, password });
      return await login(email, password);
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Components
const AurumLogo = () => (
  <div className="flex items-center space-x-2">
    <div className="w-8 h-8 bg-aurum-gold rounded-lg flex items-center justify-center">
      <TrendingUp className="w-5 h-5 text-aurum-ink" />
    </div>
    <span className="text-xl font-bold text-white">Aurum</span>
  </div>
);

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = isLogin 
      ? await login(email, password)
      : await register(name, email, password);

    if (!result.success) {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-aurum-ink flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <AurumLogo />
          <h2 className="mt-6 text-3xl font-extrabold text-white">
            {isLogin ? 'Welcome back' : 'Create your account'}
          </h2>
          <p className="mt-2 text-sm text-gray-300">
            {isLogin ? 'Sign in to your account' : 'Join Aurum Finance today'}
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            {!isLogin && (
              <input
                type="text"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-gray-800 focus:outline-none focus:ring-2 focus:ring-aurum-gold focus:border-transparent"
                required
              />
            )}
            
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-gray-800 focus:outline-none focus:ring-2 focus:ring-aurum-gold focus:border-transparent"
              required
            />
            
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-gray-800 focus:outline-none focus:ring-2 focus:ring-aurum-gold focus:border-transparent"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-aurum-ink bg-aurum-gold hover:bg-yellow-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-aurum-gold disabled:opacity-50"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Sign in' : 'Create account')}
          </button>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-aurum-gold hover:text-yellow-500"
            >
              {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const Sidebar = ({ activeTab, setActiveTab, sidebarOpen, setSidebarOpen }) => {
  const { logout, user } = useAuth();

  const navigation = [
    { name: 'Dashboard', icon: Home, id: 'dashboard' },
    { name: 'Transactions', icon: CreditCard, id: 'transactions' },
    { name: 'Net Worth', icon: TrendingUp, id: 'networth' },
    { name: 'Budgets & Goals', icon: Target, id: 'budgets' },
    { name: 'Reports', icon: BarChart3, id: 'reports' },
    { name: 'Settings', icon: Settings, id: 'settings' },
  ];

  const handleLogout = () => {
    logout();
    setSidebarOpen(false);
  };

  return (
    <>
      {/* Mobile sidebar */}
      <Transition show={sidebarOpen} as={React.Fragment}>
        <Dialog as="div" className="relative z-40 md:hidden" onClose={setSidebarOpen}>
          <Transition.Child
            as={React.Fragment}
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
          </Transition.Child>

          <div className="fixed inset-0 flex z-40">
            <Transition.Child
              as={React.Fragment}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <Dialog.Panel className="relative flex-1 flex flex-col max-w-xs w-full bg-aurum-ink">
                <div className="absolute top-0 right-0 -mr-12 pt-2">
                  <button
                    type="button"
                    className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                    onClick={() => setSidebarOpen(false)}
                  >
                    <X className="h-6 w-6 text-white" aria-hidden="true" />
                  </button>
                </div>
                
                <div className="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
                  <div className="flex-shrink-0 flex items-center px-4">
                    <AurumLogo />
                  </div>
                  <nav className="mt-5 px-2 space-y-1">
                    {navigation.map((item) => (
                      <button
                        key={item.name}
                        onClick={() => {
                          setActiveTab(item.id);
                          setSidebarOpen(false);
                        }}
                        className={`${
                          activeTab === item.id
                            ? 'bg-aurum-gold text-aurum-ink'
                            : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                        } group flex items-center px-2 py-2 text-base font-medium rounded-md w-full`}
                      >
                        <item.icon className="mr-4 h-6 w-6" />
                        {item.name}
                      </button>
                    ))}
                  </nav>
                </div>
                
                <div className="flex-shrink-0 flex border-t border-gray-700 p-4">
                  <div className="flex-shrink-0 group block">
                    <div className="flex items-center">
                      <div className="ml-3">
                        <p className="text-sm font-medium text-white">{user?.name}</p>
                        <button
                          onClick={handleLogout}
                          className="text-xs text-gray-400 hover:text-white flex items-center"
                        >
                          <LogOut className="w-3 h-3 mr-1" />
                          Sign out
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </Dialog>
      </Transition>

      {/* Desktop sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 bg-aurum-ink">
          <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
            <div className="flex items-center flex-shrink-0 px-4">
              <AurumLogo />
            </div>
            <nav className="mt-5 flex-1 px-2 space-y-1">
              {navigation.map((item) => (
                <button
                  key={item.name}
                  onClick={() => setActiveTab(item.id)}
                  className={`${
                    activeTab === item.id
                      ? 'bg-aurum-gold text-aurum-ink'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  } group flex items-center px-2 py-2 text-sm font-medium rounded-md w-full`}
                >
                  <item.icon className="mr-3 h-6 w-6" />
                  {item.name}
                </button>
              ))}
            </nav>
          </div>
          
          <div className="flex-shrink-0 flex border-t border-gray-700 p-4">
            <div className="flex-shrink-0 group block">
              <div className="flex items-center">
                <div className="ml-3">
                  <p className="text-sm font-medium text-white">{user?.name}</p>
                  <button
                    onClick={handleLogout}
                    className="text-xs text-gray-400 hover:text-white flex items-center"
                  >
                    <LogOut className="w-3 h-3 mr-1" />
                    Sign out
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

const StatCard = ({ title, value, icon: Icon, trend, color = "text-aurum-gold" }) => (
  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-400">{title}</p>
        <p className={`text-2xl font-bold ${color}`}>
          {typeof value === 'number' ? `$${value.toLocaleString()}` : value}
        </p>
      </div>
      <Icon className={`h-8 w-8 ${color}`} />
    </div>
    {trend && (
      <div className="mt-4 flex items-center">
        <TrendingUp className="h-4 w-4 text-green-400 mr-1" />
        <span className="text-sm text-green-400">{trend}</span>
      </div>
    )}
  </div>
);

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/summary`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-aurum-gold"></div>
      </div>
    );
  }

  const expenseData = Object.entries(dashboardData?.expense_breakdown || {}).map(([category, amount]) => ({
    name: category.charAt(0).toUpperCase() + category.slice(1),
    value: amount,
    percentage: ((amount / dashboardData.monthly_expenses) * 100).toFixed(1)
  }));

  const COLORS = ['#F4B400', '#FF6B35', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8'];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <div className="text-sm text-gray-400">
          {new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Net Worth"
          value={dashboardData?.net_worth || 0}
          icon={TrendingUp}
          color="text-aurum-gold"
        />
        <StatCard
          title="Monthly Income"
          value={dashboardData?.monthly_income || 0}
          icon={DollarSign}
          color="text-green-400"
        />
        <StatCard
          title="Monthly Expenses"
          value={dashboardData?.monthly_expenses || 0}
          icon={CreditCard}
          color="text-red-400"
        />
        <StatCard
          title="Cash Flow"
          value={dashboardData?.cash_flow || 0}
          icon={dashboardData?.cash_flow >= 0 ? TrendingUp : TrendingDown}
          color={dashboardData?.cash_flow >= 0 ? "text-green-400" : "text-red-400"}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Expense Breakdown</h3>
          {expenseData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={expenseData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name} ${percentage}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {expenseData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-400">
              <p>No expenses this month</p>
            </div>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Financial Overview</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Total Assets</span>
              <span className="text-green-400 font-semibold">
                ${(dashboardData?.total_assets || 0).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Total Liabilities</span>
              <span className="text-red-400 font-semibold">
                ${(dashboardData?.total_liabilities || 0).toLocaleString()}
              </span>
            </div>
            <div className="border-t border-gray-700 pt-2">
              <div className="flex justify-between items-center">
                <span className="text-white font-semibold">Net Worth</span>
                <span className="text-aurum-gold font-bold text-lg">
                  ${(dashboardData?.net_worth || 0).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const TransactionModal = ({ isOpen, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    type: 'expense',
    amount: '',
    description: '',
    category: 'food',
    date: new Date().toISOString().split('T')[0],
    is_recurring: false,
    frequency: 'monthly',
    recurring_start_date: new Date().toISOString().split('T')[0]
  });

  const categories = [
    'salary', 'freelance', 'investment', 'housing', 'food', 'transport',
    'entertainment', 'healthcare', 'education', 'shopping', 'utilities', 'other'
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    const submitData = {
      ...formData,
      amount: parseFloat(formData.amount),
      date: new Date(formData.date).toISOString()
    };
    
    if (formData.is_recurring) {
      submitData.recurring_start_date = new Date(formData.recurring_start_date).toISOString();
    }
    
    onSubmit(submitData);
    setFormData({
      type: 'expense',
      amount: '',
      description: '',
      category: 'food',
      date: new Date().toISOString().split('T')[0],
      is_recurring: false,
      frequency: 'monthly',
      recurring_start_date: new Date().toISOString().split('T')[0]
    });
  };

  return (
    <Transition appear show={isOpen} as={React.Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={React.Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={React.Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-gray-800 p-6 text-left align-middle shadow-xl transition-all border border-gray-700">
                <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-white mb-4">
                  Add Transaction
                </Dialog.Title>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Type</label>
                    <select
                      value={formData.type}
                      onChange={(e) => setFormData({...formData, type: e.target.value})}
                      className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                    >
                      <option value="expense">Expense</option>
                      <option value="income">Income</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Amount</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.amount}
                      onChange={(e) => setFormData({...formData, amount: e.target.value})}
                      className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                      placeholder="0.00"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
                    <input
                      type="text"
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                      placeholder="e.g., Groceries at Whole Foods"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Category</label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({...formData, category: e.target.value})}
                      className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                    >
                      {categories.map(cat => (
                        <option key={cat} value={cat}>
                          {cat.charAt(0).toUpperCase() + cat.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Date</label>
                    <input
                      type="date"
                      value={formData.date}
                      onChange={(e) => setFormData({...formData, date: e.target.value})}
                      className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                      required
                    />
                  </div>

                  <div>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={formData.is_recurring}
                        onChange={(e) => setFormData({...formData, is_recurring: e.target.checked})}
                        className="rounded border-gray-600 text-aurum-gold focus:ring-aurum-gold"
                      />
                      <span className="text-sm text-gray-300">Make this recurring?</span>
                    </label>
                  </div>

                  {formData.is_recurring && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Frequency</label>
                        <select
                          value={formData.frequency}
                          onChange={(e) => setFormData({...formData, frequency: e.target.value})}
                          className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                        >
                          <option value="weekly">Weekly</option>
                          <option value="monthly">Monthly</option>
                          <option value="yearly">Yearly</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Start Date</label>
                        <input
                          type="date"
                          value={formData.recurring_start_date}
                          onChange={(e) => setFormData({...formData, recurring_start_date: e.target.value})}
                          className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                          required
                        />
                      </div>
                    </>
                  )}

                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={onClose}
                      className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-aurum-gold text-aurum-ink rounded-md hover:bg-yellow-500 font-medium"
                    >
                      Add Transaction
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    category: '',
    searchQuery: ''
  });

  const categories = [
    '', 'salary', 'freelance', 'investment', 'housing', 'food', 'transport',
    'entertainment', 'healthcare', 'education', 'shopping', 'utilities', 'other'
  ];

  useEffect(() => {
    fetchTransactions();
  }, [filters]);

  const fetchTransactions = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);
      if (filters.category) params.append('category', filters.category);
      if (filters.searchQuery) params.append('search_query', filters.searchQuery);
      
      const response = await axios.get(`${API}/transactions?${params}`);
      setTransactions(response.data);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTransaction = async (transactionData) => {
    try {
      await axios.post(`${API}/transactions`, transactionData);
      fetchTransactions();
      setModalOpen(false);
    } catch (error) {
      console.error('Error adding transaction:', error);
    }
  };

  const clearFilters = () => {
    setFilters({
      startDate: '',
      endDate: '',
      category: '',
      searchQuery: ''
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-aurum-gold"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Transactions</h1>
        <button
          onClick={() => setModalOpen(true)}
          className="bg-aurum-gold text-aurum-ink px-4 py-2 rounded-lg hover:bg-yellow-500 flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Add Transaction</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-48">
            <label className="block text-sm font-medium text-gray-300 mb-1">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search descriptions..."
                value={filters.searchQuery}
                onChange={(e) => setFilters({...filters, searchQuery: e.target.value})}
                className="w-full pl-10 pr-4 py-2 rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
              />
            </div>
          </div>

          <div className="flex-1 min-w-32">
            <label className="block text-sm font-medium text-gray-300 mb-1">Category</label>
            <select
              value={filters.category}
              onChange={(e) => setFilters({...filters, category: e.target.value})}
              className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {cat ? cat.charAt(0).toUpperCase() + cat.slice(1) : 'All Categories'}
                </option>
              ))}
            </select>
          </div>

          <div className="flex-1 min-w-32">
            <label className="block text-sm font-medium text-gray-300 mb-1">Start Date</label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => setFilters({...filters, startDate: e.target.value})}
              className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
            />
          </div>

          <div className="flex-1 min-w-32">
            <label className="block text-sm font-medium text-gray-300 mb-1">End Date</label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => setFilters({...filters, endDate: e.target.value})}
              className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
            />
          </div>

          <button
            onClick={clearFilters}
            className="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-600 flex items-center space-x-2"
          >
            <X className="w-4 h-4" />
            <span>Clear</span>
          </button>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white">
            Recent Transactions ({transactions.length})
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {transactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {new Date(transaction.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                    {transaction.description}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    <span className="capitalize">{transaction.category}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <span className={transaction.type === 'income' ? 'text-green-400' : 'text-red-400'}>
                      {transaction.type === 'income' ? '+' : '-'}${transaction.amount.toLocaleString()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      transaction.type === 'income' 
                        ? 'bg-green-900 text-green-300' 
                        : 'bg-red-900 text-red-300'
                    }`}>
                      {transaction.type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {transaction.is_recurring && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-900 text-blue-300">
                        <Repeat className="w-3 h-3 mr-1" />
                        {transaction.frequency}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {transactions.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-400">No transactions found. Try adjusting your filters or add your first transaction!</p>
            </div>
          )}
        </div>
      </div>

      <TransactionModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleAddTransaction}
      />
    </div>
  );
};

const NetWorth = () => {
  const [assets, setAssets] = useState([]);
  const [liabilities, setLiabilities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [assetsResponse, liabilitiesResponse] = await Promise.all([
        axios.get(`${API}/assets`),
        axios.get(`${API}/liabilities`)
      ]);
      setAssets(assetsResponse.data);
      setLiabilities(liabilitiesResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalAssets = assets.reduce((sum, asset) => sum + asset.current_value, 0);
  const totalLiabilities = liabilities.reduce((sum, liability) => sum + liability.amount_owed, 0);
  const netWorth = totalAssets - totalLiabilities;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-aurum-gold"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Net Worth Tracker</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Total Assets"
          value={totalAssets}
          icon={TrendingUp}
          color="text-green-400"
        />
        <StatCard
          title="Total Liabilities"
          value={totalLiabilities}
          icon={TrendingDown}
          color="text-red-400"
        />
        <StatCard
          title="Net Worth"
          value={netWorth}
          icon={Wallet}
          color="text-aurum-gold"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Assets</h3>
          <div className="space-y-3">
            {assets.map((asset) => (
              <div key={asset.id} className="flex justify-between items-center p-3 bg-gray-700 rounded-lg">
                <span className="text-white">{asset.description}</span>
                <span className="text-green-400 font-semibold">${asset.current_value.toLocaleString()}</span>
              </div>
            ))}
            {assets.length === 0 && (
              <p className="text-gray-400 text-center py-8">No assets added yet</p>
            )}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Liabilities</h3>
          <div className="space-y-3">
            {liabilities.map((liability) => (
              <div key={liability.id} className="flex justify-between items-center p-3 bg-gray-700 rounded-lg">
                <span className="text-white">{liability.description}</span>
                <span className="text-red-400 font-semibold">${liability.amount_owed.toLocaleString()}</span>
              </div>
            ))}
            {liabilities.length === 0 && (
              <p className="text-gray-400 text-center py-8">No liabilities added yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const DebtModal = ({ isOpen, onClose, onSubmit, debt = null }) => {
  const [formData, setFormData] = useState({
    debt_name: '',
    total_balance: '',
    interest_rate: '',
    minimum_payment: ''
  });

  useEffect(() => {
    if (debt) {
      setFormData({
        debt_name: debt.debt_name,
        total_balance: debt.total_balance.toString(),
        interest_rate: debt.interest_rate.toString(),
        minimum_payment: debt.minimum_payment.toString()
      });
    } else {
      setFormData({
        debt_name: '',
        total_balance: '',
        interest_rate: '',
        minimum_payment: ''
      });
    }
  }, [debt]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      total_balance: parseFloat(formData.total_balance),
      interest_rate: parseFloat(formData.interest_rate),
      minimum_payment: parseFloat(formData.minimum_payment)
    });
  };

  const calculatePayoffInfo = () => {
    const balance = parseFloat(formData.total_balance) || 0;
    const rate = parseFloat(formData.interest_rate) || 0;
    const payment = parseFloat(formData.minimum_payment) || 0;

    if (balance <= 0 || rate <= 0 || payment <= 0) return null;

    const monthlyRate = rate / 100 / 12;
    const months = Math.log(1 + (balance * monthlyRate) / payment) / Math.log(1 + monthlyRate);
    const totalPaid = payment * months;
    const totalInterest = totalPaid - balance;

    return {
      months: Math.ceil(months),
      totalPaid: totalPaid,
      totalInterest: totalInterest
    };
  };

  const payoffInfo = calculatePayoffInfo();

  return (
    <Transition appear show={isOpen} as={React.Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={React.Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={React.Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-gray-800 p-6 text-left align-middle shadow-xl transition-all border border-gray-700">
                <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-white mb-4">
                  {debt ? 'Edit Debt' : 'Add Debt'}
                </Dialog.Title>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Debt Name</label>
                    <input
                      type="text"
                      value={formData.debt_name}
                      onChange={(e) => setFormData({...formData, debt_name: e.target.value})}
                      className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                      placeholder="e.g., Credit Card, Student Loan"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Total Balance</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.total_balance}
                      onChange={(e) => setFormData({...formData, total_balance: e.target.value})}
                      className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                      placeholder="0.00"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Interest Rate (APR %)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.interest_rate}
                      onChange={(e) => setFormData({...formData, interest_rate: e.target.value})}
                      className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                      placeholder="0.00"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Minimum Payment</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.minimum_payment}
                      onChange={(e) => setFormData({...formData, minimum_payment: e.target.value})}
                      className="w-full rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                      placeholder="0.00"
                      required
                    />
                  </div>

                  {payoffInfo && (
                    <div className="bg-gray-700 rounded-lg p-4 mt-4">
                      <h4 className="text-sm font-medium text-white mb-2">Payoff Projection</h4>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-300">Time to payoff:</span>
                          <span className="text-white">{payoffInfo.months} months</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Total paid:</span>
                          <span className="text-white">${payoffInfo.totalPaid.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Total interest:</span>
                          <span className="text-red-400">${payoffInfo.totalInterest.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={onClose}
                      className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-aurum-gold text-aurum-ink rounded-md hover:bg-yellow-500 font-medium"
                    >
                      {debt ? 'Update Debt' : 'Add Debt'}
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

const BudgetsAndGoals = () => {
  const [budgets, setBudgets] = useState([]);
  const [goals, setGoals] = useState([]);
  const [debts, setDebts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [debtModalOpen, setDebtModalOpen] = useState(false);
  const [editingDebt, setEditingDebt] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [budgetsResponse, goalsResponse, debtsResponse] = await Promise.all([
        axios.get(`${API}/budgets`),
        axios.get(`${API}/savings-goals`),
        axios.get(`${API}/debts`)
      ]);
      setBudgets(budgetsResponse.data);
      setGoals(goalsResponse.data);
      setDebts(debtsResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddDebt = async (debtData) => {
    try {
      await axios.post(`${API}/debts`, debtData);
      fetchData();
      setDebtModalOpen(false);
    } catch (error) {
      console.error('Error adding debt:', error);
    }
  };

  const handleUpdateDebt = async (debtData) => {
    try {
      await axios.put(`${API}/debts/${editingDebt.id}`, debtData);
      fetchData();
      setDebtModalOpen(false);
      setEditingDebt(null);
    } catch (error) {
      console.error('Error updating debt:', error);
    }
  };

  const handleDeleteDebt = async (debtId) => {
    if (window.confirm('Are you sure you want to delete this debt?')) {
      try {
        await axios.delete(`${API}/debts/${debtId}`);
        fetchData();
      } catch (error) {
        console.error('Error deleting debt:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-aurum-gold"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Budgets & Goals</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Monthly Budgets</h3>
          <div className="space-y-4">
            {budgets.map((budget) => (
              <div key={budget.id} className="p-4 bg-gray-700 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-white capitalize">{budget.category}</span>
                  <span className="text-aurum-gold font-semibold">${budget.budget_amount.toLocaleString()}</span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div className="bg-aurum-gold h-2 rounded-full" style={{ width: '0%' }}></div>
                </div>
                <p className="text-xs text-gray-400 mt-1">$0 of ${budget.budget_amount.toLocaleString()} spent</p>
              </div>
            ))}
            {budgets.length === 0 && (
              <p className="text-gray-400 text-center py-8">No budgets set yet</p>
            )}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Savings Goals</h3>
          <div className="space-y-4">
            {goals.map((goal) => {
              const progress = (goal.current_amount / goal.target_amount) * 100;
              return (
                <div key={goal.id} className="p-4 bg-gray-700 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-white">{goal.goal_name}</span>
                    <span className="text-aurum-gold font-semibold">${goal.target_amount.toLocaleString()}</span>
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2 mb-2">
                    <div 
                      className="bg-aurum-gold h-2 rounded-full" 
                      style={{ width: `${Math.min(progress, 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-400">
                    ${goal.current_amount.toLocaleString()} of ${goal.target_amount.toLocaleString()} saved ({progress.toFixed(1)}%)
                  </p>
                </div>
              );
            })}
            {goals.length === 0 && (
              <p className="text-gray-400 text-center py-8">No savings goals set yet</p>
            )}
          </div>
        </div>
      </div>

      {/* Debt Paydown Planner */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-white">Debt Paydown Planner</h3>
          <button
            onClick={() => setDebtModalOpen(true)}
            className="bg-aurum-gold text-aurum-ink px-4 py-2 rounded-lg hover:bg-yellow-500 flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Debt</span>
          </button>
        </div>
        
        <div className="space-y-4">
          {debts.map((debt) => {
            const monthlyRate = debt.interest_rate / 100 / 12;
            const months = Math.log(1 + (debt.total_balance * monthlyRate) / debt.minimum_payment) / Math.log(1 + monthlyRate);
            const totalPaid = debt.minimum_payment * months;
            const totalInterest = totalPaid - debt.total_balance;

            return (
              <div key={debt.id} className="p-4 bg-gray-700 rounded-lg">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="text-white font-medium">{debt.debt_name}</h4>
                    <p className="text-sm text-gray-300">
                      Balance: ${debt.total_balance.toLocaleString()} | 
                      APR: {debt.interest_rate}% | 
                      Min Payment: ${debt.minimum_payment.toLocaleString()}
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setEditingDebt(debt);
                        setDebtModalOpen(true);
                      }}
                      className="p-2 text-gray-400 hover:text-aurum-gold"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteDebt(debt.id)}
                      className="p-2 text-gray-400 hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-gray-400">Payoff Time</p>
                    <p className="text-white font-medium">{Math.ceil(months)} months</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Total Paid</p>
                    <p className="text-white font-medium">${totalPaid.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Total Interest</p>
                    <p className="text-red-400 font-medium">${totalInterest.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            );
          })}
          {debts.length === 0 && (
            <p className="text-gray-400 text-center py-8">No debts added yet</p>
          )}
        </div>
      </div>

      <DebtModal
        isOpen={debtModalOpen}
        onClose={() => {
          setDebtModalOpen(false);
          setEditingDebt(null);
        }}
        onSubmit={editingDebt ? handleUpdateDebt : handleAddDebt}
        debt={editingDebt}
      />
    </div>
  );
};

const Reports = () => {
  const [cashflowData, setCashflowData] = useState([]);
  const [spendingData, setSpendingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchReportsData();
  }, [dateRange]);

  const fetchReportsData = async () => {
    try {
      const [cashflowResponse, spendingResponse] = await Promise.all([
        axios.get(`${API}/reports/cashflow`),
        axios.get(`${API}/reports/spending?start_date=${dateRange.start}&end_date=${dateRange.end}`)
      ]);
      setCashflowData(cashflowResponse.data);
      setSpendingData(spendingResponse.data);
    } catch (error) {
      console.error('Error fetching reports data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-aurum-gold"></div>
      </div>
    );
  }

  const COLORS = ['#F4B400', '#FF6B35', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8'];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Financial Reports</h1>
        <div className="text-sm text-gray-400">
          Insights into your financial patterns
        </div>
      </div>

      {/* Cash Flow Trend */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Cash Flow Trend (Last 12 Months)</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={cashflowData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month_name" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
              formatter={(value) => `$${value.toLocaleString()}`}
            />
            <Legend />
            <Bar dataKey="income" fill="#10B981" name="Income" />
            <Bar dataKey="expenses" fill="#EF4444" name="Expenses" />
            <Bar dataKey="net" fill="#F4B400" name="Net" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Spending by Category */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-white">Spending by Category</h3>
          <div className="flex space-x-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Start Date</label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
                className="rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">End Date</label>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
                className="rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 className="text-md font-medium text-white mb-3">
              Total Spent: ${spendingData?.total_spent.toLocaleString() || 0}
            </h4>
            {spendingData?.categories.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={spendingData.categories}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ category, percentage }) => `${category} ${percentage.toFixed(1)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="amount"
                  >
                    {spendingData.categories.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-400">
                <p>No spending data for selected period</p>
              </div>
            )}
          </div>

          <div>
            <h4 className="text-md font-medium text-white mb-3">Category Breakdown</h4>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {spendingData?.categories.map((category, index) => (
                <div key={category.category} className="flex justify-between items-center p-3 bg-gray-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    ></div>
                    <span className="text-white capitalize">{category.category}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-white font-medium">${category.amount.toLocaleString()}</div>
                    <div className="text-sm text-gray-400">{category.percentage.toFixed(1)}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const SettingsPage = () => {
  const { user } = useAuth();
  const [activeSection, setActiveSection] = useState('profile');

  const sections = [
    { id: 'profile', name: 'Profile', icon: Settings },
    { id: 'categories', name: 'Categories', icon: Filter },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Settings</h1>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="flex">
          {/* Sidebar */}
          <div className="w-64 border-r border-gray-700">
            <nav className="space-y-1 p-4">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`${
                    activeSection === section.id
                      ? 'bg-aurum-gold text-aurum-ink'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  } group flex items-center px-3 py-2 text-sm font-medium rounded-md w-full`}
                >
                  <section.icon className="mr-3 h-5 w-5" />
                  {section.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 p-6">
            {activeSection === 'profile' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-white">Profile Information</h3>
                  <p className="text-sm text-gray-400">Update your account profile information.</p>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Name</label>
                    <input
                      type="text"
                      value={user?.name || ''}
                      className="w-full max-w-md rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                      disabled
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Email</label>
                    <input
                      type="email"
                      value={user?.email || ''}
                      className="w-full max-w-md rounded-md border-gray-600 bg-gray-700 text-white focus:border-aurum-gold focus:ring-aurum-gold"
                      disabled
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Member Since</label>
                    <input
                      type="text"
                      value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : ''}
                      className="w-full max-w-md rounded-md border-gray-600 bg-gray-700 text-gray-400 focus:border-aurum-gold focus:ring-aurum-gold"
                      disabled
                    />
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'categories' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-white">Manage Categories</h3>
                  <p className="text-sm text-gray-400">Customize your transaction categories.</p>
                </div>
                
                <div className="text-gray-400">
                  <p>Category management feature coming soon...</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const Layout = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'transactions':
        return <Transactions />;
      case 'networth':
        return <NetWorth />;
      case 'budgets':
        return <BudgetsAndGoals />;
      case 'reports':
        return <Reports />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-aurum-ink">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />
      
      <div className="md:pl-64 flex flex-col flex-1">
        <div className="sticky top-0 z-10 md:hidden pl-1 pt-1 sm:pl-3 sm:pt-3 bg-aurum-ink">
          <button
            type="button"
            className="-ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-md text-gray-500 hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-aurum-gold"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
        
        <main className="flex-1">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              {renderContent()}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AuthContent />
      </BrowserRouter>
    </AuthProvider>
  );
};

const AuthContent = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-aurum-ink flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-aurum-gold"></div>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
      <Route path="/*" element={user ? <Layout /> : <Navigate to="/login" />} />
    </Routes>
  );
};

export default App;