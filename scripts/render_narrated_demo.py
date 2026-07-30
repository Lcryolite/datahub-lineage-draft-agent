#!/usr/bin/env python3
"""Render a reviewable narrated demo from checked-in project evidence.

The narrator text contains no credentials or private data. The output is a
local draft and must be reviewed before any public upload.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".artifacts" / "lineage-draft-agent-narrated-demo-draft.mp4"
FONT = subprocess.check_output(["fc-match", "-f", "%{file}", "monospace"], text=True).splitlines()[0]

SLIDES = [
    (
        "Lineage Draft Agent",
        "A review-only migration draft grounded in DataHub metadata.\n\nNo warehouse access. No executed migration.",
        "Data migrations often start with incomplete context. Lineage Draft Agent reads catalog evidence before drafting a dbt-style transformation. It produces a review packet, not an executed migration.",
    ),
    (
        "The DataHub context path",
        "Official MCP tools used by the agent:\n\nget_entities    list_schema_fields    get_lineage\n\nGraphQL remains a constrained fallback for offline environments.",
        "For the hackathon path, the project starts the official DataHub MCP server and calls get entities, list schema fields, and get lineage. These calls provide the dataset name, real fields, and upstream evidence used by the draft.",
    ),
    (
        "End-to-end MCP evidence",
        "GitHub Actions run 30581519213 passed:\n\nofficial quickstart → public showcase data → official MCP server → review draft\n\nA real dataset with 11 fields was read. No migration was executed.",
        "The full integration runs in a clean GitHub runner. It starts official DataHub quickstart, loads public showcase data, waits for the search index, then reads a real dataset through the official MCP server before creating a review-only draft.",
    ),
    (
        "Repeatable offline rehearsal",
        "OFFLINE FIXTURE ONLY\n\npython scripts/offline_demo.py\n\nOutput records a dataset URN, schema-derived SQL, upstream lineage, and reviewed: false.",
        "For a safe recording rehearsal, the repository also includes an explicitly labelled offline fixture. It exercises the same GraphQL parsing and draft logic without a network request. The output remains marked reviewed false and never executes SQL.",
    ),
    (
        "Human review is the decision point",
        "Every draft begins with REVIEW REQUIRED.\n\nReviewers can inspect the dataset URN and lineage\nbefore deciding whether any migration should run.",
        "The point is traceability, not autonomous change. Every generated SQL draft begins with review required and carries the catalog evidence a reviewer needs before approving any downstream migration.",
    ),
]


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def render_slide(path: Path, title: str, body: str) -> None:
    run(
        "magick", "-size", "1920x1080", "xc:#101827", "-font", FONT,
        "-fill", "#f8fafc", "-gravity", "north", "-pointsize", "60", "-annotate", "+0+118", title,
        "-fill", "#cbd5e1", "-gravity", "center", "-pointsize", "34", "-annotate", "+0+70", body,
        "-fill", "#94a3b8", "-gravity", "south", "-pointsize", "24", "-annotate", "+0+70",
        "LOCAL DRAFT — review before public upload", str(path),
    )


def main() -> None:
    try:
        import edge_tts  # noqa: F401
    except ImportError as error:
        raise SystemExit("Install optional narration support: pip install edge-tts") from error

    OUTPUT.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        segments: list[Path] = []
        for index, (title, body, narration) in enumerate(SLIDES, start=1):
            image = work / f"{index:02d}.png"
            audio = work / f"{index:02d}.mp3"
            segment = work / f"{index:02d}.mp4"
            render_slide(image, title, body)
            run(sys.executable, "-m", "edge_tts", "--voice", "en-US-AvaMultilingualNeural", "--text", narration, "--write-media", str(audio))
            run("ffmpeg", "-y", "-loop", "1", "-i", str(image), "-i", str(audio), "-shortest", "-r", "30", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", str(segment))
            segments.append(segment)
        manifest = work / "segments.txt"
        manifest.write_text("".join(f"file '{path}'\n" for path in segments))
        run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest), "-c", "copy", "-movflags", "+faststart", str(OUTPUT))
    print(f"Rendered {OUTPUT}")


if __name__ == "__main__":
    main()
