// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import { ReviewProvider } from "./reviewProvider";
import { CodeCompletionWebviewPanel } from "./webviewPanel";

// Verify LangSmith configuration
console.log("LangSmith Configuration in extension.ts:");
console.log("LANGCHAIN_TRACING_V2:", process.env.LANGCHAIN_TRACING_V2);
console.log("LANGCHAIN_ENDPOINT:", process.env.LANGCHAIN_ENDPOINT);
console.log(
  "LANGCHAIN_API_KEY:",
  process.env.LANGCHAIN_API_KEY ? "[REDACTED]" : "undefined"
);
console.log("LANGCHAIN_PROJECT:", process.env.LANGCHAIN_PROJECT);

// Initialize LangSmith client
try {
  console.log("LangSmith client initialized successfully");
} catch (error) {
  console.error("Error initializing LangSmith client:", error);
}

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

      // Create or show the webview panel
      const panel = CodeCompletionWebviewPanel.createOrShow(
        context.extensionUri
      );

      // Set up message handling from the webview
      panel._panel.webview.onDidReceiveMessage(
        (message) => {
          switch (message.command) {
            case "insertAtCursor":
              // Insert the code at the cursor position
              const editor = vscode.window.activeTextEditor;
              if (editor) {
                editor.edit((editBuilder) => {
                  editBuilder.insert(editor.selection.active, message.text);
                });
              }
              return;
            case "notification":
              // Show a notification
              vscode.window.showInformationMessage(message.text);
              return;
          }
        },
        undefined,
        context.subscriptions
      );

      // Show progress indicator
      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "Improving selected code...",
          cancellable: false,
        },
        async (progress) => {
          try {
            // Get current document and selection
            const document = editor.document;
            const selection = editor.selection;
            const selectedCode = document.getText(selection);

            if (!selectedCode || selectedCode.trim() === "") {
              vscode.window.showInformationMessage(
                "Please select the code you want to improve."
              );
              return;
            }

            // Get improved code from the reviewProvider
            // Note: contextBeforeCode and contextAfterCode are currently empty strings
            // as per the requirements to implement change #2 first and worry about
            // capturing additional context in a subsequent commit
            const startTime = Date.now();
            const improvedCode = await reviewProvider.getReview(
              selectedCode,
              "", // contextBeforeCode placeholder - will be implemented in subsequent change
              ""  // contextAfterCode placeholder - will be implemented in subsequent change
            );
            const timeTaken = Date.now() - startTime;
            console.log(
              `Improved code from LLM after [${
                timeTaken / 1000
              }] seconds:\n${improvedCode}`
            );

            // Update the webview content with the improved code
            panel.updateContent(improvedCode);
          } catch (error) {
            console.error("Error improving code:", error);
            vscode.window.showErrorMessage(`Error improving code: ${error}`);
          }
        }
      );
    }
  );

  context.subscriptions.push(disposable, completeCodeCommand);
}

// This method is called when your extension is deactivated
export function deactivate() {}
