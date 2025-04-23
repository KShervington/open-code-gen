#!/usr/bin/env python3
"""
Visualization Module for Code Improvement Experiments

This script provides functions to visualize and analyze the results of code improvement experiments.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Path to store experiment results
RESULTS_DIR = Path(__file__).parent / "results"
# Path to store visualizations
VISUALIZATIONS_DIR = Path(__file__).parent / "visualizations"


def load_results(results_dir: Path = RESULTS_DIR) -> List[Dict[str, Any]]:
    """
    Load all experiment results from the results directory.
    
    Args:
        results_dir: Directory containing result files
        
    Returns:
        List of result dictionaries
    """
    results = []
    
    for file_path in results_dir.glob("*.json"):
        # Skip analysis files
        if file_path.name.startswith("analysis_"):
            continue
            
        try:
            with open(file_path, "r") as f:
                result = json.load(f)
                results.append(result)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return results


def create_dataframe(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert results to a pandas DataFrame for easier analysis.
    
    Args:
        results: List of result dictionaries
        
    Returns:
        DataFrame with experiment results
    """
    data = []
    
    for result in results:
        # Skip results with errors
        if "error" in result and result["error"]:
            continue
            
        # Extract performance metrics
        perf_metrics = result.get("performance_metrics", {})
        quality_metrics = result.get("quality_metrics", {})
        
        row = {
            "stage": result.get("stage"),
            "model": result.get("model"),
            "temperature": result.get("temperature"),
            "context_line_count": result.get("context_line_count"),
            "response_time": result.get("response_time"),
            "original_time": perf_metrics.get("original_time"),
            "improved_time": perf_metrics.get("improved_time"),
            "time_improvement": perf_metrics.get("time_improvement"),
            "original_memory": perf_metrics.get("original_memory"),
            "improved_memory": perf_metrics.get("improved_memory"),
            "memory_improvement": perf_metrics.get("memory_improvement"),
            "results_match": perf_metrics.get("results_match", False),
            "correctness_score": quality_metrics.get("correctness", {}).get("score"),
            "efficiency_score": quality_metrics.get("efficiency", {}).get("score"),
            "readability_score": quality_metrics.get("readability", {}).get("score"),
            "explanation_score": quality_metrics.get("explanation", {}).get("score"),
            "overall_score": quality_metrics.get("overall_score"),
        }
        
        data.append(row)
    
    return pd.DataFrame(data)


def plot_time_improvement_by_stage(df: pd.DataFrame, output_dir: Path):
    """Plot time improvement by stage."""
    plt.figure(figsize=(12, 8))
    
    # Create a grouped bar chart
    sns.barplot(x="stage", y="time_improvement", hue="model", data=df)
    
    plt.title("Time Improvement by Stage and Model")
    plt.xlabel("Stage")
    plt.ylabel("Time Improvement Factor (higher is better)")
    plt.yscale("log")  # Log scale for better visualization
    plt.grid(True, alpha=0.3)
    plt.legend(title="Model")
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_dir / "time_improvement_by_stage.png")
    plt.close()


def plot_memory_improvement_by_stage(df: pd.DataFrame, output_dir: Path):
    """Plot memory improvement by stage."""
    plt.figure(figsize=(12, 8))
    
    # Create a grouped bar chart
    sns.barplot(x="stage", y="memory_improvement", hue="model", data=df)
    
    plt.title("Memory Improvement by Stage and Model")
    plt.xlabel("Stage")
    plt.ylabel("Memory Improvement Factor (higher is better)")
    plt.yscale("log")  # Log scale for better visualization
    plt.grid(True, alpha=0.3)
    plt.legend(title="Model")
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_dir / "memory_improvement_by_stage.png")
    plt.close()


