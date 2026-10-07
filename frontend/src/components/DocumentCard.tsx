import React from "react";
import logoSvg from "../assets/logo.svg";

interface InfoItem {
  label: string;
  value: string | number;
}

interface DocumentCardProps {
  documentTitle: string;
  examName?: string;
  infoItems?: InfoItem[];
  children: React.ReactNode;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({
  documentTitle,
  examName = "END SEMESTER EXAMINATIONS — OCT/NOV 2026",
  infoItems = [],
  children,
}) => {
  return (
    <div className="document-paper-card">
      {/* Repeating faint diagonal watermark */}
      <div className="document-watermark" />
      <div className="document-watermark-text">
        <div>JERUSALEM COLLEGE OF ENGG</div>
        <div style={{ fontSize: "28px", marginTop: "8px" }}>OCT / NOV 2026</div>
      </div>

      <div className="document-card-content">
        {/* Document Header */}
        <div 
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: "16px",
            gap: "20px",
          }}
        >
          {/* Logo */}
          <div
            style={{
              width: "72px",
              height: "72px",
              backgroundColor: "#ffffff",
              borderRadius: "4px",
              padding: "4px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              border: "1px solid #e2e8f0",
              boxShadow: "0 2px 5px rgba(0,0,0,0.06)",
              flexShrink: 0,
            }}
          >
            <img 
              src={logoSvg} 
              alt="JCE Logo" 
              style={{ width: "100%", height: "100%", objectFit: "contain" }} 
            />
          </div>

          {/* Centered Document Titles */}
          <div style={{ textAlign: "center", flex: 1 }}>
            <h2
              style={{
                fontFamily: "'Georgia', 'Times New Roman', serif",
                fontSize: "19px",
                fontWeight: 700,
                color: "#002f66",
                margin: 0,
                letterSpacing: "0.4px",
              }}
            >
              JERUSALEM COLLEGE OF ENGINEERING, Chennai-600100
            </h2>
            <div
              style={{
                fontFamily: "'Georgia', 'Times New Roman', serif",
                fontStyle: "italic",
                fontSize: "12px",
                color: "#475569",
                marginTop: "2px",
              }}
            >
              (An Autonomous Institution Affiliated to Anna University, Chennai)
            </div>
            <div
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: "11px",
                fontWeight: 800,
                color: "#b8892b",
                letterSpacing: "1px",
                textTransform: "uppercase",
                marginTop: "4px",
              }}
            >
              OFFICE OF THE CONTROLLER OF EXAMINATIONS
            </div>
            <div
              style={{
                fontFamily: "'Georgia', serif",
                fontSize: "13px",
                fontWeight: 700,
                color: "#1e293b",
                letterSpacing: "0.8px",
                marginTop: "4px",
              }}
            >
              {examName}
            </div>
            <div
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: "14px",
                fontWeight: 800,
                color: "#0050b3",
                letterSpacing: "2px",
                textTransform: "uppercase",
                marginTop: "6px",
              }}
            >
              {documentTitle}
            </div>
          </div>

          {/* Spacer to balance the logo on left */}
          <div style={{ width: "72px", flexShrink: 0 }} />
        </div>

        {/* Thin blue dividing line */}
        <div
          style={{
            height: "2px",
            backgroundColor: "#0050b3",
            width: "100%",
            marginBottom: "16px",
          }}
        />

        {/* 4-Column Info Box if infoItems provided */}
        {infoItems.length > 0 && (
          <div className="portal-info-box">
            {infoItems.map((item, idx) => (
              <div key={idx} className="portal-info-item">
                <span className="portal-info-label">{item.label}</span>
                <span className="portal-info-value">{item.value}</span>
              </div>
            ))}
          </div>
        )}

        {/* Content Body */}
        {children}
      </div>
    </div>
  );
};
