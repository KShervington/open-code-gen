import { Ollama } from "@langchain/ollama";
import { PromptTemplate } from "@langchain/core/prompts";
import { RunnableSequence } from "@langchain/core/runnables";
import { traceable } from "langsmith/traceable";

export class ReviewProvider {
  private model: Ollama;
  private chain: RunnableSequence;
  private systemMessage: string =
    "You are a code review assistant. Your task is to review the provided code and suggest improvements.";
  private humanMessage: string = "Improve the following code:";

  constructor() {
    this.model = new Ollama({
      model: "codellama:7b",
      numGpu: 1,
      temperature: 0.5,
    });

    // Create a prompt template
    const promptTemplate = PromptTemplate.fromTemplate(
      "{system_message}\n\n{human_message}\n{code}"
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
        system_message: this.systemMessage,
        human_message: this.humanMessage,
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
