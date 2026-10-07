import React from "react";
import logoSvg from "../assets/logo.svg";
import { UserCheck } from "lucide-react";

export const TopHeader: React.FC = () => {
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
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
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
            src={logoSvg} 
            alt="Jerusalem College of Engineering Logo" 
            style={{ width: "100%", height: "100%", objectFit: "contain" }}
          />
        </div>

        {/* Text Headers */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <h1
            style={{
              fontFamily: "'Georgia', 'Times New Roman', serif",
              fontSize: "16px",
              fontWeight: 700,
              letterSpacing: "0.4px",
              color: "#ffffff",
              lineHeight: "1.25",
              margin: 0,
              textTransform: "uppercase",
            }}
          >
            Jerusalem College of Engineering, Chennai - 600100
          </h1>
          <div
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

      {/* Staff Label - No auth / static as per requirements */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          backgroundColor: "rgba(255, 255, 255, 0.12)",
          padding: "6px 14px",
          borderRadius: "20px",
          border: "1px solid rgba(255, 255, 255, 0.2)",
        }}
      >
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
          }}
        >
          <UserCheck size={18} />
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span 
            style={{ 
              fontWeight: 800, 
              fontSize: "12px", 
              letterSpacing: "0.8px",
              color: "#ffffff" 
            }}
          >
            STAFF PORTAL
          </span>
          <span 
            style={{ 
              fontSize: "10px", 
              color: "#cbd5e1",
              letterSpacing: "0.3px"
            }}
          >
            Exam Coordinator
          </span>
        </div>
      </div>
    </header>
  );
};
