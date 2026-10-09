import React from "react";
import logoPng from "../assets/logo.png";
import { KeyRound, LogOut, Menu } from "lucide-react";
import { useAuth } from "../authContext";

interface TopHeaderProps {
  onMenuClick?: () => void;
  onChangePassword?: () => void;
}

export const TopHeader: React.FC<TopHeaderProps> = ({ onMenuClick, onChangePassword }) => {
  const { user, logout } = useAuth();
  const facultyEmail = user?.email || "acoe@jerusalemengg.ac.in";

  return (
    <header
      className="portal-header-bar"
      style={{
        height: "76px",
        background: "linear-gradient(90deg, #0050b3 0%, #003d8f 60%, #002f66 100%)",
        color: "#ffffff",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 28px",
        boxShadow: "0 2px 8px rgba(0, 0, 0, 0.15)",
        zIndex: 30,
        position: "sticky",
        top: 0,
      }}
    >
      {/* College Identity */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px", minWidth: 0 }}>
        {/* Mobile hamburger */}
        <button
          type="button"
          className="mobile-menu-btn"
          onClick={onMenuClick}
          aria-label="Open navigation menu"
          style={{
            background: "rgba(255,255,255,0.12)",
            border: "1px solid rgba(255,255,255,0.25)",
            color: "#ffffff",
            borderRadius: "6px",
            padding: "8px",
            display: "none",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            flexShrink: 0,
          }}
        >
          <Menu size={20} />
        </button>

        {/* White square logo container */}
        <div
          style={{
            width: "52px",
            height: "52px",
            backgroundColor: "#ffffff",
            borderRadius: "4px",
            padding: "3px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 1px 4px rgba(0,0,0,0.2)",
            flexShrink: 0,
          }}
        >
          <img
            src={logoPng}
            alt="Jerusalem College of Engineering Logo"
            style={{ width: "100%", height: "100%", objectFit: "contain" }}
          />
        </div>

        {/* Text Headers */}
        <div style={{ display: "flex", flexDirection: "column", minWidth: 0 }}>
          <h1
            className="portal-header-title"
            style={{
              fontFamily: "'Georgia', 'Times New Roman', serif",
              fontSize: "16px",
              fontWeight: 700,
              letterSpacing: "0.4px",
              color: "#ffffff",
              lineHeight: "1.25",
              margin: 0,
              textTransform: "uppercase",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            Jerusalem College of Engineering, Chennai - 600100
          </h1>
          <div
            className="portal-header-subtitle"
            style={{
              fontFamily: "'Georgia', 'Times New Roman', serif",
              fontStyle: "italic",
              fontSize: "11.5px",
              color: "#e2e8f0",
              lineHeight: "1.25",
              marginTop: "1px",
            }}
          >
            (An Autonomous Institution Affiliated to Anna University, Chennai)
          </div>
          <div
            className="portal-header-office"
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: "10.5px",
              fontWeight: 800,
              color: "#e5a93c",
              letterSpacing: "0.8px",
              textTransform: "uppercase",
              marginTop: "2px",
            }}
          >
            Office of the Controller of Examinations
          </div>
        </div>
      </div>

      {/* Signed-in faculty actions */}
      <div style={{ display: "flex", alignItems: "center", gap: "10px", flexShrink: 0 }}>
        {user?.mustChangePassword && (
          <button
            type="button"
            onClick={onChangePassword}
            className="header-action-btn header-action-alert"
            title="Set a new password"
          >
            <KeyRound size={16} />
            <span className="header-action-label">Set Password</span>
          </button>
        )}

        <div className="header-user-chip" title={facultyEmail}>
          <div
            style={{
              width: "30px",
              height: "30px",
              borderRadius: "50%",
              backgroundColor: "#ffffff",
              color: "#003d8f",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 800,
              fontSize: "13px",
              flexShrink: 0,
            }}
          >
            A
          </div>
          <div className="header-user-text" style={{ display: "flex", flexDirection: "column" }}>
            <span
              style={{
                fontWeight: 800,
                fontSize: "12px",
                letterSpacing: "0.8px",
                color: "#ffffff",
              }}
            >
              ACOE
            </span>
            <span
              className="header-user-email"
              style={{
                fontSize: "10px",
                color: "#cbd5e1",
                letterSpacing: "0.3px",
              }}
            >
              {facultyEmail}
            </span>
          </div>
        </div>

        <button
          type="button"
          onClick={onChangePassword}
          className="header-icon-btn"
          title="Change password"
          aria-label="Change password"
        >
          <KeyRound size={17} />
        </button>

        <button
          type="button"
          onClick={logout}
          className="header-icon-btn"
          title="Sign out"
          aria-label="Sign out"
        >
          <LogOut size={17} />
        </button>
      </div>
    </header>
  );
};
