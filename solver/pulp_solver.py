"""Solve optimization models using PuLP."""
import os
import logging
import tempfile
from typing import Dict, Any

import pulp as pl

logger = logging.getLogger(__name__)

class PuLPSolver:
    """Solver for PuLP optimization models."""
    
    SOLVER_MAP = {
        "cbc": pl.PULP_CBC_CMD,
        "gurobi": pl.GUROBI_CMD,
        "glpk": pl.GLPK_CMD,
        "cplex": pl.CPLEX_CMD,
    }
    
    def __init__(self, solver_name: str = "cbc"):
        """Initialize the PuLP solver.
        
        Args:
            solver_name: Name of the solver to use (cbc, gurobi, glpk, cplex)
        """
        self.solver_name = solver_name.lower()
        if self.solver_name not in self.SOLVER_MAP:
            raise ValueError(f"Solver {solver_name} not supported. Choose from: {list(self.SOLVER_MAP.keys())}")
        self._check_solver_availability()

    def _check_solver_availability(self):
        """Check if the specified solver is available."""
        try:
            self.SOLVER_MAP[self.solver_name]().available()
        except pl.PulpSolverError:
            logger.warning(f"Solver {self.solver_name} not available. Using default CBC solver.")
            self.solver_name = "cbc"

    def solve_model(self, model_code: str) -> Dict[str, Any]:
        """Solve a PuLP model from its code representation.
        
        Args:
            model_code: String containing the PuLP model code
            
        Returns:
            Dictionary containing solution details
        """
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(model_code)
            temp_filename = f.name
        
        try:
            namespace = {
                'pl': pl,
                '__file__': temp_filename,
                'LpProblem': pl.LpProblem,
                'LpVariable': pl.LpVariable,
                'LpMaximize': pl.LpMaximize,
                'LpMinimize': pl.LpMinimize
            }
            
            exec(model_code, namespace)
            
            if 'model' not in namespace:
                raise ValueError("Model code did not create a 'model' variable")
            
            model = namespace['model']
            solver = self.SOLVER_MAP[self.solver_name](msg=False)
            model.solve(solver)
            
            return self._process_results(model)
            
        except Exception as e:
            logger.error(f"Error solving model: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            os.remove(temp_filename)
    
    def _process_results(self, model: pl.LpProblem) -> Dict[str, Any]:
        """Process solver results into a structured format.
        
        Args:
            model: Solved PuLP model instance
            
        Returns:
            Dictionary containing parsed solution details
        """
        solution = {
            "status": pl.LpStatus[model.status],
            "objective_value": pl.value(model.objective),
            "variables": {},
            "constraints": {},
            "solver_used": self.solver_name
        }
        

        for var in model.variables():
            solution["variables"][var.name] = {
                "value": var.varValue,
                "lower_bound": var.lowBound,
                "upper_bound": var.upBound,
                "category": var.cat
            }
        

        for name, constraint in model.constraints.items():
            solution["constraints"][name] = {
                "sense": "≤" if constraint.sense == pl.LpConstraintLE else 
                        "≥" if constraint.sense == pl.LpConstraintGE else "=",
                "rhs": constraint.constant,
                "expression": str(constraint)
            }
        
        return solution