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
  ArrowRight,
  Download
} from "lucide-react";

export const UploadPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewData, setPreviewData] = useState<UploadPreviewResponse | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [showColumnsGuide, setShowColumnsGuide] = useState<boolean>(true);

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

  const handleDownloadTemplate = () => {
    const templateUrl = api.getTemplateDownloadUrl();
    const link = document.createElement("a");
    link.href = templateUrl;
    link.setAttribute("download", "candidate_register_template.xlsx");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

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
    if (previewData) {
      const candidates = (previewData.all_valid && previewData.all_valid.length > 0)
        ? previewData.all_valid
        : previewData.valid_preview;
      if (candidates && candidates.length > 0) {
        commitMutation.mutate(candidates);
      }
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
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            onClick={handleDownloadTemplate}
            className="btn-gold"
            title="Download pre-formatted XLSX candidate template with 16-digit text format"
            style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
          >
            <Download size={15} /> Download Template (.xlsx)
          </button>
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
      </div>

      {/* Template Guide & Required Columns Card */}
      <div
        style={{
          backgroundColor: "#ffffff",
          border: "1px solid #d8e2ec",
          borderRadius: "6px",
          padding: "20px 24px",
          marginBottom: "24px",
          boxShadow: "0 2px 6px rgba(0, 31, 71, 0.04)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: showColumnsGuide ? "16px" : "0",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "6px",
                backgroundColor: "#f0f7ff",
                color: "#0050b3",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <FileSpreadsheet size={20} />
            </div>
            <div>
              <div style={{ fontFamily: "'Georgia', serif", fontSize: "15px", fontWeight: 700, color: "#002f66" }}>
                Excel Template Required & Supported Columns
              </div>
              <div style={{ fontSize: "12px", color: "#64748b" }}>
                Use the official .xlsx template with text-formatted cells for 16-digit register numbers
              </div>
            </div>
          </div>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <button
              onClick={handleDownloadTemplate}
              className="btn-blue"
              style={{ fontSize: "12px", padding: "6px 14px", display: "inline-flex", alignItems: "center", gap: "6px" }}
            >
              <Download size={14} /> Download Template (.xlsx)
            </button>
            <button
              onClick={() => setShowColumnsGuide(!showColumnsGuide)}
              className="btn-outline"
              style={{ fontSize: "12px", padding: "6px 12px" }}
            >
              {showColumnsGuide ? "Hide Guide" : "Show Columns Guide"}
            </button>
          </div>
        </div>

        {showColumnsGuide && (
          <div>
            <table className="portal-table" style={{ fontSize: "12px", marginTop: "12px" }}>
              <thead>
                <tr>
                  <th style={{ width: "170px" }}>Column Name</th>
                  <th style={{ width: "130px" }}>Requirement</th>
                  <th style={{ width: "230px" }}>Accepted Header Aliases</th>
                  <th style={{ width: "150px" }}>Data Type / Rule</th>
                  <th>Description / Example</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ backgroundColor: "#fefefe" }}>
                  <td style={{ fontWeight: 700, color: "#002f66" }}>Register Number</td>
                  <td>
                    <span
                      style={{
                        display: "inline-block",
                        backgroundColor: "#fee2e2",
                        color: "#991b1b",
                        fontSize: "10px",
                        fontWeight: 700,
                        padding: "2px 8px",
                        borderRadius: "3px",
                        letterSpacing: "0.5px"
                      }}
                    >
                      REQUIRED (*)
                    </span>
                  </td>
                  <td className="font-mono" style={{ fontSize: "11px", color: "#475569" }}>
                    Register Number, Reg No, register_no, regno, registration number
                  </td>
                  <td>
                    <span className="font-mono" style={{ fontWeight: 600, color: "#b91c1c" }}>
                      Text (@) — 16 digits
                    </span>
                  </td>
                  <td style={{ color: "#334155" }}>
                    Exact 16-digit numeric string (e.g. <code className="font-mono" style={{ fontWeight: 700 }}>2403310910421001</code>). Format cell as Text to prevent 15-digit Excel truncation.
                  </td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600, color: "#334155" }}>Student Name</td>
                  <td>
                    <span
                      style={{
                        display: "inline-block",
                        backgroundColor: "#f0fdf4",
                        color: "#166534",
                        fontSize: "10px",
                        fontWeight: 600,
                        padding: "2px 8px",
                        borderRadius: "3px"
                      }}
                    >
                      Optional
                    </span>
                  </td>
                  <td className="font-mono" style={{ fontSize: "11px", color: "#475569" }}>
                    Student Name, Name, student_name, candidate name
                  </td>
                  <td>Text string</td>
                  <td style={{ color: "#334155" }}>
                    Full legal student name (e.g. <span style={{ fontWeight: 500 }}>Aarav Rajan</span>).
                  </td>
                </tr>
                <tr style={{ backgroundColor: "#fefefe" }}>
                  <td style={{ fontWeight: 600, color: "#334155" }}>Branch</td>
                  <td>
                    <span
                      style={{
                        display: "inline-block",
                        backgroundColor: "#eff6ff",
                        color: "#1e40af",
                        fontSize: "10px",
                        fontWeight: 600,
                        padding: "2px 8px",
                        borderRadius: "3px"
                      }}
                    >
                      Recommended
                    </span>
                  </td>
                  <td className="font-mono" style={{ fontSize: "11px", color: "#475569" }}>
                    Branch, Dept, Department, Course, Program
                  </td>
                  <td>Text string</td>
                  <td style={{ color: "#334155" }}>
                    Academic department (e.g. <span style={{ fontWeight: 500 }}>B.E. Computer Science and Engineering</span> or <span style={{ fontWeight: 500 }}>CSE</span>). Enables hall interleaving!
                  </td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600, color: "#334155" }}>Semester</td>
                  <td>
                    <span
                      style={{
                        display: "inline-block",
                        backgroundColor: "#f1f5f9",
                        color: "#475569",
                        fontSize: "10px",
                        fontWeight: 600,
                        padding: "2px 8px",
                        borderRadius: "3px"
                      }}
                    >
                      Optional
                    </span>
                  </td>
                  <td className="font-mono" style={{ fontSize: "11px", color: "#475569" }}>
                    Semester, Sem, current semester
                  </td>
                  <td>Number (1–8)</td>
                  <td style={{ color: "#334155" }}>
                    Current semester number (e.g. <span style={{ fontWeight: 500 }}>5</span>).
                  </td>
                </tr>
                <tr style={{ backgroundColor: "#fefefe" }}>
                  <td style={{ fontWeight: 600, color: "#334155" }}>Course Code</td>
                  <td>
                    <span
                      style={{
                        display: "inline-block",
                        backgroundColor: "#f1f5f9",
                        color: "#475569",
                        fontSize: "10px",
                        fontWeight: 600,
                        padding: "2px 8px",
                        borderRadius: "3px"
                      }}
                    >
                      Optional
                    </span>
                  </td>
                  <td className="font-mono" style={{ fontSize: "11px", color: "#475569" }}>
                    Course Code, Subject Code, subject, subject_code
                  </td>
                  <td>Text code</td>
                  <td style={{ color: "#334155" }}>
                    Subject code for hall roster & notice boards (e.g. <code className="font-mono" style={{ fontWeight: 600 }}>JCS2501</code>).
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
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
          <div style={{ marginTop: "4px", fontWeight: 600, display: "flex", alignItems: "center", gap: "8px" }}>
            <span>💡 Tip: Format the register number column as <u>Text</u> before saving your Excel file, or download our ready-made template:</span>
            <button
              onClick={handleDownloadTemplate}
              style={{
                background: "none",
                border: "none",
                color: "#92400e",
                fontWeight: 700,
                cursor: "pointer",
                textDecoration: "underline",
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
                padding: 0,
                fontSize: "13px"
              }}
            >
              <Download size={13} /> candidate_register_template.xlsx
            </button>
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

        <div style={{ display: "flex", justifyContent: "center", gap: "12px", flexWrap: "wrap", alignItems: "center" }}>
          <label className="btn-blue" style={{ cursor: "pointer", display: "inline-flex" }}>
            <FileSpreadsheet size={16} /> Choose File (.xlsx / .csv)
            <input
              type="file"
              accept=".csv, .xlsx, .xls"
              style={{ display: "none" }}
              onChange={handleFileChange}
            />
          </label>

          <button
            type="button"
            onClick={handleDownloadTemplate}
            className="btn-outline"
            style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
          >
            <Download size={15} /> Download Template (.xlsx)
          </button>
        </div>

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
