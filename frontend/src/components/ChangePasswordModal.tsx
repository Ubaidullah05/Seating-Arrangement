import React, { useState } from "react";
import { X, Lock, Eye, EyeOff, KeyRound } from "lucide-react";
import { useAuth } from "../authContext";

interface ChangePasswordModalProps {
  open: boolean;
  onClose: () => void;
}

export const ChangePasswordModal: React.FC<ChangePasswordModalProps> = ({ open, onClose }) => {
  const { changePassword, user } = useAuth();
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showOld, setShowOld] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const handleClose = () => {
    setError(null);
    setSuccess(null);
    setOldPassword("");
    setNewPassword("");
    setConfirmPassword("");
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!oldPassword) {
      setError("Please enter your current password.");
      return;
    }
    if (newPassword.length < 6) {
      setError("New password must be at least 6 characters.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("New password and confirmation do not match.");
      return;
    }
    if (newPassword === oldPassword) {
      setError("New password must be different from the current password.");
      return;
    }

    setLoading(true);
    try {
      await changePassword(oldPassword, newPassword);
      setSuccess("Password changed successfully.");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => {
        handleClose();
      }, 900);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not change the password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-label="Change password">
      <div className="modal-card">
        <div className="modal-header">
          <div className="modal-title-wrap">
            <KeyRound size={18} />
            <h2>Change Password</h2>
          </div>
          <button type="button" className="modal-close" onClick={handleClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        {user?.mustChangePassword && (
          <div className="modal-notice">
            You are signed in with the default password. Please set a new password to secure your account.
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <label className="login-field-label" htmlFor="cp-old">
            Current Password
          </label>
          <div className="login-input-wrap">
            <Lock size={17} />
            <input
              id="cp-old"
              className="login-input"
              type={showOld ? "text" : "password"}
              autoComplete="current-password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              placeholder="••••••••"
            />
            <button
              type="button"
              className="login-input-eye"
              onClick={() => setShowOld((v) => !v)}
              aria-label="Toggle password visibility"
            >
              {showOld ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>

          <label className="login-field-label" htmlFor="cp-new">
            New Password
          </label>
          <div className="login-input-wrap">
            <Lock size={17} />
            <input
              id="cp-new"
              className="login-input"
              type={showNew ? "text" : "password"}
              autoComplete="new-password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Minimum 6 characters"
            />
            <button
              type="button"
              className="login-input-eye"
              onClick={() => setShowNew((v) => !v)}
              aria-label="Toggle password visibility"
            >
              {showNew ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>

          <label className="login-field-label" htmlFor="cp-confirm">
            Confirm New Password
          </label>
          <div className="login-input-wrap">
            <Lock size={17} />
            <input
              id="cp-confirm"
              className="login-input"
              type={showNew ? "text" : "password"}
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter new password"
            />
          </div>

          {error && (
            <div className="login-error" role="alert">
              {error}
            </div>
          )}
          {success && (
            <div className="modal-success" role="status">
              {success}
            </div>
          )}

          <button className="login-submit" type="submit" disabled={loading}>
            {loading ? "Updating..." : "Update Password"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChangePasswordModal;
