"""
Bot Service - Expandable from rule-based to LLM
This interface allows easy swapping between rule-based and LLM implementations
"""
from typing import Dict, List, Optional
from .knowledge_base import KNOWLEDGE_BASE

class BotService:
    """Base bot service interface - can be extended for LLM"""
    
    def get_response(self, user_input: str, context: str) -> str:
        """
        Get bot response based on user input and context
        
        Args:
            user_input: User's question/message
            context: Current page/context (e.g., "Cloud Credentials")
        
        Returns:
            Bot response string
        """
        raise NotImplementedError("Subclasses must implement get_response")


class RuleBasedBot(BotService):
    """Simple rule-based bot - can be replaced with LLMBot later"""
    
    def __init__(self):
        # Use comprehensive knowledge base
        self.knowledge_base = KNOWLEDGE_BASE
        
        # Legacy page_help for backward compatibility
        self.page_help = {
            "Cloud Credentials": {
                "keywords": ["credential", "aws", "access", "key", "secret", "what", "how", "help"],
                "responses": [
                    "To configure AWS credentials, you need to provide:\n\n"
                    "• **Access Key ID**: Your AWS access key\n"
                    "• **Secret Access Key**: Your AWS secret key\n"
                    "• **Region**: AWS region (e.g., us-east-1)\n\n"
                    "These credentials allow our agents to access your AWS account for migration tasks. "
                    "Make sure you have the necessary permissions (IAM roles) configured.",
                    
                    "AWS credentials are required for agents to interact with your cloud infrastructure. "
                    "You can find these in your AWS IAM console under 'Access Keys'. "
                    "For security, use IAM roles when possible instead of access keys."
                ]
            },
            "Source Infrastructure": {
                "keywords": ["infrastructure", "server", "vm", "what", "how", "help", "define"],
                "responses": [
                    "On this page, you should define your current infrastructure:\n\n"
                    "• **Servers/VMs**: List your current servers and virtual machines\n"
                    "• **Applications**: Applications running on your infrastructure\n"
                    "• **Databases**: Database instances and types\n"
                    "• **Network**: Network topology and dependencies\n\n"
                    "This information helps agents understand your current setup and plan the migration.",
                    
                    "Source infrastructure details help our AI agents understand your current environment. "
                    "The more accurate information you provide, the better the migration plan will be."
                ]
            },
            "Source Code": {
                "keywords": ["code", "repository", "git", "source", "what", "how", "help"],
                "responses": [
                    "Here you can configure access to your source code repositories:\n\n"
                    "• **Repository URL**: Your Git repository (GitHub, GitLab, etc.)\n"
                    "• **Branch**: Main branch to analyze\n"
                    "• **Access Token**: Authentication token for private repos\n\n"
                    "This allows agents to analyze your codebase for dependencies and migration planning.",
                    
                    "Source code access enables agents to analyze your application code, "
                    "identify dependencies, frameworks, and generate accurate migration strategies."
                ]
            },
            "Target Configuration": {
                "keywords": ["target", "aws", "configuration", "what", "how", "help", "define"],
                "responses": [
                    "Define your target cloud configuration:\n\n"
                    "• **Cloud Provider**: AWS, Azure, or GCP\n"
                    "• **Region**: Target region for deployment\n"
                    "• **Services**: Target services (EC2, ECS, Lambda, etc.)\n"
                    "• **Architecture**: Target architecture patterns\n\n"
                    "This helps agents plan the migration to your desired target environment.",
                    
                    "Target configuration defines where and how your infrastructure will be migrated. "
                    "Specify your preferred cloud provider, services, and architecture patterns."
                ]
            },
            "Project Onboarding": {
                "keywords": ["project", "create", "onboard", "what", "how", "help"],
                "responses": [
                    "Create a new migration project by filling in:\n\n"
                    "• **Project Name**: Descriptive name for your project\n"
                    "• **Description**: Overview of the migration\n"
                    "• **Requirements**: Goals and constraints\n"
                    "• **Timeline, Priority, Budget**: Project parameters\n\n"
                    "Once created, you can configure credentials, infrastructure, and start agent execution.",
                    
                    "This is where you start your migration journey. Fill in the project details, "
                    "and then proceed to configure cloud credentials and infrastructure information."
                ]
            },
            "Projects": {
                "keywords": ["project", "view", "manage", "what", "how", "help"],
                "responses": [
                    "This page shows all your migration projects:\n\n"
                    "• **View Details**: Click 'Details' to see project information\n"
                    "• **Execute Agents**: Click 'Execute' to start agent workflows\n"
                    "• **Configure**: Set up credentials, infrastructure, and target config\n"
                    "• **Delete**: Remove projects you no longer need\n\n"
                    "Use this page to manage and monitor all your migration projects.",
                    
                    "The Projects page is your dashboard for managing all migration projects. "
                    "You can view progress, configure settings, and execute agents from here."
                ]
            },
            "Agent Execution": {
                "keywords": ["agent", "execute", "run", "what", "how", "help"],
                "responses": [
                    "Execute AI agents to perform migration tasks:\n\n"
                    "• **Select Agents**: Choose which agents to run\n"
                    "• **Configure Parameters**: Set agent-specific settings\n"
                    "• **Run**: Execute agents to perform tasks\n"
                    "• **Monitor**: Track agent progress and results\n\n"
                    "Agents will perform discovery, assessment, planning, and execution tasks.",
                    
                    "Agent Execution allows you to run AI-powered agents that automate migration tasks. "
                    "Select the agents you need and configure them based on your project requirements."
                ]
            },
            "Analytics": {
                "keywords": ["analytics", "metrics", "insights", "what", "how", "help"],
                "responses": [
                    "View analytics and insights about your migrations:\n\n"
                    "• **Agent Performance**: See how agents are performing\n"
                    "• **Migration Metrics**: Track migration progress\n"
                    "• **Cost Analysis**: View cost estimates and savings\n"
                    "• **Timeline**: Monitor project timelines\n\n"
                    "Use analytics to track progress and make data-driven decisions.",
                    
                    "Analytics provides real-time insights into your migration projects. "
                    "Monitor agent performance, track metrics, and analyze costs."
                ]
            },
            "Reports": {
                "keywords": ["report", "artifact", "download", "what", "how", "help"],
                "responses": [
                    "View and download migration artifacts:\n\n"
                    "• **Wave Plans**: Migration wave plans\n"
                    "• **Strategies**: Migration strategies\n"
                    "• **Assessments**: Cloud readiness assessments\n"
                    "• **Download**: Get artifacts in various formats\n\n"
                    "All generated documents and reports are available here for download.",
                    
                    "The Reports page contains all migration artifacts generated by agents. "
                    "You can preview and download documents like wave plans and migration strategies."
                ]
            },
            "Home": {
                "keywords": ["home", "dashboard", "start", "what", "how", "help"],
                "responses": [
                    "Welcome to Nagarro Agentic Services!\n\n"
                    "• **Create Project**: Start a new migration project\n"
                    "• **View Agents**: Explore our 24 AI agents\n"
                    "• **Agent Showcase**: See agents in action\n\n"
                    "Get started by creating your first migration project.",
                    
                    "This is your home dashboard. Create projects, explore agents, "
                    "or try the Agent Showcase to see how AI agents can help with your migration."
                ]
            },
            "Agents": {
                "keywords": ["agent", "how many", "count", "total", "available", "what", "help", "list", "portfolio"],
                "responses": [
                    "We have **24 AI agents** available in our portfolio, organized into 3 focus areas:\n\n"
                    "• **Migration Agents**: Discovery, assessment, planning, and execution agents\n"
                    "• **FinOps Agents**: Cost optimization, budget management, and financial governance\n"
                    "• **AIOps Agents**: Proactive monitoring, incident management, and automated remediation\n\n"
                    "All 24 agents are ready and deployed. You can explore them by focus area on this page.",
                    
                    "There are **24 AI agents** in total, covering the complete cloud migration lifecycle:\n\n"
                    "• **Discovery Phase**: 8 agents for infrastructure scanning, application profiling, and data discovery\n"
                    "• **Assessment Phase**: 5 agents for dependency mapping, compliance checking, and cost estimation\n"
                    "• **Execution Phase**: 6 agents for provisioning, migration, configuration, and testing\n"
                    "• **FinOps & AIOps**: Additional specialized agents for operations and cost management\n\n"
                    "Each agent is specialized for specific migration tasks and can be executed individually or as part of a workflow."
                ],
                "specific_questions": {
                    "how many": "We have **24 AI agents** available, all fully implemented and ready to use. They're organized into 3 main focus areas: Migration, FinOps, and AIOps.",
                    "count": "There are **24 agents** in total. You can see them all organized by focus area on this page.",
                    "total": "The total number of agents is **24**. They cover discovery, assessment, planning, execution, FinOps, and AIOps.",
                    "available": "All **24 agents** are available and ready to use. They're organized into Migration, FinOps, and AIOps categories."
                }
            }
        }
        
        # General responses
        self.general_responses = {
            "greeting": ["Hello! How can I help you?", "Hi there! What do you need help with?", "Hey! I'm here to help."],
            "thanks": ["You're welcome!", "Happy to help!", "Glad I could assist!"],
            "unknown": [
                "I'm not sure about that. Could you rephrase your question?",
                "I don't have information about that. Try asking about the current page you're on.",
                "Let me help you with questions about this page. What would you like to know?"
            ]
        }
    
    def get_response(self, user_input: str, context: str) -> str:
        """Get response from rule-based bot using comprehensive knowledge base - SIMPLIFIED & FIXED"""
        user_lower = user_input.lower().strip()
        
        # Normalize common typos
        user_normalized = user_lower.replace("availble", "available").replace("availabel", "available")
        
        # Check for greetings
        if any(word in user_normalized for word in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"]):
            import random
            return random.choice(self.general_responses["greeting"])
        
        # Check for thanks
        if any(word in user_normalized for word in ["thanks", "thank you", "appreciate", "thank"]):
            import random
            return random.choice(self.general_responses["thanks"])
        
        # Normalize context name (handle variations)
        context_normalized = self._normalize_context(context)
        
        # Get knowledge base entry for this page
        if context_normalized in self.knowledge_base:
            kb_entry = self.knowledge_base[context_normalized]
            
            # SIMPLIFIED MATCHING: Check user input directly against answer types
            # Priority order: specific questions first, then general
            
            # 1. Count/Number questions (highest priority for specific answers)
            if any(phrase in user_normalized for phrase in ["how many", "count", "total", "number of", "how many agents", "how many are", "agents available"]):
                if "count" in kb_entry["answers"]:
                    return kb_entry["answers"]["count"]
            
            # 2. Focus areas
            if any(phrase in user_normalized for phrase in ["focus area", "focus areas", "categories", "types of", "how are organized", "groups"]):
                if "focus_areas" in kb_entry["answers"]:
                    return kb_entry["answers"]["focus_areas"]
            
            # 3. Capabilities
            if any(phrase in user_normalized for phrase in ["capability", "capabilities", "what can", "what do agents do", "what can agents", "help with", "features"]):
                if "capabilities" in kb_entry["answers"]:
                    return kb_entry["answers"]["capabilities"]
            
            # 4. Demo mode
            if any(phrase in user_normalized for phrase in ["demo mode", "demo", "mock", "test mode", "testing", "simulate", "without credentials"]):
                if "demo_mode" in kb_entry["answers"]:
                    return kb_entry["answers"]["demo_mode"]
            
            # 5. Security
            if any(phrase in user_normalized for phrase in ["security", "safe", "secure", "iam role", "iam", "role arn", "recommendation", "best practice"]):
                if "security" in kb_entry["answers"]:
                    return kb_entry["answers"]["security"]
            
            # 6. Phases
            if any(phrase in user_normalized for phrase in ["phase", "phases", "discovery", "assessment", "execution", "optimization", "lifecycle"]):
                if "phases" in kb_entry["answers"]:
                    return kb_entry["answers"]["phases"]
            
            # 7. Actions
            if any(phrase in user_normalized for phrase in ["action", "actions", "what can i do", "what can i", "delete", "edit", "execute", "run"]):
                if "actions" in kb_entry["answers"]:
                    return kb_entry["answers"]["actions"]
            
            # 8. What/Explain questions
            if any(phrase in user_normalized for phrase in ["what is", "what are", "what", "explain", "tell me", "describe", "define"]):
                if "what" in kb_entry["answers"]:
                    return kb_entry["answers"]["what"]
            
            # 9. How/Help questions
            if any(phrase in user_normalized for phrase in ["how to", "how do", "how can", "how", "help", "steps", "process", "guide"]):
                if "help" in kb_entry["answers"]:
                    return kb_entry["answers"]["help"]
            
            # 10. General fallback
            if "general" in kb_entry["answers"]:
                return kb_entry["answers"]["general"]
            elif "what" in kb_entry["answers"]:
                return kb_entry["answers"]["what"]
            elif "help" in kb_entry["answers"]:
                return kb_entry["answers"]["help"]
        
        # Try legacy page_help as fallback
        if context_normalized in self.page_help:
            page_info = self.page_help[context_normalized]
            if any(keyword in user_normalized for keyword in page_info["keywords"]):
                import random
                return random.choice(page_info["responses"])
        
        # Default response with helpful hint
        import random
        base_response = random.choice(self.general_responses["unknown"])
        if context_normalized in self.knowledge_base:
            return f"{base_response}\n\nTry asking:\n• 'What is this page?'\n• 'How do I use this?'\n• 'What should I enter?'\n• 'Help me with {context_normalized.lower()}'"
        return base_response
    
    def _normalize_context(self, context: str) -> str:
        """Normalize context name to match knowledge base keys"""
        context_map = {
            "Project Onboarding": "Project Onboarding",
            "Projects": "Projects",
            "Agent Execution": "Agent Execution",
            "Cloud Credentials": "Cloud Credentials",
            "Source Infrastructure": "Source Infrastructure",
            "Source Code": "Source Code",
            "Target Configuration": "Target Configuration",
            "Analytics": "Analytics",
            "Reports": "Reports",
            "Home": "Home",
            "Agents": "Agents",
            "All Agents": "Agents"
        }
        return context_map.get(context, context)


# Global bot instance (can be swapped for LLM later)
_bot_instance: Optional[BotService] = None

def get_bot_response(user_input: str, context: str) -> str:
    """
    Get bot response - uses rule-based by default, can be swapped for LLM
    
    Args:
        user_input: User's question
        context: Current page context
    
    Returns:
        Bot response string
    """
    global _bot_instance
    
    # Initialize bot if not already done
    if _bot_instance is None:
        _bot_instance = RuleBasedBot()
    
    return _bot_instance.get_response(user_input, context)


# Future: LLM Bot implementation
class LLMBot(BotService):
    """
    LLM-powered bot - to be implemented later
    This class can replace RuleBasedBot when ready
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        """
        Initialize LLM bot
        
        Args:
            api_key: API key for LLM service (OpenAI, Anthropic, etc.)
            model: Model to use
        """
        self.api_key = api_key
        self.model = model
        # TODO: Initialize LLM client
    
    def get_response(self, user_input: str, context: str) -> str:
        """
        Get response from LLM
        
        Args:
            user_input: User's question
            context: Current page context
        
        Returns:
            Bot response string
        """
        # TODO: Implement LLM call with context
        # Example structure:
        # prompt = f"You are a helpful assistant for a cloud migration platform. "
        #          f"The user is on the {context} page. "
        #          f"User question: {user_input}"
        # response = llm_client.generate(prompt)
        # return response
        
        # Placeholder
        return "LLM bot not yet implemented. Using rule-based bot."

