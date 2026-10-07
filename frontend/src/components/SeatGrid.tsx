import React from "react";
import type { SeatGridCell } from "../types";

interface SeatGridProps {
  grid: SeatGridCell[][];
  columnsCount?: number;
  rowsCount?: number;
}

export const SeatGrid: React.FC<SeatGridProps> = ({ grid }) => {
  if (!grid || grid.length === 0) {
    return <div style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>No seat grid data available.</div>;
  }

  const colHeaders = ["COLUMN A", "COLUMN B", "COLUMN C", "COLUMN D"];

  return (
    <div style={{ marginTop: "16px", overflowX: "auto" }}>
      {/* Front of Room / Blackboard indicator */}
      <div
        style={{
          width: "100%",
          padding: "8px",
          backgroundColor: "#1e293b",
          color: "#ffffff",
          textAlign: "center",
          fontFamily: "'Georgia', serif",
          fontSize: "12px",
          fontWeight: 700,
          letterSpacing: "1.5px",
          textTransform: "uppercase",
          borderRadius: "4px 4px 0 0",
          marginBottom: "12px",
        }}
      >
        ✦ FRONT OF HALL / BLACKBOARD & INVIGILATOR DESK ✦
      </div>

      {/* Column Headers */}
      <div 
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "12px",
          marginBottom: "8px",
          textAlign: "center",
        }}
      >
        {colHeaders.map((h, i) => (
          <div
            key={i}
            style={{
              fontFamily: "'Georgia', serif",
              fontSize: "11px",
              fontWeight: 700,
              color: "#004a99",
              letterSpacing: "1px",
              padding: "4px",
              backgroundColor: "#edf2f7",
              border: "1px solid #cbd5e1",
              borderRadius: "2px",
            }}
          >
            {h}
          </div>
        ))}
      </div>

      {/* Grid of rows */}
      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {grid.map((rowCells, rowIdx) => (
          <div
            key={rowIdx}
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: "12px",
            }}
          >
            {rowCells.map((cell) => {
              const alloc = cell.allocation;
              const isOccupied = !!alloc;

              return (
                <div
                  key={cell.seat_label}
                  style={{
                    backgroundColor: isOccupied ? "#ffffff" : "#f8fafc",
                    border: isOccupied ? "1.5px solid #0050b3" : "1px dashed #cbd5e1",
                    borderRadius: "4px",
                    padding: "8px 10px",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    minHeight: "78px",
                    boxShadow: isOccupied ? "0 2px 5px rgba(0, 80, 179, 0.08)" : "none",
                    position: "relative",
                  }}
                >
                  {/* Seat Label badge */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      marginBottom: "4px",
                    }}
                  >
                    <span
                      style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontWeight: 700,
                        fontSize: "11px",
                        backgroundColor: isOccupied ? "#0050b3" : "#94a3b8",
                        color: "#ffffff",
                        padding: "1px 6px",
                        borderRadius: "3px",
                      }}
                    >
                      {cell.seat_label}
                    </span>
                    {isOccupied && alloc.branch && (
                      <span
                        style={{
                          fontSize: "9px",
                          fontWeight: 700,
                          color: "#b8892b",
                          maxWidth: "110px",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          whiteSpace: "nowrap",
                        }}
                        title={alloc.branch}
                      >
                        {alloc.branch.replace("B.E. ", "").replace("B.Tech. ", "")}
                      </span>
                    )}
                  </div>

                  {/* Register Number & Name */}
                  {isOccupied ? (
                    <div>
                      <div
                        style={{
                          fontFamily: "'JetBrains Mono', 'Consolas', monospace",
                          fontWeight: 700,
                          fontSize: "12px",
                          color: "#0f172a",
                          letterSpacing: "0.4px",
                          marginBottom: "2px",
                        }}
                      >
                        {alloc.register_no}
                      </div>
                      <div
                        style={{
                          fontFamily: "'Georgia', serif",
                          fontSize: "11px",
                          color: "#334155",
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                        }}
                        title={alloc.student_name || ""}
                      >
                        {alloc.student_name || "Student"}
                      </div>
                    </div>
                  ) : (
                    <div
                      style={{
                        fontFamily: "'Georgia', serif",
                        fontSize: "11px",
                        color: "#94a3b8",
                        fontStyle: "italic",
                        textAlign: "center",
                        marginTop: "8px",
                      }}
                    >
                      VACANT
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
};
