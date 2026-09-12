import { useEffect, useState } from "react";
import {  getSampleWarehouse,   runFullAnalysis,
} from "../services/api";


type Position = {
  row: number;
  col: number;
};

type Robot = {
  id: number;
  start: Position;
  goal?: Position | null;
  battery_capacity?: number;
  battery_level?: number;
  energy_per_step?: number;
  status?: string;
  priority?: number;
  deadline?: number | null;
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

type Tool =
  | "shelf"
  | "robot"
  | "goal"
  | "charger"
  | "erase";

export default function Editor() {
  const [warehouse, setWarehouse] = useState<Warehouse | null>(null);
  const [tool, setTool] = useState<Tool>("shelf");
  const [selectedCost, setSelectedCost] = useState(1);
  const [message, setMessage] = useState("");

  const [batteryLevel, setBatteryLevel] = useState(20);

  useEffect(() => {
    loadWarehouse();
  }, []);


  function updateWarehouse(newWarehouse: Warehouse) {
  setWarehouse(newWarehouse);
  localStorage.setItem(
    "autodeliver_warehouse",
    JSON.stringify(newWarehouse)
  );
}

    async function loadWarehouse() {
  try {
    const savedWarehouse =
      localStorage.getItem("autodeliver_warehouse");

    if (savedWarehouse) {
        const savedData = JSON.parse(savedWarehouse);

        setWarehouse(savedData);

        if (savedData.robots?.length > 0) {
            setBatteryLevel(
            savedData.robots[0].battery_level ?? 100
            );
        }

        return;
    }

    const data = await getSampleWarehouse();

    setWarehouse(data);

    if (data.robots?.length > 0) {
    setBatteryLevel(
        data.robots[0].battery_level ?? 100
    );
    }

    localStorage.setItem(
    "autodeliver_warehouse",
    JSON.stringify(data)
    );
  } catch (error) {
    console.error(error);
    setMessage("Could not load warehouse.");
  }
}

  function isPosition(list: Position[], row: number, col: number) {
    return list.some(
      (item) => item.row === row && item.col === col
    );
  }

  function removePosition(
    list: Position[],
    row: number,
    col: number
  ) {
    return list.filter(
      (item) => !(item.row === row && item.col === col)
    );
  }

  function handleCellClick(row: number, col: number) {
    if (!warehouse) return;

    const newWarehouse: Warehouse = {
      ...warehouse,
      grid: warehouse.grid.map((r) => [...r]),
      robots: [...warehouse.robots],
      goals: [...warehouse.goals],
      charging_stations: [...warehouse.charging_stations],
    };

    if (tool === "shelf") {
      newWarehouse.grid[row][col] =
        newWarehouse.grid[row][col] === -1
          ? selectedCost
          : -1;

      updateWarehouse(newWarehouse);
      return;
    }

    if (tool === "erase") {
      newWarehouse.grid[row][col] = 1;

      newWarehouse.goals = removePosition(
        newWarehouse.goals,
        row,
        col
      );

      newWarehouse.charging_stations = removePosition(
        newWarehouse.charging_stations,
        row,
        col
      );

      newWarehouse.robots = newWarehouse.robots.filter(
        (robot) =>
          !(
            robot.start.row === row &&
            robot.start.col === col
          )
      );

      updateWarehouse(newWarehouse);
      return;
    }

    // Don't place objects on shelves.
    if (newWarehouse.grid[row][col] === -1) {
      setMessage("Remove the shelf first.");
      return;
    }

    if (tool === "goal") {
      if (
        !isPosition(newWarehouse.goals, row, col)
      ) {
        newWarehouse.goals.push({ row, col });
      }

      updateWarehouse(newWarehouse);
      return;
    }

    if (tool === "charger") {
      if (
        !isPosition(
          newWarehouse.charging_stations,
          row,
          col
        )
      ) {
        newWarehouse.charging_stations.push({
          row,
          col,
        });
      }

      updateWarehouse(newWarehouse);
      return;
    }

    if (tool === "robot") {
    const existingRobotIndex = newWarehouse.robots.findIndex(
        (robot) =>
        robot.start.row === row &&
        robot.start.col === col
    );

    // If robot already exists, update its battery
    if (existingRobotIndex !== -1) {
        newWarehouse.robots[existingRobotIndex] = {
        ...newWarehouse.robots[existingRobotIndex],
        battery_level: batteryLevel,
        };

        updateWarehouse(newWarehouse);
        setMessage(
        `Robot ${newWarehouse.robots[existingRobotIndex].id} battery set to ${batteryLevel}%.`
        );
        return;
    }

    // Otherwise create a new robot
    const nextId =
        newWarehouse.robots.length === 0
        ? 1
        : Math.max(
            ...newWarehouse.robots.map(
                (robot) => robot.id
            )
            ) + 1;

    newWarehouse.robots.push({
        id: nextId,
        start: { row, col },
        goal: null,
        battery_capacity: 100,
        battery_level: batteryLevel,
        energy_per_step: 1,
        status: "idle",
        priority: 1,
        deadline: null,
    });

  updateWarehouse(newWarehouse);
}

  }

  function resetWarehouse() {
    loadWarehouse();
    setMessage("Sample warehouse restored.");
  }


  function importWarehouse(
  event: React.ChangeEvent<HTMLInputElement>
) {
  const file = event.target.files?.[0];

  if (!file) return;

  const reader = new FileReader();

  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target?.result as string);

      if (
        !data.rows ||
        !data.cols ||
        !Array.isArray(data.grid)
      ) {
        throw new Error("Invalid warehouse format");
      }

      if (
        data.grid.length !== data.rows ||
        data.grid.some(
          (row: number[]) => row.length !== data.cols
        )
      ) {
        throw new Error("Grid dimensions do not match");
      }

      updateWarehouse(data);
      setMessage("Warehouse imported successfully.");
    } catch (error) {
      console.error(error);
      setMessage("❌ Invalid warehouse JSON file.");
    }
  };

  reader.readAsText(file);

  // Allows selecting the same file again later
  event.target.value = "";
}

