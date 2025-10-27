"""
Migration Guide: Python (LangGraph) → Java (LangChain4j)

This document outlines the step-by-step process for migrating
the telecom support system from Python to Java.
"""

# ============================================================================
# PHASE 1: FOUNDATION SETUP
# ============================================================================

"""
1.1 Project Structure (Java)
-----------------------------

com.telecom.support/
├── config/
│   └── ApplicationConfig.java      # Settings management
├── state/
│   └── ConversationState.java      # State POJO
├── router/
│   └── RouterAgent.java            # Classification
├── agents/
│   ├── TechnicalAgent.java         # RAG agent
│   ├── BillingAgent.java           # Tool-calling agent
│   └── FallbackAgent.java          # Clarification
├── retriever/
│   └── TechnicalRetriever.java     # OpenSearch retriever
├── tools/
│   └── BillingTools.java           # Tool definitions
├── graph/
│   └── SupportGraph.java           # LangChain4j graph
└── api/
    └── SupportController.java      # Spring Boot REST

pom.xml                             # Maven dependencies


1.2 Dependencies (pom.xml)
--------------------------

<dependencies>
    <!-- LangChain4j Core -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j</artifactId>
        <version>0.27.0</version>
    </dependency>
    
    <!-- LangChain4j OpenAI -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-open-ai</artifactId>
        <version>0.27.0</version>
    </dependency>
    
    <!-- LangChain4j OpenSearch -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-opensearch</artifactId>
        <version>0.27.0</version>
    </dependency>
    
    <!-- Spring Boot -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <version>3.2.0</version>
    </dependency>
    
    <!-- Redis (for session management) -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-redis</artifactId>
        <version>3.2.0</version>
    </dependency>
</dependencies>
"""

# ============================================================================
# PHASE 2: STATE MANAGEMENT
# ============================================================================

"""
2.1 ConversationState.java
--------------------------

package com.telecom.support.state;

import java.util.ArrayList;
import java.util.List;

public class ConversationState {
    private List<Message> messages;
    private String userId;
    private String currentCategory;
    private String lastAgent;
    private boolean needsClarification;
    private String retrievedContext;
    private int turnCount;
    
    // Constructors
    public ConversationState() {
        this.messages = new ArrayList<>();
        this.turnCount = 0;
    }
    
    // Getters and Setters
    public List<Message> getMessages() { return messages; }
    public void setMessages(List<Message> messages) { this.messages = messages; }
    
    public void addMessage(Message message) {
        this.messages.add(message);
    }
    
    // ... other getters/setters
    
    // Factory method
    public static ConversationState create(String userId, String initialMessage) {
        ConversationState state = new ConversationState();
        state.setUserId(userId);
        state.addMessage(new Message("human", initialMessage));
        return state;
    }
}


2.2 Message.java
----------------

package com.telecom.support.state;

public class Message {
    private String type;  // "human", "ai", "system", "tool"
    private String content;
    private String toolCallId;  // For tool messages
    
    public Message(String type, String content) {
        this.type = type;
        this.content = content;
    }
    
    // Getters and setters
}
"""

# ============================================================================
# PHASE 3: ROUTER AGENT
# ============================================================================

"""
3.1 RouterAgent.java
--------------------

package com.telecom.support.router;

import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import com.fasterxml.jackson.databind.ObjectMapper;

public class RouterAgent {
    private final OpenAiChatModel chatModel;
    private final String systemPrompt;
    private final ObjectMapper objectMapper;
    
    public RouterAgent(OpenAiChatModel chatModel) {
        this.chatModel = chatModel;
        this.systemPrompt = loadSystemPrompt();
        this.objectMapper = new ObjectMapper();
    }
    
    public String classify(String userMessage) {
        List<ChatMessage> messages = Arrays.asList(
            SystemMessage.from(systemPrompt),
            UserMessage.from(userMessage)
        );
        
        String response = chatModel.generate(messages).content().text();
        
        // Parse JSON response
        try {
            JsonNode json = objectMapper.readTree(response);
            return json.get("category").asText();
        } catch (Exception e) {
            return "other";  // Fallback
        }
    }
    
    public ConversationState execute(ConversationState state) {
        String lastMessage = state.getMessages()
            .get(state.getMessages().size() - 1)
            .getContent();
        
        String category = classify(lastMessage);
        
        state.setCurrentCategory(category);
        state.setLastAgent("router");
        state.setTurnCount(state.getTurnCount() + 1);
        
        return state;
    }
    
    private String loadSystemPrompt() {
        // Load from resources/prompts/router_system_prompt.txt
        // Implementation omitted for brevity
    }
}
"""

