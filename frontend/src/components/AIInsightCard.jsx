import {
  AlertTriangle,
  CheckCircle,
  Lightbulb,
} from "lucide-react";

function AIInsightCard({
  type = "success",
  title,
  description,
}) {
  const icons = {
    success: CheckCircle,
    warning: AlertTriangle,
    info: Lightbulb,
  };

  const Icon = icons[type];

  return (
    <div className={`ai-card ${type}`}>
      <div className="ai-icon">
        <Icon size={22} />
      </div>

      <div>
        <h4>{title}</h4>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default AIInsightCard;