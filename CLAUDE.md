# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Automated Research & Knowledge Graph**: A system using OpenAI/LangGraph to run web searches, extract concepts, infer relations, and produce Logseq-compatible markdown files for knowledge graph creation.

### Current Status
This is a new project with no implementation yet. The codebase will be built using Python with LangGraph for workflow orchestration.

## Core Requirements

### Web Search Integration
- **Always use web search API** before answering factual or investigatory requests
- Use Brave Search API for retrieving top results
- Generate search queries automatically based on research topics

### Data Processing Rules
- **Separate facts vs. inferences clearly** in all outputs
- **Include source URLs with every fact** - this is mandatory
- Extract entities and relationships from search results
- Use canonical concept naming consistently

### Output Format
- Generate Logseq `.md` files with concept pages and relations
- Use wikilink format: `[[Concept Name]]` for all concept references
- Include source citations with every factual claim
- Write in clear, concise markdown
- Group related concepts under proper headings

## Intended Architecture

### Technology Stack
- **Python** as the primary language
- **LangGraph** for orchestrating the agent workflow
- **OpenAI API** for LLM capabilities
- **Brave Search API** for web search functionality

### Workflow Pipeline
1. **Query Generation**: Automatically generate search queries from research topics
2. **Web Search**: Call Brave Search API for top results
3. **Entity Extraction**: Parse search results to extract concepts and entities
4. **Relationship Inference**: Identify and infer relationships between concepts
5. **Markdown Generation**: Format output as Logseq-compatible markdown with wikilinks

### LangGraph Implementation
- Use LangGraph to orchestrate multi-step research workflow
- Implement state management for tracking research progress
- Create nodes for each workflow step (search, extraction, inference, formatting)
- Use conditional edges for dynamic workflow branching

## Style Guidelines

- Use clear, concise markdown formatting
- Maintain consistent wikilink syntax: `[[Concept]]`
- Always cite sources as URLs
- Group related information under appropriate headings
- Distinguish between extracted facts and inferred relationships
