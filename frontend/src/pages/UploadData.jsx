import { UploadCloud } from "lucide-react";
import FileUpload from "../components/FileUpload";

function UploadData() {
  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Upload Financial Data</h1>

          <p>
            Upload your financial documents for analysis.
          </p>
        </div>
      </div>

      <div className="upload-page">
        <FileUpload />

        <div className="upload-info">
          <UploadCloud size={24} />

          <div>
            <h3>How it works</h3>

            <p>
              Upload your financial data and the system
              will analyze revenue, expenses, profitability,
              risks and financial trends.
            </p>
          </div>
        </div>

        <button className="primary-button">
          Analyze Data
        </button>
      </div>
    </div>
  );
}

export default UploadData;