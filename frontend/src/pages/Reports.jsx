import {
  FileText,
  Download,
  Calendar,
} from "lucide-react";

function Reports() {
  const reports = [
    {
      name: "Monthly Financial Report",
      period: "August 2026",
    },
    {
      name: "Financial Risk Assessment",
      period: "August 2026",
    },
    {
      name: "Revenue Forecast Report",
      period: "Q3 2026",
    },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Financial Reports</h1>

          <p>
            View and manage generated financial reports.
          </p>
        </div>

        <button className="primary-button">
          <Download size={18} />
          Generate Report
        </button>
      </div>

      <div className="report-list">
        {reports.map((report, index) => (
          <div className="report-card" key={index}>
            <div className="report-icon">
              <FileText size={25} />
            </div>

            <div className="report-details">
              <h3>{report.name}</h3>

              <span>
                <Calendar size={15} />
                {report.period}
              </span>
            </div>

            <button className="download-button">
              <Download size={18} />
              Download
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Reports;