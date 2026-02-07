<!--
Sync Impact Report:
- Version change: 1.0.0 → 2.0.0 (MAJOR: Complete rewrite for AI-Powered Todo Chatbot with new principles)
- Modified principles: All principles completely revised for AI Chatbot context
- Added sections: AI Agent Architecture, MCP Integration, Conversation State Management
- Removed sections: Previous generic template principles
- Templates requiring updates: ✅ Updated .specify/templates/plan-template.md / ✅ Updated .specify/templates/spec-template.md / ✅ Updated .specify/templates/tasks-template.md
- Follow-up TODOs: None
-->

# Phase III: AI-Powered Todo Chatbot Constitution

## Core Principles

### I. AI-First Architecture
Every feature must be designed for natural language interaction; AI agents must interpret user intents accurately, provide conversational feedback, and maintain context across interactions; All functionality accessible through both programmatic and natural language interfaces.

### II. MCP-Driven Operations
All backend operations must be implemented as standardized MCP tools; Tool contracts must be well-defined with consistent parameter and return structures; MCP tools serve as the single source of truth for all business logic and data operations.

### III. Stateless Design (NON-NEGOTIABLE)
All services must be stateless with no server-side session storage; All conversation context must be retrieved from persistent storage on each request; State recovery mechanisms must be implemented to support horizontal scalability.

### IV. Sub-Agent Orchestration
Complex operations must be delegated to specialized sub-agents; Master agent orchestrates tool calls and manages agent coordination; Skill composition must be modular and reusable across different interaction flows.

### V. Conversation Context Preservation
All conversation history must be persisted in Neon PostgreSQL; Message ordering and context relationships must be maintained; Conversation state must be recoverable to ensure continuity across sessions.

### VI. Reusable Intelligence
Business logic from Phase II must be leveraged and extended; Common patterns and utilities must be abstracted for cross-component reuse; Intelligence layers must build upon existing foundations rather than duplicating functionality.

## AI Agent Architecture Requirements

All agent implementations must follow the defined architecture:
- Master agent interprets natural language and routes to sub-agents
- Task agent handles CRUD operations through MCP tools
- Conversation agent manages history retrieval and storage
- Skill agent provides confirmations, error handling, and optimizations

Natural language command mapping must be comprehensive and intuitive, supporting the defined command patterns with proper parameter extraction and validation.

## MCP Integration Standards

MCP tools must adhere to strict contract definitions:
- Consistent parameter validation and error handling
- Proper return types with status indicators
- Reuse of Phase II business logic where applicable
- Clear separation between AI interpretation and business logic

## Conversation Flow Management

Stateless conversation flow must follow the 9-step process:
1. Receive user message from ChatKit UI
2. Fetch conversation history from DB
3. Build message array (history + new message)
4. Store user message in DB
5. Master agent invokes sub-agents
6. Task agent calls MCP tools as needed
7. Skill agent adds confirmations/errors
8. Store assistant response in DB
9. Return response + tool_calls to client

## Technology Stack Compliance

Frontend must use OpenAI ChatKit with Vercel/GitHub Pages deployment;
Backend must implement Python FastAPI with OpenAI Agents SDK and Official MCP SDK;
Database layer must use SQLModel with Neon Serverless PostgreSQL;
Authentication must leverage Better Auth with Phase II model reuse.

## Governance

All implementations must comply with this constitution; Code reviews must verify adherence to AI-first, MCP-driven, and stateless principles; New features must extend existing intelligence rather than duplicating functionality; Architecture decisions must align with agent orchestration patterns.

**Version**: 2.0.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-07