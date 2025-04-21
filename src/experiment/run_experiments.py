"""
Experiment Runner for Code Improvement Evaluation

This script runs a series of experiments to evaluate different LLM models
on code improvement tasks across various stages with different parameters.
"""

import os
import json
import time
import argparse
import traceback
import statistics
import platform
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

# Use psutil for cross-platform memory measurement
import psutil

# LangChain imports
from langchain_community.llms import Ollama
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.callbacks import StdOutCallbackHandler
from langsmith import Client, traceable
from langsmith.run_helpers import traceable as langsmith_traceable

# Load environment variables
load_dotenv()

# Set up LangSmith client if environment variables are set
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

# Initialize LangSmith client if API key is available
langsmith_client = Client(api_key=LANGCHAIN_API_KEY) if LANGCHAIN_API_KEY else None

# Global variable to control which stage to execute
CURRENT_STAGE = "baseline"  # Options: "baseline", "stage1", "stage2", "stage3", "stage4"

# Path to the test code containing find_duplicates function
TEST_CODE_PATH = Path(__file__).parents[2] / "test_code.py"

# Path to the evaluation stages configuration
EVAL_STAGES_PATH = Path(__file__).parent / "eval_stages.json"

# Path to store experiment results
RESULTS_DIR = Path(__file__).parent / "results"


def load_stages_config() -> Dict[str, Any]:
    """Load the experiment stages configuration from JSON file."""
    with open(EVAL_STAGES_PATH, "r") as f:
        return json.load(f)


def extract_code_context(code_path: Path, function_name: str, context_line_count: int) -> Dict[str, str]:
    """
    Extract the function code and surrounding context from a Python file.
    
    Args:
        code_path: Path to the Python file
        function_name: Name of the function to extract
        context_line_count: Number of lines of context to include before and after
        
    Returns:
        Dictionary with code_to_improve, context_before_code, and context_after_code
    """
    with open(code_path, "r") as f:
        lines = f.readlines()
    
    # Find the function definition
    function_start_line = -1
    function_end_line = -1
    in_function = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        if line.startswith(f"def {function_name}(") and not in_function:
            function_start_line = i
            in_function = True
            # Determine the indentation level of the function body
            for j, next_line in enumerate(lines[i+1:], start=i+1):
                if next_line.strip() and not next_line.strip().startswith("#"):
                    indent_level = len(next_line) - len(next_line.lstrip())
                    break
        elif in_function:
            # Check if we've exited the function (less indentation or next function)
            if (line.strip() and not line.strip().startswith("#") and 
                (len(line) - len(line.lstrip()) < indent_level or line.startswith("def "))):
                function_end_line = i - 1
                break
    
    # If we reached the end of the file while still in the function
    if in_function and function_end_line == -1:
        function_end_line = len(lines) - 1
    
    if function_start_line == -1:
        raise ValueError(f"Function '{function_name}' not found in {code_path}")
    
    # Extract the function code and context
    context_before_start = max(0, function_start_line - context_line_count)
    context_after_end = min(len(lines) - 1, function_end_line + context_line_count)
    
    code_to_improve = "".join(lines[function_start_line:function_end_line + 1])
    context_before_code = "".join(lines[context_before_start:function_start_line])
    context_after_code = "".join(lines[function_end_line + 1:context_after_end + 1])
    
    return {
        "code_to_improve": code_to_improve,
        "context_before_code": context_before_code,
        "context_after_code": context_after_code
    }


@langsmith_traceable(name="setup_model", project_name=LANGCHAIN_PROJECT)
def setup_model(model_name: str, temperature: float) -> Ollama:
    """Set up and return an Ollama model with the specified parameters."""
    return Ollama(
        model=model_name,
        temperature=temperature,
        num_gpu=1,
    )


@langsmith_traceable(name="create_prompt_chain", project_name=LANGCHAIN_PROJECT)
def create_prompt_chain(model: Ollama, prompt_template: str) -> LLMChain:
    """Create a prompt chain with the specified model and template."""
    prompt = PromptTemplate.from_template(prompt_template)
    return LLMChain(llm=model, prompt=prompt)


def measure_execution_time(func, *args, **kwargs):
    """Measure the execution time of a function."""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time


@langsmith_traceable(name="measure_memory_usage", project_name=LANGCHAIN_PROJECT)
def measure_memory_usage(func, *args, **kwargs):
    """Measure the memory usage of a function in a cross-platform way."""
    # Get the current process
    process = psutil.Process(os.getpid())
    
    # Get the initial memory usage (in KB)
    initial_memory = process.memory_info().rss / 1024
    
    # Run the function
    result = func(*args, **kwargs)
    
    # Get the final memory usage (in KB)
    final_memory = process.memory_info().rss / 1024
    
    # Calculate the difference (in KB)
    memory_used = final_memory - initial_memory
    
    return result, memory_used


