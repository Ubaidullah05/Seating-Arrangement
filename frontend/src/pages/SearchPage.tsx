import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { DocumentCard } from "../components/DocumentCard";
import { 
  Search, 
  Printer, 
  AlertCircle
} from "lucide-react";

export const SearchPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");

  const { data: searchResults, isLoading, isFetched } = useQuery({
    queryKey: ["search-student", submittedQuery],
    queryFn: () => submittedQuery.length >= 2 ? api.searchStudents(submittedQuery) : [],
    enabled: submittedQuery.length >= 2,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim().length >= 2) {
      setSubmittedQuery(searchTerm.trim());
    }
  };

  const handlePrintSlip = () => {
    window.print();
  };

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "24px 28px" }}>
      {/* Page Title */}
      <div className="portal-page-header">
        <div>
          <h1 className="portal-page-title">Candidate Hall & Seat Locator</h1>
          <div style={{ fontSize: "13px", color: "#64748b", marginTop: "4px" }}>
            Search allocated examination hall and seat by register number or name
          </div>
        </div>
        {searchResults && searchResults.length > 0 && (
          <button onClick={handlePrintSlip} className="btn-gold no-print">
            <Printer size={16} /> PRINT SEAT SLIP
          </button>
        )}
      </div>

      {/* Search Input Box (Hidden during print) */}
      <div
        className="no-print"
        style={{
          backgroundColor: "#ffffff",
          border: "1px solid #cbd5e1",
          borderRadius: "6px",
          padding: "24px",
          marginBottom: "28px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
        }}
      >
        <form onSubmit={handleSearch}>
          <label style={{ display: "block", fontSize: "12px", fontWeight: 700, color: "#334155", marginBottom: "8px" }}>
            ENTER REGISTER NUMBER (13/16 DIGITS OR LAST 3-4 DIGITS)
          </label>
          <div style={{ display: "flex", gap: "10px" }}>
            <div style={{ position: "relative", flex: 1 }}>
              <input
                type="text"
                placeholder="e.g. 2403310910421108 or last digits 1108..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: "100%",
                  padding: "12px 16px 12px 40px",
                  borderRadius: "4px",
                  border: "1px solid #cbd5e1",
                  fontSize: "14px",
                  fontFamily: "'JetBrains Mono', monospace",
                  fontWeight: 600,
                  color: "#0f172a",
                }}
              />
              <Search
                size={18}
                color="#64748b"
                style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)" }}
              />
            </div>

            <button
              type="submit"
              className="btn-blue"
              style={{ padding: "0 24px", fontSize: "13px", fontWeight: 700 }}
            >
              SEARCH
            </button>
          </div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "6px" }}>
            Accepts a full 13/16-digit register number (exact match), suffix matching (last 3-4 digits), or student name.
          </div>
        </form>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div style={{ textAlign: "center", padding: "32px", color: "#64748b" }}>
          Searching candidate records...
        </div>
      )}

      {/* Results View */}
      {isFetched && searchResults && searchResults.length === 0 && (
        <div
          style={{
            backgroundColor: "#f8fafc",
            border: "1px solid #e2e8f0",
            borderRadius: "4px",
            padding: "36px",
            textAlign: "center",
            color: "#64748b",
          }}
        >
          <AlertCircle size={32} color="#94a3b8" style={{ margin: "0 auto 10px auto" }} />
          <h3 style={{ fontFamily: "'Georgia', serif", fontSize: "16px", color: "#1e293b", marginBottom: "4px" }}>
            No Matching Candidates Found
          </h3>
          <p style={{ fontSize: "13px" }}>
            No student found matching query "{submittedQuery}". Please check the register number or upload students first.
          </p>
        </div>
      )}

      {searchResults && searchResults.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
          {searchResults.map((res, index) => {
            const st = res.student;
            const alloc = res.allocation;

            return (
              <DocumentCard
                key={index}
                documentTitle="EXAMINATION HALL ENTRY SLIP"
                examName={res.exam_name || "END SEMESTER EXAMINATIONS — OCT/NOV 2026"}
                infoItems={[
                  { label: "REGISTER NUMBER", value: st?.register_no || "-" },
                  { label: "CANDIDATE NAME", value: st?.name || "STUDENT" },
                  { label: "BRANCH", value: st?.branch || "-" },
                  { label: "HALL / ROOM", value: alloc?.classroom_name || "Not Allocated" },
                  { label: "FLOOR LEVEL", value: alloc?.floor_name || "-" },
                  { label: "SEAT NUMBER", value: alloc?.seat_label || "UNASSIGNED" },
                ]}
              >
                {/* Visual Seat Slip Summary Box */}
                <div
                  style={{
                    backgroundColor: "#f7f9fc",
                    border: "2px solid #0050b3",
                    borderRadius: "4px",
                    padding: "20px 24px",
                    marginTop: "16px",
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "20px",
                  }}
                >
                  {/* Left Column: Candidate Details */}
                  <div>
                    <h4 style={{ fontFamily: "'Georgia', serif", fontSize: "14px", color: "#002f66", marginBottom: "12px", borderBottom: "1px solid #cbd5e1", paddingBottom: "4px" }}>
                      Candidate Particulars
                    </h4>
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "13px" }}>
                      <div>
                        <span style={{ color: "#64748b", fontSize: "11px", display: "block" }}>REGISTER NUMBER:</span>
                        <strong className="mono-cell" style={{ fontSize: "15px", color: "#0050b3" }}>
                          {st?.register_no}
                        </strong>
                      </div>
                      <div>
                        <span style={{ color: "#64748b", fontSize: "11px", display: "block" }}>CANDIDATE NAME:</span>
                        <strong style={{ fontFamily: "'Georgia', serif" }}>{st?.name || "-"}</strong>
                      </div>
                      <div>
                        <span style={{ color: "#64748b", fontSize: "11px", display: "block" }}>BRANCH / DEGREE:</span>
                        <span>{st?.branch || "-"}</span>
                      </div>
                      <div>
                        <span style={{ color: "#64748b", fontSize: "11px", display: "block" }}>SEMESTER / COURSE:</span>
                        <span>Sem {st?.semester || "5"} — {st?.subject_code || "JCS2501"}</span>
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Hall & Seat Allocation */}
                  <div
                    style={{
                      backgroundColor: "#ffffff",
                      border: "1px solid #cbd5e1",
                      borderRadius: "4px",
                      padding: "16px",
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "center",
                      alignItems: "center",
                      textAlign: "center",
                    }}
                  >
                    <span style={{ fontSize: "11px", fontWeight: 700, color: "#b8892b", letterSpacing: "1px" }}>
                      DESIGNATED SEAT ASSIGNMENT
                    </span>
                    
                    {alloc ? (
                      <>
                        <div
                          style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: "36px",
                            fontWeight: 800,
                            color: "#0050b3",
                            margin: "8px 0",
                            lineHeight: "1",
                          }}
                        >
                          {alloc.seat_label}
                        </div>
                        <div style={{ fontFamily: "'Georgia', serif", fontSize: "16px", fontWeight: 700, color: "#0f172a" }}>
                          HALL: {alloc.classroom_name}
                        </div>
                        <div style={{ fontSize: "12px", color: "#475569", marginTop: "2px" }}>
                          Location: <strong>{alloc.floor_name}</strong>
                        </div>
                      </>
                    ) : (
                      <div style={{ color: "#d97706", fontWeight: 700, marginTop: "12px", fontSize: "14px" }}>
                        Candidate not yet allocated to an examination hall.
                      </div>
                    )}
                  </div>
                </div>

                {/* Candidate Instructions */}
                <div style={{ marginTop: "20px", fontSize: "11px", color: "#475569", lineHeight: "1.6", borderTop: "1px solid #e2e8f0", paddingTop: "12px" }}>
                  <strong>Important Notice to Candidate:</strong> Candidates must occupy their designated seat 15 minutes before the examination commences. Possession of electronic communication devices is strictly prohibited inside the examination hall.
                </div>
              </DocumentCard>
            );
          })}
        </div>
      )}
    </div>
  );
};
