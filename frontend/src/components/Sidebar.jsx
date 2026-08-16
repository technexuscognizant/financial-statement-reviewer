import {
  LayoutDashboard,
  Upload,
  BarChart3,
  TrendingUp,
  BrainCircuit,
  FileText,
  Settings,
  LogOut,
} from "lucide-react";

import { NavLink } from "react-router-dom";

function Sidebar() {
  const menuItems = [
    {
      name: "Dashboard",
      path: "/",
      icon: LayoutDashboard,
    },
    {
      name: "Upload Data",
      path: "/upload",
      icon: Upload,
    },
    {
      name: "Analysis",
      path: "/analysis",
      icon: BarChart3,
    },
    {
      name: "Predictions",
      path: "/predictions",
      icon: TrendingUp,
    },
    {
      name: "AI Insights",
      path: "/insights",
      icon: BrainCircuit,
    },
    {
      name: "Reports",
      path: "/reports",
      icon: FileText,
    },
  ];

  return (
    <aside
      style={{
        width: "250px",
        minHeight: "100vh",
        backgroundColor: "#111827",
        color: "white",
        padding: "20px",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          marginBottom: "30px",
        }}
      >
        <BrainCircuit size={28} />

        <div>
          <h2 style={{ margin: 0 }}>FinAI</h2>
          <small>Financial Intelligence</small>
        </div>
      </div>

      <nav
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "8px",
        }}
      >
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "12px",
                borderRadius: "8px",
                textDecoration: "none",
                color: "white",
                backgroundColor: isActive
                  ? "#2563eb"
                  : "transparent",
              })}
            >
              <Icon size={19} />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div
        style={{
          marginTop: "40px",
          paddingTop: "20px",
          borderTop: "1px solid #374151",
        }}
      >
        <button
          type="button"
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            gap: "12px",
            padding: "12px",
            background: "transparent",
            border: "none",
            color: "white",
            cursor: "pointer",
          }}
        >
          <Settings size={19} />
          <span>Settings</span>
        </button>

        <button
          type="button"
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            gap: "12px",
            padding: "12px",
            background: "transparent",
            border: "none",
            color: "white",
            cursor: "pointer",
          }}
        >
          <LogOut size={19} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;