def extract_code_from_response(response: str) -> str:
    """Extract code blocks from a markdown-formatted response."""
    import re
    
    # Look for Python code blocks in markdown format
    code_blocks = re.findall(r'```(?:python)?\s*([\s\S]*?)```', response)
    
    if code_blocks:
        # Return the largest code block (most likely the improved function)
        return max(code_blocks, key=len).strip()
    
    return ""


@langsmith_traceable(name="evaluate_code_performance", project_name=LANGCHAIN_PROJECT)
def evaluate_code_performance(original_code: str, improved_code: str, function_name: str) -> Dict[str, Any]:
    """
    Evaluate the performance of the original and improved code.
    
    Args:
        original_code: The original function code
        improved_code: The improved function code
        function_name: The name of the function
        
    Returns:
        Dictionary with performance metrics
    """
    # Create a temporary module to execute the code
    spec = importlib.util.spec_from_loader("temp_module", loader=None)
    temp_module = importlib.util.module_from_spec(spec)
    
    # Add necessary imports to the module
    exec("from typing import List\nimport time", temp_module.__dict__)
    
    # Execute the original code in the module
    exec(original_code, temp_module.__dict__)
    
    # Prepare test data
    test_data = list(range(100)) + list(range(50))  # Some duplicates
    
    # Measure original function performance
    original_func = getattr(temp_module, function_name)
    original_result, original_time = measure_execution_time(original_func, test_data)
    _, original_memory = measure_memory_usage(original_func, test_data)
    
    # Create a new module for the improved code
    spec = importlib.util.spec_from_loader("improved_module", loader=None)
    improved_module = importlib.util.module_from_spec(spec)
    
    # Add necessary imports to the module
    exec("from typing import List\nimport time", improved_module.__dict__)
    
    try:
        # Execute the improved code in the module
        exec(improved_code, improved_module.__dict__)
        
        # Measure improved function performance
        improved_func = getattr(improved_module, function_name)
        improved_result, improved_time = measure_execution_time(improved_func, test_data)
        _, improved_memory = measure_memory_usage(improved_func, test_data)
        
        # Check if results are equivalent
        results_match = sorted(original_result) == sorted(improved_result)
        
        return {
            "original_time": original_time,
            "improved_time": improved_time,
            "time_improvement": original_time / improved_time if improved_time > 0 else float('inf'),
            "original_memory": original_memory,
            "improved_memory": improved_memory,
            "memory_improvement": original_memory / improved_memory if improved_memory > 0 else float('inf'),
            "results_match": results_match,
            "error": None
        }
    except Exception as e:
        return {
            "original_time": original_time,
            "improved_time": None,
            "time_improvement": None,
            "original_memory": original_memory,
            "improved_memory": None,
            "memory_improvement": None,
            "results_match": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@langsmith_traceable(name="evaluate_response_quality", project_name=LANGCHAIN_PROJECT)
def evaluate_response_quality(original_code: str, improved_code: str, response: str) -> Dict[str, Any]:
    """
    Evaluate the quality of the LLM's response using another LLM as a judge.
    
    Args:
        original_code: The original function code
        improved_code: The improved function code extracted from the response
        response: The full response from the LLM
        
    Returns:
        Dictionary with quality metrics
    """
    # Use a separate model as a judge
    judge_model = ChatOllama(
        model="llama3.2:3b",  # Using a consistent model for judging
        temperature=0.2,  # Low temperature for more consistent evaluations
    )
    
    judge_prompt = PromptTemplate.from_template(
        """You are an expert code reviewer tasked with evaluating the quality of code improvements.
        
        Original Code:
        ```python
        {original_code}
        ```
        
        Improved Code:
        ```python
        {improved_code}
        ```
        
        Full Response:
        {full_response}
        
        Please evaluate the code improvement on the following criteria on a scale of 1-10:
        1. Correctness: Does the improved code maintain the same functionality?
        2. Efficiency: Is the improved code more efficient in terms of time and space complexity?
        3. Readability: Is the improved code more readable and maintainable?
        4. Explanation Quality: How well did the response explain the improvements?
        
        For each criterion, provide a score and a brief justification.
        Then provide an overall score (average of the four criteria).
        
        Format your response as JSON:
        {{
            "correctness": {{
                "score": X,
                "justification": "..."
            }},
            "efficiency": {{
                "score": X,
                "justification": "..."
            }},
            "readability": {{
                "score": X,
                "justification": "..."
            }},
            "explanation": {{
                "score": X,
                "justification": "..."
            }},
            "overall_score": X.X
        }}
        """
    )
    
    judge_chain = LLMChain(llm=judge_model, prompt=judge_prompt)
    
    try:
        judge_response = judge_chain.run(
            original_code=original_code,
            improved_code=improved_code,
            full_response=response
        )
        
        # Extract the JSON from the response
        import re
        json_match = re.search(r'({[\s\S]*})', judge_response)
        if json_match:
            try:
                evaluation = json.loads(json_match.group(1))
                return evaluation
            except json.JSONDecodeError:
                return {"error": "Failed to parse judge response as JSON"}
        else:
            return {"error": "No JSON found in judge response"}
    except Exception as e:
        return {"error": str(e)}


@langsmith_traceable(name="run_experiment", project_name=LANGCHAIN_PROJECT)
def run_experiment(stage_name: str, stages_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Run the experiment for a specific stage.
    
    Args:
        stage_name: Name of the stage to run
        stages_config: Configuration for all stages
        
    Returns:
        List of results for each model in the stage
    """
    if stage_name not in stages_config:
        raise ValueError(f"Stage '{stage_name}' not found in configuration")
    
    stage_config = stages_config[stage_name]
    results = []
    
    # Extract the function code and context
    context_data = extract_code_context(
        TEST_CODE_PATH, 
        "find_duplicates", 
        stage_config["contextLineCount"]
    )
    
    # Set up callbacks for logging
    callbacks = [StdOutCallbackHandler()]
    
    for model_name in stage_config["models"]:
        print(f"\nRunning experiment for model: {model_name} in stage: {stage_name}")
        
        try:
            # Set up the model with the specified parameters
            model = setup_model(
                model_name=model_name,
                temperature=stage_config["modelParameters"]["temperature"]
            )
            
            # Create the prompt chain
            chain = create_prompt_chain(model, stage_config["promptTemplate"])
            
            # Prepare the structured context
            structured_context = json.dumps(context_data, indent=2)
            
            # Run the chain
            start_time = time.time()
            response = chain.run(
                system_message="You are a code review assistant who is an expert at reviewing code and suggesting improvements.",
                human_message=stage_config["humanMessage"],
                structured_context=structured_context,
                callbacks=callbacks
            )
            end_time = time.time()
            
            # Extract the improved code from the response
            improved_code = extract_code_from_response(response)
            
            # Evaluate the code performance
            performance_metrics = evaluate_code_performance(
                context_data["code_to_improve"],
                improved_code,
                "find_duplicates"
            )
            
            # Evaluate the response quality
            quality_metrics = evaluate_response_quality(
                context_data["code_to_improve"],
                improved_code,
                response
            )
            
            # Collect results
            result = {
                "stage": stage_name,
                "model": model_name,
                "temperature": stage_config["modelParameters"]["temperature"],
                "context_line_count": stage_config["contextLineCount"],
                "response_time": end_time - start_time,
                "improved_code": improved_code,
                "full_response": response,
                "performance_metrics": performance_metrics,
                "quality_metrics": quality_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(result)
            
            # Save individual result to file
            result_file = RESULTS_DIR / f"{stage_name}_{model_name.replace(':', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, "w") as f:
                json.dump(result, f, indent=2)
            
            print(f"Experiment completed for {model_name}. Results saved to {result_file}")
            
        except Exception as e:
            print(f"Error running experiment for {model_name}: {e}")
            traceback.print_exc()
            
            # Record the error
            error_result = {
                "stage": stage_name,
                "model": model_name,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(error_result)
            
            # Save error result to file
            error_file = RESULTS_DIR / f"{stage_name}_{model_name.replace(':', '_')}_ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(error_file, "w") as f:
                json.dump(error_result, f, indent=2)
    
    return results


def safe_mean(values, default=0):
    """Calculate mean safely, returning default if the list is empty."""
    try:
        return statistics.mean(values) if values else default
    except statistics.StatisticsError:
        return default


@langsmith_traceable(name="analyze_results", project_name=LANGCHAIN_PROJECT)
def analyze_results(all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze the results of all experiments.
    
    Args:
        all_results: List of results from all experiments
        
    Returns:
        Dictionary with analysis metrics
    """
    analysis = {
        "stages": {},
        "models": {},
        "overall": {
            "total_experiments": len(all_results),
            "successful_experiments": sum(1 for r in all_results if "error" not in r or not r["error"]),
            "average_response_time": safe_mean([r.get("response_time", 0) for r in all_results if "response_time" in r]),
        }
    }
    
    # Group results by stage
    for stage_name in set(r.get("stage", "") for r in all_results if "stage" in r):
        stage_results = [r for r in all_results if r.get("stage") == stage_name]
        
        # Calculate stage metrics
        analysis["stages"][stage_name] = {
            "total_experiments": len(stage_results),
            "successful_experiments": sum(1 for r in stage_results if "error" not in r or not r["error"]),
            "average_response_time": safe_mean([r.get("response_time", 0) for r in stage_results if "response_time" in r]),
            "average_time_improvement": safe_mean([
                r.get("performance_metrics", {}).get("time_improvement", 1) 
                for r in stage_results 
                if r.get("performance_metrics", {}).get("time_improvement") is not None
            ]),
            "average_memory_improvement": safe_mean([
                r.get("performance_metrics", {}).get("memory_improvement", 1) 
                for r in stage_results 
                if r.get("performance_metrics", {}).get("memory_improvement") is not None
            ]),
            "average_quality_score": safe_mean([
                r.get("quality_metrics", {}).get("overall_score", 0) 
                for r in stage_results 
                if r.get("quality_metrics", {}).get("overall_score") is not None
            ]),
        }
    
    # Group results by model
    for model_name in set(r.get("model", "") for r in all_results if "model" in r):
        model_results = [r for r in all_results if r.get("model") == model_name]
        
        # Calculate model metrics
        analysis["models"][model_name] = {
            "total_experiments": len(model_results),
            "successful_experiments": sum(1 for r in model_results if "error" not in r or not r["error"]),
            "average_response_time": safe_mean([r.get("response_time", 0) for r in model_results if "response_time" in r]),
            "average_time_improvement": safe_mean([
                r.get("performance_metrics", {}).get("time_improvement", 1) 
                for r in model_results 
                if r.get("performance_metrics", {}).get("time_improvement") is not None
            ]),
            "average_memory_improvement": safe_mean([
                r.get("performance_metrics", {}).get("memory_improvement", 1) 
                for r in model_results 
                if r.get("performance_metrics", {}).get("memory_improvement") is not None
            ]),
            "average_quality_score": safe_mean([
                r.get("quality_metrics", {}).get("overall_score", 0) 
                for r in model_results 
                if r.get("quality_metrics", {}).get("overall_score") is not None
            ]),
        }
    
    return analysis


def main():
    """Main function to run the experiments."""
    parser = argparse.ArgumentParser(description="Run code improvement experiments")
    parser.add_argument("--stage", choices=["baseline", "stage1", "stage2", "stage3", "stage4", "all"], 
                        default=CURRENT_STAGE, help="Stage to run (default: %(default)s)")
    args = parser.parse_args()
    
    # Create results directory if it doesn't exist
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Load the stages configuration
    stages_config = load_stages_config()
    
    all_results = []
    
    if args.stage == "all":
        # Run all stages
        for stage_name in stages_config.keys():
            stage_results = run_experiment(stage_name, stages_config)
            all_results.extend(stage_results)
    else:
        # Run a specific stage
        stage_results = run_experiment(args.stage, stages_config)
        all_results.extend(stage_results)
    
    # Analyze the results
    analysis = analyze_results(all_results)
    
    # Save the analysis to file
    analysis_file = RESULTS_DIR / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(analysis_file, "w") as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\nExperiments completed. Analysis saved to {analysis_file}")
    
    # Print a summary of the analysis
    print("\nSummary:")
    print(f"Total experiments: {analysis['overall']['total_experiments']}")
    print(f"Successful experiments: {analysis['overall']['successful_experiments']}")
    print(f"Average response time: {analysis['overall']['average_response_time']:.2f} seconds")
    
    print("\nResults by stage:")
    for stage_name, stage_analysis in analysis["stages"].items():
        print(f"  {stage_name}:")
        print(f"    Average time improvement: {stage_analysis.get('average_time_improvement', 'N/A'):.2f}x")
        print(f"    Average memory improvement: {stage_analysis.get('average_memory_improvement', 'N/A'):.2f}x")
        print(f"    Average quality score: {stage_analysis.get('average_quality_score', 'N/A'):.2f}/10")
    
    print("\nResults by model:")
    for model_name, model_analysis in analysis["models"].items():
        print(f"  {model_name}:")
        print(f"    Average time improvement: {model_analysis.get('average_time_improvement', 'N/A'):.2f}x")
        print(f"    Average memory improvement: {model_analysis.get('average_memory_improvement', 'N/A'):.2f}x")
        print(f"    Average quality score: {model_analysis.get('average_quality_score', 'N/A'):.2f}/10")


if __name__ == "__main__":
    main()
