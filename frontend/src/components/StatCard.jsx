function StatCard({
  title,
  value,
  change,
  icon: Icon,
  positive = true,
}) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <div className="stat-icon">
          <Icon size={22} />
        </div>

        <span
          className={
            positive ? "change positive" : "change negative"
          }
        >
          {positive ? "↑" : "↓"} {change}
        </span>
      </div>

      <p>{title}</p>

      <h2>{value}</h2>

      <span className="stat-period">
        Compared with last month
      </span>
    </div>
  );
}

export default StatCard;