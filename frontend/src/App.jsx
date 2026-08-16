import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";

function Dashboard() {
  return (
    <div>
      <h1>Financial AI Dashboard</h1>
      <p>Welcome to FinAI.</p>
    </div>
  );
}

function Upload() {
  return <h1>Upload Data</h1>;
}

function Analysis() {
  return <h1>Financial Analysis</h1>;
}

function Predictions() {
  return <h1>Predictions</h1>;
}

function Insights() {
  return <h1>AI Insights</h1>;
}

function Reports() {
  return <h1>Reports</h1>;
}

function App() {
  return (
    <BrowserRouter>
      <div
        style={{
          display: "flex",
          minHeight: "100vh",
        }}
      >
        <Sidebar />

        <main
          style={{
            flex: 1,
            padding: "40px",
            backgroundColor: "#f5f7fb",
            color: "#111827",
          }}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;