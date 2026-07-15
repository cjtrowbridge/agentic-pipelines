#!/usr/bin/env python3
"""Operate a bounded local Pipelines runtime from a host repository."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
if str(FRAMEWORK_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_ROOT))

from pipeline_runtime.api import InferenceClient
from pipeline_runtime.config import ConfigError, load_api_config
from pipeline_runtime.definition import DefinitionError, load_definition
from pipeline_runtime.prompts import PromptError
from pipeline_runtime.runner import PipelineRunner
from pipeline_runtime.state import StateError
from pipeline_runtime.thread_capture import ThreadCaptureWriter


def _runner(pipeline: Path, api_config: Path | None = None) -> PipelineRunner:
    definition = load_definition(pipeline)
    client = None
    if api_config is not None:
        config = load_api_config(api_config)
        client = InferenceClient(config, thread_writer=ThreadCaptureWriter(definition.thread_root))
    return PipelineRunner(definition, client)


def main() -> int:
    parser = argparse.ArgumentParser(description="Operate a local, deterministic-first pipeline.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight", help="Validate API config and, when supplied, the complete pipeline contract.")
    preflight.add_argument("--api-config", type=Path, default=Path("api.yaml"))
    preflight.add_argument("--pipeline", type=Path)

    for command in ("discover", "run", "inspect-entity", "report", "analyze", "retry-cohort", "rollback-entity"):
        item = subparsers.add_parser(command)
        item.add_argument("--pipeline", type=Path, default=Path("pipeline.yaml"))
        if command in {"run", "analyze"}:
            item.add_argument("--api-config", type=Path, default=Path("api.yaml"))
        if command == "analyze":
            item.add_argument("--run-id")
            item.add_argument("--max-entities", type=int, default=25)
            item.add_argument("--max-runtime-minutes", type=float, default=50)
            item.add_argument("--dry-run", action="store_true")
        elif command == "inspect-entity":
            item.add_argument("entity_id")
        elif command == "retry-cohort":
            item.add_argument("--report", type=Path, required=True)
            item.add_argument("--cohort-id", required=True)
        elif command == "rollback-entity":
            item.add_argument("entity_id")

    args = parser.parse_args()
    runner: PipelineRunner | None = None
    try:
        if args.command == "preflight":
            config = load_api_config(args.api_config)
            print(f"API valid: provider={config.provider}, endpoint={config.endpoint}, model={config.model}")
            if args.pipeline:
                runner = _runner(args.pipeline, args.api_config)
                print(f"Pipeline valid: {runner.definition.pipeline_id}; stages={','.join(runner.definition.stages)}")
            return 0
        runner = _runner(args.pipeline, args.api_config if args.command in {"run", "analyze"} else None)
        if args.command == "discover":
            print(json.dumps({"new_or_changed": runner.discover()}))
        elif args.command == "run":
            print(json.dumps(runner.run(args.max_entities, args.max_runtime_minutes, args.dry_run), indent=2))
        elif args.command == "inspect-entity":
            print(json.dumps(runner.inspect(args.entity_id), indent=2))
        elif args.command == "report":
            print(runner.report())
        elif args.command == "analyze":
            print(runner.analyze(args.run_id))
        elif args.command == "retry-cohort":
            print(json.dumps({"retry_eligible": runner.retry_cohort(args.report, args.cohort_id)}))
        elif args.command == "rollback-entity":
            print(runner.rollback_entity(args.entity_id))
        return 0
    except (ConfigError, DefinitionError, PromptError, StateError, OSError, ValueError) as exc:
        print(f"PIPELINE FAILED: {exc}", file=sys.stderr)
        return 2
    finally:
        if runner is not None:
            runner.close()


if __name__ == "__main__":
    raise SystemExit(main())
