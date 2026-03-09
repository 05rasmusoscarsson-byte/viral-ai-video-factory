"""
orchestrator.py

Minimal orchestrator for a TikTok viral video factory pipeline.

Pipeline:
    Agent 01 -> Script Generator
    Agent 02 -> Voice Generator          (placeholder)
    Agent 03 -> Visual Segment Builder   (placeholder)
    Agent 04 -> Subtitle Generator       (placeholder)
    Agent 05 -> Video Composer           (placeholder)
    Agent 06 -> Publisher / Exporter     (placeholder)

Goals:
- Simple
- Production-ready structure
- Easy to extend
- Clean error handling
- JSON artifact storage
"""

from __future__ import annotations

import json
import logging
import os
import traceback
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Import Agent 01 from your existing module.
# Assumes this file is in the same project/package.
from agent_01_script_generator import (
    Agent01ScriptGenerator,
    ScriptGeneratorConfig,
)

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("tiktok_factory.orchestrator")

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------

@dataclass
class Config:
    """
    Central config for the pipeline.

    Reads API keys from environment by default.
    Extend this as more agents become real.
    """
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    elevenlabs_api_key: Optional[str] = os.getenv("ELEVENLABS_API_KEY")

    base_output_dir: str = "outputs"
    pipeline_name: str = "tiktok_video_factory"

    # Agent 01 config
    agent_01_model: str = "gpt-4.1"
    agent_01_max_retries: int = 5
    agent_01_timeout_seconds: int = 60

    @property
    def root_dir(self) -> Path:
        return Path(self.base_output_dir) / self.pipeline_name

    def validate(self) -> None:
        """
        Validate only what the current pipeline actually needs.
        Do not require keys for placeholder agents yet.
        """
        if not self.openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable.")


# -----------------------------------------------------------------------------
# Orchestrator
# -----------------------------------------------------------------------------

