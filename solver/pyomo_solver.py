"""Solve optimization models using Pyomo."""
import os
import logging
import tempfile
from typing import Dict, Any

import pyomo.environ as pyo

logger = logging.getLogger(__name__)

class PyomoSolver:
    """Solver for Pyomo optimization models."""
    
    def __init__(self, solver_name: str = "highs"):
        """Initialize the Pyomo solver."""
        self.solver_name = solver_name
        self._check_solver_availability()
    
    def _check_solver_availability(self):
        """Check if the specified solver is available."""
        if not pyo.SolverFactory(self.solver_name).available():
            logger.warning(f"Solver {self.solver_name} is not available. Results may be affected.")
    
    def solve_model(self, model_code: str) -> Dict[str, Any]:
        """Solve a Pyomo model from its code representation."""
        # Create a temporary file for the model
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(model_code)
            temp_filename = f.name
        
        try:

            namespace = {
                'pyo': pyo,
                '__file__': temp_filename,
            }
            
            exec(model_code, namespace)
            
            if 'model' not in namespace:
                raise ValueError("Model code did not create a 'model' variable")
            
            model = namespace['model']
            
            solver = pyo.SolverFactory(self.solver_name)
            results = solver.solve(model)
            
            solution = self._process_results(model, results)
            
            return solution
            
        except Exception as e:
            logger.error(f"Error solving model: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            os.remove(temp_filename)
    
    def _process_results(self, model: Any, results: Any) -> Dict[str, Any]:
        """Process solver results into a structured format."""
        solution = {
            "status": str(results.solver.status),
            "termination_condition": str(results.solver.termination_condition),
            "objective_value": None,
            "variables": {},
            "constraints": {},
            "solver_time": results.solver.time,
        }
        
        
        return solution