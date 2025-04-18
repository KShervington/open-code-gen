import { Ollama } from "@langchain/ollama";

export class ReviewProvider {
  private model: Ollama;

  constructor() {
    this.model = new Ollama({
      model: "qwen2.5-coder:7b",
    });
    console.log("ReviewProvider initialized");
  }

  async getReview(generatedCode: string): Promise<string> {
    console.log("Generating review");

    // Call LLM for Code Completion (Placeholder - Replace with actual LLM interaction)
    const review = await this.model.invoke(generatedCode);

    console.log("Review generated");

    return review;
  }
}
