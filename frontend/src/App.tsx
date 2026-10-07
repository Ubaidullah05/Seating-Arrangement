import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { Sidebar } from "./components/Sidebar";
import { TopHeader } from "./components/TopHeader";

import { DashboardPage } from "./pages/DashboardPage";
import { UploadPage } from "./pages/UploadPage";
import { RoomsPage } from "./pages/RoomsPage";
import { GeneratePage } from "./pages/GeneratePage";
import { SeatingPlansPage } from "./pages/SeatingPlansPage";
import { SearchPage } from "./pages/SearchPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 1000 * 30, // 30s
    },
  },
});

export const App: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div style={{ display: "flex", minHeight: "100vh", backgroundColor: "#f4f6f9" }}>
          {/* Fixed Left Sidebar */}
          <Sidebar
            collapsed={sidebarCollapsed}
            onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          />

          {/* Main Content Area */}
          <div 
            className="portal-main-wrapper"
            style={{ 
              flex: 1, 
              display: "flex", 
              flexDirection: "column", 
              minWidth: 0,
              overflowX: "hidden" 
            }}
          >
            {/* Top Header Bar */}
            <TopHeader />

            {/* Dynamic Page Views */}
            <main style={{ flex: 1, paddingBottom: "48px" }}>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/rooms" element={<RoomsPage />} />
                <Route path="/generate" element={<GeneratePage />} />
                <Route path="/plans" element={<SeatingPlansPage />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
