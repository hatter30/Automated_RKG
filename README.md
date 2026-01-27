# Automated Research & Knowledge Graph System

Automated research system using OpenAI + Brave Search API + LangGraph to generate Logseq-compatible knowledge graphs.

## Overview

This system takes a research topic (e.g., "GNN") and automatically:
1. Generates diverse search queries
2. Executes web searches via Brave Search API
3. Extracts concepts and entities from results
4. Infers relationships between concepts
5. Generates Logseq-compatible markdown files with wikilinks

## Features

- **Web Search Integration**: Brave Search API for retrieving top results
- **LLM-Powered Extraction**: OpenAI for concept extraction and relationship inference
- **Fact vs Inference Separation**: Clearly distinguishes facts (with citations) from inferred knowledge
- **Logseq Format**: Generates markdown with wikilinks (`[[Concept]]`) for knowledge graph visualization
- **Source Citations**: Every fact includes source URLs

## Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Brave Search API key

### Setup

1. Clone the repository:
```bash
cd Automated_RKG
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Add your API keys to `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here
```

## API Keys

### OpenAI API
Get your key at: https://platform.openai.com/api-keys

### Brave Search API
Get your key at: https://brave.com/search/api/

## Usage

### Basic Usage

```bash
python -m src.main "GNN"
```

### Custom Output Directory

```bash
python -m src.main "Graph Neural Networks" --output-dir custom/output
```

### Python API

```python
from src.main import run_research

output_path = run_research("GNN")
print(f"Generated at: {output_path}")
```

## Output Format

The system generates Logseq-compatible markdown files:

### Main Topic Page (`GNN.md`)
```markdown
# GNN

*Research conducted: 2026-01-28*

## Key Concepts
### Technologies
- [[GNN]]
- [[Graph Convolutional Network]]

### Methods
- [[Message Passing]]

## Relationships

### Facts (Extracted from Sources)
- **Fact**: [[GNN]] uses [[Message Passing]]
  - Sources: [Title](https://url)

### Inferred Relationships
- **Inferred**: [[GNN]] is_a [[Neural Network]]

## Sources
- [Source Title](https://url)
```

### Individual Concept Pages
Each concept gets its own page with:
- Description
- Aliases
- Related concepts
- Source citations

## Project Structure

```
Automated_RKG/
├── config/              # Configuration management
├── src/
│   ├── models/         # Data models (Concept, Relationship, etc.)
│   ├── graph/          # LangGraph workflow and nodes
│   ├── services/       # API services (OpenAI, Brave Search)
│   ├── prompts/        # LLM prompt templates
│   └── utils/          # Utilities
├── output/logseq/      # Generated markdown files
└── requirements.txt
```

## Configuration

Edit `.env` to customize:

```env
# Model selection
OPENAI_MODEL=gpt-4-turbo-preview

# Search settings
MAX_SEARCH_RESULTS=10
MAX_QUERIES_PER_TOPIC=5

# Output
OUTPUT_DIR=output/logseq

# Logging
LOG_LEVEL=INFO
```

## Example: GNN Research

```bash
python -m src.main "GNN"
```

**Expected Output:**
- 10-20 concepts extracted (GNN, GCN, Message Passing, etc.)
- 15-30 relationships identified
- Clear separation of facts vs inferences
- All facts include source URLs
- Logseq-compatible markdown format

## Workflow Pipeline

```
Query Generation → Web Search → Entity Extraction → Relationship Inference → Markdown Generation
```

1. **Query Generation**: Generates 3-5 diverse search queries using OpenAI
2. **Web Search**: Executes searches via Brave Search API
3. **Entity Extraction**: Extracts concepts with types and descriptions
4. **Relationship Inference**: Identifies connections between concepts
5. **Markdown Generation**: Creates Logseq-compatible output

## Troubleshooting

### API Key Issues
- Verify your API keys are correct in `.env`
- Check you have sufficient credits/quota

### No Results
- Try a more specific research topic
- Check your internet connection
- Verify Brave Search API is accessible

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (must be 3.10+)

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
ruff check src/
```

### Type Checking
```bash
mypy src/
```

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
