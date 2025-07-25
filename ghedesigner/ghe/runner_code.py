from pathlib import Path
import time
from ghedesigner.enums import BHPipeType
from ghedesigner.media import Soil, Grout, Pipe, GHEFluid
from pygfunction.boreholes import Borehole
from ghedesigner.ghe.simulation import SimulationParameters
from ghedesigner.ghe.multiple_ghe_hp_addition import MultiGHEHP
import pandas as pd
import json

# Timing
start_time = time.time()

# --- Load JSON ---
json_path = Path("find_design_bi_rectangle_single_u_tube.json")
with open(json_path, 'r') as f:
    data = json.load(f)

# Extract objects
fluid_data = data["fluid"]
soil_data = data["ground-heat-exchanger"]["ghe1"]["soil"]
grout_data = data["ground-heat-exchanger"]["ghe1"]["grout"]
pipe_data = data["ground-heat-exchanger"]["ghe1"]["pipe"]
borehole_data = data["ground-heat-exchanger"]["ghe1"]["borehole"]
geometric_data = data["ground-heat-exchanger"]["ghe1"]["geometric_constraints"]

fluid = GHEFluid(fluid_data["fluid_name"], fluid_data["concentration_percent"], fluid_data["temperature"])
r_in = pipe_data["inner_diameter"] / 2.0
r_out = pipe_data["outer_diameter"] / 2.0
s = pipe_data["shank_spacing"]
pipe_positions = Pipe.place_pipes(s, r_out, 1)
pipe = Pipe(pipe_positions, r_in, r_out, s, pipe_data["roughness"], pipe_data["conductivity"], pipe_data["rho_cp"])
soil = Soil(soil_data["conductivity"], soil_data["rho_cp"], soil_data["undisturbed_temp"])
grout = Grout(grout_data["conductivity"], grout_data["rho_cp"])
borehole = Borehole(100.0, borehole_data["buried_depth"], borehole_data["diameter"] / 2.0, 0.0, 0.0)

sim_params = SimulationParameters(num_months=12)
sim_params.set_design_heights(geometric_data["max_height"], geometric_data["min_height"])

# Dummy loads (non-zero so simulation produces data)
hourly_ground_loads = [5000.0] * 8760

# --- Run simulation ---
ghe_obj = MultiGHEHP(
    v_flow_system=0.5,
    b_spacing=5.0,
    bhe_type=BHPipeType.SINGLEUTUBE,
    fluid=fluid,
    borehole=borehole,
    pipe=pipe,
    grout=grout,
    soil=soil,
    sim_params=sim_params,
    hourly_extraction_ground_loads=hourly_ground_loads
)

print("Running detailed multi-GHE simulation...")
ghe_obj._simulate_detailed()

end_time = time.time()
print(f"Elapsed time: {end_time - start_time:.2f} seconds")