import { ChatLlamaCpp } from "@langchain/community/chat_models/llama_cpp";

// Load llama model from hugging face url
const llama = ChatLlamaCpp.initialize({
  modelPath: "<path-to-local-model>",
});
