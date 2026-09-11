import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import Simulator from "./pages/Simulator";

function App() {
  const [page, setPage] = useState<"dashboard" | "simulator">(
    "dashboard"
  );

  return (
    <div className="min-h-screen">

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0d1422] border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">

          {/* Logo */}
          <button
            onClick={() => setPage("dashboard")}
            className="text-xl font-bold text-white"
          >
            AutoDeliver
          </button>

          {/* Navigation buttons */}
          <div className="flex gap-2">

            <button
              onClick={() => setPage("dashboard")}
              className={`px-4 py-2 rounded-lg text-sm transition ${
                page === "dashboard"
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              }`}
            >
              Dashboard
            </button>

            <button
              onClick={() => setPage("simulator")}
              className={`px-4 py-2 rounded-lg text-sm transition ${
                page === "simulator"
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              }`}
            >
              Simulator
            </button>

          </div>

        </div>
      </nav>

      {/* Page */}
      <div className="pt-16">

        {page === "dashboard" ? (
          <Dashboard />
        ) : (
          <Simulator />
        )}

      </div>

    </div>
  );
}

export default App;