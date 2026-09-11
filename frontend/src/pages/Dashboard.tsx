import { useState } from "react";

const warehouse = [
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
  [1, 1, -1, -1, -1, 1, 1, 1, 1, -1, 1, 1],
  [1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, 1],
  [1, -1, -1, 1, -1, 1, 1, 1, 1, -1, -1, 1],
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
  [1, -1, 1, 1, -1, -1, -1, 1, 1, 1, 1, 1],
  [1, -1, 1, 1, 1, 1, 1, 1, -1, -1, 1, 1],
  [1, 1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1],
  [1, 1, 1, -1, 1, 1, -1, -1, -1, 1, 1, 1],
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
];

const robots = [
  { id: 1, row: 0, col: 0, goal: "(0, 11)" },
  { id: 2, row: 9, col: 0, goal: "(9, 11)" },
];

const goals = [
  { row: 0, col: 11 },
  { row: 9, col: 11 },
];

const chargers = [
  { row: 4, col: 5 },
  { row: 9, col: 6 },
];

export default function Dashboard() {
  const [algorithm, setAlgorithm] = useState("A*");
  const [running, setRunning] = useState(false);

  const cellType = (row: number, col: number) => {
    if (robots.some((r) => r.row === row && r.col === col)) {
      return "robot";
    }

    if (goals.some((g) => g.row === row && g.col === col)) {
      return "goal";
    }

    if (chargers.some((c) => c.row === row && c.col === col)) {
      return "charger";
    }

    if (warehouse[row][col] === -1) {
      return "obstacle";
    }

    return "normal";
  };

  const runSimulation = () => {
    setRunning(true);

    setTimeout(() => {
      setRunning(false);
    }, 1200);
  };

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
            System Ready
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
                10 × 12 grid • 2 autonomous robots
              </p>
            </div>

            <span className="text-xs text-blue-400">
              ● LIVE GRID
            </span>

          </div>


          {/* GRID CARD */}
          <div className="rounded-2xl border border-slate-800 bg-[#0d1320] p-5 shadow-2xl">

            <div className="mx-auto max-w-[850px]">

              <div
                className="grid overflow-hidden rounded-lg border border-slate-700"
                style={{
                  gridTemplateColumns: "repeat(12, minmax(0, 1fr))",
                }}
              >

                {warehouse.map((row, r) =>
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
              onClick={runSimulation}
              className="rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-3 text-xs font-semibold shadow-lg shadow-blue-900/30 transition hover:-translate-y-0.5"
            >
              {running ? "⏳ Running..." : "▶ Run Simulation"}
            </button>

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
                  Heuristic guided search
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
                LIVE
              </span>

            </div>


            <div className="grid grid-cols-2 gap-3">

              <Metric title="Path Cost" value="20" subtitle="total cost" />

              <Metric
                title="Nodes Expanded"
                value={
                  algorithm === "GBFS"
                    ? "21"
                    : algorithm === "UCS"
                    ? "109"
                    : "93"
                }
                subtitle="search effort"
              />

              <Metric
                title="Max Frontier"
                value={
                  algorithm === "GBFS"
                    ? "15"
                    : algorithm === "UCS"
                    ? "12"
                    : "19"
                }
                subtitle="memory"
              />

              <Metric
                title="Runtime"
                value={
                  algorithm === "GBFS"
                    ? "0.20 ms"
                    : algorithm === "UCS"
                    ? "0.76 ms"
                    : "0.86 ms"
                }
                subtitle="execution"
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
                  GBFS
                </h3>

              </div>

            </div>

            <p className="mt-4 text-[11px] leading-5 text-slate-400">
              For this warehouse configuration, GBFS provides the fastest
              search while maintaining the same path cost.
            </p>

            <div className="mt-3 text-[10px] text-purple-300">
              ✓ Strong heuristic quality
            </div>

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

              {robots.map((robot) => (

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
                      Goal → {robot.goal}
                    </p>

                  </div>

                  <span className="text-[8px] text-green-400">
                    READY
                  </span>

                </div>

              ))}

            </div>

          </div>


          <button className="w-full rounded-xl border border-slate-700 bg-[#111827] py-3 text-xs font-semibold text-slate-300 transition hover:border-blue-500 hover:text-white">
            📊 Compare All Algorithms
          </button>

          <button className="w-full py-2 text-xs text-slate-500 hover:text-slate-300">
            ↑ Import Warehouse JSON
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