import type {
  DashboardStats, Floor, Classroom, Exam, RoomSeatingPlan,
  NoticeBoardResponse, StudentSearchResult, UploadPreviewResponse,
  StudentCreate, LoginResponse, StudentSeat
} from "../types";

const API_BASE = "http://127.0.0.1:8000/api/v1";
const AUTH_STORAGE_KEY = "jce_auth";

function getStoredToken(): string | null {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed?.token ?? null;
  } catch {
    return null;
  }
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers);
  const token = getStoredToken();
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
  if (!res.ok) {
    const isLoginAttempt =
      endpoint.startsWith("/auth/student/login") || endpoint.startsWith("/auth/faculty/login");
    if (res.status === 401 && !isLoginAttempt) {
      // Session expired — drop it and send the user back to the login page
      localStorage.removeItem(AUTH_STORAGE_KEY);
      if (window.location.pathname !== "/login") {
        window.location.assign("/login");
      }
    }
    let errMessage = "Network request failed";
    try {
      const errData = await res.json();
      errMessage = errData.message || errData.detail || JSON.stringify(errData);
    } catch {
      errMessage = `HTTP error ${res.status}: ${res.statusText}`;
    }
    throw new Error(errMessage);
  }
  return res.json();
}

export const api = {
  // Authentication
  loginStudent: (register_no: string, password: string): Promise<LoginResponse> =>
    request<LoginResponse>("/auth/student/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ register_no, password }),
    }),

  loginFaculty: (email: string, password: string): Promise<LoginResponse> =>
    request<LoginResponse>("/auth/faculty/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    }),

  changePassword: (old_password: string, new_password: string): Promise<{ message: string }> =>
    request("/auth/faculty/change-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ old_password, new_password }),
    }),

  getMySeats: (): Promise<StudentSeat[]> => request<StudentSeat[]>("/auth/student/seats"),

  // Dashboard
  getDashboardStats: (): Promise<DashboardStats> => 
    request<DashboardStats>("/allocations/dashboard-stats"),

  // Classrooms & Floors
  getFloors: (): Promise<Floor[]> => 
    request<Floor[]>("/classrooms/floors"),

  updateClassroom: (id: number, data: { rows_per_column?: number; is_active?: boolean }): Promise<Classroom> => 
    request<Classroom>(`/classrooms/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),

  // Students & Uploads
  uploadStudentsPreview: async (file: File): Promise<UploadPreviewResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/students/upload-preview`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || err.message || "Failed to parse upload file");
    }
    return res.json();
  },

  commitStudents: (students: StudentCreate[]): Promise<{ message: string; imported_count: number }> => 
    request("/students/commit-upload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ students }),
    }),

  clearAllStudents: (): Promise<{ message: string }> => 
    request("/students/all", { method: "DELETE" }),

  searchStudents: (query: string, examId?: number | null): Promise<StudentSearchResult[]> => {
    const params = new URLSearchParams({ q: query });
    if (examId) params.append("exam_id", examId.toString());
    return request<StudentSearchResult[]>(`/students/search?${params.toString()}`);
  },

  // Exams
  getExams: (): Promise<Exam[]> => 
    request<Exam[]>("/exams"),

  // Allocation
  generateAllocation: (params: {
    name: string;
    exam_date: string;
    session: string;
    seed?: number | null;
    reshuffle?: boolean;
  }): Promise<{ message: string; exam_id: number; exam_name: string; allocated_count: number; seed: number }> => 
    request("/allocations/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    }),

  getRoomPlan: (examId: number, classroomId: number): Promise<RoomSeatingPlan> => 
    request<RoomSeatingPlan>(`/allocations/room-plan?exam_id=${examId}&classroom_id=${classroomId}`),

  getNoticeBoard: (examId: number): Promise<NoticeBoardResponse> => 
    request<NoticeBoardResponse>(`/allocations/notice-board?exam_id=${examId}`),

  // Export URLs
  getExportPdfUrl: (examId: number) => `${API_BASE}/export/pdf?exam_id=${examId}`,
  getExportXlsxUrl: (examId: number) => `${API_BASE}/export/xlsx?exam_id=${examId}`,
  getExportNoticeBoardXlsxUrl: (examId: number) => `${API_BASE}/export/notice-board-xlsx?exam_id=${examId}`,
  getExportNoticeBoardPdfUrl: (examId: number) => `${API_BASE}/export/notice-board-pdf?exam_id=${examId}`,
  getTemplateDownloadUrl: () => `${API_BASE}/students/template`,

  // Direct safe downloads via Fetch & Blob (handles CORS, errors, and prevents page redirect)
  downloadExportPdf: async (examId: number): Promise<void> => {
    return downloadFileFromUrl(`${API_BASE}/export/pdf?exam_id=${examId}`, `Seating_Plan_Exam_${examId}.pdf`);
  },

  downloadExportXlsx: async (examId: number): Promise<void> => {
    return downloadFileFromUrl(`${API_BASE}/export/xlsx?exam_id=${examId}`, `Seating_Plan_Exam_${examId}.xlsx`);
  },

  downloadExportNoticeBoardXlsx: async (examId: number): Promise<void> => {
    return downloadFileFromUrl(`${API_BASE}/export/notice-board-xlsx?exam_id=${examId}`, `Notice_Board_Exam_${examId}.xlsx`);
  },

  downloadExportNoticeBoardPdf: async (examId: number): Promise<void> => {
    return downloadFileFromUrl(`${API_BASE}/export/notice-board-pdf?exam_id=${examId}`, `Notice_Board_Exam_${examId}.pdf`);
  },

  downloadTemplate: async (): Promise<void> => {
    return downloadFileFromUrl(`${API_BASE}/students/template`, "candidate_register_template.xlsx");
  },
};

/**
 * Downloads a file cleanly by fetching it as a blob and triggering a download.
 * If the server returns an error JSON (e.g. 400 no allocations), extracts the error message
 * and throws it so UI components can display an error notification instead of redirecting.
 */
export async function downloadFileFromUrl(url: string, defaultFilename: string): Promise<void> {
  const res = await fetch(url);
  if (!res.ok) {
    let errMessage = "Download failed";
    try {
      const errData = await res.json();
      errMessage = errData.message || errData.detail || JSON.stringify(errData);
    } catch {
      errMessage = `Server error ${res.status}: ${res.statusText}`;
    }
    throw new Error(errMessage);
  }

  // Extract filename from Content-Disposition header if available
  let filename = defaultFilename;
  const disposition = res.headers.get("content-disposition") || res.headers.get("Content-Disposition");
  if (disposition) {
    const match = disposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';\n]+)["']?/i);
    if (match && match[1]) {
      filename = decodeURIComponent(match[1].trim());
    }
  }

  const blob = await res.blob();
  const blobUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = blobUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  setTimeout(() => {
    window.URL.revokeObjectURL(blobUrl);
  }, 1000);
}

