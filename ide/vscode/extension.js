// Minimal VS Code extension: a Copilot-style inline completion provider plus a
// "Review Selection" command, both backed by the internal sovereign gateway.
// No bundler needed — uses Node's global fetch (VS Code ships Node 18+).
const vscode = require("vscode");

function gatewayUrl() {
  return vscode.workspace.getConfiguration("sovereign").get("gatewayUrl", "http://localhost:8080");
}

// Inline completion (fill-in-middle) via /v1/completions — the Copilot alternative.
const inlineProvider = {
  async provideInlineCompletionItems(document, position) {
    const prefix = document.getText(new vscode.Range(new vscode.Position(0, 0), position));
    const suffix = document.getText(
      new vscode.Range(position, document.lineAt(document.lineCount - 1).range.end)
    );
    try {
      const resp = await fetch(`${gatewayUrl()}/v1/completions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: "code-gen", prompt: prefix, suffix, max_tokens: 64 }),
      });
      if (!resp.ok) return { items: [] };
      const data = await resp.json();
      const text = (data.choices && data.choices[0] && data.choices[0].text) || "";
      return text ? { items: [{ insertText: text, range: new vscode.Range(position, position) }] } : { items: [] };
    } catch (_e) {
      return { items: [] };
    }
  },
};

async function reviewSelection() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) return;
  const code = editor.document.getText(editor.selection) || editor.document.getText();
  const resp = await fetch(`${gatewayUrl()}/v1/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Sovereign-Task": "code-review" },
    body: JSON.stringify({
      model: "code-review",
      messages: [{ role: "user", content: `Review this code for bugs and issues:\n\n${code}` }],
    }),
  });
  const data = await resp.json();
  const review = data.choices?.[0]?.message?.content ?? "No review returned.";
  const doc = await vscode.workspace.openTextDocument({ content: review, language: "markdown" });
  vscode.window.showTextDocument(doc, { viewColumn: vscode.ViewColumn.Beside });
}

function activate(context) {
  context.subscriptions.push(
    vscode.languages.registerInlineCompletionItemProvider({ pattern: "**" }, inlineProvider),
    vscode.commands.registerCommand("sovereign.reviewSelection", reviewSelection)
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
