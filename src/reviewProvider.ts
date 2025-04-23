import { Ollama } from "@langchain/ollama";
import { PromptTemplate } from "@langchain/core/prompts";
import { RunnableSequence } from "@langchain/core/runnables";
import { traceable } from "langsmith/traceable";

// Define interface for the structured prompt data
export interface CodeReviewPrompt {
  code_to_improve: string;
  context_before_code?: string;
  context_after_code?: string;
}

export class ReviewProvider {
  private model: Ollama;
  private chain: RunnableSequence;
  private systemMessage: string =
    "You are a code review assistant who is an expert at reviewing code and suggesting improvements.";
  private humanMessage: string =
    "Improve the specified code based on the information given. I need you to think step-by-step and show your work.\n\nStep 1: Understand the Goal: Briefly restate what the original code does and what the goal of the improvement is based on the provided information.\nStep 2: Identify Problems/Opportunities: Examine the original code line-by-line or section-by-section. What specific parts violate the requirements or could be done better (e.g., inefficient loop, unclear variable name, missing validation)? List them.\nStep 3: Devise Solutions: For each problem identified in Step 2, outline the specific change you will make. Why is this the right fix? Are there alternatives you considered?\nStep 4: Construct the Improved Code: Write the new version of the code integrating the solutions from Step 3.\nStep 5: Explain the Result: Compare the new code to the old. Highlight the key changes and explain how they fulfill the requirements and lead to better code.\n\nEnsure your response follows these steps clearly. Format the entire output, including all steps and the final code, using markdown.";

  constructor() {
    this.model = new Ollama({
      model: "qwen2.5-coder:7b",
      numGpu: 1,
      temperature: 0.5,
    });

    // Create a prompt template that uses the structured JSON format
    const promptTemplate = PromptTemplate.fromTemplate(
      "{system_message}\n\n{human_message}\n\nCode Context:\n```json\n{structured_context}\n```"
    );

    // Create a chain that will be traced
    this.chain = RunnableSequence.from([promptTemplate, this.model]);

    console.log("ReviewProvider initialized");
  }

  getReview = traceable(
    async (
      selectedCode: string,
      contextBeforeCode?: string,
      contextAfterCode?: string
    ): Promise<string> => {
      console.log("Generating review with structured context");

      try {
        // Create structured context object
        const structuredContext: CodeReviewPrompt = {
          code_to_improve: selectedCode,
        };

        // Add optional context if provided
        if (contextBeforeCode) {
          structuredContext.context_before_code = contextBeforeCode;
        }

        if (contextAfterCode) {
          structuredContext.context_after_code = contextAfterCode;
        }

        // Convert to JSON string for the prompt
        const structuredContextJson = JSON.stringify(
          structuredContext,
          null,
          2
        );

        // Use the chain to invoke model with structured context
        const review = await this.chain.invoke({
          system_message: this.systemMessage,
          human_message: this.humanMessage,
          structured_context: structuredContextJson,
        });

        console.log("Review generated successfully");
        return review;
      } catch (error) {
        console.error("Error generating review:", error);
        throw error;
      }
    }
  );
}
