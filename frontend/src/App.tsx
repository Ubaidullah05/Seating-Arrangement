import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { AuthProvider } from "./auth";
import { useAuth } from "./authContext";
import { Sidebar } from "./components/Sidebar";
import { TopHeader } from "./components/TopHeader";
import { ChangePasswordModal } from "./components/ChangePasswordModal";

import { DashboardPage } from "./pages/DashboardPage";
import { UploadPage } from "./pages/UploadPage";
import { RoomsPage } from "./pages/RoomsPage";
import { GeneratePage } from "./pages/GeneratePage";
import { SeatingPlansPage } from "./pages/SeatingPlansPage";
import { SearchPage } from "./pages/SearchPage";
import { LoginPage } from "./pages/LoginPage";
import { StudentPortalPage } from "./pages/StudentPortalPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 1000 * 30, // 30s
    },
  },
});

/** Staff (faculty) shell: sidebar + header + main content, with auth guard. */
const FacultyLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [changePasswordOpen, setChangePasswordOpen] = useState(false);

  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "faculty") return <Navigate to="/student" replace />;

  return (
    <div style={{ display: "flex", minHeight: "100vh", backgroundColor: "#f4f6f9" }}>
      {/* Fixed Left Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        mobileOpen={mobileOpen}
        onNavigate={() => setMobileOpen(false)}
      />

      {/* Mobile sidebar backdrop */}
      <div
        className={`sidebar-overlay${mobileOpen ? " visible" : ""}`}
        onClick={() => setMobileOpen(false)}
        aria-hidden="true"
      />

      {/* Main Content Area */}
      <div
        className="portal-main-wrapper"
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          minWidth: 0,
          overflowX: "hidden",
        }}
      >
        {/* Top Header Bar */}
        <TopHeader
          onMenuClick={() => setMobileOpen((v) => !v)}
          onChangePassword={() => setChangePasswordOpen(true)}
        />

        {/* Dynamic Page Views */}
        <main style={{ flex: 1, paddingBottom: "48px" }}>{children}</main>
      </div>

      <ChangePasswordModal
        open={changePasswordOpen}
        onClose={() => setChangePasswordOpen(false)}
      />
    </div>
  );
};

const AppRoutes: React.FC = () => {
  const { user } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={
          user ? (
            <Navigate to={user.role === "student" ? "/student" : "/"} replace />
          ) : (
            <LoginPage />
          )
        }
      />

      <Route
        path="/student"
        element={
          user?.role === "student" ? (
            <StudentPortalPage />
          ) : (
            <Navigate to={user ? "/" : "/login"} replace />
          )
        }
      />

      <Route
        path="/"
        element={
          <FacultyLayout>
            <DashboardPage />
          </FacultyLayout>
        }
      />
      <Route
        path="/upload"
        element={
          <FacultyLayout>
            <UploadPage />
          </FacultyLayout>
        }
      />
      <Route
        path="/rooms"
        element={
          <FacultyLayout>
            <RoomsPage />
          </FacultyLayout>
        }
      />
      <Route
        path="/generate"
        element={
          <FacultyLayout>
            <GeneratePage />
          </FacultyLayout>
        }
      />
      <Route
        path="/plans"
        element={
          <FacultyLayout>
            <SeatingPlansPage />
          </FacultyLayout>
        }
      />
      <Route
        path="/search"
        element={
          <FacultyLayout>
            <SearchPage />
          </FacultyLayout>
        }
      />

      <Route
        path="*"
        element={
          <Navigate
            to={user ? (user.role === "student" ? "/student" : "/") : "/login"}
            replace
          />
        }
      />
    </Routes>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </QueryClientProvider>
    </AuthProvider>
  );
};

export default App;
