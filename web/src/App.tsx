import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "./context/ThemeContext";
import { LanguageProvider } from "./context/LanguageContext";
import { ToastProvider } from "./context/ToastContext";
import { InspectionProvider } from "./context/InspectionContext";
import { Navbar } from "./components/Navbar";
import { Footer } from "./components/Footer";
import { RoadOverviewPage } from "./pages/RoadOverviewPage";
import { RoadScannerPage } from "./pages/RoadScannerPage";
import { RoadAuditReportPage } from "./pages/RoadAuditReportPage";
import { ReviewPage } from "./pages/ReviewPage";
import { BenchmarksPage } from "./pages/BenchmarksPage";
import { MethodPage } from "./pages/MethodPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const AppShell: React.FC = () => {
  const [isOffline, setIsOffline] = useState<boolean>(() => !navigator.onLine);

  useEffect(() => {
    const onOnline = () => setIsOffline(false);
    const onOffline = () => setIsOffline(true);

    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  return (
    <div className="relative min-h-screen flex flex-col font-sans antialiased bg-bg text-text selection:bg-accent selection:text-black transition-colors">
      {isOffline && (
        <div
          className="bg-accent/20 border-b border-accent/40 text-text text-xs py-2 px-4 text-center font-mono font-medium"
          role="status"
        >
          Device currently disconnected from network. Local offline inspection active.
        </div>
      )}

      <Navbar />

      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Routes>
          {/* 6 Core Functional Modules: Home | Detect | Records | Review | Benchmarks | Method */}
          <Route path="/" element={<RoadOverviewPage />} />
          <Route path="/detect" element={<RoadScannerPage />} />
          <Route path="/records" element={<RoadAuditReportPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/benchmarks" element={<BenchmarksPage />} />
          <Route path="/method" element={<MethodPage />} />

          {/* Legacy navigation aliases and clean redirects */}
          <Route path="/overview" element={<Navigate to="/" replace />} />
          <Route path="/scanner" element={<Navigate to="/detect" replace />} />
          <Route path="/scan" element={<Navigate to="/detect" replace />} />
          <Route path="/report" element={<Navigate to="/records" replace />} />
          <Route path="/dashboard" element={<Navigate to="/records" replace />} />
          <Route path="/maintenance" element={<Navigate to="/records" replace />} />
          <Route path="/priority-list" element={<Navigate to="/records" replace />} />
          <Route path="/about" element={<Navigate to="/method" replace />} />
          <Route path="/pipeline" element={<Navigate to="/method" replace />} />
          <Route path="/surveys" element={<Navigate to="/records" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <Footer />
    </div>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <LanguageProvider>
          <ToastProvider>
            <InspectionProvider>
              <BrowserRouter>
                <AppShell />
              </BrowserRouter>
            </InspectionProvider>
          </ToastProvider>
        </LanguageProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
