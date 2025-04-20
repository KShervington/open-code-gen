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
    "Improve the specified code based on information given. Format your answer as markdown.";

  constructor() {
    this.model = new Ollama({
      model: "codellama:7b",
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
