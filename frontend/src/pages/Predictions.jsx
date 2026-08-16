import { TrendingUp, Target, Calendar } from "lucide-react";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { predictionData } from "../data/mockData";

function Predictions() {
  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Financial Predictions</h1>

          <p>
            Forecasted financial performance.
          </p>
        </div>
      </div>

      <div className="prediction-cards">
        <div className="prediction-card">
          <TrendingUp size={25} />

          <span>Predicted Revenue</span>

          <h2>₹15.8L</h2>

          <small>Expected growth: +12.4%</small>
        </div>

        <div className="prediction-card">
          <Target size={25} />

          <span>Expected Profit</span>

          <h2>₹7.3L</h2>

          <small>Expected margin: 46.2%</small>
        </div>

        <div className="prediction-card">
          <Calendar size={25} />

          <span>Forecast Period</span>

          <h2>4 Months</h2>

          <small>July - October 2026</small>
        </div>
      </div>

      <div className="chart-card">
        <div className="card-header">
          <div>
            <h3>Revenue Forecast</h3>

            <p>
              Projected revenue for upcoming months
            </p>
          </div>

          <span className="forecast-badge">
            AI Forecast
          </span>
        </div>

        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={predictionData}>
              <CartesianGrid strokeDasharray="3 3" />

              <XAxis dataKey="month" />

              <YAxis />

              <Tooltip />

              <Area
                type="monotone"
                dataKey="revenue"
                stroke="#6366f1"
                fill="#6366f1"
                fillOpacity={0.2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Predictions;