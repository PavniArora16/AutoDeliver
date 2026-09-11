const API_BASE_URL = "http://127.0.0.1:8000";


// ============================================================
// GET SAMPLE WAREHOUSE
// ============================================================

export async function getSampleWarehouse() {
  const response = await fetch(
    `${API_BASE_URL}/warehouse/sample`
  );

  if (!response.ok) {
    throw new Error("Failed to load sample warehouse");
  }

  return response.json();
}


// ============================================================
// RUN COMPLETE SIMULATION
// ============================================================

export async function runSimulation(
  warehouse: any
) {
  const response = await fetch(
    `${API_BASE_URL}/simulation/run`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },

      body: JSON.stringify({
        warehouse: warehouse
      })
    }
  );

  if (!response.ok) {
    throw new Error("Simulation failed");
  }

  return response.json();
}


// ============================================================
// GET ONE ROBOT AT ONE TIMESTEP
// ============================================================

export async function getSimulationStep(
  warehouse: any,
  robotId: number,
  timeStep: number
) {
  const response = await fetch(
    `${API_BASE_URL}/simulation/step`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },

      body: JSON.stringify({
        warehouse: warehouse,
        robot_id: robotId,
        time_step: timeStep
      })
    }
  );

  if (!response.ok) {
    throw new Error("Failed to get simulation step");
  }

  return response.json();
}


// ============================================================
// GET ALL ROBOTS AT ONE TIMESTEP
// ============================================================

export async function getSimulationState(
  warehouse: any,
  timeStep: number
) {
  const response = await fetch(
    `${API_BASE_URL}/simulation/state`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },

      body: JSON.stringify({
        warehouse: warehouse,
        time_step: timeStep
      })
    }
  );

  if (!response.ok) {
    throw new Error("Failed to get simulation state");
  }

  return response.json();
}


// ============================================================
// GET COMPLETE MULTI-ROBOT TIMELINE
// ============================================================

export async function getSimulationTimeline(
  warehouse: any
) {
  const response = await fetch(
    `${API_BASE_URL}/simulation/timeline`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },

      body: JSON.stringify({
        warehouse: warehouse
      })
    }
  );

  if (!response.ok) {
    throw new Error("Failed to get simulation timeline");
  }

  return response.json();
}

export async function runRecommendation(warehouse: any) {
  const response = await fetch(
    `${API_BASE_URL}/recommendation/run`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify({
        warehouse: warehouse,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Recommendation analysis failed");
  }

  return response.json();
}


export async function runFullAnalysis(warehouse: any) {
  const response = await fetch(
    `${API_BASE_URL}/analysis/run`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify(warehouse),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    console.error("FULL ANALYSIS ERROR:", response.status, errorText);
    throw new Error(
      `Full analysis failed (${response.status}): ${errorText}`
    );
  }

  return response.json();
}