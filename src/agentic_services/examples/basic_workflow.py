"""
Example: Basic Workflow Usage
Demonstrates how to use the Nagarro Agentic Services Platform
"""

import asyncio
import json
import logging
from agentic_services.orchestrator import WorkflowOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def example_full_workflow():
    """
    Example: Run complete workflow from requirements to artifacts
    """
    logger.info("=" * 60)
    logger.info("Example: Full Workflow Execution")
    logger.info("=" * 60)
    
    # Sample project requirements
    requirements = """
    Build a REST API for a task management system with the following features:
    
    1. User Authentication (JWT-based)
    2. CRUD operations for tasks
    3. Task assignment to users
    4. Task status tracking (todo, in-progress, done)
    5. Due date management
    6. Email notifications for due tasks
    
    Technical Requirements:
    - Python/FastAPI backend
    - PostgreSQL database
    - Redis for caching
    - Docker containerization
    - CI/CD with GitHub Actions
    """
    
    context = """
    Target deployment: AWS ECS
    Expected users: ~1000 concurrent users
    Data retention: 2 years
    Security: SOC 2 compliance required
    """
    
    constraints = {
        'timeline_weeks': 12,
        'team_size': 4,
        'budget': 'medium'
    }
    
    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator()
    
    try:
        # Execute full workflow
        logger.info("Starting workflow execution...")
        results = await orchestrator.execute_full_workflow(
            project_id='task-api-2024',
            requirements=requirements,
            context=context,
            constraints=constraints
        )
        
        # Display results summary
        logger.info("\n" + "=" * 60)
        logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Workflow ID: {results['workflow_id']}")
        logger.info(f"Duration: {results['duration_seconds']:.2f} seconds")
        logger.info(f"Agents Executed: {', '.join(results['agents_executed'])}")
        
        # Discovery summary
        discovery = results['discovery']
        logger.info(f"\n📋 DISCOVERY:")
        logger.info(f"  Project Type: {discovery.get('project_type')}")
        logger.info(f"  Data URI: {discovery.get('s3_uri')}")
        
        # Analysis summary
        analysis = results['analysis']
        complexity = analysis.get('complexity_assessment', {})
        architecture = analysis.get('recommended_architecture', {})
        logger.info(f"\n🔍 ANALYSIS:")
        logger.info(f"  Complexity: {complexity.get('level')}")
        logger.info(f"  Architecture: {architecture.get('pattern')}")
        logger.info(f"  Data URI: {analysis.get('s3_uri')}")
        
        # Planning summary
        planning = results['planning']
        effort = planning.get('effort_estimation', {})
        logger.info(f"\n📅 PLANNING:")
        logger.info(f"  Total Sprints: {len(planning.get('sprints', []))}")
        logger.info(f"  Story Points: {effort.get('total_story_points')}")
        logger.info(f"  Data URI: {planning.get('s3_uri')}")
        
        # Artifacts summary
        artifacts = results['artifacts']
        logger.info(f"\n📦 ARTIFACTS:")
        logger.info(f"  Total Artifacts: {len(artifacts.get('artifacts', []))}")
        logger.info(f"  Data URI: {artifacts.get('s3_uri')}")
        
        logger.info("\n" + "=" * 60)
        
        return results
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        raise


async def example_discovery_only():
    """
    Example: Run only discovery phase
    """
    logger.info("=" * 60)
    logger.info("Example: Discovery Only")
    logger.info("=" * 60)
    
    requirements = """
    Build a simple e-commerce platform with:
    - Product catalog
    - Shopping cart
    - Checkout with Stripe integration
    - Order tracking
    """
    
    orchestrator = WorkflowOrchestrator()
    
    result = await orchestrator.execute_discovery_only(
        project_id='ecommerce-mvp',
        requirements=requirements
    )
    
    logger.info(f"Discovery completed: {result.get('s3_uri')}")
    logger.info(f"Project Type: {result.get('project_type')}")
    
    return result


async def example_individual_agents():
    """
    Example: Use agents individually
    """
    from agentic_services.agents import DiscoveryAgent, AnalysisAgent
    
    logger.info("=" * 60)
    logger.info("Example: Individual Agent Usage")
    logger.info("=" * 60)
    
    # Step 1: Discovery
    discovery_agent = DiscoveryAgent()
    discovery_result = await discovery_agent.execute({
        'project_id': 'mobile-app',
        'requirements': 'Build a React Native app for food delivery',
        'context': 'iOS and Android support required'
    })
    
    logger.info(f"✅ Discovery completed: {discovery_result.get('project_type')}")
    
    # Step 2: Analysis (using discovery results)
    analysis_agent = AnalysisAgent()
    analysis_result = await analysis_agent.execute({
        'project_id': 'mobile-app',
        'discovery_data': discovery_result
    })
    
    logger.info(f"✅ Analysis completed: {analysis_result.get('recommended_architecture', {}).get('pattern')}")
    
    return {
        'discovery': discovery_result,
        'analysis': analysis_result
    }


async def main():
    """
    Main example runner
    """
    print("\n🚀 Nagarro Agentic Services Platform - Examples\n")
    
    # Choose which example to run
    example_choice = 1  # Change this to run different examples
    
    if example_choice == 1:
        print("Running: Full Workflow Example\n")
        await example_full_workflow()
    
    elif example_choice == 2:
        print("Running: Discovery Only Example\n")
        await example_discovery_only()
    
    elif example_choice == 3:
        print("Running: Individual Agents Example\n")
        await example_individual_agents()
    
    print("\n✨ Example completed!\n")


if __name__ == "__main__":
    # Note: This example assumes AWS credentials are configured
    # and the required AWS resources (S3 buckets, DynamoDB tables) exist
    
    print("""
    ⚠️  IMPORTANT: Before running this example:
    
    1. Ensure AWS credentials are configured
    2. Create required S3 buckets (see .env.example)
    3. Create DynamoDB tables
    4. Configure Bedrock model access
    
    This is a DEMO script. In production, agents would run via:
    - ECS tasks triggered by EventBridge
    - API Gateway endpoints
    - Streamlit UI
    """)
    
    # Uncomment to run:
    # asyncio.run(main())
    
    print("\n📝 To run this example, uncomment the asyncio.run(main()) line above.\n")
