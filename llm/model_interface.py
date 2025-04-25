import os
import logging
from typing import Dict, Any, Optional

import openai

logger = logging.getLogger(__name__)

class LLMInterface:

    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        """Initialize the LLM interface.
        
        Args:
            model_name: Name of the language model to use
            api_key: API key for accessing the language model service
        """
        self.model_name = model_name
        if api_key:
            openai.api_key = api_key
        elif "OPENAI_API_KEY" in os.environ:
            openai.api_key = os.environ["OPENAI_API_KEY"]
        else:
            raise ValueError("API key must be provided or set as OPENAI_API_KEY environment variable")
            
        logger.info(f"Initialized LLM interface with model: {model_name}")

    def generate_optimization_model(self, problem_description: str, framework: str = "pyomo") -> str:
        """Generate an optimization model from a problem description.
        
        Args:
            problem_description: Natural language description of the optimization problem
            framework: Optimization framework to use ('pyomo' or 'pulp')
            
        Returns:
            String containing the generated model code
        """
        prompt = self._build_prompt(problem_description, framework)
        logger.debug(f"Generated prompt: {prompt}")
        
        response = self._call_model(prompt)
        logger.info("Generated optimization model successfully")
        
        return response

    def _build_prompt(self, problem_description: str, framework: str) -> str:
        """Build a prompt for generating an optimization model."""
        return f"""
        You are an expert in mathematical optimization and operations research.
        
        Please convert the following optimization problem description into valid Python code using the {framework} framework.
        
        Include the objective function, constraints, variable definitions, and solver configuration.
        Make sure to structure the code clearly with appropriate comments for each section.
        Use appropriate variable names that reflect their meaning in the problem.
        
        Problem description:
        {problem_description}
        
        Return only the Python code without any additional explanation.
        """

    def _call_model(self, prompt: str) -> str:
        """Call the language model with the given prompt."""
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "You are an expert in optimization modeling."},
                          {"role": "user", "content": prompt}],
                temperature=0.2,  # Lower temperature for more deterministic outputs
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling LLM API: {e}")
            raise