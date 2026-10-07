import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { 
  Shuffle, 
  Sparkles, 
  AlertCircle, 
  CheckCircle2, 
  ArrowRight,
  RefreshCw
} from "lucide-react";

export const GeneratePage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [examName, setExamName] = useState("END SEMESTER EXAMINATIONS — OCT/NOV 2026");
  const [examDate, setExamDate] = useState("2026-10-15");
  const [session, setSession] = useState("FN");
  const [customSeed, setCustomSeed] = useState<string>("");
  const [resultData, setResultData] = useState<{
    message: string;
    exam_id: number;
    allocated_count: number;
    seed: number;
  } | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { data: stats } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: api.getDashboardStats,
  });

  const generateMutation = useMutation({
    mutationFn: (params: any) => api.generateAllocation(params),
    onSuccess: (data) => {
      setResultData(data);
      setErrorMessage(null);
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
      queryClient.invalidateQueries({ queryKey: ["exams"] });
    },
    onError: (err: Error) => {
      setErrorMessage(err.message);
      setResultData(null);
    },
  });

  const handleGenerate = (isReshuffle = false) => {
    setErrorMessage(null);
    const seedVal = customSeed.trim() ? parseInt(customSeed.trim()) : undefined;
    generateMutation.mutate({
      name: examName,
      exam_date: examDate,
      session,
      seed: seedVal,
      reshuffle: isReshuffle,
    });
  };

  const handleRandomizeSeed = () => {
    const randomVal = Math.floor(100000 + Math.random() * 900000);
    setCustomSeed(randomVal.toString());
  };

  const isCapacityExceeded = stats ? stats.total_students > stats.total_capacity : false;

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "24px 28px" }}>
      {/* Page Title */}
      <div className="portal-page-header">
        <div>
          <h1 className="portal-page-title">Generate Seating Arrangement</h1>
          <div style={{ fontSize: "13px", color: "#64748b", marginTop: "4px" }}>
            Configure examination schedule parameters and execute randomized allocation
          </div>
        </div>
      </div>

      {/* Capacity Health Summary Banner */}
      {stats && (
        <div
          style={{
            backgroundColor: isCapacityExceeded ? "#fef2f2" : "#f0fdf4",
            border: isCapacityExceeded ? "1px solid #fecaca" : "1px solid #bbf7d0",
            borderLeft: isCapacityExceeded ? "5px solid #dc2626" : "5px solid #16a34a",
            borderRadius: "4px",
            padding: "16px 20px",
            marginBottom: "24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            {isCapacityExceeded ? (
              <AlertCircle size={24} color="#dc2626" />
            ) : (
              <CheckCircle2 size={24} color="#16a34a" />
            )}
            <div>
              <div style={{ fontWeight: 700, fontSize: "14px", color: isCapacityExceeded ? "#991b1b" : "#166534" }}>
                {isCapacityExceeded
                  ? "Seating Capacity Warning: Not enough active seats!"
                  : "Exam Capacity Verified: Ready for Allocation"}
              </div>
              <div style={{ fontSize: "12px", color: isCapacityExceeded ? "#b91c1c" : "#15803d", marginTop: "2px" }}>
                Registered Students: <strong>{stats.total_students}</strong> &nbsp;|&nbsp; Active Hall Capacity: <strong>{stats.total_capacity} seats</strong> ({stats.total_active_rooms} rooms active)
              </div>
            </div>
          </div>

          {isCapacityExceeded && (
            <button
              onClick={() => navigate("/rooms")}
              className="btn-outline"
              style={{ fontSize: "12px" }}
            >
              Activate More Rooms
            </button>
          )}
        </div>
      )}

      {/* Main Parameters Card */}
      <div
        style={{
          backgroundColor: "#ffffff",
          border: "1px solid #cbd5e1",
          borderRadius: "4px",
          padding: "28px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
          marginBottom: "24px",
        }}
      >
        <h3 style={{ fontFamily: "'Georgia', serif", fontSize: "16px", color: "#002f66", marginBottom: "18px" }}>
          Examination Details & Shuffle Engine
        </h3>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" }}>
          {/* Examination Name */}
          <div style={{ gridColumn: "1 / -1" }}>
            <label style={{ display: "block", fontSize: "12px", fontWeight: 700, color: "#334155", marginBottom: "6px" }}>
              EXAMINATION TITLE / NAME
            </label>
            <input
              type="text"
              value={examName}
              onChange={(e) => setExamName(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 14px",
                borderRadius: "4px",
                border: "1px solid #cbd5e1",
                fontSize: "14px",
                fontFamily: "'Georgia', serif",
                color: "#0f172a",
              }}
            />
          </div>

          {/* Exam Date */}
          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: 700, color: "#334155", marginBottom: "6px" }}>
              EXAMINATION DATE
            </label>
            <div style={{ position: "relative" }}>
              <input
                type="date"
                value={examDate}
                onChange={(e) => setExamDate(e.target.value)}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  borderRadius: "4px",
                  border: "1px solid #cbd5e1",
                  fontSize: "14px",
                  fontFamily: "'Inter', sans-serif",
                }}
              />
            </div>
          </div>

          {/* Session */}
          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: 700, color: "#334155", marginBottom: "6px" }}>
              SESSION TIMING
            </label>
            <select
              value={session}
              onChange={(e) => setSession(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 14px",
                borderRadius: "4px",
                border: "1px solid #cbd5e1",
                fontSize: "14px",
                fontFamily: "'Inter', sans-serif",
                backgroundColor: "#ffffff",
              }}
            >
              <option value="FN">FN — Forenoon (10:00 AM – 01:00 PM)</option>
              <option value="AN">AN — Afternoon (02:00 PM – 05:00 PM)</option>
            </select>
          </div>

          {/* Reproducible Seed (Optional) */}
          <div style={{ gridColumn: "1 / -1" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
              <label style={{ fontSize: "12px", fontWeight: 700, color: "#334155" }}>
                REPRODUCIBILITY SEED (OPTIONAL)
              </label>
              <button
                type="button"
                onClick={handleRandomizeSeed}
                style={{
                  background: "none",
                  border: "none",
                  color: "#0050b3",
                  fontSize: "12px",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                }}
              >
                <Sparkles size={13} /> Generate Random Seed
              </button>
            </div>
            <input
              type="number"
              placeholder="Leave empty for auto-generated seed, or enter integer"
              value={customSeed}
              onChange={(e) => setCustomSeed(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 14px",
                borderRadius: "4px",
                border: "1px solid #cbd5e1",
                fontSize: "14px",
                fontFamily: "'JetBrains Mono', monospace",
              }}
            />
            <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
              Using the same seed number will consistently reproduce the identical randomized seat arrangement.
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: "flex", gap: "12px", borderTop: "1px solid #e2e8f0", paddingTop: "20px" }}>
          <button
            onClick={() => handleGenerate(false)}
            disabled={generateMutation.isPending || isCapacityExceeded}
            className="btn-gold"
            style={{ padding: "10px 22px", fontSize: "14px" }}
          >
            <Shuffle size={16} /> Run Random Allocation
          </button>

          <button
            onClick={() => {
              handleRandomizeSeed();
              handleGenerate(true);
            }}
            disabled={generateMutation.isPending || isCapacityExceeded}
            className="btn-outline"
            style={{ padding: "10px 18px", fontSize: "13px" }}
          >
            <RefreshCw size={15} /> Re-Shuffle with New Seed
          </button>
        </div>

        {generateMutation.isPending && (
          <div style={{ marginTop: "16px", color: "#0050b3", fontSize: "13px", fontWeight: 600 }}>
            Running even distribution algorithm across active examination halls...
          </div>
        )}
      </div>

      {/* Error Feedback */}
      {errorMessage && (
        <div
          style={{
            backgroundColor: "#fef2f2",
            border: "1px solid #fecaca",
            color: "#991b1b",
            padding: "16px",
            borderRadius: "4px",
            marginBottom: "20px",
            fontSize: "13px",
          }}
        >
          <strong>Allocation Error:</strong> {errorMessage}
        </div>
      )}

      {/* Success Feedback */}
      {resultData && (
        <div
          style={{
            backgroundColor: "#ffffff",
            border: "1px solid #bbf7d0",
            borderLeft: "5px solid #16a34a",
            borderRadius: "4px",
            padding: "24px",
            boxShadow: "0 4px 12px rgba(22, 163, 74, 0.1)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#16a34a", fontWeight: 700, fontSize: "14px" }}>
                <CheckCircle2 size={20} /> Seating Allocation Generated Successfully!
              </div>
              <h3 style={{ fontFamily: "'Georgia', serif", fontSize: "16px", color: "#002f66", margin: "8px 0" }}>
                {resultData.message}
              </h3>
              <div style={{ fontSize: "13px", color: "#475569" }}>
                Seed applied: <code style={{ fontFamily: "monospace", fontWeight: 700, color: "#0050b3" }}>{resultData.seed}</code> &nbsp;|&nbsp;
                Allocated Candidates: <strong>{resultData.allocated_count}</strong>
              </div>
            </div>

            <button
              onClick={() => navigate("/plans")}
              className="btn-blue"
              style={{ display: "flex", alignItems: "center", gap: "6px", padding: "10px 18px" }}
            >
              View Seating Plans <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
