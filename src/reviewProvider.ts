import { Ollama } from "@langchain/ollama";

export class ReviewProvider {
  private model: Ollama;

  constructor() {
    this.model = new Ollama({
      model: "qwen2.5-coder:7b",
    });
    console.log("ReviewProvider initialized");
  }

  async getReview(selectedCode: string): Promise<string> {
    console.log("Generating review");

    // Use LangChain prompt template
    const prompt = `Improve the following code:\n\n{code}`;
    const input = prompt.replace('{code}', selectedCode);

    // Call LLM for code improvement
    const review = await this.model.invoke(input);

    console.log("Review generated");

    return review;
  }
}
