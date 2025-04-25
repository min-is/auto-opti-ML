# autooptiml/llm/prompt_engineering.py
"""Prompt engineering strategies for optimization problems."""
from typing import Dict, List, Any, Optional

class PromptTemplate:
    """Class for creating and managing prompt templates."""
    
    FRAMEWORKS = {
        "pyomo": {
            "description": "Pyomo is a Python-based open-source optimization modeling language.",
            "import_statement": "import pyomo.environ as pyo",
            "examples": [
                """
                # Example Pyomo model for a simple production problem
                import pyomo.environ as pyo
                
                # Create a concrete model
                model = pyo.ConcreteModel()
                
                # Define sets
                model.i = pyo.Set(initialize=['product1', 'product2'])
                
                # Define parameters
                model.profit = pyo.Param(model.i, initialize={'product1': 10, 'product2': 15})
                model.resource_usage = pyo.Param(model.i, initialize={'product1': 5, 'product2': 7})
                model.resource_limit = pyo.Param(initialize=100)
                
                # Define variables
                model.x = pyo.Var(model.i, domain=pyo.NonNegativeReals)
                
                # Define objective
                def obj_rule(model):
                    return sum(model.profit[i] * model.x[i] for i in model.i)
                model.objective = pyo.Objective(rule=obj_rule, sense=pyo.maximize)
                
                # Define constraints
                def resource_constraint_rule(model):
                    return sum(model.resource_usage[i] * model.x[i] for i in model.i) <= model.resource_limit
                model.resource_constraint = pyo.Constraint(rule=resource_constraint_rule)
                
                # Solve the model
                solver = pyo.SolverFactory('highs')
                results = solver.solve(model)
                
                # Display results
                print("Optimization completed successfully")
                for i in model.i:
                    print(f"{i}: {pyo.value(model.x[i])}")
                """
            ]
        },
        "pulp": {
            "description": "PuLP is an LP modeler written in Python, allowing for easy creation of linear programs.",
            "import_statement": "from pulp import *",
            "examples": [
                """
                # Example PuLP model for a simple production problem
                from pulp import *
                
                # Create the model
                model = LpProblem(name="production_problem", sense=LpMaximize)
                
                # Define the variables
                x1 = LpVariable(name="product1", lowBound=0)
                x2 = LpVariable(name="product2", lowBound=0)
                
                # Define the objective function
                model += 10 * x1 + 15 * x2, "Profit"
                
                # Define the constraints
                model += 5 * x1 + 7 * x2 <= 100, "Resource_Constraint"
                
                # Solve the model
                model.solve(solver=HIGHS(msg=False))
                
                # Display results
                print("Optimization completed successfully")
                print(f"product1: {value(x1)}")
                print(f"product2: {value(x2)}")
                """
            ]
        }
    }
    
    @classmethod
    def few_shot_optimization_prompt(cls, problem_description: str, framework: str = "pyomo") -> str:
        """Create a few-shot prompt for optimization problem formulation."""
        if framework not in cls.FRAMEWORKS:
            raise ValueError(f"Framework {framework} not supported. Choose from: {list(cls.FRAMEWORKS.keys())}")
        
        framework_info = cls.FRAMEWORKS[framework]
        
        template = f"""
        You are an expert in mathematical optimization and operations research.
        
        I need you to formulate an optimization problem using the {framework} framework.
        
        {framework_info["description"]}
        
        Please create a well-structured {framework} model with the following components:
        1. Proper import statements (e.g., {framework_info["import_statement"]})
        2. Clear variable definitions with appropriate domains
        3. Objective function (clearly indicate if maximizing or minimizing)
        4. All necessary constraints
        5. Solver configuration (preferably using HiGHS or Gurobi)
        6. Code to display the results
        
        Please add detailed comments explaining each component of the model.
        
        Here's an example of how to structure the model:
        {framework_info["examples"][0]}
        
        Now, please create a similar model for the following problem:
        
        {problem_description}
        
        Return only the Python code without any additional explanation.
        """
        
        return template
