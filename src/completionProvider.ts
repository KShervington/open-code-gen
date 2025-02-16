import * as vscode from "vscode";
import { Ollama } from "@langchain/ollama";

export class CodeCompletionProvider implements vscode.CompletionItemProvider {
  private model: Ollama;

  constructor() {
    this.model = new Ollama({
      model: "llama3.2:1b",
    });
  }

  async provideCompletionItems(
    document: vscode.TextDocument,
    position: vscode.Position,
    token: vscode.CancellationToken,
    context: vscode.CompletionContext
  ): Promise<vscode.CompletionList> {
    const linePrefix = document
      .lineAt(position)
      .text.slice(0, position.character);

    // Basic trigger condition: Suggest completions after typing at least 3 characters
    if (linePrefix.trim().length < 3) {
      return new vscode.CompletionList([], false);
    }

    // 1. Get Code Context
    const codeContext = this.getCodeContext(document, position);

    // 2. Call LLM for Code Completion (Placeholder - Replace with actual LLM interaction)
    const llmCompletions = await this.getLLMCompletions(codeContext);

    // 3. Create and Return Completion Items
    const completionItems = llmCompletions.map((completion) => {
      const completionItem = new vscode.CompletionItem(
        completion,
        vscode.CompletionItemKind.Snippet
      );
      completionItem.insertText = completion; // Or vscode.SnippetString for more complex snippets
      completionItem.documentation = new vscode.MarkdownString(
        `Code completion from Llama model`
      ); // Optional documentation
      return completionItem;
    });

    return new vscode.CompletionList(completionItems, false);
  }

  private getCodeContext(
    document: vscode.TextDocument,
    position: vscode.Position
  ): string {
    // You can customize how much context you send to the LLM
    const currentLine = document.lineAt(position.line).text;
    const precedingLines = document.getText(
      new vscode.Range(
        new vscode.Position(Math.max(0, position.line - 2), 0),
        position
      )
    ); // Last 2 lines and current line up to cursor
    return precedingLines + currentLine.slice(0, position.character);
  }

  private async getLLMCompletions(context: string): Promise<string[]> {
    // ** Placeholder for LLM Interaction - Replace with your LangChain and Llama API logic **

    console.log("Code Context from getLLMCompletions(): ", context);

    return ["Testing completion 1", "Testing completion 2"];
  }
}