async function analyzeWarehouse() {
  if (!warehouse) return;

  try {
    setMessage("Running A*, UCS and GBFS analysis...");

    const result = await runFullAnalysis(warehouse);

    console.log("EDITOR ANALYSIS RESULT:", result);

    setMessage(
      `Analysis complete. Recommended algorithm: ${
        result.recommendation?.recommended_algorithm || "—"
      }`
    );
  } catch (error) {
    console.error(error);
    setMessage("❌ Analysis failed.");
  }
}



    function generateRandomWarehouse() {
  if (!warehouse) return;

  const rows = warehouse.rows;
  const cols = warehouse.cols;

  const grid = Array.from({ length: rows }, () =>
    Array.from({ length: cols }, () =>
      Math.random() < 0.20 ? -1 : 1
    )
  );

    grid[0][0] = 1;
    grid[rows - 1][cols - 1] = 1;
    grid[Math.floor(rows / 2)][Math.floor(cols / 2)] = 1;

const newWarehouse: Warehouse = {
  ...warehouse,
  grid,
  robots: [
    {
      id: 1,
      start: { row: 0, col: 0 },
      goal: {
        row: rows - 1,
        col: cols - 1,
      },
      battery_capacity: 100,
      battery_level: 100,
      energy_per_step: 1,
      status: "idle",
      priority: 1,
      deadline: null,
    },
  ],
  goals: [
    {
      row: rows - 1,
      col: cols - 1,
    },
  ],
  charging_stations: [
    {
      row: Math.floor(rows / 2),
      col: Math.floor(cols / 2),
    },
  ],
};

    updateWarehouse(newWarehouse);
    setMessage("Random warehouse generated.");
    }

  function exportWarehouse() {
    if (!warehouse) return;

    const blob = new Blob(
      [JSON.stringify(warehouse, null, 2)],
      { type: "application/json" }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "warehouse.json";
    link.click();

    URL.revokeObjectURL(url);

    setMessage("Warehouse exported.");
  }

  function getCellContent(row: number, col: number) {
    if (!warehouse) return "";

    const robot = warehouse.robots.find(
      (r) =>
        r.start.row === row &&
        r.start.col === col
    );

    if (robot) return "🤖";

    if (
      isPosition(warehouse.goals, row, col)
    ) {
      return "🎯";
    }

    if (
      isPosition(
        warehouse.charging_stations,
        row,
        col
      )
    ) {
      return "⚡";
    }

    if (warehouse.grid[row][col] === -1) {
      return "▦";
    }

    return "";
  }

  if (!warehouse) {
    return (
      <div className="min-h-screen bg-[#070b14] text-white flex items-center justify-center">
        Loading editor...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#070b14] text-white p-6">
      <div className="mx-auto max-w-7xl">

        <div className="mb-6">
          <h1 className="text-2xl font-bold">
            🏭 Warehouse Editor
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            Design your warehouse and configure robots,
            goals and charging stations.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1fr_280px]">

          {/* GRID */}

          <div className="rounded-2xl border border-slate-800 bg-[#0d1320] p-5">

            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="font-semibold">
                  {warehouse.name}
                </h2>

                <p className="text-xs text-slate-500">
                  {warehouse.rows} × {warehouse.cols}
                </p>
              </div>

              <span className="text-xs text-blue-400">
                EDIT MODE
              </span>
            </div>

            <div
              className="mx-auto grid max-w-[850px] overflow-hidden rounded-lg border border-slate-700"
              style={{
                gridTemplateColumns: `repeat(${warehouse.cols}, minmax(0, 1fr))`,
              }}
            >
              {warehouse.grid.map((row, r) =>
                row.map((_, c) => {

                  const isShelf =
                    warehouse.grid[r][c] === -1;

                  const robot =
                    warehouse.robots.some(
                      (item) =>
                        item.start.row === r &&
                        item.start.col === c
                    );

                  const goal =
                    isPosition(
                      warehouse.goals,
                      r,
                      c
                    );

                  const charger =
                    isPosition(
                      warehouse.charging_stations,
                      r,
                      c
                    );

                  return (
                    <button
                      key={`${r}-${c}`}
                      onClick={() =>
                        handleCellClick(r, c)
                      }
                      className={`
                        aspect-square
                        flex items-center justify-center
                        border-b border-r border-slate-800
                        text-lg transition
                        ${
                          isShelf
                            ? "bg-slate-700 hover:bg-slate-600"
                            : "bg-[#111a29] hover:bg-[#1b2a42]"
                        }
                        ${
                          robot
                            ? "bg-blue-950 ring-1 ring-inset ring-blue-500"
                            : ""
                        }
                        ${
                          goal
                            ? "bg-green-950 ring-1 ring-inset ring-green-500"
                            : ""
                        }
                        ${
                          charger
                            ? "bg-yellow-950 ring-1 ring-inset ring-yellow-500"
                            : ""
                        }
                      `}
                    >
                      {getCellContent(r, c)}
                    </button>
                  );
                })
              )}
            </div>

            <div className="mt-5 flex flex-wrap gap-4 text-xs text-slate-400">
              <span>▦ Shelf</span>
              <span>🤖 Robot</span>
              <span>🎯 Goal</span>
              <span>⚡ Charger</span>
              <span>⬜ Free</span>
            </div>
          </div>

          {/* CONTROLS */}

          <aside className="space-y-4">

            <div className="rounded-2xl border border-slate-800 bg-[#0d1320] p-5">

              <h2 className="mb-4 text-sm font-semibold">
                Editor Tools
              </h2>

              <div className="space-y-2">

                {(
                  [
                    ["shelf", "▦ Shelf"],
                    ["robot", "🤖 Robot"],
                    ["goal", "🎯 Goal"],
                    ["charger", "⚡ Charger"],
                    ["erase", "🧹 Erase"],
                  ] as [Tool, string][]
                ).map(([value, label]) => (

                  <button
                    key={value}
                    onClick={() => setTool(value)}
                    className={`
                      w-full rounded-lg border px-4 py-3
                      text-left text-xs font-semibold
                      transition
                      ${
                        tool === value
                          ? "border-blue-500 bg-blue-600 text-white"
                          : "border-slate-700 bg-[#111827] text-slate-400 hover:border-blue-500"
                      }
                    `}
                  >
                    {label}
                  </button>

                ))}

              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-[#0d1320] p-5">

              <label className="text-xs text-slate-400">
                Traversal Cost
              </label>

              <input
                type="number"
                min="1"
                max="20"
                value={selectedCost}
                onChange={(e) =>
                  setSelectedCost(
                    Number(e.target.value)
                  )
                }
                className="mt-2 w-full rounded-lg border border-slate-700 bg-[#111827] px-3 py-2 text-sm text-white outline-none"
              />

              <p className="mt-2 text-[10px] text-slate-500">
                Used when creating a new walkable cell.
              </p>
            </div>
            
            <div className="rounded-2xl border border-slate-800 bg-[#0d1320] p-5">
                <label className="text-xs text-slate-400">
                    Robot Battery Level (%)
                </label>

                <input
                    type="number"
                    min="0"
                    max="100"
                    value={batteryLevel}
                    onChange={(e) => {
                        const value = Math.max(
                        0,
                        Math.min(100, Number(e.target.value))
                        );

                        setBatteryLevel(value);

                        if (warehouse && warehouse.robots.length > 0) {
                        const newWarehouse: Warehouse = {
                            ...warehouse,
                            robots: warehouse.robots.map((robot, index) =>
                            index === 0
                                ? {
                                    ...robot,
                                    battery_level: value,
                                }
                                : robot
                            ),
                        };

                        updateWarehouse(newWarehouse);
                        }
                    }}
  className="mt-2 w-full rounded-lg border border-slate-700 bg-[#111827] px-3 py-2 text-sm text-white outline-none"
/>

                <p className="mt-2 text-[10px] text-slate-500">
                    Set to 20% or below to force charging before the task.
                </p>
                </div>


            <button
                onClick={analyzeWarehouse}
                className="w-full rounded-xl bg-gradient-to-r from-green-600 to-emerald-600 py-3 text-xs font-semibold text-white shadow-lg shadow-green-900/20 hover:-translate-y-0.5"
                >
                🧠 Run Warehouse Analysis
            </button>

            <button
                onClick={generateRandomWarehouse}
                className="w-full rounded-xl border border-purple-700 bg-purple-950/30 py-3 text-xs font-semibold text-purple-300 hover:bg-purple-900/40"
                >
                🎲 Generate Random Warehouse
            </button>
            
            <button
              onClick={resetWarehouse}
              className="w-full rounded-xl border border-slate-700 bg-[#111827] py-3 text-xs font-semibold text-slate-300 hover:border-blue-500"
            >
              ↻ Reset Sample Warehouse
            </button>

            <label className="block w-full cursor-pointer rounded-xl border border-slate-700 bg-[#111827] py-3 text-center text-xs font-semibold text-slate-300 hover:border-blue-500">
            📤 Import JSON

            <input
                type="file"
                accept=".json"
                onChange={importWarehouse}
                className="hidden"
            />
            </label>
            
            <button
              onClick={exportWarehouse}
              className="w-full rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 py-3 text-xs font-semibold"
            >
              📥 Export JSON
            </button>

            {message && (
              <p className="rounded-lg border border-green-900/50 bg-green-950/20 p-3 text-xs text-green-400">
                ✓ {message}
              </p>
            )}

            <div className="rounded-xl border border-slate-800 bg-[#101827] p-4 text-xs text-slate-400">
              <p>
                <strong className="text-white">
                  How to use:
                </strong>
              </p>

              <p className="mt-2">
                Select a tool and click cells on the grid.
              </p>
            </div>

          </aside>
        </div>
      </div>
    </div>
  );
}