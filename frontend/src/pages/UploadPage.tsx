import React, { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";
import type { UploadPreviewResponse } from "../types";
import { 
  UploadCloud, 
  FileSpreadsheet, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Info,
  Trash2,
  ArrowRight
} from "lucide-react";

export const UploadPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewData, setPreviewData] = useState<UploadPreviewResponse | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  // Upload & preview mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => api.uploadStudentsPreview(file),
    onSuccess: (data) => {
      setPreviewData(data);
      setStatusMessage(null);
    },
    onError: (err: Error) => {
      setStatusMessage(`Upload failed: ${err.message}`);
    },
  });

  // Commit mutation
  const commitMutation = useMutation({
    mutationFn: (students: any[]) => api.commitStudents(students),
    onSuccess: (data) => {
      setStatusMessage(`Success: ${data.message}`);
      setPreviewData(null);
      setSelectedFile(null);
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    },
    onError: (err: Error) => {
      setStatusMessage(`Import failed: ${err.message}`);
    },
  });

  // Clear all mutation
  const clearMutation = useMutation({
    mutationFn: () => api.clearAllStudents(),
    onSuccess: (data) => {
      setStatusMessage(data.message);
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewData(null);
      setStatusMessage(null);
      uploadMutation.mutate(file);
    }
  };

  const handleCommit = () => {
    if (previewData && previewData.valid_preview) {
      commitMutation.mutate(previewData.valid_preview);
    }
  };

  return (
    <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "24px 28px" }}>
      {/* Page Title */}
      <div className="portal-page-header">
        <div>
          <h1 className="portal-page-title">Candidate Register Upload & Validation</h1>
          <div style={{ fontSize: "13px", color: "#64748b", marginTop: "4px" }}>
            Upload candidate files (.xlsx or .csv) for examination allocation
          </div>
        </div>
        <button
          onClick={() => {
            if (confirm("Are you sure you want to clear all candidate records? This will also remove any previous allocations.")) {
              clearMutation.mutate();
            }
          }}
          className="btn-outline"
          style={{ color: "#b91c1c", borderColor: "#fca5a5" }}
        >
          <Trash2 size={15} /> Clear All Students
        </button>
      </div>

      {/* Critical Format Guidance Tip Box */}
      <div
        style={{
          backgroundColor: "#fffbeb",
          border: "1px solid #fde68a",
          borderLeft: "5px solid #d97706",
          borderRadius: "4px",
          padding: "16px 20px",
          marginBottom: "24px",
          display: "flex",
          gap: "14px",
        }}
      >
        <Info size={22} color="#d97706" style={{ flexShrink: 0, marginTop: "2px" }} />
        <div style={{ fontSize: "13px", color: "#92400e", lineHeight: "1.5" }}>
          <strong>Important Register Number Precision Advisory:</strong>
          <div>
            Every candidate register number is a <strong>16-digit numeric text string</strong> (e.g., <code style={{ fontFamily: "monospace", fontWeight: 700 }}>2403310910421108</code>).
            Microsoft Excel standard numeric cells only hold 15 significant digits and may corrupt the 16th digit or convert to scientific notation (<code style={{ fontFamily: "monospace" }}>2.4033E+15</code>).
          </div>
          <div style={{ marginTop: "4px", fontWeight: 600 }}>
            💡 Tip: Format the register number column as <u>Text</u> before saving your Excel file.
          </div>
        </div>
      </div>

      {/* Upload Drop Zone Card */}
      <div
        style={{
          backgroundColor: "#ffffff",
          border: "2px dashed #94a3b8",
          borderRadius: "6px",
          padding: "36px 24px",
          textAlign: "center",
          marginBottom: "28px",
          transition: "border-color 0.2s",
        }}
      >
        <div
          style={{
            width: "56px",
            height: "56px",
            borderRadius: "50%",
            backgroundColor: "#f0f7ff",
            color: "#0050b3",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 14px auto",
          }}
        >
          <UploadCloud size={28} />
        </div>
        <h3 style={{ fontFamily: "'Georgia', serif", fontSize: "17px", color: "#0f172a", marginBottom: "6px" }}>
          Select Student Register File
        </h3>
        <p style={{ fontSize: "13px", color: "#64748b", marginBottom: "18px" }}>
          Upload .xlsx or .csv containing register numbers. Column headers like <em>"Register Number"</em>, <em>"Reg No"</em>, or <em>"register_no"</em> are recognized automatically.
        </p>

        <label className="btn-blue" style={{ cursor: "pointer", display: "inline-flex" }}>
          <FileSpreadsheet size={16} /> Choose File (.xlsx / .csv)
          <input
            type="file"
            accept=".csv, .xlsx, .xls"
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
        </label>

        {selectedFile && (
          <div style={{ marginTop: "12px", fontSize: "12px", color: "#334155", fontWeight: 600 }}>
            Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
          </div>
        )}

        {uploadMutation.isPending && (
          <div style={{ marginTop: "14px", color: "#0050b3", fontSize: "13px", fontWeight: 600 }}>
            Analyzing and validating 16-digit register numbers...
          </div>
        )}
      </div>

      {statusMessage && (
        <div
          style={{
            padding: "14px 18px",
            borderRadius: "4px",
            marginBottom: "20px",
            fontSize: "13px",
            backgroundColor: statusMessage.startsWith("Success") ? "#f0fdf4" : "#fef2f2",
            border: statusMessage.startsWith("Success") ? "1px solid #bbf7d0" : "1px solid #fecaca",
            color: statusMessage.startsWith("Success") ? "#166534" : "#991b1b",
          }}
        >
          {statusMessage}
        </div>
      )}

      {/* Validation Report & Preview */}
      {previewData && (
        <div
          style={{
            backgroundColor: "#ffffff",
            border: "1px solid #cbd5e1",
            borderRadius: "4px",
            padding: "24px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
          }}
        >
          {/* Summary Badges */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "14px",
              marginBottom: "24px",
            }}
          >
            <div style={{ padding: "12px", borderRadius: "4px", backgroundColor: "#f8fafc", border: "1px solid #e2e8f0" }}>
              <div style={{ fontSize: "11px", color: "#64748b", fontWeight: 700 }}>TOTAL ROWS PARSED</div>
              <div style={{ fontSize: "22px", fontWeight: 700, color: "#1e293b", marginTop: "4px" }}>
                {previewData.total_rows}
              </div>
            </div>

            <div style={{ padding: "12px", borderRadius: "4px", backgroundColor: "#f0fdf4", border: "1px solid #bbf7d0" }}>
              <div style={{ fontSize: "11px", color: "#166534", fontWeight: 700, display: "flex", alignItems: "center", gap: "4px" }}>
                <CheckCircle2 size={13} /> VALID 16-DIGIT ROWS
              </div>
              <div style={{ fontSize: "22px", fontWeight: 700, color: "#16a34a", marginTop: "4px" }}>
                {previewData.valid_count}
              </div>
            </div>

            <div style={{ padding: "12px", borderRadius: "4px", backgroundColor: "#fef2f2", border: "1px solid #fecaca" }}>
              <div style={{ fontSize: "11px", color: "#991b1b", fontWeight: 700, display: "flex", alignItems: "center", gap: "4px" }}>
                <XCircle size={13} /> INVALID ROWS
              </div>
              <div style={{ fontSize: "22px", fontWeight: 700, color: "#dc2626", marginTop: "4px" }}>
                {previewData.invalid_count}
              </div>
            </div>

            <div style={{ padding: "12px", borderRadius: "4px", backgroundColor: "#fffbeb", border: "1px solid #fde68a" }}>
              <div style={{ fontSize: "11px", color: "#92400e", fontWeight: 700, display: "flex", alignItems: "center", gap: "4px" }}>
                <AlertTriangle size={13} /> DUPLICATE ROWS
              </div>
              <div style={{ fontSize: "22px", fontWeight: 700, color: "#d97706", marginTop: "4px" }}>
                {previewData.duplicate_count}
              </div>
            </div>
          </div>

          {/* Invalid Rows Report */}
          {previewData.invalid_rows.length > 0 && (
            <div style={{ marginBottom: "24px" }}>
              <h4 style={{ fontFamily: "'Georgia', serif", fontSize: "14px", color: "#dc2626", marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
                <XCircle size={16} /> Rejected Rows Report ({previewData.invalid_rows.length} rows)
              </h4>
              <table className="portal-table" style={{ fontSize: "12px" }}>
                <thead>
                  <tr>
                    <th style={{ width: "80px" }}>Row #</th>
                    <th style={{ width: "220px" }}>Cell Value</th>
                    <th>Reason / Issue Detected</th>
                  </tr>
                </thead>
                <tbody>
                  {previewData.invalid_rows.map((inv, idx) => (
                    <tr key={idx}>
                      <td style={{ textAlign: "center", fontWeight: 700 }}>{inv.row_number}</td>
                      <td className="mono-cell" style={{ color: "#dc2626" }}>{inv.raw_value || "Empty"}</td>
                      <td style={{ color: "#991b1b" }}>{inv.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Duplicate Rows Report */}
          {previewData.duplicate_rows.length > 0 && (
            <div style={{ marginBottom: "24px" }}>
              <h4 style={{ fontFamily: "'Georgia', serif", fontSize: "14px", color: "#d97706", marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
                <AlertTriangle size={16} /> Duplicate Candidates Flagged ({previewData.duplicate_rows.length} rows)
              </h4>
              <table className="portal-table" style={{ fontSize: "12px" }}>
                <thead>
                  <tr>
                    <th style={{ width: "80px" }}>Row #</th>
                    <th style={{ width: "220px" }}>Register Number</th>
                    <th>Duplicate Detail</th>
                  </tr>
                </thead>
                <tbody>
                  {previewData.duplicate_rows.map((dup, idx) => (
                    <tr key={idx}>
                      <td style={{ textAlign: "center", fontWeight: 700 }}>{dup.row_number}</td>
                      <td className="mono-cell">{dup.register_no}</td>
                      <td style={{ color: "#92400e" }}>{dup.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Valid Preview Table */}
          {previewData.valid_preview.length > 0 && (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                <h4 style={{ fontFamily: "'Georgia', serif", fontSize: "14px", color: "#004a99", margin: 0 }}>
                  Valid Candidates Preview (Showing first {previewData.valid_preview.length} of {previewData.valid_count})
                </h4>
                <button
                  onClick={handleCommit}
                  disabled={commitMutation.isPending}
                  className="btn-gold"
                  style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
                >
                  <ArrowRight size={15} /> Commit & Import ({previewData.valid_count} Students)
                </button>
              </div>

              <table className="portal-table" style={{ fontSize: "12px" }}>
                <thead>
                  <tr>
                    <th style={{ width: "50px" }}>#</th>
                    <th style={{ width: "200px" }}>Register Number (16-Digit)</th>
                    <th>Student Name</th>
                    <th>Branch / Degree</th>
                    <th>Semester</th>
                    <th>Course Code</th>
                  </tr>
                </thead>
                <tbody>
                  {previewData.valid_preview.map((st, idx) => (
                    <tr key={idx}>
                      <td style={{ textAlign: "center" }}>{idx + 1}</td>
                      <td className="mono-cell" style={{ color: "#004a99" }}>{st.register_no}</td>
                      <td>{st.name || "-"}</td>
                      <td>{st.branch || "-"}</td>
                      <td style={{ textAlign: "center" }}>{st.semester || "-"}</td>
                      <td style={{ textAlign: "center" }}>{st.subject_code || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
