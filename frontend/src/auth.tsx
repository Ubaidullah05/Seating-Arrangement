import React, { useCallback, useEffect, useMemo, useState } from "react";
import type { AuthUser, LoginResponse } from "./types";
import { api } from "./api/client";
import { AuthContext } from "./authContext";

const STORAGE_KEY = "jce_auth";

function loadStoredUser(): AuthUser | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as AuthUser;
    if (!parsed?.token || !parsed?.role) return null;
    return parsed;
  } catch {
    return null;
  }
}

function toAuthUser(res: LoginResponse): AuthUser {
  return {
    role: res.role,
    token: res.access_token,
    email: res.email ?? null,
    mustChangePassword: res.must_change_password ?? false,
    student: res.student ?? null,
  };
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(() => loadStoredUser());

  useEffect(() => {
    if (user) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [user]);

  const loginStudent = useCallback(async (registerNo: string, dob: string) => {
    const res = await api.loginStudent(registerNo, dob);
    const next = toAuthUser(res);
    setUser(next);
    return next;
  }, []);

  const loginFaculty = useCallback(async (email: string, password: string) => {
    const res = await api.loginFaculty(email, password);
    const next = toAuthUser(res);
    setUser(next);
    return next;
  }, []);

  const changePassword = useCallback(async (oldPassword: string, newPassword: string) => {
    await api.changePassword(oldPassword, newPassword);
    setUser((prev) => (prev ? { ...prev, mustChangePassword: false } : prev));
  }, []);

  const markPasswordChanged = useCallback(() => {
    setUser((prev) => (prev ? { ...prev, mustChangePassword: false } : prev));
  }, []);

  const logout = useCallback(() => {
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loginStudent, loginFaculty, changePassword, markPasswordChanged, logout }),
    [user, loginStudent, loginFaculty, changePassword, markPasswordChanged, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
