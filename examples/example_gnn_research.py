"""Example: Research GNN (Graph Neural Networks)"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import run_research


def main():
    """Run research on GNN topic."""

    topic = "GNN"

    print(f"Researching topic: {topic}")
    print("=" * 50)

    try:
        output_path = run_research(topic)

        print("\n" + "=" * 50)
        print("Research Complete!")
        print(f"Output: {output_path}")
        print("\nGenerated files:")

        output_dir = Path(output_path).parent
        for md_file in sorted(output_dir.glob("*.md")):
            print(f"  - {md_file.name}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
