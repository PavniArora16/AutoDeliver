import { useEffect, useMemo, useState } from "react";
import {
  getSampleWarehouse,
  getSimulationTimeline,
} from "../services/api";


// ============================================================
// TYPES
// ============================================================

type Position = {
  row: number;
  col: number;
};

type Robot = {
  id: number;
  start: Position;
  goal: Position | null;
  battery_capacity: number;
  battery_level: number;
  energy_per_step: number;
  status: string;
  priority: number;
  deadline: number | null;
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

type SimulationStep = {
  time_step: number;
  position: Position;
  battery_level: number;
  battery_percentage: number;
  status: string;
  is_charging: boolean;
  is_goal_reached: boolean;
};

type RobotState = {
  robot_id: number;
  step: SimulationStep;
};

type TimelineStep = {
  time_step: number;
  robots: RobotState[];
};

type TimelineResponse = {
  success: boolean;
  makespan: number;
  timeline: TimelineStep[];
};


// ============================================================
// COMPONENT
// ============================================================

export default function Simulator() {

  const [warehouse, setWarehouse] =
    useState<Warehouse | null>(null);

  const [timeline, setTimeline] =
    useState<TimelineStep[]>([]);

  const [currentTime, setCurrentTime] =
    useState(0);

  const [isPlaying, setIsPlaying] =
    useState(false);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  // ==========================================================
  // LOAD WAREHOUSE + TIMELINE
  // ==========================================================

  useEffect(() => {

    async function loadSimulation() {

      try {

        setLoading(true);
        setError("");

        // Get warehouse from backend
        const warehouseData =
          await getSampleWarehouse();

        setWarehouse(warehouseData);

        // Get complete simulation timeline
        const timelineData: TimelineResponse =
          await getSimulationTimeline(
            warehouseData
          );

        if (!timelineData.success) {

          throw new Error(
            "Simulation could not be generated"
          );

        }

        setTimeline(
          timelineData.timeline
        );

        setCurrentTime(0);

      } catch (err) {

        console.error(err);

        setError(
          "Could not connect to the AutoDeliver backend."
        );

      } finally {

        setLoading(false);

      }
    }

    loadSimulation();

  }, []);


  // ==========================================================
  // AUTOMATIC ANIMATION
  // ==========================================================

  useEffect(() => {

    if (!isPlaying) {
      return;
    }

    if (timeline.length === 0) {
      return;
    }

    if (currentTime >= timeline.length - 1) {

      setIsPlaying(false);

      return;
    }

    const timer = setTimeout(() => {

      setCurrentTime(
        previous => previous + 1
      );

    }, 700);

    return () => clearTimeout(timer);

  }, [
    isPlaying,
    currentTime,
    timeline
  ]);


  // ==========================================================
  // CURRENT TIMELINE STATE
  // ==========================================================

  const currentState =
    timeline[currentTime];


  // ==========================================================
  // ROBOT STATES
  // ==========================================================

  const robotStates = useMemo(() => {

    if (!currentState) {
      return {};
    }

    const states: Record<
      number,
      SimulationStep
    > = {};

    for (
      const robot of currentState.robots
    ) {

      states[robot.robot_id] =
        robot.step;

    }

    return states;

  }, [currentState]);


  // ==========================================================
  // PLAY / PAUSE
  // ==========================================================

  function togglePlay() {

    if (
      timeline.length === 0
    ) {
      return;
    }

    if (
      currentTime >= timeline.length - 1
    ) {

      setCurrentTime(0);

    }

    setIsPlaying(
      previous => !previous
    );

  }


  // ==========================================================
  // RESET
  // ==========================================================

  function resetSimulation() {

    setIsPlaying(false);
    setCurrentTime(0);

  }


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {

    return (
      <div className="min-h-screen bg-[#070b14] text-white flex items-center justify-center">

        <div className="text-center">

          <div className="text-4xl mb-4">
            🤖
          </div>

          <h2 className="text-xl font-semibold">
            Connecting to AutoDeliver...
          </h2>

          <p className="text-gray-400 mt-2">
            Loading warehouse simulation
          </p>

        </div>

      </div>
    );

  }


  // ==========================================================
  // ERROR
  // ==========================================================

  if (error || !warehouse) {

    return (
      <div className="min-h-screen bg-[#070b14] text-white flex items-center justify-center">

        <div className="bg-[#111827] border border-red-500/30 rounded-xl p-8 text-center max-w-md">

          <div className="text-4xl mb-4">
            ⚠️
          </div>

          <h2 className="text-xl font-semibold">
            Backend Connection Failed
          </h2>

          <p className="text-gray-400 mt-3">
            {error}
          </p>

          <p className="text-gray-500 text-sm mt-4">
            Make sure FastAPI is running on
            port 8000.
          </p>

        </div>

      </div>
    );

  }


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div className="min-h-screen bg-[#070b14] text-white">

      {/* ====================================================
          HEADER
      ==================================================== */}

      <header className="border-b border-white/10 px-8 py-5">

        <div className="flex items-center justify-between">

          <div>

            <h1 className="text-2xl font-bold">
              AutoDeliver
            </h1>

            <p className="text-sm text-gray-400">
              Intelligent Multi-Agent Warehouse Robot Simulator
            </p>

          </div>

          <div className="flex items-center gap-2">

            <span className="w-2 h-2 rounded-full bg-green-400" />

            <span className="text-sm text-green-400">
              Backend Connected
            </span>

          </div>

        </div>

      </header>


      {/* ====================================================
          MAIN
      ==================================================== */}

      <main className="max-w-7xl mx-auto px-6 py-8">

        <div className="flex items-center justify-between mb-6">

          <div>

            <h2 className="text-xl font-semibold">
              {warehouse.name}
            </h2>

            <p className="text-sm text-gray-400">
              {warehouse.rows} × {warehouse.cols} warehouse
              {" • "}
              {warehouse.robots.length} robots
            </p>

          </div>

          <div className="text-right">

            <p className="text-xs text-gray-500">
              SIMULATION TIME
            </p>

            <p className="text-xl font-bold">
              {currentTime}
              <span className="text-gray-500">
                {" / "}
                {timeline.length > 0
                  ? timeline.length - 1
                  : 0}
              </span>
            </p>

          </div>

        </div>


        {/* ==================================================
            CONTENT GRID
        ================================================== */}

        <div className="grid lg:grid-cols-[1fr_320px] gap-6">


          {/* =================================================
              WAREHOUSE
          ================================================= */}

          <div className="bg-[#0d1422] border border-white/10 rounded-2xl p-5">

            <div className="flex items-center justify-between mb-5">

              <div>

                <h3 className="font-semibold">
                  Live Warehouse
                </h3>

                <p className="text-xs text-gray-500">
                  Backend-generated simulation
                </p>

              </div>

              <span className="text-xs text-blue-400">
                ● LIVE GRID
              </span>

            </div>


            {/* ==============================================
                GRID
            ============================================== */}

            <div
              className="grid border border-white/10 rounded-lg overflow-hidden"
              style={{
                gridTemplateColumns:
                  `repeat(${warehouse.cols}, minmax(0, 1fr))`
              }}
            >

              {warehouse.grid.map(
                (row, rowIndex) =>

                row.map(
                  (cell, colIndex) => {

                    const position = {
                      row: rowIndex,
                      col: colIndex
                    };

                    const robot =
                      warehouse.robots.find(
                        robot => {

                          const state =
                            robotStates[robot.id];

                          if (!state) {
                            return false;
                          }

                          return (
                            state.position.row === rowIndex &&
                            state.position.col === colIndex
                          );

                        }
                      );

                    const isGoal =
                      warehouse.goals.some(
                        goal =>
                          goal.row === rowIndex &&
                          goal.col === colIndex
                      );

                    const isCharging =
                      warehouse.charging_stations.some(
                        station =>
                          station.row === rowIndex &&
                          station.col === colIndex
                      );

                    const isObstacle =
                      cell === -1;

                    return (

                      <div
                        key={`${rowIndex}-${colIndex}`}
                        className={`
                          aspect-square
                          flex items-center justify-center
                          border-r border-b border-white/5
                          relative
                          transition-all duration-300
                          ${
                            isObstacle
                              ? "bg-[#334155]"
                              : "bg-[#101a2a]"
                          }
                        `}
                      >

                        {/* SHELF */}

                        {isObstacle && (

                          <div className="w-1/2 h-1/2 bg-slate-500 rounded-md" />

                        )}


                        {/* CHARGING STATION */}

                        {isCharging &&
                          !robot && (

                          <div className="text-lg">
                            ⚡
                          </div>

                        )}


                        {/* GOAL */}

                        {isGoal &&
                          !robot && (

                          <div className="text-lg">
                            🎯
                          </div>

                        )}


                        {/* ROBOT */}

                        {robot && (

                          <div
                            className={`
                              text-xl
                              z-10
                              transition-all duration-500
                              ${
                                robotStates[robot.id]
                                  ?.is_charging
                                  ? "scale-125"
                                  : ""
                              }
                            `}
                          >

                            🤖

                          </div>

                        )}

                      </div>

                    );

                  }

                )

              )}

            </div>


            {/* ==============================================
                LEGEND
            ============================================== */}

            <div className="flex flex-wrap gap-5 mt-5 text-xs text-gray-400">

              <span>
                ⬜ Free
              </span>

              <span>
                🟫 Shelf
              </span>

              <span>
                🤖 Robot
              </span>

              <span>
                🎯 Goal
              </span>

              <span>
                ⚡ Charging
              </span>

            </div>

          </div>


          {/* =================================================
              ROBOT STATUS
          ================================================= */}

          <div className="space-y-4">

            <div className="bg-[#0d1422] border border-white/10 rounded-2xl p-5">

              <h3 className="font-semibold mb-4">
                Multi-Agent Status
              </h3>


              <div className="space-y-3">

                {warehouse.robots.map(
                  robot => {

                    const state =
                      robotStates[robot.id];

                    if (!state) {
                      return null;
                    }

                    const battery =
                      state.battery_percentage;

                    return (

                      <div
                        key={robot.id}
                        className="bg-[#111a2b] rounded-xl p-4 border border-white/5"
                      >

                        <div className="flex items-center justify-between">

                          <div className="flex items-center gap-3">

                            <div className="w-9 h-9 rounded-lg bg-blue-500/10 flex items-center justify-center">
                              🤖
                            </div>

                            <div>

                              <p className="font-medium">
                                Robot {robot.id + 1}
                              </p>

                              <p className="text-xs text-gray-500">

                                ({state.position.row},{" "}
                                {state.position.col})

                              </p>

                            </div>

                          </div>

                          <span className="text-xs text-blue-400 capitalize">
                            {state.status}
                          </span>

                        </div>


                        {/* BATTERY */}

                        <div className="mt-4">

                          <div className="flex justify-between text-xs mb-1">

                            <span className="text-gray-500">
                              Battery
                            </span>

                            <span>
                              {battery}%
                            </span>

                          </div>

                          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">

                            <div
                              className="h-full bg-blue-500 transition-all duration-500"
                              style={{
                                width: `${battery}%`
                              }}
                            />

                          </div>

                        </div>


                        {/* GOAL */}

                        <div className="mt-3 text-xs">

                          {state.is_goal_reached ? (

                            <span className="text-green-400">
                              ✓ Goal reached
                            </span>

                          ) : state.is_charging ? (

                            <span className="text-yellow-400">
                              ⚡ Charging
                            </span>

                          ) : (

                            <span className="text-gray-500">
                              Moving toward goal
                            </span>

                          )}

                        </div>

                      </div>

                    );

                  }

                )}

              </div>

            </div>


            {/* =================================================
                SIMULATION CONTROLS
            ================================================= */}

            <div className="bg-[#0d1422] border border-white/10 rounded-2xl p-5">

              <h3 className="font-semibold mb-4">
                Simulation Controls
              </h3>

              <div className="flex gap-3">

                <button
                  onClick={togglePlay}
                  className="flex-1 bg-blue-600 hover:bg-blue-500 rounded-lg py-2.5 font-medium transition"
                >
                  {isPlaying
                    ? "⏸ Pause"
                    : "▶ Play"}
                </button>

                <button
                  onClick={resetSimulation}
                  className="px-4 bg-gray-800 hover:bg-gray-700 rounded-lg transition"
                >
                  ↺
                </button>

              </div>


              {/* TIMELINE SLIDER */}

              <input
                type="range"
                min="0"
                max={Math.max(
                  timeline.length - 1,
                  0
                )}
                value={currentTime}
                onChange={event =>
                  setCurrentTime(
                    Number(event.target.value)
                  )
                }
                className="w-full mt-5"
              />

            </div>

          </div>

        </div>

      </main>

    </div>

  );

}