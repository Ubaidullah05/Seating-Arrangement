export interface Student {
  id: number;
  register_no: string; // 16 digits
  name?: string | null;
  branch?: string | null;
  semester?: number | null;
  subject_code?: string | null;
}

export interface StudentCreate {
  register_no: string;
  name?: string | null;
  branch?: string | null;
  semester?: number | null;
  subject_code?: string | null;
}

export interface InvalidRow {
  row_number: number;
  raw_value?: string | null;
  reason: string;
}

export interface DuplicateRow {
  row_number: number;
  register_no: string;
  reason: string;
}

export interface UploadPreviewResponse {
  filename: string;
  total_rows: number;
  valid_count: number;
  invalid_count: number;
  duplicate_count: number;
  invalid_rows: InvalidRow[];
  duplicate_rows: DuplicateRow[];
  valid_preview: StudentCreate[];
}

export interface Classroom {
  id: number;
  floor_id: number;
  name: string;
  columns: number;
  rows_per_column: number;
  capacity: number;
  is_active: boolean;
}

export interface Floor {
  id: number;
  name: string;
  floor_number: number;
  classrooms: Classroom[];
}

export interface Exam {
  id: number;
  name: string;
  exam_date: string;
  session: string;
  seed?: number | null;
  created_at?: string;
  total_allocated: number;
}

export interface AllocationItem {
  id: number;
  student_id: number;
  register_no: string;
  student_name?: string | null;
  branch?: string | null;
  semester?: number | null;
  subject_code?: string | null;
  floor_name: string;
  classroom_id: number;
  classroom_name: string;
  seat_label: string;
}

export interface SeatGridCell {
  seat_label: string;
  column: string;
  row: number;
  allocation?: AllocationItem | null;
}

export interface RoomSeatingPlan {
  classroom_id: number;
  classroom_name: string;
  floor_name: string;
  floor_id: number;
  columns: number;
  rows_per_column: number;
  capacity: number;
  allocated_count: number;
  grid: SeatGridCell[][];
  min_register_no?: string | null;
  max_register_no?: string | null;
}

export interface NoticeBoardRoomRange {
  classroom_name: string;
  floor_name: string;
  student_count: number;
  min_register_no?: string | null;
  max_register_no?: string | null;
  ranges_summary: string;
}

export interface NoticeBoardResponse {
  exam: Exam;
  total_students: number;
  rooms: NoticeBoardRoomRange[];
}

export interface StudentSearchResult {
  found: boolean;
  student?: Student | null;
  allocation?: AllocationItem | null;
  exam_name?: string | null;
}

export interface DashboardStats {
  total_students: number;
  total_active_rooms: number;
  total_inactive_rooms: number;
  total_capacity: number;
  total_allocated: number;
  total_unallocated: number;
  active_exam_id?: number | null;
  active_exam_name?: string | null;
  active_exam_date?: string | null;
  active_exam_session?: string | null;
}
