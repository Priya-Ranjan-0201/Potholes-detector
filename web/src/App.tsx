import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { ThemeProvider } from "./context/ThemeContext";
import { LanguageProvider } from "./context/LanguageContext";
import { ToastProvider } from "./context/ToastContext";
import { InspectionProvider } from "./context/InspectionContext";
import { Navbar } from "./components/Navbar";
import { Footer } from "./components/Footer";
import { RoadScannerPage } from "./pages/RoadScannerPage";
import { RoadAuditReportPage } from "./pages/RoadAuditReportPage";

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
    <div className="relative min-h-screen flex flex-col font-sans antialiased text-slate-900 dark:text-slate-100 bg-[var(--bg)] transition-colors">
      <AnimatePresence>
        {isOffline && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden bg-[#FF5A00]/20 border-b border-[#FF5A00]/40 text-[#FFD200] text-xs py-2 px-4 text-center font-mono font-bold"
            role="status"
          >
            Offline Notice: Device currently disconnected from network.
          </motion.div>
        )}
      </AnimatePresence>

      <Navbar />

      <main className="flex-1 w-full max-w-6xl mx-auto px-4 sm:px-6 py-6">
        <Routes>
          {/* Dedicated 2-Page Website Routes */}
          <Route path="/" element={<RoadScannerPage />} />
          <Route path="/scanner" element={<RoadScannerPage />} />
          <Route path="/report" element={<RoadAuditReportPage />} />

          {/* Legacy redirects all cleanly funneling into the 2 pages */}
          <Route path="/analyse" element={<Navigate to="/" replace />} />
          <Route path="/detect" element={<Navigate to="/" replace />} />
          <Route path="/surveys" element={<Navigate to="/" replace />} />
          <Route path="/priority-list" element={<Navigate to="/report" replace />} />
          <Route path="/benchmarks" element={<Navigate to="/" replace />} />
          <Route path="/about" element={<Navigate to="/" replace />} />
          <Route path="/dashboard" element={<Navigate to="/report" replace />} />
          <Route path="/maintenance" element={<Navigate to="/report" replace />} />
          <Route path="/login" element={<Navigate to="/" replace />} />
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
