TCM-Agent-Web: Production-Ready RAG Microservice for Traditional Chinese Medicine
An advanced, agentic RAG (Retrieval-Augmented Generation) system built to transform Traditional Chinese Medicine (TCM) knowledge into interactive, personalized diagnostic insights. Powered by Qwen3-Max and optimized for high-concurrency production environments.

🏗 System Architecture
The system utilizes a multi-layered orchestration logic to bridge the gap between unstructured medical knowledge and precise user diagnostics.

🚀 Key Engineering Highlights
1. Agentic RAG & Knowledge Integration
Specialized Knowledge Base: Vectorized 82 high-authority TCM expert entries to ensure factual grounding and eliminate LLM hallucinations.

Semantic Retrieval: Implemented dense vector search to retrieve medical context with high relevance before LLM inference.

2. State-of-the-Art Memory Management
Sliding Window Buffer: Maintains the last 5 conversation turns to provide coherent multi-turn dialogue while minimizing token costs and latency.

Personalized Profiling: Dynamically injects user attributes (age, gender, body constitution) into the system prompt for tailored medical advice.

3. Production-Grade Security & Scaling
Anti-Abuse System: Integrated IP-based rate limiting and device fingerprinting to protect API resources from automated abuse.

Async Orchestration: Built on Flask 3.0 with asynchronous logic to handle streaming responses and high concurrent user sessions.

4. Modern UI/UX & Deployment
Responsive Design: Full support for Mobile, Tablet, and Desktop using modern CSS frameworks.

CI/CD Ready: Fully containerized and optimized for one-click deployment via Render or Docker.

🛠 Tech Stack
Backend: Python 3.9+, Flask 3.0, Asyncio

AI/LLM: Qwen3-Max / OpenAI API compatibility

Security: Redis-based Rate Limiting, Device Fingerprinting

Frontend: Markdown-enabled Reactive UI

Author
Anthony (Hong Dongfang) Senior AI Architect | Ex-CloudWalk Senior Engineer | ACM Regional Silver Medalist
