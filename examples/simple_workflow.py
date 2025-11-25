#!/usr/bin/env python3
"""
Simple Workflow Example
Demonstrates how to use the Agentic Services platform
"""

import asyncio
import logging
from agentic_services.orchestrator import WorkflowOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run a simple workflow example"""
    
    # Define project requirements
    project_id = "example-rest-api"
    requirements = """
Build a RESTful API service for a task management application.

Requirements:
- User authentication and authorization
- CRUD operations for tasks (create, read, update, delete)
- Task categories and priorities
- Due dates and reminders
- RESTful API design with JSON responses
- PostgreSQL database
- Docker containerization
- API documentation with Swagger/OpenAPI

Technology preferences:
- Python with FastAPI or Flask
- SQLAlchemy ORM
- JWT authentication
- Redis for caching (optional)

Non-functional requirements:
- Response time < 200ms for simple queries
- Support 100 concurrent users
- 99.5% uptime
- Secure (HTTPS, input validation, SQL injection prevention)
"""
    
    context = """
This is for an internal team productivity tool. 
Team size: 5-10 users initially, may grow to 50.
Timeline: MVP in 4 weeks.
"""
    
    constraints = {
        "timeline": "4 weeks",
        "team_size": 2,
        "budget": "medium",
        "experience_level": "intermediate"
    }
    
    # Create orchestrator
    logger.info("="*80)
    logger.info("Starting Agentic Services Workflow Example")
    logger.info("="*80)
    
    orchestrator = WorkflowOrchestrator()
    
    try:
        # Run full workflow
        results = await orchestrator.execute_full_workflow(
            project_id=project_id,
            requirements=requirements,
            context=context,
            constraints=constraints
        )
        
        # Display results summary
        logger.info("\n" + "="*80)
        logger.info("WORKFLOW COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        logger.info(f"Project ID: {results['project_id']}")
        logger.info(f"Workflow ID: {results['workflow_id']}")
        logger.info(f"Duration: {results['duration_seconds']:.2f} seconds")
        logger.info(f"Agents executed: {', '.join(results['agents_executed'])}")
        
        # Discovery results
        if 'discovery' in results:
            discovery = results['discovery']
            logger.info("\n--- DISCOVERY RESULTS ---")
            logger.info(f"Project Type: {discovery.get('project_type')}")
            logger.info(f"S3 URI: {discovery.get('s3_uri')}")
        
        # Analysis results
        if 'analysis' in results:
            analysis = results['analysis']
            logger.info("\n--- ANALYSIS RESULTS ---")
            logger.info(f"S3 URI: {analysis.get('s3_uri')}")
        
        # Planning results
        if 'planning' in results:
            planning = results['planning']
            logger.info("\n--- PLANNING RESULTS ---")
            logger.info(f"S3 URI: {planning.get('s3_uri')}")
        
        # Artifact results
        if 'artifacts' in results:
            artifacts = results['artifacts']
            logger.info("\n--- ARTIFACTS GENERATED ---")
            logger.info(f"S3 URI: {artifacts.get('s3_uri')}")
        
        logger.info("\n" + "="*80)
        logger.info("Check the S3 URIs above for detailed results")
        logger.info("="*80 + "\n")
        
        return results
        
    except Exception as e:
        logger.error(f"\nWorkflow failed: {e}", exc_info=True)
        return None


if __name__ == '__main__':
    # Run the async main function
    asyncio.run(main())
