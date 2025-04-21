# Code Improvement Experiment Framework

This framework is designed to evaluate the performance of various LLM models in improving code across different experimental stages. It emulates the functionality of the IDE extension created in this project, focusing on improving the `find_duplicates` function.

## Overview

The experiment framework evaluates:
1. **Time and space complexity** of code produced by different models
2. **Token usage** (via LangSmith integration)
3. **Quality of responses** (using an LLM as a judge)

Each evaluation is performed across multiple experimental stages defined in `eval_stages.json`.

## Experiment Stages

The experiment is structured into several stages, each testing different aspects:

1. **Baseline**: Establishes a baseline for code improvements and explanations
2. **Stage 1**: Evaluates how chain-of-thought prompting affects code generations
3. **Stage 2**: Evaluates how additional code context affects quality
4. **Stage 3**: Evaluates how temperature affects quality
5. **Stage 4**: Evaluates the combined effect of context, temperature, and chain-of-thought

## Prerequisites

- Python 3.8+
- Ollama installed and running locally
- Required Python packages:
  ```
  langchain
  langchain_community
  langsmith
  matplotlib
  pandas
  seaborn
  ```

## Setup

1. Install the required packages:
   ```bash
   pip install langchain langchain_community langsmith matplotlib pandas seaborn
   ```

2. Set up LangSmith for token usage tracking (optional but recommended):
   ```bash
   export LANGCHAIN_TRACING_V2=true
   export LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
   export LANGCHAIN_API_KEY=your_api_key
   export LANGCHAIN_PROJECT=code-improvement-experiments
   ```

3. Make sure Ollama is running with the required models:
   ```bash
   # Pull the required models
   ollama pull codellama:7b
   ollama pull qwen2.5-coder:7b
   ollama pull qwq:32b
   ollama pull deepseek-r1:32b
   ```

## Running Experiments

### Running a Single Stage

To run experiments for a specific stage:

```bash
python run_experiments.py --stage baseline
```

Available stages: `baseline`, `stage1`, `stage2`, `stage3`, `stage4`

### Running All Stages

To run experiments for all stages:

```bash
python run_experiments.py --stage all
```

### Controlling the Current Stage

You can also modify the `CURRENT_STAGE` global variable in `run_experiments.py` to control which stage to execute by default.

## Visualizing Results

After running experiments, you can visualize the results:

```bash
python visualize_results.py
```

This will generate various visualizations and an HTML report in the `visualizations` directory.

## Interpreting Results

### Results Structure

Each experiment generates a JSON file with the following information:
- Stage and model details
- Response time
- Improved code
- Full LLM response
- Performance metrics:
  - Execution time of original vs. improved code
  - Memory usage of original vs. improved code
  - Whether results match functionally
- Quality metrics (from LLM judge):
  - Correctness score (1-10)
  - Efficiency score (1-10)
  - Readability score (1-10)
  - Explanation quality score (1-10)
  - Overall score (average)

### Key Metrics to Consider

1. **Time Improvement Factor**: How much faster the improved code runs compared to the original. Higher is better.
2. **Memory Improvement Factor**: How much less memory the improved code uses. Higher is better.
   - **Note on "Infinity" values**: When you see "Infinity" in memory improvement results, it indicates that the improved code used so little additional memory that it was either not measurable or exactly zero. This happens because memory improvement is calculated as `original_memory / improved_memory`. When `improved_memory` is zero or extremely small, the result approaches infinity. This is actually a positive result, indicating extremely memory-efficient code improvements.
3. **Quality Scores**: Subjective evaluation of code quality by an LLM judge. Higher is better.
4. **Response Time**: How long it took the model to generate the improvement. Lower is better.

### Visualizations

The visualization script generates several plots:
- Time improvement by stage and model
- Memory improvement by stage and model
- Quality scores by stage
- Model comparison across all metrics
- Correlation matrix between different metrics

## HTML Report

The HTML report provides a comprehensive view of the experiment results, including:
- Summary tables by stage and model
- All visualizations embedded in one document

## Example Analysis

When analyzing the results, consider questions like:
- Which model performs best for code improvement in terms of efficiency?
- Does chain-of-thought prompting (stage1) improve code quality?
- Does additional context (stage2) help models generate better code?
- How does temperature affect the quality and correctness of code?
- Which combination of parameters produces the most efficient code?

## Extending the Framework

To extend this framework:
1. Add new stages to `eval_stages.json`
2. Add new models to the existing stages
3. Modify the evaluation metrics in `run_experiments.py`
4. Add new visualizations in `visualize_results.py`

## Troubleshooting

- **Model not found**: Ensure Ollama is running and the model is pulled
- **Memory errors**: Reduce the batch size or use smaller models
- **Visualization errors**: Check that all experiments completed successfully

## Notes on Token Usage

If LangSmith integration is enabled, you can view detailed token usage statistics in the LangSmith dashboard. This helps analyze:
- Input token count per model and stage
- Output token count per model and stage
- Cost implications of different prompting strategies