def plot_quality_scores_by_stage(df: pd.DataFrame, output_dir: Path):
    """Plot quality scores by stage, properly averaging across models with valid metrics."""
    plt.figure(figsize=(14, 10))
    
    # Melt the DataFrame to get all scores in one column
    melted_df = pd.melt(
        df, 
        id_vars=["stage", "model"], 
        value_vars=["correctness_score", "efficiency_score", "readability_score", "explanation_score", "overall_score"],
        var_name="metric",
        value_name="score"
    )
    
    # Remove rows with NaN scores
    melted_df = melted_df.dropna(subset=["score"])
    
    # Create a summary DataFrame that shows the number of models with valid metrics for each stage
    models_per_stage = melted_df.groupby(["stage", "metric"]).size().reset_index(name="model_count")
    
    # Group by stage and metric, and calculate mean score
    aggregated_df = melted_df.groupby(["stage", "metric"])["score"].mean().reset_index()
    
    # Merge with model count information
    aggregated_df = pd.merge(aggregated_df, models_per_stage, on=["stage", "metric"])
    
    # Create a grouped bar chart with the aggregated data
    plt.figure(figsize=(16, 12))
    
    # Main plot for scores
    ax = plt.subplot(111)
    bars = sns.barplot(x="stage", y="score", hue="metric", data=aggregated_df, ax=ax)
    
    # Add text annotations showing how many models contributed to each bar
    for i, bar in enumerate(bars.patches):
        # Get the index in the aggregated_df that corresponds to this bar
        idx = i % len(aggregated_df)
        # Get the model count for this bar
        model_count = aggregated_df.iloc[idx]["model_count"]
        # Add text annotation
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'n={model_count}', ha='center', va='bottom', fontsize=8)
    
    plt.title("Average Quality Scores by Stage (Across Models with Valid Metrics)")
    plt.xlabel("Stage")
    plt.ylabel("Average Score (1-10)")
    plt.grid(True, alpha=0.3)
    plt.legend(title="Metric")
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_dir / "quality_scores_by_stage.png")
    plt.close()
    
    # Create a second plot showing scores by stage and model
    plt.figure(figsize=(18, 12))
    g = sns.catplot(
        data=melted_df, 
        x="stage", 
        y="score", 
        hue="model", 
        col="metric",
        kind="bar",
        height=5, 
        aspect=0.8,
        sharey=True,
        col_wrap=3
    )
    g.set_axis_labels("Stage", "Score (1-10)")
    g.set_titles("{col_name}")
    g.fig.suptitle("Quality Scores by Stage, Model, and Metric", y=1.02, fontsize=16)
    
    # Save the detailed plot
    plt.tight_layout()
    plt.savefig(output_dir / "quality_scores_detailed.png")
    plt.close()


def plot_model_comparison(df: pd.DataFrame, output_dir: Path):
    """Plot model comparison across all metrics."""
    plt.figure(figsize=(16, 12))
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Time improvement
    sns.barplot(x="model", y="time_improvement", data=df, ax=axes[0, 0])
    axes[0, 0].set_title("Time Improvement by Model")
    axes[0, 0].set_ylabel("Time Improvement Factor")
    axes[0, 0].set_yscale("log")
    axes[0, 0].grid(True, alpha=0.3)
    
    # Memory improvement
    sns.barplot(x="model", y="memory_improvement", data=df, ax=axes[0, 1])
    axes[0, 1].set_title("Memory Improvement by Model")
    axes[0, 1].set_ylabel("Memory Improvement Factor")
    axes[0, 1].set_yscale("log")
    axes[0, 1].grid(True, alpha=0.3)
    
    # Overall quality score
    sns.barplot(x="model", y="overall_score", data=df, ax=axes[1, 0])
    axes[1, 0].set_title("Overall Quality Score by Model")
    axes[1, 0].set_ylabel("Score (1-10)")
    axes[1, 0].grid(True, alpha=0.3)
    
    # Response time
    sns.barplot(x="model", y="response_time", data=df, ax=axes[1, 1])
    axes[1, 1].set_title("Response Time by Model")
    axes[1, 1].set_ylabel("Time (seconds)")
    axes[1, 1].grid(True, alpha=0.3)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_dir / "model_comparison.png")
    plt.close()


