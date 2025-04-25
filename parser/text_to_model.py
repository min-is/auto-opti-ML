"""Parse LLM-generated text into optimization models."""
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class OptimizationModelParser:
    """Parse and extract optimization models from LLM-generated text."""
    
    def __init__(self):
        """Initialize the parser."""
        pass
        
    def extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from Markdown-formatted text."""

        pattern = r'``````'
        code_blocks = re.findall(pattern, text, re.DOTALL)
        
        if not code_blocks:

            logger.warning("No code blocks found, treating entire text as code")
            return [text]
            
        return code_blocks
    
    def parse_to_model(self, text: str, framework: str = "pyomo") -> Dict[str, Any]:
        """Parse LLM-generated text into a structured model representation."""
        code_blocks = self.extract_code_blocks(text)
        
        code = max(code_blocks, key=len)
        
        if framework.lower() == "pyomo":
            return self._parse_pyomo_model(code)
        elif framework.lower() == "pulp":
            return self._parse_pulp_model(code)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _parse_pyomo_model(self, code: str) -> Dict[str, Any]:
        """Parse a Pyomo model from code."""
        model_components = {
            "raw_code": code,
            "imports": [],
            "sets": [],
            "parameters": [],
            "variables": [],
            "objective": None,
            "constraints": [],
            "solver": None,
        }
        
        import_pattern = r'import\s+([^\n]+)'
        imports = re.findall(import_pattern, code)
        model_components["imports"] = [imp.strip() for imp in imports]
        
        model_pattern = r'model\s*=\s*pyo\.ConcreteModel\(\)'
        if re.search(model_pattern, code):
            model_components["model_type"] = "concrete"
        else:
            model_components["model_type"] = "abstract"
        
        
        return model_components
    
    def _parse_pulp_model(self, code: str) -> Dict[str, Any]:
        """Parse a PuLP model from code."""
        model_components = {
            "raw_code": code,
            "imports": [],
            "variables": [],
            "objective_sense": None,
            "constraints": [],
            "solver": None,
        }
        
        
        return model_components