# ============================================================================
# PHASE 4: TECHNICAL AGENT (RAG)
# ============================================================================

"""
4.1 TechnicalRetriever.java
---------------------------

package com.telecom.support.retriever;

import dev.langchain4j.store.embedding.opensearch.OpenSearchEmbeddingStore;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.segment.TextSegment;

public class TechnicalRetriever {
    private final OpenSearchEmbeddingStore embeddingStore;
    private final EmbeddingModel embeddingModel;
    
    public TechnicalRetriever(
        OpenSearchEmbeddingStore store,
        EmbeddingModel model
    ) {
        this.embeddingStore = store;
        this.embeddingModel = model;
    }
    
    public List<Document> retrieveContext(String query, int k) {
        // Embed query
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        
        // Search
        List<EmbeddingMatch<TextSegment>> matches = 
            embeddingStore.findRelevant(queryEmbedding, k);
        
        // Convert to documents
        return matches.stream()
            .map(match -> new Document(match.embedded().text()))
            .collect(Collectors.toList());
    }
    
    public String formatContext(List<Document> documents) {
        StringBuilder context = new StringBuilder();
        for (int i = 0; i < documents.size(); i++) {
            context.append(String.format(
                "[Source %d]\n%s\n\n---\n\n",
                i + 1,
                documents.get(i).text()
            ));
        }
        return context.toString();
    }
}


4.2 TechnicalAgent.java
-----------------------

package com.telecom.support.agents;

import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.data.message.*;

public class TechnicalAgent {
    private final OpenAiChatModel chatModel;
    private final TechnicalRetriever retriever;
    private final String systemPrompt;
    
    public ConversationState execute(ConversationState state) {
        String userQuestion = state.getMessages()
            .get(state.getMessages().size() - 1)
            .getContent();
        
        // Retrieve context
        List<Document> docs = retriever.retrieveContext(userQuestion, 3);
        String context = retriever.formatContext(docs);
        
        // Build prompt
        String formattedPrompt = systemPrompt
            .replace("{context}", context)
            .replace("{question}", userQuestion);
        
        // Generate response
        List<ChatMessage> messages = Arrays.asList(
            SystemMessage.from(formattedPrompt),
            UserMessage.from(userQuestion)
        );
        
        String answer = chatModel.generate(messages).content().text();
        
        // Update state
        state.addMessage(new Message("ai", answer));
        state.setRetrievedContext(context);
        state.setLastAgent("technical");
        
        return state;
    }
}
"""

# ============================================================================
# PHASE 5: BILLING AGENT (TOOLS)
# ============================================================================

"""
5.1 BillingTools.java
---------------------

package com.telecom.support.tools;

import dev.langchain4j.agent.tool.Tool;

public class BillingTools {
    
    @Tool("Retrieve current subscription plan for a user")
    public String getSubscription(String userId) {
        // Implementation
        // Call actual billing API
        return "{ \"plan\": \"Premium 5G\", \"cost\": 89.99 }";
    }
    
    @Tool("Create a refund case in the billing system")
    public String openRefundCase(
        String userId,
        String reason,
        Double amount
    ) {
        // Implementation
        return "{ \"case_id\": \"REF-1001\", \"status\": \"pending\" }";
    }
    
    @Tool("Get the complete refund policy document")
    public String getRefundPolicy() {
        // Implementation
        return "Our refund policy...";
    }
}


5.2 BillingAgent.java
---------------------

package com.telecom.support.agents;

import dev.langchain4j.service.AiServices;
import dev.langchain4j.model.openai.OpenAiChatModel;

interface BillingService {
    String answer(String userMessage);
}

public class BillingAgent {
    private final BillingService service;
    
    public BillingAgent(OpenAiChatModel chatModel, BillingTools tools) {
        this.service = AiServices.builder(BillingService.class)
            .chatLanguageModel(chatModel)
            .tools(tools)
            .build();
    }
    
    public ConversationState execute(ConversationState state) {
        String userMessage = state.getMessages()
            .get(state.getMessages().size() - 1)
            .getContent();
        
        String answer = service.answer(userMessage);
        
        state.addMessage(new Message("ai", answer));
        state.setLastAgent("billing");
        
        return state;
    }
}
"""

# ============================================================================
# PHASE 6: GRAPH ORCHESTRATION
# ============================================================================

