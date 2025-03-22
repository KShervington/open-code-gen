import { Ollama } from "@langchain/ollama";
import { performance } from "perf_hooks";

async function testInferenceSpeed(modelName, prompt) {
  const model = new Ollama({ model: modelName });

  const start = performance.now();
  const response = await model.invoke(prompt);
  const end = performance.now();

  const inferenceTime = end - start;

  return inferenceTime;
}

// Tests for starcoder2, codellama, and qwen2.5-coder models
const modelName = "qwen2.5-coder:7b";
const prompt = "function helloWorld() {";
const numTrials = 20;
let timeTracker = [];

for (let i = 0; i < numTrials; i++) {
  timeTracker.push(testInferenceSpeed(modelName, prompt).catch(console.error));
}

// Get average time from timeTracker
Promise.all(timeTracker).then((times) => {
  const averageTime = times.reduce((a, b) => a + b) / times.length;
  console.log("Average inference time: ", averageTime / 1000);
});
