import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { DocumentCard } from "../components/DocumentCard";
import { SeatGrid } from "../components/SeatGrid";
import { 
  Printer, 
  FileDown, 
  FileSpreadsheet, 
  Grid3X3, 
  List, 
  ClipboardCheck,
  Loader2,
  AlertCircle,
  X
} from "lucide-react";

export const SeatingPlansPage: React.FC = () => {
  const [selectedExamId, setSelectedExamId] = useState<number | null>(null);
  const [selectedFloorId, setSelectedFloorId] = useState<number | null>(null);
  const [selectedClassroomId, setSelectedClassroomId] = useState<number | null>(null);
  const [activeView, setActiveView] = useState<"grid" | "table" | "handover">("grid");

  // Export download states
  const [downloading, setDownloading] = useState<"pdf" | "xlsx" | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  // Fetch Exams
  const { data: exams } = useQuery({
    queryKey: ["exams"],
    queryFn: api.getExams,
  });

  // Fetch Floors with classrooms
  const { data: floors } = useQuery({
    queryKey: ["floors"],
    queryFn: api.getFloors,
  });

  // Derive selections during render (no setState-in-effect)
  const currentExam = exams?.find(e => e.id === selectedExamId) || exams?.[0] || null;
  const currentFloor = floors?.find(f => f.id === selectedFloorId) || floors?.[0] || null;
  const currentClassroom =
    currentFloor?.classrooms.find(c => c.id === selectedClassroomId) ||
    currentFloor?.classrooms[0] ||
    null;

  const effectiveExamId = currentExam?.id ?? null;
  const effectiveClassroomId = currentClassroom?.id ?? null;

  // Fetch Room Plan
  const { data: roomPlan, isLoading: isPlanLoading, isError: isPlanError, error: planError } = useQuery({
    queryKey: ["room-plan", effectiveExamId, effectiveClassroomId],
    queryFn: () => (effectiveExamId && effectiveClassroomId) ? api.getRoomPlan(effectiveExamId, effectiveClassroomId) : null,
    enabled: !!(effectiveExamId && effectiveClassroomId),
  });

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = async (type: "pdf" | "xlsx") => {
    if (!effectiveExamId) return;
    setDownloading(type);
    setDownloadError(null);
    try {
      if (type === "pdf") {
        await api.downloadExportPdf(effectiveExamId);
      } else if (type === "xlsx") {
        await api.downloadExportXlsx(effectiveExamId);
      }
    } catch (err: any) {
      console.error("Export error:", err);
      setDownloadError(
        err.message || "Failed to download export file. Please verify that seating allocations exist for this exam."
      );
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div style={{ maxWidth: "1140px", margin: "0 auto", padding: "24px 28px" }}>
      {/* Page Header Row with Action Buttons */}
      <div className="portal-page-header">
        <div>
          <h1 className="portal-page-title">Examination Seating Arrangement Plans</h1>
          <div style={{ fontSize: "13px", color: "#64748b", marginTop: "4px" }}>
            Visual seating layout, invigilator attendance sheets and answer booklet handover forms
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }} className="no-print">
          {effectiveExamId && (
            <>
              <button
                type="button"
                onClick={() => handleDownload("pdf")}
                disabled={!!downloading}
                className="btn-outline"
                style={{
                  fontSize: "12px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  cursor: downloading ? "not-allowed" : "pointer",
                  opacity: downloading && downloading !== "pdf" ? 0.6 : 1,
                  backgroundColor: "#ffffff",
                }}
                title="Download complete PDF with 1 page per classroom"
              >
                {downloading === "pdf" ? (
                  <Loader2 size={15} className="animate-spin" color="#dc2626" />
                ) : (
                  <FileDown size={15} color="#dc2626" />
                )}
                {downloading === "pdf" ? "Exporting PDF..." : "Export PDF"}
              </button>

              <button
                type="button"
                onClick={() => handleDownload("xlsx")}
                disabled={!!downloading}
                className="btn-outline"
                style={{
                  fontSize: "12px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  cursor: downloading ? "not-allowed" : "pointer",
                  opacity: downloading && downloading !== "xlsx" ? 0.6 : 1,
                  backgroundColor: "#ffffff",
                }}
                title="Download Excel file preserving register numbers as text"
              >
                {downloading === "xlsx" ? (
                  <Loader2 size={15} className="animate-spin" color="#16a34a" />
                ) : (
                  <FileSpreadsheet size={15} color="#16a34a" />
                )}
                {downloading === "xlsx" ? "Exporting Excel..." : "Export Excel (XLSX)"}
              </button>

            </>
          )}

          <button onClick={handlePrint} className="btn-gold" style={{ cursor: "pointer" }}>
            <Printer size={16} /> PRINT
          </button>
        </div>
      </div>

      {/* Export Error Alert Banner */}
      {downloadError && (
        <div
          className="no-print"
          style={{
            backgroundColor: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: "6px",
            padding: "12px 16px",
            marginBottom: "18px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "12px",
            color: "#991b1b",
            fontSize: "13px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <AlertCircle size={18} color="#dc2626" style={{ flexShrink: 0 }} />
            <div>
              <strong>Export Warning:</strong> {downloadError}
            </div>
          </div>
          <button
            type="button"
            onClick={() => setDownloadError(null)}
            style={{
              background: "none",
              border: "none",
              color: "#991b1b",
              cursor: "pointer",
              padding: "4px",
              display: "flex",
              alignItems: "center",
            }}
            title="Dismiss notification"
          >
            <X size={16} />
          </button>
        </div>
      )}


      {/* Filter Selector Bar (Hidden during Print) */}
      <div
        className="no-print"
        style={{
          backgroundColor: "#ffffff",
          border: "1px solid #cbd5e1",
          borderRadius: "4px",
          padding: "16px 20px",
          marginBottom: "24px",
          display: "flex",
          flexWrap: "wrap",
          gap: "16px",
          alignItems: "center",
          justifyContent: "space-between",
          boxShadow: "0 2px 4px rgba(0,0,0,0.03)",
        }}
      >
        <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", alignItems: "center" }}>
          {/* Exam Selector */}
          <div>
            <label style={{ display: "block", fontSize: "11px", fontWeight: 700, color: "#64748b", marginBottom: "4px" }}>
              EXAMINATION
            </label>
            <select
              value={effectiveExamId || ""}
              onChange={(e) => setSelectedExamId(Number(e.target.value))}
              style={{
                padding: "8px 12px",
                borderRadius: "4px",
                border: "1px solid #cbd5e1",
                fontFamily: "'Georgia', serif",
                fontSize: "13px",
                fontWeight: 600,
                color: "#002f66",
              }}
            >
              {exams?.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name} ({e.exam_date} - {e.session})
                </option>
              ))}
            </select>
          </div>

          {/* Floor Selector */}
          <div>
            <label style={{ display: "block", fontSize: "11px", fontWeight: 700, color: "#64748b", marginBottom: "4px" }}>
              FLOOR LEVEL
            </label>
            <select
              value={selectedFloorId || currentFloor?.id || ""}
              onChange={(e) => {
                const fid = Number(e.target.value);
                setSelectedFloorId(fid);
                const fl = floors?.find(f => f.id === fid);
                if (fl && fl.classrooms.length > 0) {
                  setSelectedClassroomId(fl.classrooms[0].id);
                }
              }}
              style={{
                padding: "8px 12px",
                borderRadius: "4px",
                border: "1px solid #cbd5e1",
                fontSize: "13px",
              }}
            >
              {floors?.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.name}
                </option>
              ))}
            </select>
          </div>

          {/* Classroom Selector */}
          <div>
            <label style={{ display: "block", fontSize: "11px", fontWeight: 700, color: "#64748b", marginBottom: "4px" }}>
              EXAM HALL / ROOM
            </label>
            <select
              value={effectiveClassroomId || ""}
              onChange={(e) => setSelectedClassroomId(Number(e.target.value))}
              style={{
                padding: "8px 12px",
                borderRadius: "4px",
                border: "1px solid #cbd5e1",
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: "13px",
                fontWeight: 700,
                color: "#0050b3",
              }}
            >
              {currentFloor?.classrooms.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.capacity} seats)
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div>
          <label style={{ display: "block", fontSize: "11px", fontWeight: 700, color: "#64748b", marginBottom: "4px" }}>
            DISPLAY FORMAT
          </label>
          <div style={{ display: "flex", border: "1px solid #cbd5e1", borderRadius: "4px", overflow: "hidden" }}>
            <button
              onClick={() => setActiveView("grid")}
              style={{
                padding: "7px 14px",
                border: "none",
                backgroundColor: activeView === "grid" ? "#0050b3" : "#ffffff",
                color: activeView === "grid" ? "#ffffff" : "#475569",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              <Grid3X3 size={14} /> Visual Seat Grid
            </button>
            <button
              onClick={() => setActiveView("table")}
              style={{
                padding: "7px 14px",
                border: "none",
                backgroundColor: activeView === "table" ? "#0050b3" : "#ffffff",
                color: activeView === "table" ? "#ffffff" : "#475569",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              <List size={14} /> Attendance Table
            </button>
            <button
              onClick={() => setActiveView("handover")}
              style={{
                padding: "7px 14px",
                border: "none",
                backgroundColor: activeView === "handover" ? "#0050b3" : "#ffffff",
                color: activeView === "handover" ? "#ffffff" : "#475569",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              <ClipboardCheck size={14} /> Handover
            </button>
          </div>
        </div>
      </div>

      {/* Classroom Plan View Loading / Error / Content */}
      {isPlanLoading && (
        <div style={{ padding: "60px 20px", textAlign: "center", color: "#64748b", backgroundColor: "#ffffff", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
          <Loader2 size={32} className="animate-spin" style={{ margin: "0 auto 12px auto", color: "#0050b3" }} />
          <div style={{ fontWeight: 600, color: "#1e293b", fontSize: "15px" }}>Loading Hall Seating Plan...</div>
          <div style={{ fontSize: "13px", marginTop: "4px" }}>Computing grid layout and seat assignments</div>
        </div>
      )}

      {isPlanError && (
        <div style={{ padding: "40px 20px", textAlign: "center", backgroundColor: "#ffffff", borderRadius: "6px", border: "1px solid #fecaca" }}>
          <AlertCircle size={36} color="#dc2626" style={{ margin: "0 auto 12px auto" }} />
          <div style={{ fontWeight: 700, color: "#991b1b", fontSize: "16px" }}>Unable to Load Seating Plan</div>
          <div style={{ fontSize: "13px", color: "#64748b", marginTop: "6px" }}>
            {(planError as any)?.message || "Failed to load room plan details."}
          </div>
        </div>
      )}

      {!isPlanLoading && roomPlan && currentExam && (
        <DocumentCard
          documentTitle={
            activeView === "handover"
              ? `ANSWER SCRIPT HANDOVER SHEET — HALL ${roomPlan.classroom_name}`
              : `SEATING ARRANGEMENT — HALL ${roomPlan.classroom_name}`
          }
          examName={currentExam.name}
          infoItems={[
            { label: "EXAMINATION", value: currentExam.name },
            { label: "EXAM DATE", value: currentExam.exam_date },
            { label: "SESSION", value: currentExam.session === "FN" ? "FN (09:00 AM – 12:00 PM)" : currentExam.session === "AN" ? "AN (01:00 PM – 04:00 PM)" : currentExam.session },
            { label: "FLOOR LEVEL", value: roomPlan.floor_name },
            { label: "HALL NO", value: roomPlan.classroom_name },
            { label: "TOTAL ALLOCATED", value: `${roomPlan.allocated_count} / ${roomPlan.capacity} Seats` },
            { label: "REG NO RANGE", value: `${roomPlan.min_register_no || "-"} to ${roomPlan.max_register_no || "-"}` },
            { 
              label: activeView === "handover" ? "DOCUMENT TYPE" : "LAYOUT", 
              value: activeView === "handover" ? "Answer Booklet Handover & Invigilator Account" : `4 Columns × ${roomPlan.rows_per_column} Rows` 
            },
          ]}
        >
          {activeView === "grid" && (
            <SeatGrid grid={roomPlan.grid} />
          )}

          {activeView === "table" && (
            <div style={{ marginTop: "16px" }}>
              <table className="portal-table">
                <thead>
                  <tr>
                    <th style={{ width: "60px", textAlign: "center" }}>S.no</th>
                    <th style={{ width: "220px", textAlign: "center" }}>Register Number</th>
                    <th>Name</th>
                    <th style={{ width: "90px", textAlign: "center" }}>Seatno</th>
                    <th style={{ width: "170px", textAlign: "center" }}>Candidate Signature</th>
                  </tr>
                </thead>
                <tbody>
                  {roomPlan.grid
                    .flatMap(row => row)
                    .filter(cell => cell.allocation)
                    .map((cell, index) => {
                      const alloc = cell.allocation!;
                      return (
                        <tr key={cell.seat_label}>
                          <td style={{ textAlign: "center", fontWeight: 600 }}>{index + 1}</td>
                          <td className="mono-cell" style={{ textAlign: "center" }}>
                            {alloc.register_no}
                          </td>
                          <td style={{ fontWeight: 500 }}>{alloc.student_name || "-"}</td>
                          <td className="mono-cell" style={{ textAlign: "center", color: "#0050b3", fontWeight: 700 }}>
                            {cell.seat_label}
                          </td>
                          <td style={{ borderBottom: "1px solid #94a3b8" }}>&nbsp;</td>
                        </tr>
                      );
                    })}
                  {roomPlan.allocated_count === 0 && (
                    <tr>
                      <td colSpan={5} style={{ textAlign: "center", padding: "32px", color: "#64748b" }}>
                        No students allocated to this classroom for this examination.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {activeView === "handover" && (() => {
            const allocatedCells = roomPlan.grid.flatMap(row => row).filter(cell => cell.allocation);

            return (
              <div style={{ marginTop: "16px" }}>
                {/* Information Header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                  <div style={{ fontSize: "12px", color: "#334155" }}>
                    <strong>Total Allocated:</strong> {roomPlan.allocated_count} Candidates
                  </div>
                </div>

                {/* Handover Table: S.no, Register Number, Name, Seatno, Status, Handover */}
                <table className="portal-table">
                  <thead>
                    <tr>
                      <th style={{ width: "60px", textAlign: "center" }}>S.no</th>
                      <th style={{ width: "220px", textAlign: "center" }}>Register Number</th>
                      <th>Name</th>
                      <th style={{ width: "90px", textAlign: "center" }}>Seatno</th>
                      <th style={{ width: "130px", textAlign: "center" }}>Status</th>
                      <th style={{ width: "160px", textAlign: "center" }}>Handover</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allocatedCells.map((cell, index) => {
                      const alloc = cell.allocation!;

                      return (
                        <tr key={cell.seat_label}>
                          <td style={{ textAlign: "center", fontWeight: 600 }}>{index + 1}</td>
                          <td className="mono-cell" style={{ textAlign: "center" }}>
                            {alloc.register_no}
                          </td>
                          <td style={{ fontWeight: 500 }}>{alloc.student_name || "-"}</td>
                          <td className="mono-cell" style={{ textAlign: "center", color: "#0050b3", fontWeight: 700 }}>
                            {cell.seat_label}
                          </td>
                          <td style={{ textAlign: "center" }}>&nbsp;</td>
                          <td style={{ textAlign: "center" }}>&nbsp;</td>
                        </tr>
                      );
                    })}
                    {roomPlan.allocated_count === 0 && (
                      <tr>
                        <td colSpan={6} style={{ textAlign: "center", padding: "32px", color: "#64748b" }}>
                          No students allocated to this classroom for this examination.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>

                {/* Handover Official Verification Sign-off Box */}
                <div style={{ marginTop: "32px", borderTop: "1px dashed #cbd5e1", paddingTop: "20px" }}>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "32px" }}>
                    <div style={{ border: "1px solid #e2e8f0", padding: "16px", borderRadius: "4px", backgroundColor: "#fafbfc" }}>
                      <div style={{ fontSize: "11px", fontWeight: 700, color: "#002f66" }}>HALL INVIGILATOR DECLARATION</div>
                      <div style={{ fontSize: "12px", color: "#334155", marginTop: "6px" }}>
                        I hereby certify that all answer booklets of present candidates have been collected, accounted for, and handed over.
                      </div>
                      <div style={{ marginTop: "32px", borderBottom: "1px solid #94a3b8", width: "100%" }}></div>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
                        <span>Invigilator Signature & Name</span>
                        <span>Date & Time</span>
                      </div>
                    </div>

                    <div style={{ border: "1px solid #e2e8f0", padding: "16px", borderRadius: "4px", backgroundColor: "#fafbfc" }}>
                      <div style={{ fontSize: "11px", fontWeight: 700, color: "#002f66" }}>EXAM CELL / COE OFFICE ACKNOWLEDGEMENT</div>
                      <div style={{ fontSize: "12px", color: "#334155", marginTop: "6px" }}>
                        Received answer booklets for Hall {roomPlan.classroom_name}. Packets verified against the student seating roster.
                      </div>
                      <div style={{ marginTop: "32px", borderBottom: "1px solid #94a3b8", width: "100%" }}></div>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
                        <span>Exam Cell Officer Signature</span>
                        <span>Receipt Stamp / Time</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })()}
        </DocumentCard>
      )}

    </div>
  );
};