class TikTokFactoryOrchestrator:
    """
    Main pipeline orchestrator.
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.config.validate()
        self._create_folder_structure()

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def run_pipeline(self, topic: str) -> Dict[str, Any]:
        """
        Run the full pipeline for one topic.

        Returns a result summary dict and stores intermediate artifacts on disk.
        """
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty.")

        run_id = self._generate_run_id()
        run_dir = self.config.root_dir / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Starting pipeline | run_id=%s | topic=%s", run_id, topic)

        result: Dict[str, Any] = {
            "run_id": run_id,
            "topic": topic,
            "status": "running",
            "started_at": self._utc_now(),
            "artifacts": {},
            "errors": [],
        }

        self._save_json(run_dir / "pipeline_status.json", result)

        try:
            # -----------------------------------------------------------------
            # Agent 01 - Script Generator
            # -----------------------------------------------------------------
            script_output = self._run_agent_01(topic=topic)
            script_path = run_dir / "agent_01_script.json"
            self._save_json(script_path, script_output)
            result["artifacts"]["agent_01_script"] = str(script_path)

            # -----------------------------------------------------------------
            # Agent 02 - Voice Generator
            # -----------------------------------------------------------------
            agent_02_output = self._run_agent_02(script_output, run_dir)
            agent_02_path = run_dir / "agent_02_voice.json"
            self._save_json(agent_02_path, agent_02_output)
            result["artifacts"]["agent_02_voice"] = str(agent_02_path)

            # -----------------------------------------------------------------
            # Agent 03 - Visual Segment Builder
            # -----------------------------------------------------------------
            agent_03_output = self._run_agent_03(script_output, agent_02_output, run_dir)
            agent_03_path = run_dir / "agent_03_visuals.json"
            self._save_json(agent_03_path, agent_03_output)
            result["artifacts"]["agent_03_visuals"] = str(agent_03_path)

            # -----------------------------------------------------------------
            # Agent 04 - Subtitle Generator
            # -----------------------------------------------------------------
            agent_04_output = self._run_agent_04(script_output, agent_02_output, run_dir)
            agent_04_path = run_dir / "agent_04_subtitles.json"
            self._save_json(agent_04_path, agent_04_output)
            result["artifacts"]["agent_04_subtitles"] = str(agent_04_path)

            # -----------------------------------------------------------------
            # Agent 05 - Video Composer
            # -----------------------------------------------------------------
            agent_05_output = self._run_agent_05(
                script_output,
                agent_02_output,
                agent_03_output,
                agent_04_output,
                run_dir,
            )
            agent_05_path = run_dir / "agent_05_video.json"
            self._save_json(agent_05_path, agent_05_output)
            result["artifacts"]["agent_05_video"] = str(agent_05_path)

            # -----------------------------------------------------------------
            # Agent 06 - Publisher / Exporter
            # -----------------------------------------------------------------
            agent_06_output = self._run_agent_06(agent_05_output, run_dir)
            agent_06_path = run_dir / "agent_06_publish.json"
            self._save_json(agent_06_path, agent_06_output)
            result["artifacts"]["agent_06_publish"] = str(agent_06_path)

            result["status"] = "completed"
            result["completed_at"] = self._utc_now()

        except Exception as exc:
            logger.exception("Pipeline failed | run_id=%s", run_id)
            result["status"] = "failed"
            result["failed_at"] = self._utc_now()
            result["errors"].append(
                {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                }
            )

        self._save_json(run_dir / "pipeline_status.json", result)
        logger.info("Pipeline finished | run_id=%s | status=%s", run_id, result["status"])
        return result

    # -------------------------------------------------------------------------
    # Agent Implementations
    # -------------------------------------------------------------------------

    def _run_agent_01(self, topic: str) -> Dict[str, Any]:
        """
        Real implementation using Agent 01.
        """
        logger.info("Running Agent 01 - Script Generator")

        agent_config = ScriptGeneratorConfig(
            api_key=self.config.openai_api_key,
            model=self.config.agent_01_model,
            max_retries=self.config.agent_01_max_retries,
            timeout_seconds=self.config.agent_01_timeout_seconds,
        )
        agent = Agent01ScriptGenerator(config=agent_config)
        return agent.generate_script(topic)

    def _run_agent_02(self, script_output: Dict[str, Any], run_dir: Path) -> Dict[str, Any]:
        """
        Placeholder: Voice Generator.
        TODO:
        - Import and call agent_02_voice_generator
        - Generate MP3/WAV from script timestamps
        - Store returned file paths and metadata
        """
        logger.info("Running Agent 02 - Voice Generator (placeholder)")
        return {
            "status": "todo",
            "message": "Agent 02 not implemented yet.",
            "expected_input": "Agent 01 script JSON",
            "run_dir": str(run_dir),
        }

    def _run_agent_03(
        self,
        script_output: Dict[str, Any],
        voice_output: Dict[str, Any],
        run_dir: Path,
    ) -> Dict[str, Any]:
        """
        Placeholder: Visual Segment Builder.
        TODO:
        - Build shot list
        - Generate scene prompts / B-roll prompts
        - Map visuals to timestamps
        """
        logger.info("Running Agent 03 - Visual Segment Builder (placeholder)")
        return {
            "status": "todo",
            "message": "Agent 03 not implemented yet.",
            "segments": script_output.get("timestamps", []),
            "run_dir": str(run_dir),
        }

    def _run_agent_04(
        self,
        script_output: Dict[str, Any],
        voice_output: Dict[str, Any],
        run_dir: Path,
    ) -> Dict[str, Any]:
        """
        Placeholder: Subtitle Generator.
        TODO:
        - Generate SRT/VTT/word-level subtitle data
        - Prefer real alignment data from voice output
        """
        logger.info("Running Agent 04 - Subtitle Generator (placeholder)")
        return {
            "status": "todo",
            "message": "Agent 04 not implemented yet.",
            "caption": script_output.get("caption"),
            "run_dir": str(run_dir),
        }

    def _run_agent_05(
        self,
        script_output: Dict[str, Any],
        voice_output: Dict[str, Any],
        visuals_output: Dict[str, Any],
        subtitles_output: Dict[str, Any],
        run_dir: Path,
    ) -> Dict[str, Any]:
        """
        Placeholder: Video Composer.
        TODO:
        - Combine voice, visuals, subtitles
        - Render final short-form video
        """
        logger.info("Running Agent 05 - Video Composer (placeholder)")
        return {
            "status": "todo",
            "message": "Agent 05 not implemented yet.",
            "run_dir": str(run_dir),
        }

    def _run_agent_06(self, video_output: Dict[str, Any], run_dir: Path) -> Dict[str, Any]:
        """
        Placeholder: Publisher / Exporter.
        TODO:
        - Export delivery bundle
        - Optionally upload to CMS / scheduler / social API
        """
        logger.info("Running Agent 06 - Publisher / Exporter (placeholder)")
        return {
            "status": "todo",
            "message": "Agent 06 not implemented yet.",
            "run_dir": str(run_dir),
        }

    # -------------------------------------------------------------------------
    # Storage / Filesystem
    # -------------------------------------------------------------------------

    def _create_folder_structure(self) -> None:
        """
        Create a sane folder structure up front.
        """
        folders = [
            self.config.root_dir,
            self.config.root_dir / "runs",
            self.config.root_dir / "logs",
            self.config.root_dir / "cache",
            self.config.root_dir / "exports",
        ]
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)

    def _save_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------

    @staticmethod
    def _generate_run_id() -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        short_id = uuid.uuid4().hex[:8]
        return f"{ts}_{short_id}"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()


# -----------------------------------------------------------------------------
# Example Usage
# -----------------------------------------------------------------------------

def main() -> None:
    """
    Example usage:
        export OPENAI_API_KEY="your_key"
        python orchestrator.py
    """
    config = Config(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
        base_output_dir="outputs",
        pipeline_name="tiktok_video_factory",
        agent_01_model="gpt-4.1",
    )

    orchestrator = TikTokFactoryOrchestrator(config=config)

    topic = "Why most startup founders waste their first $1,000 on ads"
    result = orchestrator.run_pipeline(topic=topic)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
