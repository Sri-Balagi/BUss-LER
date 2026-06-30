# AI Kernel Architecture

The BizOS AI Kernel is the capability-oriented AI platform for the entire operating system. It serves as the single abstraction layer above any underlying AI provider (e.g., Gemini, OpenAI, Local models), ensuring that business logic services never interact with provider SDKs directly.

## 1. Core Principles

- **Capability-Based**: The AI Kernel exposes what it can *do* (`generate()`, `embed()`, `summarize()`) rather than how it does it. Future capabilities (`plan()`, `reason()`, `simulate()`) will be added to the interface as the system evolves.
- **Provider Agnostic**: The AI Kernel uses Domain Models (`AIRequest`, `AIResponse`, `EmbeddingRequest`, `EmbeddingResponse`) to move data between the system and the provider.
- **No Embedded Prompts**: Business logic contains no AI instructions. Prompts are managed centrally via the `PromptManager`.
- **Strict Logging Isolation**: Operational logs record latencies, tokens, and errors. Prompts and generation outputs are never written to production logs.

## 2. Components

### 2.1 Provider Registry (`ProviderRegistry`)
Owns all registered providers. A provider is any class implementing the `AbstractAIProvider` interface (e.g., `GeminiProvider`). When the application starts up, providers are instantiated (validating API keys) and loaded into the registry.

### 2.2 Provider Router (`ProviderRouter`)
Selects the appropriate provider for a given request. Currently, this routes to a default provider. In the future, this can be expanded to route based on requested capabilities (e.g., routing complex planning to Gemini 2.5 Pro and rapid embeddings to Gemini Flash or a Local model).

### 2.3 Prompt Manager (`PromptManager`)
Maintains versioned prompt templates.
```python
"memory_summarization": {
    "v1": "Summarize the following memory in one clear, concise sentence..."
}
```
Services request prompts using an ID (`"memory_summarization"`) and context dictionary. The manager interpolates the variables safely before passing it to the provider.

### 2.4 AbstractAIKernel
The primary entrypoint injected into consumers like the `MemoryService`.

## 3. Request Lifecycle

1. **Service Calls Kernel**: `MemoryService` requests a summarization by passing an `AIRequest(prompt_id="memory_summarization", context={...})`.
2. **Prompt Resolution**: `AIKernel` asks `PromptManager` to fully resolve the template text.
3. **Provider Routing**: `AIKernel` asks `ProviderRouter` for the active provider.
4. **Execution**: The chosen `AbstractAIProvider` (e.g. `GeminiProvider`) transforms the request into SDK-specific calls, executing the prompt over the network.
5. **Normalization**: The provider receives the SDK response and normalizes it into an `AIResponse` containing the text and `AIResponseMetadata` (latency, tokens, provider name).
6. **Logging**: `AIKernel` logs the metadata structurally.
7. **Return**: The `AIResponse` is returned to the `MemoryService`.

## 4. Exception Translation

All SDK-specific exceptions (e.g., Google `APIError`, `ClientError`) are caught within the Provider implementations and re-raised as `AIKernelError` or `ProviderConfigurationError`. This prevents infrastructure leakage into the business domains.

## 5. Future Extensibility

- **New Providers**: Adding OpenAI or Claude simply requires writing a new class implementing `AbstractAIProvider` and registering it in `dependencies.py`.
- **BizOS Foundation Models**: When internal custom models are deployed, they will be registered similarly.
- **Local Runtimes**: For off-grid capabilities, a local LLM provider can be integrated transparently.
