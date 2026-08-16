import {
  DollarSign,
  CreditCard,
  TrendingUp,
  Activity,
} from "lucide-react";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

import StatCard from "../components/StatCard";
import AIInsightCard from "../components/AIInsightCard";

import {
  monthlyData,
  transactions,
} from "../data/mockData";

function Dashboard() {
  const expenseData = [
    { name: "Operations", value: 35 },
    { name: "Marketing", value: 25 },
    { name: "Salaries", value: 30 },
    { name: "Other", value: 10 },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Financial Dashboard</h1>
          <p>
            Monitor your business financial performance.
          </p>
        </div>

        <span className="date-badge">
          August 2026
        </span>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Total Revenue"
          value="₹12.4L"
          change="12.4%"
          icon={DollarSign}
        />

        <StatCard
          title="Total Expenses"
          value="₹7.2L"
          change="4.8%"
          icon={CreditCard}
          positive={false}
        />

        <StatCard
          title="Net Profit"
          value="₹5.2L"
          change="18.2%"
          icon={TrendingUp}
        />

        <StatCard
          title="Financial Health"
          value="82 / 100"
          change="6.5%"
          icon={Activity}
        />
      </div>

      <div className="dashboard-grid">
        <div className="chart-card large">
          <div className="card-header">
            <div>
              <h3>Revenue vs Expenses</h3>
              <p>Monthly financial performance</p>
            </div>
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />

                <XAxis dataKey="month" />

                <YAxis />

                <Tooltip />

                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#6366f1"
                  fill="#6366f1"
                  fillOpacity={0.15}
                />

                <Area
                  type="monotone"
                  dataKey="expenses"
                  stroke="#f97316"
                  fill="#f97316"
                  fillOpacity={0.1}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="card-header">
            <div>
              <h3>Expense Distribution</h3>
              <p>Where your money goes</p>
            </div>
          </div>

          <div className="pie-container">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={expenseData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  innerRadius={55}
                >
                  {expenseData.map((_, index) => (
                    <Cell
                      key={index}
                      fill={
                        [
                          "#6366f1",
                          "#22c55e",
                          "#f97316",
                          "#ec4899",
                        ][index]
                      }
                    />
                  ))}
                </Pie>

                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="bottom-grid">
        <div className="panel">
          <div className="card-header">
            <div>
              <h3>Recent Transactions</h3>
              <p>Latest financial activity</p>
            </div>
          </div>

          <div className="transaction-list">
            {transactions.map((transaction) => (
              <div
                className="transaction"
                key={transaction.id}
              >
                <div className="transaction-info">
                  <div className="transaction-icon">
                    $
                  </div>

                  <div>
                    <strong>
                      {transaction.description}
                    </strong>

                    <span>
                      {transaction.date}
                    </span>
                  </div>
                </div>

                <strong
                  className={
                    transaction.amount > 0
                      ? "amount positive-text"
                      : "amount negative-text"
                  }
                >
                  {transaction.amount > 0
                    ? "+"
                    : ""}
                  ₹
                  {Math.abs(
                    transaction.amount
                  ).toLocaleString("en-IN")}
                </strong>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="card-header">
            <div>
              <h3>AI Financial Summary</h3>
              <p>Latest intelligent insights</p>
            </div>
          </div>

          <div className="insights-list">
            <AIInsightCard
              type="success"
              title="Healthy Profit Growth"
              description="Your net profit increased by 18.2% compared with the previous month."
            />

            <AIInsightCard
              type="warning"
              title="Marketing Expenses"
              description="Marketing expenses increased by 18%. Consider reviewing campaign performance."
            />

            <AIInsightCard
              type="info"
              title="Positive Forecast"
              description="Current trends indicate continued revenue growth next quarter."
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;