"""
6.1 SupportGraph.java
---------------------

package com.telecom.support.graph;

public class SupportGraph {
    private final RouterAgent router;
    private final TechnicalAgent technical;
    private final BillingAgent billing;
    private final FallbackAgent fallback;
    
    public ConversationState execute(ConversationState state) {
        // Step 1: Route
        state = router.execute(state);
        
        // Step 2: Conditional execution
        String category = state.getCurrentCategory();
        
        switch (category) {
            case "technical":
                state = technical.execute(state);
                break;
            case "billing":
                state = billing.execute(state);
                break;
            case "other":
            default:
                state = fallback.execute(state);
                break;
        }
        
        return state;
    }
}
"""

# ============================================================================
# PHASE 7: REST API (SPRING BOOT)
# ============================================================================

"""
7.1 SupportController.java
--------------------------

package com.telecom.support.api;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class SupportController {
    private final SupportGraph graph;
    private final SessionManager sessionManager;
    
    @PostMapping("/chat")
    public ChatResponse chat(@RequestBody ChatRequest request) {
        // Get or create session
        ConversationState state = sessionManager.getOrCreate(
            request.getThreadId(),
            request.getUserId()
        );
        
        // Add user message
        state.addMessage(new Message("human", request.getMessage()));
        
        // Execute graph
        state = graph.execute(state);
        
        // Save state
        sessionManager.save(request.getThreadId(), state);
        
        // Extract response
        String response = state.getMessages()
            .get(state.getMessages().size() - 1)
            .getContent();
        
        return new ChatResponse(
            response,
            request.getThreadId(),
            state.getLastAgent(),
            state.getCurrentCategory()
        );
    }
}
"""

# ============================================================================
# PHASE 8: DEPLOYMENT
# ============================================================================

"""
8.1 Docker Compose (docker-compose.yml)
---------------------------------------

version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENSEARCH_URL=http://opensearch:9200
      - REDIS_URL=redis://redis:6379
    depends_on:
      - opensearch
      - redis
  
  opensearch:
    image: opensearchproject/opensearch:2.11.0
    ports:
      - "9200:9200"
    environment:
      - discovery.type=single-node
      - DISABLE_SECURITY_PLUGIN=true
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"


8.2 Dockerfile
--------------

FROM openjdk:17-slim

WORKDIR /app

COPY target/telecom-support-*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
"""

# ============================================================================
# MIGRATION CHECKLIST
# ============================================================================

"""
□ Phase 1: Foundation
  □ Maven project setup
  □ Dependencies configured
  □ Application properties

□ Phase 2: Data Models
  □ ConversationState POJO
  □ Message class
  □ Request/Response DTOs

□ Phase 3: Router
  □ RouterAgent implementation
  □ JSON parsing
  □ System prompt loading

□ Phase 4: Technical Agent
  □ OpenSearch setup
  □ Document embedding
  □ TechnicalRetriever
  □ TechnicalAgent with RAG

□ Phase 5: Billing Agent
  □ Tool definitions with @Tool
  □ BillingService interface
  □ Tool calling via AiServices

□ Phase 6: Orchestration
  □ SupportGraph implementation
  □ Conditional routing
  □ State management

□ Phase 7: API
  □ Spring Boot REST controller
  □ Redis session management
  □ Error handling

□ Phase 8: Deployment
  □ Docker containerization
  □ OpenSearch migration
  □ CI/CD pipeline
  □ Monitoring setup
"""

# ============================================================================
# KEY DIFFERENCES: PYTHON vs JAVA
# ============================================================================

"""
1. Type System
   Python: Duck typing, runtime checks
   Java: Static typing, compile-time checks
   → Benefit: Catch errors earlier in Java

2. Async/Await
   Python: Native async/await with asyncio
   Java: CompletableFuture or reactive (Reactor/RxJava)
   → Migration: Synchronous first, optimize later

3. Tool Calling
   Python: LangChain decorators
   Java: @Tool annotations with AiServices
   → Very similar patterns!

4. Vector Store
   Python: FAISS (in-memory)
   Java: OpenSearch (distributed)
   → Better scalability in Java

5. State Management
   Python: MemorySaver (in-process)
   Java: Redis (distributed)
   → Better for multi-instance deployments

6. Configuration
   Python: python-dotenv + Pydantic
   Java: Spring @ConfigurationProperties
   → More robust validation in Java
"""

print(__doc__)
