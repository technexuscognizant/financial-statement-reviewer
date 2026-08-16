import {
  TrendingUp,
  TrendingDown,
  ShieldCheck,
  Percent,
} from "lucide-react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import StatCard from "../components/StatCard";
import { monthlyData } from "../data/mockData";

function Analysis() {
  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Financial Analysis</h1>
          <p>
            Detailed analysis of your financial performance.
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Revenue"
          value="₹12.4L"
          change="12.4%"
          icon={TrendingUp}
        />

        <StatCard
          title="Expenses"
          value="₹7.2L"
          change="4.8%"
          icon={TrendingDown}
          positive={false}
        />

        <StatCard
          title="Profit Margin"
          value="41.9%"
          change="5.2%"
          icon={Percent}
        />

        <StatCard
          title="Risk Score"
          value="18 / 100"
          change="8.1%"
          icon={ShieldCheck}
        />
      </div>

      <div className="chart-card">
        <div className="card-header">
          <div>
            <h3>Profit Trend</h3>
            <p>Monthly net profit performance</p>
          </div>
        </div>

        <div className="chart-container analysis-chart">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />

              <XAxis dataKey="month" />

              <YAxis />

              <Tooltip />

              <Line
                type="monotone"
                dataKey="profit"
                stroke="#6366f1"
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="analysis-summary">
        <h3>Financial Health Assessment</h3>

        <div className="health-score">
          <div className="score-circle">
            <strong>82</strong>
            <span>/100</span>
          </div>

          <div>
            <h2>Excellent Financial Health</h2>

            <p>
              Your business demonstrates strong profitability,
              controlled expenses and positive revenue growth.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analysis;