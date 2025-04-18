// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import { ReviewProvider } from "./reviewProvider";

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
  // Use the console to output diagnostic information (console.log) and errors (console.error)
  // This line of code will only be executed once when your extension is activated
  console.log('Congratulations, your extension "open-code-gen" is now active!');

  // The command has been defined in the package.json file
  // Now provide the implementation of the command with registerCommand
  // The commandId parameter must match the command field in package.json
  const disposable = vscode.commands.registerCommand(
    "open-code-gen.helloWorld",
    () => {
      // The code you place here will be executed every time your command is executed
      // Display a message box to the user
      vscode.window.showInformationMessage("Hello World from open-code-gen!");
    }
  );

  // Initialize the ReviewProvider for code completion
  const reviewProvider = new ReviewProvider();

  // Register the command for code completion via context menu
  const completeCodeCommand = vscode.commands.registerCommand(
    "open-code-gen.completeCode",
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showInformationMessage("No active editor found");
        return;
      }

      // Show progress indicator
      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "Generating code completion...",
          cancellable: false,
        },
        async (progress) => {
          try {
            // Get current document and position
            const document = editor.document;
            const position = editor.selection.active;

            // Get code context (similar to what's in completionProvider)
            const numLines = 6; // Number of preceding lines for context
            const codeContext = document.getText(
              new vscode.Range(
                new vscode.Position(Math.max(0, position.line - numLines), 0),
                position
              )
            );

            // Get completion from the reviewProvider
            const startTime = Date.now();
            const completion = await reviewProvider.getReview(codeContext);
            const timeTaken = Date.now() - startTime;
            console.log(
              `Completion from LLM after [${timeTaken / 1000}] seconds:\n${completion}`
            );

            // Insert the completion at the current position
            editor.edit((editBuilder) => {
              editBuilder.insert(position, completion);
            });
          } catch (error) {
            console.error("Error generating code completion:", error);
            vscode.window.showErrorMessage(
              `Error generating code completion: ${error}`
            );
          }
        }
      );
    }
  );

  context.subscriptions.push(disposable, completeCodeCommand);
}

// This method is called when your extension is deactivated
export function deactivate() {}