def plot_correlation_matrix(df: pd.DataFrame, output_dir: Path):
    """Plot correlation matrix between different metrics."""
    # Select numeric columns and exclude original metrics
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    
    # Remove original_time and original_memory as they're not useful for correlation analysis
    # since they're the same for all improvements of the same function
    columns_to_exclude = ['original_time', 'original_memory']
    analysis_df = numeric_df.drop(columns=[col for col in columns_to_exclude if col in numeric_df.columns])
    
    # Calculate correlation matrix
    corr_matrix = analysis_df.corr()
    
    # Plot heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Correlation Matrix of Improvement Metrics")
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_dir / "correlation_matrix.png")
    plt.close()


def generate_html_report(df: pd.DataFrame, output_dir: Path):
    """Generate an HTML report with tables and embedded visualizations."""
    # Group by stage
    stage_summary = df.groupby("stage").agg({
        "time_improvement": ["mean", "std", "min", "max"],
        "memory_improvement": ["mean", "std", "min", "max"],
        "overall_score": ["mean", "std", "min", "max"],
        "response_time": ["mean", "std", "min", "max"]
    }).reset_index()
    
    # Group by model
    model_summary = df.groupby("model").agg({
        "time_improvement": ["mean", "std", "min", "max"],
        "memory_improvement": ["mean", "std", "min", "max"],
        "overall_score": ["mean", "std", "min", "max"],
        "response_time": ["mean", "std", "min", "max"]
    }).reset_index()
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Code Improvement Experiment Results</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .visualization {{ margin: 20px 0; text-align: center; }}
            .visualization img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <h1>Code Improvement Experiment Results</h1>
        
        <h2>Summary by Stage</h2>
        {stage_summary.to_html(index=False)}
        
        <h2>Summary by Model</h2>
        {model_summary.to_html(index=False)}
        
        <h2>Visualizations</h2>
        
        <div class="visualization">
            <h3>Time Improvement by Stage and Model</h3>
            <img src="time_improvement_by_stage.png" alt="Time Improvement by Stage">
        </div>
        
        <div class="visualization">
            <h3>Memory Improvement by Stage and Model</h3>
            <img src="memory_improvement_by_stage.png" alt="Memory Improvement by Stage">
        </div>
        
        <div class="visualization">
            <h3>Quality Scores by Stage</h3>
            <img src="quality_scores_by_stage.png" alt="Quality Scores by Stage">
        </div>
        
        <div class="visualization">
            <h3>Model Comparison</h3>
            <img src="model_comparison.png" alt="Model Comparison">
        </div>
        
        <div class="visualization">
            <h3>Correlation Matrix</h3>
            <img src="correlation_matrix.png" alt="Correlation Matrix">
        </div>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(output_dir / "report.html", "w") as f:
        f.write(html_content)


def main():
    """Main function to visualize experiment results."""
    parser = argparse.ArgumentParser(description="Visualize code improvement experiment results")
    parser.add_argument("--results-dir", type=str, default=str(RESULTS_DIR),
                        help="Directory containing result files")
    parser.add_argument("--output-dir", type=str, default=str(VISUALIZATIONS_DIR),
                        help="Directory to save visualizations")
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    output_dir = Path(args.output_dir)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load results
    results = load_results(results_dir)
    
    if not results:
        print("No results found. Run experiments first.")
        return
    
    # Create DataFrame
    df = create_dataframe(results)
    
    # Generate visualizations
    plot_time_improvement_by_stage(df, output_dir)
    plot_memory_improvement_by_stage(df, output_dir)
    plot_quality_scores_by_stage(df, output_dir)
    plot_model_comparison(df, output_dir)
    plot_correlation_matrix(df, output_dir)
    
    # Generate HTML report
    generate_html_report(df, output_dir)
    
    print(f"Visualizations and report generated in {output_dir}")


if __name__ == "__main__":
    main()
