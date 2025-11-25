#!/usr/bin/env python3
"""
Command-Line Interface for Nagarro Agentic Services Platform
Run agent workflows locally or in production
"""

import asyncio
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional
import uuid

from agentic_services.orchestrator import WorkflowOrchestrator
from agentic_services.agents import (
    DiscoveryAgent,
    AnalysisAgent,
    PlanningAgent,
    ArtifactGenerationAgent
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_parser() -> argparse.ArgumentParser:
    """Setup command-line argument parser"""
    parser = argparse.ArgumentParser(
        description='Agentic Services CLI - Run AI agent workflows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full workflow
  %(prog)s workflow --requirements "Build a REST API" --project-id my-project
  
  # Run discovery only
  %(prog)s discovery --requirements "Build a REST API" --output discovery.json
  
  # Run from file
  %(prog)s workflow --requirements-file requirements.txt --project-id my-project
  
  # Enable debug logging
  %(prog)s workflow --requirements "Build a REST API" --debug
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Full workflow command
    workflow_parser = subparsers.add_parser(
        'workflow',
        help='Run complete workflow (discovery → analysis → planning → artifacts)'
    )
    workflow_parser.add_argument(
        '--requirements', '-r',
        type=str,
        help='Project requirements text'
    )
    workflow_parser.add_argument(
        '--requirements-file', '-f',
        type=Path,
        help='Path to requirements file'
    )
    workflow_parser.add_argument(
        '--context', '-c',
        type=str,
        help='Additional context (optional)'
    )
    workflow_parser.add_argument(
        '--project-id', '-p',
        type=str,
        help='Project ID (auto-generated if not provided)'
    )
    workflow_parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file for results (default: stdout)'
    )
    workflow_parser.add_argument(
        '--constraints',
        type=str,
        help='JSON string with time/budget/team constraints'
    )
    
    # Discovery-only command
    discovery_parser = subparsers.add_parser(
        'discovery',
        help='Run discovery agent only'
    )
    discovery_parser.add_argument(
        '--requirements', '-r',
        type=str,
        help='Project requirements text'
    )
    discovery_parser.add_argument(
        '--requirements-file', '-f',
        type=Path,
        help='Path to requirements file'
    )
    discovery_parser.add_argument(
        '--project-id', '-p',
        type=str,
        help='Project ID (auto-generated if not provided)'
    )
    discovery_parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file for results (default: stdout)'
    )
    
    # Analysis-only command
    analysis_parser = subparsers.add_parser(
        'analysis',
        help='Run analysis agent only'
    )
    analysis_parser.add_argument(
        '--discovery-file', '-d',
        type=Path,
        required=True,
        help='Path to discovery results JSON file'
    )
    analysis_parser.add_argument(
        '--project-id', '-p',
        type=str,
        help='Project ID'
    )
    analysis_parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file for results'
    )
    
    # Planning-only command
    planning_parser = subparsers.add_parser(
        'planning',
        help='Run planning agent only'
    )
    planning_parser.add_argument(
        '--analysis-file', '-a',
        type=Path,
        required=True,
        help='Path to analysis results JSON file'
    )
    planning_parser.add_argument(
        '--project-id', '-p',
        type=str,
        help='Project ID'
    )
    planning_parser.add_argument(
        '--constraints',
        type=str,
        help='JSON string with constraints'
    )
    planning_parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file for results'
    )
    
    # Artifacts-only command
    artifacts_parser = subparsers.add_parser(
        'artifacts',
        help='Run artifact generation agent only'
    )
    artifacts_parser.add_argument(
        '--planning-file', '-p',
        type=Path,
        required=True,
        help='Path to planning results JSON file'
    )
    artifacts_parser.add_argument(
        '--project-id',
        type=str,
        help='Project ID'
    )
    artifacts_parser.add_argument(
        '--types',
        type=str,
        nargs='+',
        default=['all'],
        help='Artifact types to generate'
    )
    artifacts_parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file for results'
    )
    
    # Global options
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


async def run_full_workflow(args) -> dict:
    """Run complete workflow"""
    # Get requirements
    requirements = get_requirements(args)
    if not requirements:
        logger.error("Requirements are required. Use --requirements or --requirements-file")
        sys.exit(1)
    
    # Generate project ID if not provided
    project_id = args.project_id or f"project-{uuid.uuid4().hex[:8]}"
    
    # Parse constraints if provided
    constraints = None
    if args.constraints:
        try:
            constraints = json.loads(args.constraints)
        except json.JSONDecodeError:
            logger.error("Invalid JSON for --constraints")
            sys.exit(1)
    
    # Create orchestrator and run workflow
    logger.info(f"Starting workflow for project: {project_id}")
    orchestrator = WorkflowOrchestrator()
    
    try:
        results = await orchestrator.execute_full_workflow(
            project_id=project_id,
            requirements=requirements,
            context=args.context,
            constraints=constraints
        )
        logger.info("Workflow completed successfully!")
        return results
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        sys.exit(1)


