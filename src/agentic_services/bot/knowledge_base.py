"""
Comprehensive Knowledge Base for Chat Bot
Q&A database organized by page with multiple question variations
"""

KNOWLEDGE_BASE = {
    "Agents": {
        "questions": [
            # Count/Number questions
            ["how many agents", "how many agents are there", "how many agents available", "total agents", 
             "number of agents", "agent count", "how many ai agents", "what is the total", "count of agents",
             "how many do you have", "how many are available", "total number"],
            # General info
            ["what are the agents", "list agents", "show agents", "what agents", "which agents",
             "tell me about agents", "explain agents", "what can agents do"],
            # Focus areas
            ["what are the focus areas", "focus areas", "categories", "types of agents", "agent categories",
             "what groups", "how are agents organized"],
            # Specific agents
            ["migration agents", "finops agents", "aiops agents", "discovery agents", "assessment agents"],
            # Capabilities
            ["what can agents do", "agent capabilities", "what do agents help with", "agent features"],
        ],
        "answers": {
            "count": "We have **24 AI agents** available, all fully implemented and ready to use. They're organized into 3 main focus areas: **Migration & Modernization** (12 agents), **Cost Optimization & FinOps** (5 agents), and **AIOps & Intelligent Operations** (7 agents).",
            "general": "Our platform includes **24 specialized AI agents** that automate cloud migration tasks:\n\n"
                      "• **Migration & Modernization** (12 agents): Infrastructure scanning, application profiling, data discovery, dependency mapping, network analysis, provisioning, migration, configuration, testing, and rollback\n\n"
                      "• **Cost Optimization & FinOps** (5 agents): Cost estimation, capacity planning, performance baselining, cost optimization, and performance optimization\n\n"
                      "• **AIOps & Intelligent Operations** (7 agents): Security auditing, compliance checking, risk assessment, licensing analysis, security hardening, monitoring setup, and documentation generation",
            "focus_areas": "Agents are organized into **3 focus areas**:\n\n"
                          "1. **Migration & Modernization** (M) - 12 agents for end-to-end cloud migration\n"
                          "2. **Cost Optimization & FinOps** (F) - 5 agents for cost management and optimization\n"
                          "3. **AIOps & Intelligent Operations** (A) - 7 agents for security, compliance, and operations",
            "capabilities": "Our 24 agents can help with:\n\n"
                           "• **Discovery**: Scan infrastructure, profile applications, discover data sources\n"
                           "• **Assessment**: Map dependencies, check compliance, estimate costs, assess risks\n"
                           "• **Execution**: Provision infrastructure, migrate data and applications, configure systems\n"
                           "• **Optimization**: Optimize costs and performance, harden security, set up monitoring"
        }
    },
    "Cloud Credentials": {
        "questions": [
            # What/How questions
            ["what are aws credentials", "what credentials", "what do i need", "what should i enter",
             "how to configure", "how do i set up", "how to add credentials", "what is required"],
            # Specific fields
            ["access key", "secret key", "aws access key", "secret access key", "region", "aws region",
             "iam role", "role arn", "what is access key", "what is secret key"],
            # Demo mode
            ["demo mode", "what is demo mode", "mock data", "testing mode", "no credentials"],
            # Security
            ["security", "safe", "secure", "iam role vs access key", "which is better", "recommendation"],
            # Help/General
            ["help", "what is this page", "what do i do here", "how does this work", "explain"],
        ],
        "answers": {
            "what": "On this page, you configure AWS credentials so agents can access your cloud infrastructure:\n\n"
                   "**Required Information:**\n"
                   "• **Access Key ID**: Your AWS access key (found in IAM console)\n"
                   "• **Secret Access Key**: Your AWS secret key (keep this secure!)\n"
                   "• **Region**: AWS region (e.g., us-east-1, eu-west-1)\n\n"
                   "**Alternative:** Use IAM Role ARN for better security (recommended for production)",
            "demo_mode": "**Demo Mode** allows you to test the platform without real AWS credentials:\n\n"
                        "✅ No AWS credentials needed\n"
                        "✅ Uses simulated/mock data\n"
                        "✅ Fast execution (~1.5s per agent)\n"
                        "✅ Perfect for testing and demonstrations\n"
                        "✅ No AWS costs\n\n"
                        "Enable Demo Mode if you want to explore the platform without connecting to real AWS.",
            "security": "**Security Best Practices:**\n\n"
                       "🔒 **For Production**: Use IAM Role ARN (cross-account role) - more secure\n"
                       "🔑 **For Development/Testing**: Access keys are acceptable\n\n"
                       "IAM roles are recommended because:\n"
                       "• No long-lived credentials to manage\n"
                       "• Automatic credential rotation\n"
                       "• Better audit trail\n"
                       "• More granular permissions",
            "help": "This page configures AWS access for your migration project. You can either:\n\n"
                   "1. **Enable Demo Mode** - Test without real credentials (uses mock data)\n"
                   "2. **Enter AWS Credentials** - Access Key ID, Secret Key, and Region\n"
                   "3. **Use IAM Role ARN** - More secure option for production\n\n"
                   "Agents need these credentials to interact with your AWS account during migration."
        }
    },
    "Source Infrastructure": {
        "questions": [
            # What/How
            ["what is source infrastructure", "what should i enter", "what information", "how to define",
             "what do i need to provide", "what details", "how does this work"],
            # Types
            ["source type", "migration type", "cloud to cloud", "on premises", "hybrid", "aws to aws"],
            # Specific fields
            ["servers", "vms", "virtual machines", "applications", "databases", "network", "topology"],
            # Help
            ["help", "what is this page", "explain", "what do i do", "purpose"],
        ],
        "answers": {
            "what": "Define your **current infrastructure** that needs to be migrated:\n\n"
                   "**What to Provide:**\n"
                   "• **Environment Type**: Cloud-to-cloud, On-premises to cloud, or Hybrid\n"
                   "• **Servers/VMs**: List of servers and virtual machines\n"
                   "• **Applications**: Applications running on your infrastructure\n"
                   "• **Databases**: Database instances and types\n"
                   "• **Network**: Network topology and connectivity\n\n"
                   "This information helps agents understand your current setup and plan the migration accurately.",
            "types": "**Migration Types:**\n\n"
                    "1. **Cloud to Cloud (AWS to AWS)** - Migrating within AWS (region/account)\n"
                    "2. **Cloud to Cloud (Other to AWS)** - Migrating from Azure/GCP to AWS\n"
                    "3. **On-Premises to Cloud** - Migrating from datacenter to AWS\n"
                    "4. **Hybrid** - Mixed environment migration\n\n"
                    "Select the type that matches your migration scenario.",
            "help": "This page captures details about your **current infrastructure** before migration:\n\n"
                   "**Why it's important:**\n"
                   "• Agents need to understand your current environment\n"
                   "• Helps identify dependencies and relationships\n"
                   "• Enables accurate migration planning\n"
                   "• Reduces risks during migration\n\n"
                   "Provide as much detail as possible for the best migration plan."
        }
    },
    "Source Code": {
        "questions": [
            # What/How
            ["what is source code", "what should i enter", "repository", "git", "github", "gitlab",
             "how to configure", "what do i need"],
            # Fields
            ["repository url", "branch", "access token", "authentication", "private repo"],
            # Help
            ["help", "what is this page", "why do i need this", "what if no code", "infrastructure only"],
        ],
        "answers": {
            "what": "Configure access to your **source code repositories**:\n\n"
                   "**What to Provide:**\n"
                   "• **Repository URL**: Your Git repository (GitHub, GitLab, Bitbucket, etc.)\n"
                   "• **Branch**: Main branch to analyze (usually 'main' or 'master')\n"
                   "• **Access Token**: Authentication token for private repositories\n\n"
                   "**Why it's needed:**\n"
                   "Agents analyze your codebase to identify dependencies, frameworks, and generate accurate migration strategies.",
            "no_code": "If your migration is **infrastructure-only** (no custom applications):\n\n"
                      "✅ You can skip source code configuration\n"
                      "✅ Check 'This migration includes application source code' to disable\n"
                      "✅ Agents will focus on infrastructure migration only\n\n"
                      "This is common for lift-and-shift migrations or infrastructure modernization.",
            "help": "This page configures access to your application source code:\n\n"
                   "**When you need it:**\n"
                   "• Migrating custom applications\n"
                   "• Refactoring or replatforming apps\n"
                   "• Need dependency analysis\n\n"
                   "**When you can skip:**\n"
                   "• Infrastructure-only migrations\n"
                   "• No custom code to migrate\n"
                   "• Using pre-built cloud services only"
        }
    },
    "Target Configuration": {
        "questions": [
            # What/How
            ["what is target configuration", "target", "where to migrate", "destination", "what should i enter",
             "how to configure", "what do i need"],
            # Fields
            ["cloud provider", "aws", "azure", "gcp", "region", "services", "architecture", "ec2", "lambda"],
            # Help
            ["help", "what is this page", "explain", "what do i do"],
        ],
        "answers": {
            "what": "Define your **target cloud environment** where resources will be migrated:\n\n"
                   "**What to Configure:**\n"
                   "• **Cloud Provider**: AWS, Azure, or GCP\n"
                   "• **Region**: Target region for deployment (e.g., us-east-1)\n"
                   "• **Services**: Target services (EC2, ECS, Lambda, RDS, etc.)\n"
                   "• **Architecture**: Target architecture patterns (microservices, serverless, etc.)\n\n"
                   "This helps agents plan the migration to your desired target environment.",
            "help": "This page defines **where and how** your infrastructure will be migrated:\n\n"
                   "**Key Decisions:**\n"
                   "• Which cloud provider (AWS, Azure, GCP)\n"
                   "• Which region to deploy to\n"
                   "• Which services to use\n"
                   "• What architecture pattern to adopt\n\n"
                   "Agents use this to generate migration plans and provisioning scripts."
        }
    },
    "Project Onboarding": {
        "questions": [
            # What/How
            ["how to create project", "what is required", "what fields", "how do i start", "what should i enter",
             "project name", "description", "requirements"],
            # Fields
            ["timeline", "priority", "budget", "complexity", "what is priority", "what is timeline"],
            # Help
            ["help", "what is this page", "how does this work", "explain", "what do i do"],
        ],
        "answers": {
            "what": "Create a new **migration project** by filling in:\n\n"
                   "**Required:**\n"
                   "• **Project Name**: Descriptive name (e.g., 'E-Commerce Platform Migration')\n\n"
                   "**Optional but Recommended:**\n"
                   "• **Description**: Overview of the migration\n"
                   "• **Requirements & Goals**: Detailed requirements, constraints, and objectives\n"
                   "• **Timeline**: Expected duration (1-3 months, 3-6 months, etc.)\n"
                   "• **Priority**: Business priority (High, Medium, Low)\n"
                   "• **Budget**: Estimated budget range\n"
                   "• **Complexity**: Technical complexity level\n\n"
                   "Once created, you'll configure credentials, infrastructure, and start agent execution.",
            "help": "This is where you **start your migration journey**:\n\n"
                   "**Steps:**\n"
                   "1. Fill in project details\n"
                   "2. Click 'Create Project'\n"
                   "3. Configure Cloud Credentials\n"
                   "4. Define Source Infrastructure\n"
                   "5. Set Target Configuration\n"
                   "6. Execute Agents\n\n"
                   "The more information you provide, the better the migration plan will be."
        }
    },
    "Projects": {
        "questions": [
            # What/How
            ["what is this page", "how to manage projects", "view projects", "what can i do",
             "how to delete", "how to edit", "project details"],
            # Actions
            ["delete project", "edit project", "execute", "view details", "configure"],
            # Help
            ["help", "explain", "what do i do here"],
        ],
        "answers": {
            "what": "This page shows **all your migration projects**:\n\n"
                   "**You can:**\n"
                   "• **View Details**: Click 'Details' to see project information\n"
                   "• **Execute Agents**: Click 'Execute' to start agent workflows\n"
                   "• **Configure**: Set up credentials, infrastructure, and target config\n"
                   "• **Delete**: Remove projects you no longer need\n\n"
                   "Use this page to manage and monitor all your migration projects.",
            "actions": "**Available Actions:**\n\n"
                      "📋 **Details**: View full project information, progress, and settings\n"
                      "⚡ **Execute**: Start agent execution for this project\n"
                      "✏️ **Edit**: Modify project details (coming soon)\n"
                      "🗑️ **Delete**: Permanently remove the project\n\n"
                      "Click 'Details' first to access configuration options."
        }
    },
    "Agent Execution": {
        "questions": [
            # What/How
            ["how to execute agents", "how to run agents", "what is this page", "how does this work",
             "what can i do", "how to start"],
            # Phases
            ["discovery", "assessment", "execution", "optimization", "phases", "what are the phases"],
            # Agents
            ["which agents", "what agents to run", "run all", "run individual"],
            # Help
            ["help", "explain", "what do i do"],
        ],
        "answers": {
            "what": "Execute **AI agents** to perform migration tasks:\n\n"
                   "**Phases:**\n"
                   "1. **Discovery**: Scan infrastructure, profile applications, discover data\n"
                   "2. **Assessment**: Map dependencies, check compliance, estimate costs\n"
                   "3. **Execution**: Provision infrastructure, migrate data and applications\n"
                   "4. **Optimization**: Optimize costs, performance, security\n\n"
                   "You can run agents individually or run all agents in a phase.",
            "phases": "**Migration Phases:**\n\n"
                     "🔍 **Discovery** (8 agents): Infrastructure scanning, application profiling, data discovery\n"
                     "📊 **Assessment** (5 agents): Dependency mapping, compliance, cost estimation, risk assessment\n"
                     "🚀 **Execution** (6 agents): Provisioning, data migration, application migration, configuration\n"
                     "⚡ **Optimization** (5 agents): Cost optimization, performance optimization, security hardening\n\n"
                     "Run phases in order for best results.",
            "help": "This page allows you to **run AI agents** for your migration project:\n\n"
                   "**How to use:**\n"
                   "1. Select a phase (Discovery, Assessment, Execution, Optimization)\n"
                   "2. Choose individual agents or click 'Run All' for the phase\n"
                   "3. Monitor progress and results\n"
                   "4. Review agent outputs and artifacts\n\n"
                   "Agents will perform automated tasks based on your project configuration."
        }
    },
    "Analytics": {
        "questions": [
            # What/How
            ["what is analytics", "what metrics", "what insights", "what can i see", "how to view"],
            # Metrics
            ["agent performance", "migration metrics", "cost analysis", "timeline", "progress"],
            # Help
            ["help", "what is this page", "explain"],
        ],
        "answers": {
            "what": "View **analytics and insights** about your migrations:\n\n"
                   "**Available Metrics:**\n"
                   "• **Agent Performance**: How agents are performing\n"
                   "• **Migration Metrics**: Track migration progress\n"
                   "• **Cost Analysis**: View cost estimates and savings\n"
                   "• **Timeline**: Monitor project timelines\n\n"
                   "Use analytics to track progress and make data-driven decisions.",
            "help": "This page provides **real-time insights** into your migration projects:\n\n"
                   "**What you'll see:**\n"
                   "• Agent execution statistics\n"
                   "• Migration progress tracking\n"
                   "• Cost analysis and savings\n"
                   "• Timeline and milestone tracking\n\n"
                   "Use this to monitor your migration health and performance."
        }
    },
    "Reports": {
        "questions": [
            # What/How
            ["what reports", "what artifacts", "what documents", "what can i download", "how to download"],
            # Types
            ["wave plan", "migration strategy", "assessment", "artifacts", "documents"],
            # Help
            ["help", "what is this page", "explain"],
        ],
        "answers": {
            "what": "View and download **migration artifacts**:\n\n"
                   "**Available Artifacts:**\n"
                   "• **Wave Plans**: Detailed migration wave plans\n"
                   "• **Migration Strategies**: Comprehensive migration strategies\n"
                   "• **Assessments**: Cloud readiness assessments\n"
                   "• **Download**: Get artifacts in various formats (PDF, Markdown, etc.)\n\n"
                   "All generated documents and reports are available here for download.",
            "help": "This page contains all **migration artifacts** generated by agents:\n\n"
                   "**What you'll find:**\n"
                   "• Wave plans for phased migrations\n"
                   "• Migration strategy documents\n"
                   "• Cloud readiness assessments\n"
                   "• Technical documentation\n\n"
                   "You can preview and download all artifacts generated during your migration."
        }
    },
    "Home": {
        "questions": [
            # What/How
            ["what is this", "what can i do", "how to start", "where to begin", "getting started"],
            # Features
            ["create project", "view agents", "live demo", "features", "capabilities"],
            # Help
            ["help", "explain", "what is nagarro"],
        ],
        "answers": {
            "what": "Welcome to **Nagarro Agentic Services**!\n\n"
                   "**Quick Start:**\n"
                   "• **Create Project**: Start a new migration project\n"
                  "• **View Agents**: Explore our 24 AI agents\n"
                  "• **Agent Showcase**: See agents in action\n\n"
                   "Get started by creating your first migration project.",
            "help": "This is your **home dashboard** for cloud migration:\n\n"
                   "**What you can do:**\n"
                   "• Create and manage migration projects\n"
                  "• Explore 24 specialized AI agents\n"
                  "• Try the Agent Showcase\n"
                   "• Monitor project progress\n\n"
                   "Start by creating a project or exploring our agents."
        }
    }
}






