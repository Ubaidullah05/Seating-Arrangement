import React, { useState, useEffect } from "react";
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
  ClipboardList,
  Loader2,
  AlertCircle,
  X
} from "lucide-react";

export const SeatingPlansPage: React.FC = () => {
  const [selectedExamId, setSelectedExamId] = useState<number | null>(null);
  const [selectedFloorId, setSelectedFloorId] = useState<number | null>(null);
  const [selectedClassroomId, setSelectedClassroomId] = useState<number | null>(null);
  const [activeView, setActiveView] = useState<"grid" | "table" | "notice">("grid");

  // Export download states
  const [downloading, setDownloading] = useState<"pdf" | "xlsx" | "notice-xlsx" | "notice-pdf" | null>(null);
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

  // Set default selections once loaded
  useEffect(() => {
    if (exams && exams.length > 0 && !selectedExamId) {
      setSelectedExamId(exams[0].id);
    }
  }, [exams, selectedExamId]);

  useEffect(() => {
    if (floors && floors.length > 0) {
      if (!selectedFloorId) setSelectedFloorId(floors[0].id);
      const targetFloor = floors.find(f => selectedFloorId ? f.id === selectedFloorId : true) || floors[0];
      if (targetFloor.classrooms.length > 0 && !selectedClassroomId) {
        setSelectedClassroomId(targetFloor.classrooms[0].id);
      }
    }
  }, [floors, selectedFloorId, selectedClassroomId]);

  const currentFloor = floors?.find(f => f.id === selectedFloorId) || floors?.[0];
  const currentExam = exams?.find(e => e.id === selectedExamId) || exams?.[0];

  // Fetch Room Plan
  const { data: roomPlan, isLoading: isPlanLoading, isError: isPlanError, error: planError } = useQuery({
    queryKey: ["room-plan", selectedExamId, selectedClassroomId],
    queryFn: () => (selectedExamId && selectedClassroomId) ? api.getRoomPlan(selectedExamId, selectedClassroomId) : null,
    enabled: !!(selectedExamId && selectedClassroomId && activeView !== "notice"),
  });

  // Fetch Notice Board data
  const { 
    data: noticeBoard, 
    isLoading: isNoticeLoading, 
    isError: isNoticeError, 
    error: noticeError 
  } = useQuery({
    queryKey: ["notice-board", selectedExamId],
    queryFn: () => selectedExamId ? api.getNoticeBoard(selectedExamId) : null,
    enabled: !!(selectedExamId && activeView === "notice"),
  });

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = async (type: "pdf" | "xlsx" | "notice-xlsx" | "notice-pdf") => {
    if (!selectedExamId) return;
    setDownloading(type);
    setDownloadError(null);
    try {
      if (type === "pdf") {
        await api.downloadExportPdf(selectedExamId);
      } else if (type === "xlsx") {
        await api.downloadExportXlsx(selectedExamId);
      } else if (type === "notice-xlsx") {
        await api.downloadExportNoticeBoardXlsx(selectedExamId);
      } else if (type === "notice-pdf") {
        await api.downloadExportNoticeBoardPdf(selectedExamId);
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
            Visual seating layout, invigilator attendance sheets and notice board rosters
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }} className="no-print">
          {selectedExamId && (
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
                title="Download Excel file preserving 16-digit register numbers as text"
              >
                {downloading === "xlsx" ? (
                  <Loader2 size={15} className="animate-spin" color="#16a34a" />
                ) : (
                  <FileSpreadsheet size={15} color="#16a34a" />
                )}
                {downloading === "xlsx" ? "Exporting Excel..." : "Export Excel (XLSX)"}
              </button>

              <button
                type="button"
                onClick={() => handleDownload("notice-xlsx")}
                disabled={!!downloading}
                className="btn-outline"
                style={{
                  fontSize: "12px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  cursor: downloading ? "not-allowed" : "pointer",
                  opacity: downloading && downloading !== "notice-xlsx" ? 0.6 : 1,
                  backgroundColor: "#ffffff",
                }}
                title="Download Notice Board Summary Excel"
              >
                {downloading === "notice-xlsx" ? (
                  <Loader2 size={15} className="animate-spin" color="#0050b3" />
                ) : (
                  <FileSpreadsheet size={15} color="#0050b3" />
                )}
                {downloading === "notice-xlsx" ? "Exporting Notice..." : "Notice Board (XLSX)"}
              </button>

              <button
                type="button"
                onClick={() => handleDownload("notice-pdf")}
                disabled={!!downloading}
                className="btn-outline"
                style={{
                  fontSize: "12px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  cursor: downloading ? "not-allowed" : "pointer",
                  opacity: downloading && downloading !== "notice-pdf" ? 0.6 : 1,
                  backgroundColor: "#ffffff",
                }}
                title="Download Notice Board Summary as Printable PDF"
              >
                {downloading === "notice-pdf" ? (
                  <Loader2 size={15} className="animate-spin" color="#b8892b" />
                ) : (
                  <FileDown size={15} color="#b8892b" />
                )}
                {downloading === "notice-pdf" ? "Exporting PDF..." : "Notice Board (PDF)"}
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
              value={selectedExamId || ""}
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

          {activeView !== "notice" && (
            <>
              {/* Floor Selector */}
              <div>
                <label style={{ display: "block", fontSize: "11px", fontWeight: 700, color: "#64748b", marginBottom: "4px" }}>
                  FLOOR LEVEL
                </label>
                <select
                  value={selectedFloorId || ""}
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
                  value={selectedClassroomId || ""}
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
            </>
          )}
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
              onClick={() => setActiveView("notice")}
              style={{
                padding: "7px 14px",
                border: "none",
                backgroundColor: activeView === "notice" ? "#0050b3" : "#ffffff",
                color: activeView === "notice" ? "#ffffff" : "#475569",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              <ClipboardList size={14} /> Notice Board Summary
            </button>
          </div>
        </div>
      </div>

      {/* Notice Board View Loading / Error / Empty / Content */}
      {activeView === "notice" && isNoticeLoading && (
        <div style={{ padding: "60px 20px", textAlign: "center", color: "#64748b", backgroundColor: "#ffffff", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
          <Loader2 size={32} className="animate-spin" style={{ margin: "0 auto 12px auto", color: "#0050b3" }} />
          <div style={{ fontWeight: 600, color: "#1e293b", fontSize: "15px" }}>Loading Notice Board Summary...</div>
          <div style={{ fontSize: "13px", marginTop: "4px" }}>Retrieving room allocations and register number ranges</div>
        </div>
      )}

      {activeView === "notice" && isNoticeError && (
        <div style={{ padding: "40px 20px", textAlign: "center", backgroundColor: "#ffffff", borderRadius: "6px", border: "1px solid #fecaca" }}>
          <AlertCircle size={36} color="#dc2626" style={{ margin: "0 auto 12px auto" }} />
          <div style={{ fontWeight: 700, color: "#991b1b", fontSize: "16px" }}>Unable to Load Notice Board</div>
          <div style={{ fontSize: "13px", color: "#64748b", marginTop: "6px" }}>
            {(noticeError as any)?.message || "Failed to retrieve notice board data. Please verify your connection or generate allocations."}
          </div>
        </div>
      )}

      {activeView === "notice" && !isNoticeLoading && !isNoticeError && noticeBoard && noticeBoard.rooms.length === 0 && (
        <div style={{ padding: "60px 20px", textAlign: "center", backgroundColor: "#ffffff", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
          <ClipboardList size={40} color="#94a3b8" style={{ margin: "0 auto 12px auto" }} />
          <div style={{ fontSize: "16px", fontWeight: 700, color: "#1e293b" }}>No Seating Allocations Found</div>
          <div style={{ fontSize: "13px", color: "#64748b", marginTop: "6px", maxWidth: "480px", margin: "6px auto 0 auto" }}>
            There are currently no classroom allocations generated for <strong>{noticeBoard.exam.name}</strong>.
            Please visit the <strong>Allocation Generator</strong> tab to compute seat assignments first.
          </div>
        </div>
      )}

      {activeView === "notice" && !isNoticeLoading && noticeBoard && noticeBoard.rooms.length > 0 && (
        <DocumentCard
          documentTitle="NOTICE BOARD SEATING SUMMARY"
          examName={noticeBoard.exam.name}
          infoItems={[
            { label: "EXAMINATION", value: noticeBoard.exam.name },
            { label: "EXAM DATE", value: noticeBoard.exam.exam_date },
            { label: "SESSION", value: noticeBoard.exam.session },
            { label: "TOTAL CANDIDATES", value: `${noticeBoard.total_students} Students` },
          ]}
        >
          <div style={{ marginTop: "16px" }}>
            <table className="portal-table">
              <thead>
                <tr>
                  <th style={{ width: "60px", textAlign: "center" }}>S.No</th>
                  <th>Floor Level</th>
                  <th style={{ width: "130px", textAlign: "center" }}>Hall / Room No</th>
                  <th style={{ width: "120px", textAlign: "center" }}>Total Seats</th>
                  <th style={{ width: "230px", textAlign: "center" }}>Starting Register No</th>
                  <th style={{ width: "230px", textAlign: "center" }}>Ending Register No</th>
                </tr>
              </thead>
              <tbody>
                {noticeBoard.rooms.map((rm, idx) => (
                  <tr key={idx}>
                    <td style={{ textAlign: "center" }}>{idx + 1}</td>
                    <td>{rm.floor_name}</td>
                    <td className="mono-cell" style={{ textAlign: "center", color: "#004a99" }}>
                      {rm.classroom_name}
                    </td>
                    <td style={{ textAlign: "center", fontWeight: 700 }}>{rm.student_count}</td>
                    <td className="mono-cell" style={{ textAlign: "center", color: "#0f172a" }}>
                      {rm.min_register_no || "-"}
                    </td>
                    <td className="mono-cell" style={{ textAlign: "center", color: "#0f172a" }}>
                      {rm.max_register_no || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </DocumentCard>
      )}

      {/* Classroom Plan View Loading / Error / Content */}
      {activeView !== "notice" && isPlanLoading && (
        <div style={{ padding: "60px 20px", textAlign: "center", color: "#64748b", backgroundColor: "#ffffff", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
          <Loader2 size={32} className="animate-spin" style={{ margin: "0 auto 12px auto", color: "#0050b3" }} />
          <div style={{ fontWeight: 600, color: "#1e293b", fontSize: "15px" }}>Loading Hall Seating Plan...</div>
          <div style={{ fontSize: "13px", marginTop: "4px" }}>Computing grid layout and seat assignments</div>
        </div>
      )}

      {activeView !== "notice" && isPlanError && (
        <div style={{ padding: "40px 20px", textAlign: "center", backgroundColor: "#ffffff", borderRadius: "6px", border: "1px solid #fecaca" }}>
          <AlertCircle size={36} color="#dc2626" style={{ margin: "0 auto 12px auto" }} />
          <div style={{ fontWeight: 700, color: "#991b1b", fontSize: "16px" }}>Unable to Load Seating Plan</div>
          <div style={{ fontSize: "13px", color: "#64748b", marginTop: "6px" }}>
            {(planError as any)?.message || "Failed to load room plan details."}
          </div>
        </div>
      )}

      {activeView !== "notice" && !isPlanLoading && roomPlan && currentExam && (
        <DocumentCard
          documentTitle={`SEATING ARRANGEMENT — HALL ${roomPlan.classroom_name}`}
          examName={currentExam.name}
          infoItems={[
            { label: "EXAMINATION", value: currentExam.name },
            { label: "EXAM DATE", value: currentExam.exam_date },
            { label: "SESSION", value: currentExam.session },
            { label: "FLOOR LEVEL", value: roomPlan.floor_name },
            { label: "HALL NO", value: roomPlan.classroom_name },
            { label: "TOTAL ALLOCATED", value: `${roomPlan.allocated_count} / ${roomPlan.capacity} Seats` },
            { label: "REG NO RANGE", value: `${roomPlan.min_register_no || "-"} to ${roomPlan.max_register_no || "-"}` },
            { label: "LAYOUT", value: `4 Columns × ${roomPlan.rows_per_column} Rows` },
          ]}
        >
          {activeView === "grid" ? (
            <SeatGrid grid={roomPlan.grid} />
          ) : (
            <div style={{ marginTop: "16px" }}>
              <table className="portal-table">
                <thead>
                  <tr>
                    <th style={{ width: "50px", textAlign: "center" }}>Seat</th>
                    <th style={{ width: "210px", textAlign: "center" }}>Register Number (16-Digit)</th>
                    <th>Candidate Name</th>
                    <th>Branch / Department</th>
                    <th style={{ width: "80px", textAlign: "center" }}>Sem</th>
                    <th style={{ width: "130px", textAlign: "center" }}>Candidate Signature</th>
                  </tr>
                </thead>
                <tbody>
                  {roomPlan.grid
                    .flatMap(row => row)
                    .filter(cell => cell.allocation)
                    .map((cell) => {
                      const alloc = cell.allocation!;
                      return (
                        <tr key={cell.seat_label}>
                          <td className="mono-cell" style={{ textAlign: "center", color: "#0050b3" }}>
                            {cell.seat_label}
                          </td>
                          <td className="mono-cell" style={{ textAlign: "center" }}>
                            {alloc.register_no}
                          </td>
                          <td>{alloc.student_name || "-"}</td>
                          <td>{alloc.branch || "-"}</td>
                          <td style={{ textAlign: "center" }}>{alloc.semester || "5"}</td>
                          <td style={{ borderBottom: "1px solid #94a3b8" }}>&nbsp;</td>
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
            </div>
          )}
        </DocumentCard>
      )}

    </div>
  );
};
