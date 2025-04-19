import { Ollama } from "@langchain/ollama";
import { PromptTemplate } from "@langchain/core/prompts";
import { RunnableSequence } from "@langchain/core/runnables";
import { traceable } from "langsmith/traceable";
import { Client } from "langsmith";
import * as dotenv from 'dotenv';

export class ReviewProvider {
  private model: Ollama;
  private chain: RunnableSequence;
  private client: Client;

  constructor() {
    // The environment variables are already set in extension.ts
    // Initialize LangSmith client
    this.client = new Client();
    
    // Log LangSmith configuration for debugging
    console.log("LangSmith Configuration in ReviewProvider:");
    console.log("LANGCHAIN_TRACING_V2:", process.env.LANGCHAIN_TRACING_V2);
    console.log("LANGCHAIN_ENDPOINT:", process.env.LANGCHAIN_ENDPOINT);
    console.log("LANGCHAIN_API_KEY:", process.env.LANGCHAIN_API_KEY ? "[REDACTED]" : "undefined");
    console.log("LANGCHAIN_PROJECT:", process.env.LANGCHAIN_PROJECT);
    
    this.model = new Ollama({
      model: "codellama:7b",
    });

    // Create a prompt template
    const promptTemplate = PromptTemplate.fromTemplate(
      "Improve the following code:\n\n{code}"
    );

    // Create a chain that will be traced
    this.chain = RunnableSequence.from([promptTemplate, this.model]);

    console.log("ReviewProvider initialized");
  }

  getReview = traceable(async (selectedCode: string): Promise<string> => {
    console.log("Generating review");

    try {
      // Use the chain instead of direct model invocation
      const review = await this.chain.invoke({
        code: selectedCode,
      });

      console.log("Review generated successfully");
      return review;
    } catch (error) {
      console.error("Error generating review:", error);
      throw error;
    }
  });
}
