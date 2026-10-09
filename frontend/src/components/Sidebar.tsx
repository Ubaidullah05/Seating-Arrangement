import React from "react";
import { NavLink } from "react-router-dom";
import { 
  LayoutDashboard, 
  UploadCloud, 
  Building2, 
  Shuffle, 
  Grid3X3, 
  Search,
  Menu,
  ChevronLeft
} from "lucide-react";

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  mobileOpen?: boolean;
  onNavigate?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle, mobileOpen = false, onNavigate }) => {
  const navItems = [
    { name: "DASHBOARD", path: "/", icon: LayoutDashboard },
    { name: "UPLOAD STUDENTS", path: "/upload", icon: UploadCloud },
    { name: "ROOM CONFIGURATION", path: "/rooms", icon: Building2 },
    { name: "GENERATE SEATING", path: "/generate", icon: Shuffle },
    { name: "SEATING PLANS", path: "/plans", icon: Grid3X3 },
    { name: "SEARCH STUDENT", path: "/search", icon: Search },
  ];

  return (
    <aside 
      className={`portal-sidebar${mobileOpen ? " mobile-open" : ""}`}
      style={{
        width: collapsed ? "72px" : "290px",
        minHeight: "100vh",
        background: "linear-gradient(180deg, #004a99 0%, #002f66 60%, #001f42 100%)",
        color: "#ffffff",
        transition: "width 0.25s ease",
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        boxShadow: "3px 0 10px rgba(0, 0, 0, 0.15)",
        zIndex: 40,
        position: "sticky",
        top: 0,
        height: "100vh",
      }}
    >
      {/* Sidebar Header */}
      <div 
        style={{
          height: "76px",
          display: "flex",
          alignItems: "center",
          justifyContent: collapsed ? "center" : "space-between",
          padding: collapsed ? "0" : "0 18px",
          borderBottom: "1px solid rgba(255, 255, 255, 0.12)",
        }}
      >
        {!collapsed && (
          <span 
            style={{
              fontFamily: "'Georgia', 'Merriweather', serif",
              fontSize: "19px",
              fontWeight: 700,
              letterSpacing: "0.2px",
              color: "#ffffff",
              whiteSpace: "nowrap",
            }}
          >
            Single Window Portal
          </span>
        )}
        <button
          onClick={onToggle}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          style={{
            background: "transparent",
            border: "none",
            color: "#ffffff",
            cursor: "pointer",
            padding: "8px",
            borderRadius: "4px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {collapsed ? <Menu size={22} /> : <ChevronLeft size={22} />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav style={{ padding: "16px 0", flex: 1, overflowY: "auto" }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              title={collapsed ? item.name : undefined}
              onClick={onNavigate}
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: "14px",
                padding: collapsed ? "14px 0" : "13px 20px",
                justifyContent: collapsed ? "center" : "flex-start",
                color: "#ffffff",
                textDecoration: "none",
                fontWeight: 700,
                fontSize: "12px",
                letterSpacing: "0.8px",
                backgroundColor: isActive ? "#1f5fa8" : "transparent",
                borderLeft: isActive ? "4px solid #b8892b" : "4px solid transparent",
                transition: "all 0.15s ease",
              })}
            >
              <Icon size={20} strokeWidth={2} style={{ flexShrink: 0 }} />
              {!collapsed && (
                <span style={{ whiteSpace: "nowrap" }}>
                  {item.name}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Sidebar Footer info */}
      {!collapsed && (
        <div 
          style={{
            padding: "16px 20px",
            borderTop: "1px solid rgba(255, 255, 255, 0.1)",
            fontSize: "11px",
            color: "rgba(255, 255, 255, 0.6)",
            lineHeight: "1.4",
          }}
        >
          <div style={{ fontWeight: 600, color: "#e5a93c" }}>Office of the COE</div>
          <div>Jerusalem College of Engineering</div>
        </div>
      )}
    </aside>
  );
};
