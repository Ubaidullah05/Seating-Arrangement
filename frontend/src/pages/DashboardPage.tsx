import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { 
  Users, 
  Building2, 
  CheckCircle2, 
  AlertCircle, 
  Shuffle, 
  UploadCloud, 
  Calendar,
  Layers
} from "lucide-react";

export const DashboardPage: React.FC = () => {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: api.getDashboardStats,
    refetchInterval: 5000,
  });

  const { data: floors } = useQuery({
    queryKey: ["floors"],
    queryFn: api.getFloors,
  });

  return (
    <div style={{ maxWidth: "1180px", margin: "0 auto", padding: "24px 28px" }}>
      {/* Page Title Row */}
      <div className="portal-page-header">
        <div>
          <h1 className="portal-page-title">Executive Examination Dashboard</h1>
          <div style={{ fontSize: "13px", color: "#64748b", marginTop: "4px" }}>
            Jerusalem College of Engineering | Office of the Controller of Examinations
          </div>
        </div>
        <Link to="/plans" className="btn-gold no-print">
          VIEW SEATING PLANS
        </Link>
      </div>

      {isLoading && (
        <div style={{ padding: "40px", textAlign: "center", color: "#64748b" }}>
          Loading dashboard statistics...
        </div>
      )}

      {error && (
        <div style={{ padding: "16px", backgroundColor: "#fee2e2", color: "#991b1b", borderRadius: "4px", marginBottom: "20px" }}>
          Error loading dashboard: {String(error)}
        </div>
      )}

      {stats && (
        <>
          {/* Active Examination Banner */}
          <div
            style={{
              backgroundColor: "#ffffff",
              border: "1px solid #d8e2ec",
              borderRadius: "4px",
              padding: "20px 24px",
              marginBottom: "24px",
              boxShadow: "0 2px 6px rgba(0, 31, 71, 0.04)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              borderLeft: "5px solid #0050b3",
            }}
          >
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#b8892b", fontWeight: 700, fontSize: "11px", letterSpacing: "1px", textTransform: "uppercase" }}>
                <Calendar size={15} /> ACTIVE EXAMINATION
              </div>
              <h2 style={{ fontFamily: "'Georgia', serif", fontSize: "18px", color: "#002f66", margin: "4px 0" }}>
                {stats.active_exam_name || "END SEMESTER EXAMINATIONS — OCT/NOV 2026"}
              </h2>
              <div style={{ fontSize: "13px", color: "#475569" }}>
                Date: <strong>{stats.active_exam_date || "15/10/2026"}</strong> &nbsp;|&nbsp; Session: <strong>{stats.active_exam_session || "FN (10:00 AM - 01:00 PM)"}</strong>
              </div>
            </div>

            <div style={{ display: "flex", gap: "12px" }}>
              <Link to="/generate" className="btn-blue" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <Shuffle size={15} /> GENERATE SEATING
              </Link>
              <Link to="/upload" className="btn-outline" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <UploadCloud size={15} /> UPLOAD STUDENTS
              </Link>
            </div>
          </div>

          {/* Metric Cards Grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "18px",
              marginBottom: "28px",
            }}
          >
            {/* Registered Students */}
            <div
              style={{
                backgroundColor: "#ffffff",
                border: "1px solid #e2e8f0",
                borderRadius: "4px",
                padding: "18px 20px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.03)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "12px", fontWeight: 600 }}>
                <span>REGISTERED STUDENTS</span>
                <Users size={18} color="#0050b3" />
              </div>
              <div style={{ fontFamily: "'Georgia', serif", fontSize: "28px", fontWeight: 700, color: "#0f172a", marginTop: "8px" }}>
                {stats.total_students}
              </div>
              <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
                16-digit verified candidates
              </div>
            </div>

            {/* Total Allocated */}
            <div
              style={{
                backgroundColor: "#ffffff",
                border: "1px solid #e2e8f0",
                borderRadius: "4px",
                padding: "18px 20px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.03)",
                borderTop: "3px solid #16a34a",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "12px", fontWeight: 600 }}>
                <span>SEATS ALLOCATED</span>
                <CheckCircle2 size={18} color="#16a34a" />
              </div>
              <div style={{ fontFamily: "'Georgia', serif", fontSize: "28px", fontWeight: 700, color: "#16a34a", marginTop: "8px" }}>
                {stats.total_allocated}
              </div>
              <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
                Assigned to exam halls
              </div>
            </div>

            {/* Unallocated */}
            <div
              style={{
                backgroundColor: "#ffffff",
                border: "1px solid #e2e8f0",
                borderRadius: "4px",
                padding: "18px 20px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.03)",
                borderTop: stats.total_unallocated > 0 ? "3px solid #d97706" : "3px solid #cbd5e1",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "12px", fontWeight: 600 }}>
                <span>UNALLOCATED STUDENTS</span>
                <AlertCircle size={18} color={stats.total_unallocated > 0 ? "#d97706" : "#64748b"} />
              </div>
              <div style={{ fontFamily: "'Georgia', serif", fontSize: "28px", fontWeight: 700, color: stats.total_unallocated > 0 ? "#d97706" : "#475569", marginTop: "8px" }}>
                {stats.total_unallocated}
              </div>
              <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
                Awaiting exam generation
              </div>
            </div>

            {/* Active Classrooms */}
            <div
              style={{
                backgroundColor: "#ffffff",
                border: "1px solid #e2e8f0",
                borderRadius: "4px",
                padding: "18px 20px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.03)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "12px", fontWeight: 600 }}>
                <span>ACTIVE CLASSROOMS</span>
                <Building2 size={18} color="#0050b3" />
              </div>
              <div style={{ fontFamily: "'Georgia', serif", fontSize: "28px", fontWeight: 700, color: "#0f172a", marginTop: "8px" }}>
                {stats.total_active_rooms}
              </div>
              <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
                Across {floors ? floors.length : 6} floors & blocks
              </div>
            </div>

            {/* Total Capacity */}
            <div
              style={{
                backgroundColor: "#ffffff",
                border: "1px solid #e2e8f0",
                borderRadius: "4px",
                padding: "18px 20px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.03)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "12px", fontWeight: 600 }}>
                <span>AVAILABLE SEAT CAPACITY</span>
                <Layers size={18} color="#b8892b" />
              </div>
              <div style={{ fontFamily: "'Georgia', serif", fontSize: "28px", fontWeight: 700, color: "#b8892b", marginTop: "8px" }}>
                {stats.total_capacity}
              </div>
              <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
                24 - 28 seats per room
              </div>
            </div>
          </div>

          {/* Floor & Room Infrastructure Overview */}
          <div
            style={{
              backgroundColor: "#ffffff",
              border: "1px solid #cbd5e1",
              borderRadius: "4px",
              padding: "24px",
              boxShadow: "0 2px 8px rgba(0, 0, 0, 0.04)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <div>
                <h3 style={{ fontFamily: "'Georgia', serif", fontSize: "16px", color: "#002f66", margin: 0 }}>
                  Campus Examination Halls Infrastructure
                </h3>
                <div style={{ fontSize: "12px", color: "#64748b", marginTop: "2px" }}>
                  Active room layout by floor and block (Ground, First, Second, Third, LS, VH)
                </div>
              </div>
              <Link to="/rooms" className="btn-outline" style={{ fontSize: "12px" }}>
                CONFIGURE ROOMS
              </Link>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {floors?.map((fl) => (
                <div
                  key={fl.id}
                  style={{
                    border: "1px solid #e2e8f0",
                    borderRadius: "4px",
                    padding: "14px 18px",
                    backgroundColor: "#fbfcfe",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px", alignItems: "center" }}>
                    <span style={{ fontFamily: "'Georgia', serif", fontWeight: 700, color: "#004a99", fontSize: "14px" }}>
                      {fl.name}
                    </span>
                    <span style={{ fontSize: "12px", color: "#64748b" }}>
                      {fl.classrooms.filter(r => r.is_active).length} of {fl.classrooms.length} Halls Active
                    </span>
                  </div>

                  <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                    {fl.classrooms.map((rm) => (
                      <div
                        key={rm.id}
                        style={{
                          padding: "6px 12px",
                          borderRadius: "4px",
                          border: rm.is_active ? "1px solid #0050b3" : "1px solid #cbd5e1",
                          backgroundColor: rm.is_active ? "#f0f7ff" : "#f1f5f9",
                          color: rm.is_active ? "#002f66" : "#94a3b8",
                          fontFamily: "'JetBrains Mono', monospace",
                          fontSize: "12px",
                          fontWeight: 700,
                          display: "flex",
                          alignItems: "center",
                          gap: "6px",
                        }}
                      >
                        <span>{rm.name}</span>
                        <span style={{ fontSize: "10px", opacity: 0.8, fontWeight: 500 }}>
                          ({rm.capacity} seats)
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
