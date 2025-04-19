import { Ollama } from "@langchain/ollama";
import { PromptTemplate } from "@langchain/core/prompts";
import { RunnableSequence } from "@langchain/core/runnables";
import { traceable } from "langsmith/traceable";
import { Client } from "langsmith";
import * as dotenv from "dotenv";

export class ReviewProvider {
  private model: Ollama;
  private chain: RunnableSequence;

  constructor() {
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
      // Use the chain to invoke model
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
