import React, { useEffect, useState } from "react";
import { LogOut, MapPin, CalendarDays, Armchair, DoorOpen } from "lucide-react";
import logoPng from "../assets/logo.png";
import { api } from "../api/client";
import { useAuth } from "../authContext";
import type { StudentSeat } from "../types";

function formatExamDate(dateStr: string, session: string): string {
  if (!dateStr) return "";
  const sessionLabel = session === "FN" ? "Forenoon" : session === "AN" ? "Afternoon" : session;
  const parts = dateStr.split("-");
  if (parts.length !== 3) return `${dateStr} · ${sessionLabel}`;
  const [d, m, y] = parts.map(Number);
  const date = new Date(y, m - 1, d);
  const formatted = date.toLocaleDateString("en-IN", {
    weekday: "short",
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
  return `${formatted} · ${sessionLabel}`;
}

export const StudentPortalPage: React.FC = () => {
  const { user, logout } = useAuth();
  const [seats, setSeats] = useState<StudentSeat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api
      .getMySeats()
      .then((data) => {
        if (!cancelled) setSeats(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load your exam hall.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const student = user?.student;

  return (
    <div className="student-portal">
      <header className="student-portal-header">
        <div className="student-portal-brand">
          <img src={logoPng} alt="Jerusalem College of Engineering" className="student-portal-logo" />
          <div className="student-portal-brand-text">
            <span className="student-portal-college">Jerusalem College of Engineering</span>
            <span className="student-portal-office">Office of the Controller of Examinations</span>
          </div>
        </div>
        <button className="student-portal-logout" onClick={logout} type="button">
          <LogOut size={16} />
          Logout
        </button>
      </header>

      <main className="student-portal-main">
        <div className="student-portal-welcome">
          <h1>My Exam Hall</h1>
          {student && (
            <p>
              <strong>{student.name || "Student"}</strong> · {student.register_no}
            </p>
          )}
        </div>

        {loading && <div className="student-portal-status">Loading your exam hall…</div>}

        {error && <div className="student-portal-error">{error}</div>}

        {!loading && !error && seats.length === 0 && (
          <div className="student-portal-empty">
            <DoorOpen size={44} strokeWidth={1.5} />
            <p>No exam hall has been allotted to you yet.</p>
            <span>Please check with the examination office once seat allocation is published.</span>
          </div>
        )}

        <div className="student-hall-list">
          {seats.map((seat) => (
            <article className="student-hall-card" key={`${seat.exam_id}-${seat.classroom_name}-${seat.seat_label}`}>
              <div className="student-hall-exam">
                <span className="student-hall-exam-name">{seat.exam_name}</span>
                <span className="student-hall-date">
                  <CalendarDays size={14} />
                  {formatExamDate(seat.exam_date, seat.session)}
                </span>
              </div>

              <div className="student-hall-highlight">
                <div className="student-hall-room">
                  <span className="student-hall-room-label">Examination Hall</span>
                  <span className="student-hall-room-value">{seat.classroom_name}</span>
                </div>
                <div className="student-hall-seat">
                  <span className="student-hall-room-label">Seat No.</span>
                  <span className="student-hall-seat-value">{seat.seat_label}</span>
                </div>
              </div>

              <div className="student-hall-meta">
                <span>
                  <MapPin size={14} />
                  {seat.floor_name}
                </span>
                <span>
                  <Armchair size={14} />
                  Seat {seat.seat_label} · Hall {seat.classroom_name}
                </span>
              </div>
            </article>
          ))}
        </div>
      </main>

      <footer className="student-portal-footer">
        © Jerusalem College of Engineering · Single Window Portal
      </footer>
    </div>
  );
};

export default StudentPortalPage;
