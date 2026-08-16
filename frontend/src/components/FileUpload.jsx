import { useState } from "react";
import { UploadCloud, FileText, X } from "lucide-react";

function FileUpload() {
  const [file, setFile] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const removeFile = () => {
    setFile(null);
  };

  return (
    <div className="upload-wrapper">
      {!file ? (
        <label className="upload-box">
          <input
            type="file"
            accept=".csv,.xlsx,.xls,.pdf"
            onChange={handleFileChange}
          />

          <UploadCloud size={50} />

          <h3>Upload Financial Data</h3>

          <p>
            Drag & drop your file here or click to browse
          </p>

          <span>
            Supported formats: CSV, XLSX, XLS, PDF
          </span>

          <button type="button">
            Browse Files
          </button>
        </label>
      ) : (
        <div className="selected-file">
          <FileText size={32} />

          <div>
            <strong>{file.name}</strong>
            <span>
              {(file.size / 1024).toFixed(1)} KB
            </span>
          </div>

          <button onClick={removeFile}>
            <X size={20} />
          </button>
        </div>
      )}
    </div>
  );
}

export default FileUpload;