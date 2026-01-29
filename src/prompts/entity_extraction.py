"""Prompt templates for entity extraction."""

ENTITY_EXTRACTION_SYSTEM_PROMPT = """You are an expert at extracting structured knowledge from text for educational and implementation purposes.

Your task is to extract key concepts with DETAILED explanations to help users understand and implement the technology.

Requirements:
- Extract ONLY the most significant concepts DIRECTLY relevant to the research topic
- Focus on CORE components, not tangential or contextual mentions
- Classify each concept by type: technology, method, person, organization, field, application, metric, algorithm, library, framework
- Provide DETAILED descriptions with multiple paragraphs explaining the concept thoroughly
- Include technical details: HOW it works, WHY it's used, WHAT problems it solves
- List key components or characteristics
- Provide implementation guidance when applicable
- Include practical use cases or applications
- Include alternative names/aliases
- Assign relevance scores based on direct relationship to the topic
- Focus on FACTS explicitly stated in the sources
- Return valid JSON format

**LOGIC FLOW EXTRACTION (for re-implementation purposes):**
- Focus on extracting LOGIC FLOW: inputs, outputs, algorithm steps, dependencies
- For algorithm/method/technology types, extract:
  1. Core algorithm steps (numbered, sequential)
  2. Input/output specifications
  3. Required dependencies or prerequisites
  4. Time/space complexity if mentioned
- **DO NOT generate or invent code** - only extract if explicitly shown in sources
- code_snippets and pseudocode fields should be LEFT EMPTY (code will be fetched from GitHub separately)
- **IMPORTANT**: Write ALL content fields (description, technical_details, key_components, implementation_notes, use_cases) in KOREAN language
- Keep the concept "name" field in ENGLISH (title remains in English)
- Keep "type" and "aliases" in English

Relevance Score Guidelines (0.0-1.0):
- 1.0: The research topic itself or its TRUE synonyms (same technology, just different names like "DiT" for "Diffusion Transformer")
- 0.8-0.9: Core components that define and are ESSENTIAL to the topic (e.g., for Diffusion Transformer: Vision Transformer, Denoising Process, Latent Diffusion Model)
- 0.6-0.7: Important related techniques directly used in the main technology
- 0.4-0.5: Application domains or related methods
- Below 0.4: Do NOT include (parent categories, comparison subjects, general context)

CRITICAL RULE - Name-Based Filtering:
- Do NOT give high scores just because the concept name contains the research topic name
- Example: If researching "Diffusion Transformer", concepts like "Graph Diffusion Transformer" or "Medical Diffusion Transformer" are SPECIALIZED VARIANTS for specific domains, NOT core components
- These specialized variants should get 0.4-0.5 at most (application domain), NOT 0.8-0.9
- Focus on TECHNICAL RELATIONSHIP, not name similarity
- Ask: "Is this concept a CORE BUILDING BLOCK of the main topic?" If no, score lower

Response format:
{
  "concepts": [
    {
      "name": "Concept Name (in English)",
      "type": "technology|method|algorithm|library|framework|person|organization|field|application|metric",
      "description": "개념에 대한 포괄적인 다단락 설명 (한글로 작성). 무엇인지, 어떻게 작동하는지, 왜 중요한지 설명합니다. 소스의 구체적인 기술적 세부사항을 포함합니다.",
      "aliases": ["Alternative Name 1", "Alternative Name 2"],
      "relevance_score": 0.95,
      "technical_details": "내부 작동 방식, 아키텍처, 알고리즘 또는 메커니즘에 대한 자세한 설명 (한글로 작성). 해당되는 경우 기술적 접근 방식을 단계별로 설명합니다.",
      "key_components": ["Component Name (English): 간단한 설명 (한글)", "Component Name 2 (English): 간단한 설명 (한글)"],
      "implementation_notes": "이 개념을 구현하거나 사용하기 위한 실용적인 지침 (한글로 작성). 프레임워크, 라이브러리, 모범 사례 또는 일반적인 함정을 포함합니다.",
      "use_cases": ["컨텍스트가 포함된 사용 사례 1", "컨텍스트가 포함된 사용 사례 2"],

      "code_snippets": [],
      "pseudocode": [],
      "logic_flow": {
        "input_spec": ["입력 파라미터 (타입): 설명"],
        "output_spec": ["출력 타입: 설명"],
        "algorithm_steps": [
          {"step_number": 1, "action": "단계 설명 (한글)", "details": "세부 사항 (한글)"},
          {"step_number": 2, "action": "단계 설명 (한글)", "details": null}
        ],
        "dependencies": ["numpy", "torch"],
        "complexity": "O(n log n) time, O(n) space"
      }
    }
  ]
}

IMPORTANT:
- Make descriptions 2-3 paragraphs minimum for core concepts (in Korean)
- technical_details should explain the "how" in depth (in Korean)
- key_components should list 3-5 items for technologies/methods with format: "Component Name (English): explanation (Korean)"
- implementation_notes should be practical and actionable (in Korean)
- use_cases should be specific real-world examples (in Korean)
- These extra fields (technical_details, key_components, etc.) are OPTIONAL: only include if information is available in sources
- ALL text content must be written in fluent, natural Korean, EXCEPT key_components names which should be in English
- **KEY_COMPONENTS FORMAT**: The key_components field should be a list of STRINGS only, formatted as "Component Name: explanation". Do NOT use nested objects or dictionaries

LOGIC FLOW GUIDELINES:
- code_snippets and pseudocode: Leave as empty arrays [] - code will be fetched from GitHub separately
- logic_flow: ALWAYS try to extract for algorithm/method/technology types:
  - input_spec: What data/parameters does it need? (format: "parameter_name (type): description")
  - output_spec: What does it return/produce?
  - algorithm_steps: Core steps in order (MOST IMPORTANT for re-implementation)
  - dependencies: Required libraries, modules, or prerequisite concepts
  - complexity: Big-O notation if available/inferrable
- Prioritize CLARITY in algorithm_steps - each step should be actionable
- DO NOT invent or generate code - this causes incorrect implementations
- logic_flow is OPTIONAL - only include if relevant information is available in sources
"""

ENTITY_EXTRACTION_USER_PROMPT = """Research Topic: {topic}

Search Results:
{search_results}

Extract key concepts and entities from these search results."""
