import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  GraduationCap,
  Briefcase,
  Calendar,
  CreditCard,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
} from "lucide-react";
import logoPng from "../assets/logo.png";
import { useAuth } from "../authContext";

type Tab = "student" | "faculty";

const REGISTER_RE = /^(?:\d{13}|\d{16})$/;
const DOB_RE = /^(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/\d{4}$/;
const FACULTY_EMAIL_RE = /^[A-Za-z0-9._%+-]+@jerusalemengg\.ac\.in$/;

function isValidDob(value: string): boolean {
  if (!DOB_RE.test(value)) return false;
  const [day, month, year] = value.split("/").map(Number);
  const date = new Date(year, month - 1, day);
  return (
    date.getFullYear() === year &&
    date.getMonth() === month - 1 &&
    date.getDate() === day
  );
}

function formatDob(value: string): string {
  const digits = value.replace(/\D/g, "").slice(0, 8);
  let formatted = digits.slice(0, 2);
  if (digits.length > 2) formatted += `/${digits.slice(2, 4)}`;
  if (digits.length > 4) formatted += `/${digits.slice(4, 8)}`;
  return formatted;
}

export const LoginPage: React.FC = () => {
  const [tab, setTab] = useState<Tab>("student");
  const [registerNo, setRegisterNo] = useState("");
  const [dob, setDob] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { loginStudent, loginFaculty } = useAuth();
  const navigate = useNavigate();

  const resetError = () => setError(null);

  const handleTabChange = (next: Tab) => {
    setTab(next);
    setError(null);
  };

  const handleStudentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    resetError();
    const reg = registerNo.trim().replace(/^'/, "");
    const dobValue = dob.trim();

    if (!REGISTER_RE.test(reg)) {
      setError("Register number must be exactly 13 or 16 numeric digits.");
      return;
    }
    if (!isValidDob(dobValue)) {
      setError("Date of birth must be in DD/MM/YYYY format (e.g. 15/08/2005). No other formats are accepted.");
      return;
    }

    setLoading(true);
    try {
      await loginStudent(reg, dobValue);
      navigate("/student", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleFacultySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    resetError();
    const mail = email.trim().toLowerCase();

    if (!FACULTY_EMAIL_RE.test(mail)) {
      setError("Please use your institutional email (e.g. acoe@jerusalemengg.ac.in).");
      return;
    }
    if (!password) {
      setError("Please enter your password.");
      return;
    }

    setLoading(true);
    try {
      await loginFaculty(mail, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo-wrap">
          <img src={logoPng} alt="Jerusalem College of Engineering" className="login-logo" />
        </div>

        <h1 className="login-title">Jerusalem College of Engineering</h1>
        <p className="login-subtitle">SINGLE WINDOW PORTAL</p>

        <div className="login-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={tab === "student"}
            className={`login-tab${tab === "student" ? " active" : ""}`}
            onClick={() => handleTabChange("student")}
          >
            <GraduationCap size={17} strokeWidth={2.2} />
            Student
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === "faculty"}
            className={`login-tab${tab === "faculty" ? " active" : ""}`}
            onClick={() => handleTabChange("faculty")}
          >
            <Briefcase size={17} strokeWidth={2.2} />
            Faculty &amp; Staff
          </button>
        </div>

        {tab === "student" ? (
          <form onSubmit={handleStudentSubmit} noValidate>
            <label className="login-field-label" htmlFor="login-register-no">
              Register Number
            </label>
            <div className="login-input-wrap">
              <CreditCard size={18} strokeWidth={2} />
              <input
                id="login-register-no"
                className="login-input"
                type="text"
                inputMode="numeric"
                autoComplete="username"
                maxLength={16}
                placeholder="2403310910421001"
                value={registerNo}
                onChange={(e) => {
                  setRegisterNo(e.target.value.replace(/[^\d]/g, ""));
                  resetError();
                }}
              />
            </div>

            <label className="login-field-label" htmlFor="login-dob">
              Date of Birth (DD/MM/YYYY)
            </label>
            <div className="login-input-wrap">
              <Calendar size={18} strokeWidth={2} />
              <input
                id="login-dob"
                className="login-input"
                type="text"
                inputMode="numeric"
                autoComplete="current-password"
                maxLength={10}
                placeholder="DD/MM/YYYY"
                value={dob}
                onChange={(e) => {
                  setDob(formatDob(e.target.value));
                  resetError();
                }}
              />
            </div>

            <button className="login-submit" type="submit" disabled={loading}>
              {loading ? "Signing in..." : "Sign in"}
              {!loading && <ArrowRight size={18} strokeWidth={2.5} />}
            </button>
          </form>
        ) : (
          <form onSubmit={handleFacultySubmit} noValidate>
            <label className="login-field-label" htmlFor="login-email">
              Institutional Email
            </label>
            <div className="login-input-wrap">
              <Mail size={18} strokeWidth={2} />
              <input
                id="login-email"
                className="login-input"
                type="email"
                autoComplete="username"
                placeholder="acoe@jerusalemengg.ac.in"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  resetError();
                }}
              />
            </div>

            <label className="login-field-label" htmlFor="login-password">
              Password
            </label>
            <div className="login-input-wrap">
              <Lock size={18} strokeWidth={2} />
              <input
                id="login-password"
                className="login-input"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  resetError();
                }}
              />
              <button
                type="button"
                className="login-input-eye"
                aria-label={showPassword ? "Hide password" : "Show password"}
                onClick={() => setShowPassword((v) => !v)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            <button className="login-submit" type="submit" disabled={loading}>
              {loading ? "Signing in..." : "Sign in"}
              {!loading && <ArrowRight size={18} strokeWidth={2.5} />}
            </button>
          </form>
        )}

        {error && (
          <div className="login-error" role="alert">
            {error}
          </div>
        )}
      </div>

      <div className="login-footer">© Jerusalem College of Engineering</div>
    </div>
  );
};

export default LoginPage;