async def run_discovery(args) -> dict:
    """Run discovery agent only"""
    requirements = get_requirements(args)
    if not requirements:
        logger.error("Requirements are required")
        sys.exit(1)
    
    project_id = args.project_id or f"project-{uuid.uuid4().hex[:8]}"
    
    logger.info(f"Running discovery for project: {project_id}")
    agent = DiscoveryAgent()
    
    try:
        results = await agent.execute({
            'project_id': project_id,
            'requirements': requirements,
            'context': getattr(args, 'context', '')
        })
        logger.info("Discovery completed!")
        return results
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)
        sys.exit(1)


async def run_analysis(args) -> dict:
    """Run analysis agent only"""
    # Load discovery data
    discovery_data = load_json_file(args.discovery_file)
    project_id = args.project_id or discovery_data.get('project_id', f"project-{uuid.uuid4().hex[:8]}")
    
    logger.info(f"Running analysis for project: {project_id}")
    agent = AnalysisAgent()
    
    try:
        results = await agent.execute({
            'project_id': project_id,
            'discovery_data': discovery_data
        })
        logger.info("Analysis completed!")
        return results
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        sys.exit(1)


async def run_planning(args) -> dict:
    """Run planning agent only"""
    # Load analysis data
    analysis_data = load_json_file(args.analysis_file)
    project_id = args.project_id or analysis_data.get('project_id', f"project-{uuid.uuid4().hex[:8]}")
    
    # Parse constraints
    constraints = {}
    if args.constraints:
        try:
            constraints = json.loads(args.constraints)
        except json.JSONDecodeError:
            logger.error("Invalid JSON for --constraints")
            sys.exit(1)
    
    logger.info(f"Running planning for project: {project_id}")
    agent = PlanningAgent()
    
    try:
        results = await agent.execute({
            'project_id': project_id,
            'analysis_data': analysis_data,
            'constraints': constraints
        })
        logger.info("Planning completed!")
        return results
    except Exception as e:
        logger.error(f"Planning failed: {e}", exc_info=True)
        sys.exit(1)


async def run_artifacts(args) -> dict:
    """Run artifact generation agent only"""
    # Load planning data
    planning_data = load_json_file(args.planning_file)
    project_id = args.project_id or planning_data.get('project_id', f"project-{uuid.uuid4().hex[:8]}")
    
    logger.info(f"Running artifact generation for project: {project_id}")
    agent = ArtifactGenerationAgent()
    
    try:
        results = await agent.execute({
            'project_id': project_id,
            'planning_data': planning_data,
            'artifact_types': args.types
        })
        logger.info("Artifact generation completed!")
        return results
    except Exception as e:
        logger.error(f"Artifact generation failed: {e}", exc_info=True)
        sys.exit(1)


def get_requirements(args) -> Optional[str]:
    """Get requirements from args or file"""
    if args.requirements:
        return args.requirements
    elif args.requirements_file:
        return args.requirements_file.read_text(encoding='utf-8')
    return None


def load_json_file(path: Path) -> dict:
    """Load JSON file"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {path}: {e}")
        sys.exit(1)


def save_output(results: dict, output_path: Optional[Path]):
    """Save or print results"""
    output_json = json.dumps(results, indent=2)
    
    if output_path:
        output_path.write_text(output_json, encoding='utf-8')
        logger.info(f"Results saved to: {output_path}")
    else:
        print("\n" + "="*80)
        print("RESULTS:")
        print("="*80)
        print(output_json)
        print("="*80 + "\n")


def main():
    """Main CLI entry point"""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Check command
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run appropriate command
    try:
        if args.command == 'workflow':
            results = asyncio.run(run_full_workflow(args))
        elif args.command == 'discovery':
            results = asyncio.run(run_discovery(args))
        elif args.command == 'analysis':
            results = asyncio.run(run_analysis(args))
        elif args.command == 'planning':
            results = asyncio.run(run_planning(args))
        elif args.command == 'artifacts':
            results = asyncio.run(run_artifacts(args))
        else:
            parser.print_help()
            sys.exit(1)
        
        # Save or print results
        save_output(results, args.output if hasattr(args, 'output') else None)
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
