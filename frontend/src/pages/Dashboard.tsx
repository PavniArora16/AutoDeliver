import { useEffect, useState } from "react";
import {
  getSampleWarehouse,
  runFullAnalysis,
} from "../services/api";

type Position = {
  row: number;
  col: number;
};

type Robot = {
  id: number;
  start: Position;
  goal?: Position | null;
  battery_level?: number;
  battery_capacity?: number;
  status?: string;
};

type Warehouse = {
  name: string;
  rows: number;
  cols: number;
  grid: number[][];
  robots: Robot[];
  goals: Position[];
  charging_stations: Position[];
};

type AlgorithmResult = {
  found?: boolean;

  // Individual benchmark result
  path_cost?: number;
  nodes_expanded?: number;
  max_frontier_size?: number;
  runtime_ms?: number;

  // Backend benchmark summary
  average_path_cost?: number;
  average_path_length?: number;
  average_nodes_expanded?: number;
  average_frontier_size?: number;
  average_runtime_ms?: number;
  success_rate?: number;
};

type AnalysisData = {
  recommendation?: any;
  benchmark?: any;
  features?: any;
};

export default function Dashboard() {
  const [warehouse, setWarehouse] = useState<Warehouse | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [algorithm, setAlgorithm] = useState("A*");
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [lastRun, setLastRun] = useState<Date | null>(null);
  const [analysisMessage, setAnalysisMessage] = useState("");

  // --------------------------------------------------
  // LOAD REAL DATA FROM BACKEND
  // --------------------------------------------------

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const warehouseData = await getSampleWarehouse();
      setWarehouse(warehouseData);

      const analysisData = await runFullAnalysis(warehouseData);

      console.log("========== FULL ANALYSIS RESPONSE ==========");
      console.log(analysisData);

      console.log("BENCHMARK:", analysisData?.benchmark);

      console.log(
        "BENCHMARK RESULTS:",
        JSON.stringify(analysisData?.benchmark?.results, null, 2)
      );

      console.log(
        "BENCHMARK SUMMARY:",
        JSON.stringify(analysisData?.benchmark?.summary, null, 2)
      );

      console.log("RECOMMENDATION:", analysisData?.recommendation);
      console.log("MULTI AGENT:", analysisData?.multi_agent);
      console.log("============================================");

      setAnalysis(analysisData);

    } catch (err) {
      console.error(err);
      setError(
        "Could not connect to the AutoDeliver backend. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  }

  // --------------------------------------------------
  // HELPERS
  // --------------------------------------------------

  const getRecommendationName = () => {
    if (!analysis?.recommendation) return "—";

    const recommendation = analysis.recommendation;

    if (typeof recommendation === "string") {
      return recommendation;
    }

    return (
      recommendation.algorithm ||
      recommendation.recommended_algorithm ||
      recommendation.name ||
      "—"
    );
  };

  const getRecommendationReason = () => {
    if (!analysis?.recommendation) return "Run the analysis to generate a recommendation.";

    const recommendation = analysis.recommendation;

    if (typeof recommendation === "string") {
      return `The recommender selected ${recommendation} for this warehouse configuration.`;
    }

    return (
      recommendation.explanation ||
      recommendation.reason ||
      recommendation.message ||
      `The recommender selected ${getRecommendationName()} for this warehouse configuration.`
    );
  };

  const getAlgorithmResults = (): Record<string, AlgorithmResult> => {
    if (!analysis?.benchmark) return {};

    const benchmark = analysis.benchmark;

    // Backend returns algorithm-wise averages inside benchmark.summary
    if (benchmark.summary) {
      return benchmark.summary;
    }

    return {};
  };

  const getResultForAlgorithm = (algo: string): AlgorithmResult => {
    const results = getAlgorithmResults();

    const possibleNames =
      algo === "A*"
        ? ["A*", "astar", "a_star", "AStar"]
        : algo === "UCS"
          ? ["UCS", "ucs", "uniform_cost_search"]
          : ["GBFS", "gbfs", "greedy_best_first_search"];

    for (const name of possibleNames) {
      if (results[name]) {
        return results[name];
      }
    }

    return {};
  };

  const selectedResult = getResultForAlgorithm(algorithm);
  const pathCost = selectedResult.average_path_cost;
  const nodesExpanded = selectedResult.average_nodes_expanded;
  const frontierSize = selectedResult.average_frontier_size;
  const runtimeMs = selectedResult.average_runtime_ms;


  const formatNumber = (value: any, decimals = 2) => {
    if (value === undefined || value === null) return "—";

    const number = Number(value);

    if (Number.isNaN(number)) return "—";

    return number.toFixed(decimals);
  };

  const formatRuntime = (value: any) => {
    if (value === undefined || value === null) return "—";

    const number = Number(value);

    if (Number.isNaN(number)) return "—";

    return `${number.toFixed(2)} ms`;
  };

  const cellType = (row: number, col: number) => {
    if (!warehouse) return "normal";

    if (
      warehouse.robots.some(
        (robot) =>
          robot.start.row === row &&
          robot.start.col === col
      )
    ) {
      return "robot";
    }

    if (
      warehouse.goals.some(
        (goal) => goal.row === row && goal.col === col
      )
    ) {
      return "goal";
    }

    if (
      warehouse.charging_stations.some(
        (station) =>
          station.row === row &&
          station.col === col
      )
    ) {
      return "charger";
    }

    if (warehouse.grid[row][col] === -1) {
      return "obstacle";
    }

    return "normal";
  };

  // --------------------------------------------------
  // SIMULATION BUTTON
  // --------------------------------------------------

const runAnalysis = async () => {
  console.log("RUN ANALYSIS BUTTON CLICKED");

  if (!warehouse) {
    console.log("No warehouse data available");
    return;
  }

  try {
    setRunning(true);
    setError("");

    console.log("Sending request to backend...");

    const result = await runFullAnalysis(warehouse);

    console.log("Analysis response received:", result);

    setAnalysis(result);
    setLastRun(new Date());
  } catch (err) {
    console.error("ANALYSIS ERROR:", err);
    setError("Simulation/analysis failed.");
  } finally {
    setRunning(false);
  }
};

  // --------------------------------------------------
  // LOADING
  // --------------------------------------------------

  if (loading) {
    return (
      <div className="min-h-screen bg-[#070b14] text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🤖</div>
          <h2 className="text-xl font-semibold">
            Loading AutoDeliver...
          </h2>
          <p className="mt-2 text-sm text-slate-500">
            Connecting to the backend and running analysis
          </p>
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // ERROR
  // --------------------------------------------------

  if (error || !warehouse) {
    return (
      <div className="min-h-screen bg-[#070b14] text-white flex items-center justify-center p-6">
        <div className="max-w-md rounded-2xl border border-red-900/50 bg-[#0d1320] p-8 text-center">
          <div className="text-4xl mb-4">⚠️</div>

          <h2 className="text-xl font-bold">
            Backend Connection Error
          </h2>

          <p className="mt-3 text-sm text-slate-400">
            {error || "Warehouse data could not be loaded."}
          </p>

          <button
            onClick={loadDashboard}
            className="mt-6 rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold hover:bg-blue-500"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const recommendation = getRecommendationName();

  return (
    <div className="min-h-screen bg-[#070b14] text-white">

      {/* HEADER */}
      <header className="border-b border-slate-800 bg-[#0a0f1c] px-8 py-5">
        <div className="flex items-center justify-between">

          <div className="flex items-center gap-4">

            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-2xl shadow-lg shadow-blue-900/30">
              🤖
            </div>

            <div>
              <h1 className="text-xl font-bold">
                AutoDeliver
              </h1>

              <p className="text-xs text-slate-500">
                Intelligent Multi-Agent Warehouse Robot Simulator
              </p>
            </div>

          </div>

          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="h-2 w-2 rounded-full bg-green-500 shadow-lg shadow-green-500/50"></span>
            Backend Connected
          </div>

        </div>
      </header>


      {/* MAIN */}
      <main className="mx-auto grid max-w-[1450px] grid-cols-1 gap-6 p-6 xl:grid-cols-[1fr_370px]">

        {/* LEFT */}
        <section>

          <div className="mb-4 flex items-center justify-between">

            <div>
              <h2 className="text-lg font-semibold">
                Warehouse Simulation
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                {warehouse.rows} x {warehouse.cols} grid •{" "}
                {warehouse.robots.length} autonomous robots
              </p>
            </div>

            <span className="text-xs text-blue-400">
              ● LIVE GRID
            </span>

          </div>


          {/* GRID */}
          <div className="rounded-2xl border border-slate-800 bg-[#0d1320] p-5 shadow-2xl">

            <div className="mx-auto max-w-[850px]">

              <div
                className="grid overflow-hidden rounded-lg border border-slate-700"
                style={{
                  gridTemplateColumns: `repeat(${warehouse.cols}, minmax(0, 1fr))`,
                }}
              >

                {warehouse.grid.map((row, r) =>
                  row.map((_, c) => {

                    const type = cellType(r, c);

                    return (
                      <div
                        key={`${r}-${c}`}
                        className={`
                          aspect-square
                          border-b border-r border-slate-800
                          flex items-center justify-center
                          transition
                          ${type === "normal" ? "bg-[#111a29] hover:bg-[#17243a]" : ""}
                          ${type === "obstacle" ? "bg-slate-700" : ""}
                          ${type === "robot" ? "bg-blue-950 ring-1 ring-inset ring-blue-500" : ""}
                          ${type === "goal" ? "bg-green-950 ring-1 ring-inset ring-green-500" : ""}
                          ${type === "charger" ? "bg-yellow-950 ring-1 ring-inset ring-yellow-500" : ""}
                        `}
                      >

                        {type === "obstacle" && (
                          <div className="h-1/2 w-1/2 rounded bg-slate-500" />
                        )}

                        {type === "robot" && (
                          <span className="text-lg">🤖</span>
                        )}

                        {type === "goal" && (
                          <span className="text-lg">🎯</span>
                        )}

                        {type === "charger" && (
                          <span className="text-lg">⚡</span>
                        )}

                      </div>
                    );
                  })
                )}

              </div>

            </div>


            {/* LEGEND */}
            <div className="mt-5 flex flex-wrap gap-5 border-t border-slate-800 pt-4 text-[11px] text-slate-400">

              <span>⬜ Free</span>
              <span>⬛ Shelf / Obstacle</span>
              <span>🤖 Robot</span>
              <span>🎯 Goal</span>
              <span>⚡ Charging</span>

            </div>

          </div>


          {/* CONTROLS */}
          <div className="mt-5 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-[#0d1320] p-5">

            <div>

              <p className="mb-2 text-xs text-slate-400">
                Pathfinding Algorithm
              </p>

              <div className="flex gap-2">

                {["A*", "UCS", "GBFS"].map((algo) => (

                  <button
                    key={algo}
                    onClick={() => setAlgorithm(algo)}
                    className={`
                      rounded-lg border px-5 py-2 text-xs font-semibold transition
                      ${
                        algorithm === algo
                          ? "border-blue-500 bg-blue-600 text-white shadow-lg shadow-blue-900/30"
                          : "border-slate-700 bg-[#111827] text-slate-400 hover:border-blue-500"
                      }
                    `}
                  >
                    {algo}
                  </button>

                ))}

              </div>

            </div>


            <button
              onClick={runAnalysis}
              disabled={running}
              className="rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-3 text-xs font-semibold shadow-lg shadow-blue-900/30 transition hover:-translate-y-0.5 disabled:opacity-60"
            >
              {running ? "⏳ Running..." : "▶ Run Analysis"}
            </button>

            {lastRun && (
              <p className="mt-2 text-[10px] text-slate-500">
                Last analyzed: {lastRun.toLocaleTimeString()}
              </p>
            )}

            {analysisMessage && (
              <p className="mt-2 text-[10px] text-green-400">
                ✓ {analysisMessage}
              </p>
            )}

          </div>

        </section>


        {/* RIGHT SIDEBAR */}
        <aside className="space-y-4">

          {/* ALGORITHM */}
          <div className="rounded-2xl border border-slate-800 bg-[#0d1320] p-5">

            <div className="mb-4 flex justify-between text-xs text-slate-400">

              <span>Selected Algorithm</span>

              <span className="rounded bg-green-950 px-2 py-1 text-[9px] text-green-400">
                ACTIVE
              </span>

            </div>

            <div className="flex items-center gap-3">

              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-950 text-xl text-blue-400">
                ✦
              </div>

              <div>
                <h3 className="text-lg font-bold">
                  {algorithm}
                </h3>

                <p className="text-[10px] text-slate-500">
                  Pathfinding algorithm
                </p>
              </div>

            </div>

          </div>


          {/* METRICS */}
          <div className="rounded-2xl border border-slate-800 bg-[#0d1320] p-5">

            <div className="mb-4 flex justify-between">

              <span className="text-xs text-slate-400">
                Performance Metrics
              </span>

              <span className="text-[9px] text-blue-400">
                BACKEND
              </span>

            </div>


            <div className="grid grid-cols-2 gap-3">

              <Metric
                title="Path Cost"
                value={formatNumber(pathCost)}
                subtitle="average cost"
              />

              <Metric
                title="Nodes Expanded"
                value={formatNumber(nodesExpanded, 0)}
                subtitle="average search effort"
              />

              <Metric
                title="Max Frontier"
                value={formatNumber(frontierSize, 0)}
                subtitle="average frontier"
              />

              <Metric
                title="Runtime"
                value={formatRuntime(runtimeMs)}
                subtitle="average execution"
              />

            </div>

          </div>


          {/* RECOMMENDATION */}
          <div className="rounded-2xl border border-purple-900/60 bg-purple-950/20 p-5">

            <div className="flex items-center gap-3">

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-900/40 text-purple-300">
                ★
              </div>

              <div>

                <p className="text-[10px] text-purple-300/70">
                  AI Recommendation
                </p>

                <h3 className="text-lg font-bold text-purple-300">
                  {recommendation}
                </h3>

              </div>

            </div>

            <p className="mt-4 text-[11px] leading-5 text-slate-400">
              {getRecommendationReason()}
            </p>

          </div>


          {/* ROBOTS */}
          <div className="rounded-2xl border border-slate-800 bg-[#0d1320] p-5">

            <div className="mb-4 flex justify-between">

              <span className="text-xs text-slate-400">
                Multi-Agent Status
              </span>

              <span className="text-[9px] text-green-400">
                ● ONLINE
              </span>

            </div>


            <div className="space-y-2">

              {warehouse.robots.map((robot) => (

                <div
                  key={robot.id}
                  className="flex items-center rounded-xl border border-slate-800 bg-[#101827] p-3"
                >

                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-950">
                    🤖
                  </div>

                  <div className="ml-3 flex-1">

                    <p className="text-xs font-semibold">
                      Robot {robot.id}
                    </p>

                    <p className="text-[9px] text-slate-500">
                      Goal →{" "}
                      {robot.goal
                        ? `(${robot.goal.row}, ${robot.goal.col})`
                        : "Not assigned"}
                    </p>

                  </div>

                  <span className="text-[8px] text-green-400">
                    {robot.status || "READY"}
                  </span>

                </div>

              ))}

            </div>

          </div>


          {/* COMPARE */}
          <button
            onClick={() => {
              setAlgorithm("A*");
            }}
            className="w-full rounded-xl border border-slate-700 bg-[#111827] py-3 text-xs font-semibold text-slate-300 transition hover:border-blue-500 hover:text-white"
          >
            📊 Compare All Algorithms
          </button>


          <button
            onClick={loadDashboard}
            className="w-full py-2 text-xs text-slate-500 hover:text-slate-300"
          >
            ↻ Refresh Backend Analysis
          </button>

        </aside>

      </main>


      {/* FOOTER */}
      <footer className="border-t border-slate-800 px-8 py-4 text-[10px] text-slate-600">

        <div className="flex justify-between">

          <span>
            AutoDeliver • Intelligent Warehouse Optimization
          </span>

          <span>
            A* • UCS • GBFS • Multi-Agent Planning
          </span>

        </div>

      </footer>

    </div>
  );
}


// --------------------------------------------------
// METRIC COMPONENT
// --------------------------------------------------

function Metric({
  title,
  value,
  subtitle,
}: {
  title: string;
  value: string;
  subtitle: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-[#101827] p-3">

      <p className="text-[9px] text-slate-500">
        {title}
      </p>

      <p className="mt-1 text-xl font-bold">
        {value}
      </p>

      <p className="text-[8px] text-slate-600">
        {subtitle}
      </p>

    </div>
  );
}