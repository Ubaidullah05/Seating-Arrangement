import { createContext, useContext } from "react";
import type { AuthUser } from "./types";

export interface AuthContextValue {
  user: AuthUser | null;
  loginStudent: (registerNo: string, dob: string) => Promise<AuthUser>;
  loginFaculty: (email: string, password: string) => Promise<AuthUser>;
  changePassword: (oldPassword: string, newPassword: string) => Promise<void>;
  markPasswordChanged: () => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
