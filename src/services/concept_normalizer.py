"""Service for normalizing concept names to canonical forms."""
from typing import Dict, Set
import re
import unicodedata


class ConceptNormalizer:
    """Service for normalizing concept names to canonical forms."""

    def __init__(self):
        self.canonical_map: Dict[str, str] = {}
        self.known_concepts: Set[str] = set()

    def normalize(self, concept_name: str) -> str:
        """
        Normalize a concept name to its canonical form.

        Rules:
        - Remove parenthetical acronyms (e.g., "GNN (Graph Neural Network)" → "Graph Neural Network")
        - Normalize to singular form
        - Title case for multi-word concepts
        - Keep acronyms uppercase
        - Remove extra whitespace
        - Use existing canonical form if known

        Args:
            concept_name: Raw concept name to normalize

        Returns:
            Canonical concept name
        """
        # Clean whitespace
        cleaned = " ".join(concept_name.split())

        # Normalize unicode characters (e.g., "Fréchet" → "Frechet")
        # NFD decomposes characters, then filter out combining marks
        cleaned = unicodedata.normalize('NFD', cleaned)
        cleaned = ''.join(char for char in cleaned if unicodedata.category(char) != 'Mn')
        cleaned = unicodedata.normalize('NFC', cleaned)  # Recompose

        # Remove parenthetical content (e.g., "(GNN)", "(Mpnn)")
        # This handles "Graph Neural Network (GNN)" → "Graph Neural Network"
        base_name = re.sub(r'\s*\([^)]*\)', '', cleaned).strip()

        # Create a comparison key (lowercase, singular)
        comparison_key = base_name.lower()

        # Remove trailing 's' for plural normalization (only if word ends with 's' and is >3 chars)
        # "Networks" → "Network", but "Process" stays "Process"
        if comparison_key.endswith('s') and len(comparison_key) > 3:
            singular_key = comparison_key[:-1]
        else:
            singular_key = comparison_key

        # Check if we've seen this before (check both forms)
        if singular_key in self.canonical_map:
            return self.canonical_map[singular_key]
        if comparison_key in self.canonical_map:
            return self.canonical_map[comparison_key]

        # Detect acronyms (all caps, 2-5 letters)
        if re.match(r"^[A-Z]{2,5}$", base_name):
            canonical = base_name
        else:
            # Title case for regular concepts, prefer singular form
            if base_name.lower().endswith('s') and len(base_name) > 3:
                # Use singular form
                canonical = base_name[:-1].title()
            else:
                canonical = base_name.title()

        # Store mappings for both singular and original forms
        self.canonical_map[singular_key] = canonical
        self.canonical_map[comparison_key] = canonical
        self.canonical_map[cleaned.lower()] = canonical  # Original with parentheses
        self.known_concepts.add(canonical)

        return canonical

    def add_alias(self, alias: str, canonical: str) -> None:
        """
        Register an alias for a canonical concept.

        Args:
            alias: Alternative name for the concept
            canonical: Canonical name to map to
        """
        self.canonical_map[alias.lower()] = canonical
        self.known_concepts.add(canonical)
