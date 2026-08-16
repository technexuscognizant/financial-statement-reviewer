import {
  BrainCircuit,
  AlertTriangle,
  Lightbulb,
  CheckCircle,
} from "lucide-react";

import AIInsightCard from "../components/AIInsightCard";

function AIInsights() {
  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>AI Financial Insights</h1>

          <p>
            Intelligent recommendations based on your
            financial data.
          </p>
        </div>
      </div>

      <div className="ai-overview">
        <div className="ai-overview-icon">
          <BrainCircuit size={40} />
        </div>

        <div>
          <h2>AI Analysis Complete</h2>

          <p>
            Your financial data has been analyzed for
            trends, risks, anomalies and opportunities.
          </p>
        </div>
      </div>

      <div className="insight-grid">
        <AIInsightCard
          type="success"
          title="Strong Revenue Growth"
          description="Revenue increased consistently during the last six months."
        />

        <AIInsightCard
          type="warning"
          title="Expense Anomaly Detected"
          description="Marketing expenses increased significantly compared with historical averages."
        />

        <AIInsightCard
          type="info"
          title="Cash Flow Opportunity"
          description="Current cash flow trends indicate an opportunity to increase investment in high-performing areas."
        />

        <AIInsightCard
          type="success"
          title="Low Financial Risk"
          description="The current financial indicators suggest a relatively low overall financial risk."
        />
      </div>

      <div className="recommendation-panel">
        <div className="recommendation-header">
          <Lightbulb size={24} />

          <h3>AI Recommendations</h3>
        </div>

        <div className="recommendation">
          <CheckCircle size={20} />

          <span>
            Maintain current revenue growth strategy.
          </span>
        </div>

        <div className="recommendation">
          <CheckCircle size={20} />

          <span>
            Review marketing expenses and campaign ROI.
          </span>
        </div>

        <div className="recommendation">
          <CheckCircle size={20} />

          <span>
            Continue monitoring monthly cash flow.
          </span>
        </div>

        <div className="recommendation">
          <AlertTriangle size={20} />

          <span>
            Monitor unusual changes in operating expenses.
          </span>
        </div>
      </div>
    </div>
  );
}

export default AIInsights;