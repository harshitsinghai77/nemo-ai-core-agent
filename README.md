## Nemo AI Core Agent - AWS AI Agent Global Hackathon

#### Cut Your Feature Delivery Time in Half. Nemo AI converts your Jira Stories into ready-to-review Pull Requests.

**An intelligent multi-agent system that autonomously converts Jira stories into ready-to-review Github Pull Request using AWS Bedrock and AgentCore.**

[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange)](https://aws.amazon.com/bedrock/)
[![AgentCore](https://img.shields.io/badge/AWS-AgentCore-blue)](https://aws.amazon.com/bedrock/agentcore/)
[![Strands SDK](https://img.shields.io/badge/Strands-SDK-green)](https://strands.ai/)
[![Python](https://img.shields.io/badge/Python-3.13+-blue)](https://python.org)

## Project Overview

Nemo AI is an autonomous AI agent that turns Jira stories into first draft of Pull Request — automatically. It understands your jira story, analyzes your existing codebase, and creates a GitHub Pull Request with a first draft of the solution. It works with your existing tools like Jira, Confluence, GitHub, and AWS, so it fits naturally into your development workflow.

### Hackathon Requirements

**LLM**: AWS Bedrock (Claude Sonnet 4, Nova Pro)  
**AgentCore**: Code Interpreter for secure code execution  
**Autonomous Capabilities**: Multi-agent workflow with reasoning  
**External Integrations**: MCP Servers (Context7 MCP and AWS Knowledge MCP Server), GitHub, Confluence, Jira  
**Best Strands SDK Implementation**: Advanced multi-agent patterns  

## Architecture

### Core Engine (This Repository)
The core engine that manages the complete workflow from ingesting Jira story to Github Pull request. Built using a sophisticated multi-agent architecture with AWS Bedrock and AgentCore integration.

### System Internals

#### Multi-Agent Workflow Architecture
The system employs a **7-agent pipeline** that processes Jira stories through distinct phases:

1. **Planner Agent** (`planner_prompt`) - Analyzes Jira stories and creates implementation plans
2. **Senior Engineer Agent** - The only agent that writes code, implements changes
3. **Code Reviewer Agent** - Comprehensive code review covering security, quality, and design
4. **Coding Standards Agent** - Python best practices and PEP compliance
5. **System Design Agent** - Architecture and design patterns review
6. **Algorithm Specialist** - Performance and efficiency analysis
7. **Story Scoring Agent** - Validates implementation against Jira requirements
8. **Documentation Agent** - Generates a Pull Request (PR) comment writeup based on the changes.
 
#### Dual Workflow Support
- **Code Development Workflow** (`workflow.py`) - for The First Draft - Nemo AI serves as an autonomous software developer that turns Jira stories into ready-to-review pull requests. When a story moves to `In Progress`
- **Unpaid Intern** (`data_analyst_workflow.py`) - Nemo AI's data analyst intern that delivers fast, accurate business insights without requiring SQL or Python skills.

#### AWS Bedrock Integration
- **Claude Sonnet 4** - Primary model for complex reasoning and code generation
- **AWS Nova Pro** - Secondary model for specialized review tasks
- **AgentCore Code Interpreter** - Secure Python execution environment for data analysis 

### Supporting Microservices Platform

| Service | Repository | Purpose |
|---------|------------|---------|
| **DynamoDB Storage** | [nemo-ai-dynamodb](https://github.com/harshitsinghai77/nemo-ai-dynamodb) | Database for Jira story data ingested via Lambda. |
| **Observability** | [nemo-ai-observability-infra](https://github.com/harshitsinghai77/nemo-ai-observability-infra) | CloudWatch integration for Bedrock AgentCore Observability |
| **Message Queue** | [nemo-ai-sqs](https://github.com/harshitsinghai77/nemo-ai-sqs) | Enables decoupled communication between Jira Ingestion Lambda and Core Engine Lambda using a producer-consumer architecture. |
| **Jira Integration** | [nemo-ai-jira-ingestion-api](https://github.com/harshitsinghai77/nemo-ai-jira-ingestion-api) | Exposes an API endpoint to receive Jira webhooks, processes story data, and publishes messages to SQS for downstream consumption. |
| **ECS Task Definitions** | [nemo-ai-ecs-fargate-core](https://github.com/harshitsinghai77/nemo-ai-ecs-fargate-core) | Contains ECS Fargate task definitions used to deploy and manage containerized services. No service logic included. |

## Repository Structure & Navigation

### Core Components

```
src/
├── core/                           # Main workflow orchestration
│   ├── workflow.py                 # Multi-agent code development pipeline
│   ├── data_analyst_workflow.py    # Data analysis workflow with Code Interpreter
│   └── run_workflow.py             # Workflow dispatcher and GitHub integration
├── custom_tools/                   # Strands SDK tool implementations
│   ├── editor.py                   # Code editing capabilities
│   ├── file_read.py               # File reading operations
│   ├── file_write.py              # File writing operations
│   └── shell.py                   # Shell command execution
├── prompt/                         # Agent system prompts
│   └── agent_prompt.py            # All 7 agent prompts and instructions
├── utils/                          # Utility modules
│   ├── github_utils.py            # GitHub API integration and PR management
│   ├── change_manifest.py         # Git diff tracking and change detection
│   ├── aws_secrets.py             # AWS Secrets Manager integration
│   └── otel_utils.py              # OpenTelemetry observability setup
└── ckg/                           # Code Knowledge Graph (experimental)
    ├── ast_reader.py              # Abstract Syntax Tree analysis
    └── ckg_vector_store_*.py      # Vector store implementations
```

### Entry Points

- **`main.py`** - AWS Lambda handler for SQS-triggered workflows
- **`ecs_main.py`** - ECS Fargate task for long-running workflows
- **`cdk_app.py`** - AWS CDK infrastructure deployment

### Key Workflow Classes

#### DataAnalystWorkflow (`data_analyst_workflow.py`)
- **FileHandler** - Manages file operations and uploads to Code Interpreter
- **CodeInterpreterSession** - AWS AgentCore Code Interpreter management
- **DataAnalystAgent** - Strands agent with Python execution tools

#### Multi-Agent Pipeline (`workflow.py`)
- **Agent Initialization** - Sets up 7 specialized agents with different models
- **MCP Integration** - Context7 and AWS Documentation MCP servers
- **Change Tracking** - Git-based manifest system for code changes
- **Review Orchestration** - Parallel execution of review agents

## Technology Stack

### AWS Services Architecture

#### Core AI Services
- **Amazon Bedrock**: Foundation models orchestration
  - `us.anthropic.claude-sonnet-4-20250514-v1:0` - Primary reasoning and code generation
  - `us.amazon.nova-pro-v1:0` - Specialized review tasks and analysis
  - Cross-region failover with retry configuration
  - Model access through IAM roles and resource-based policies

- **Bedrock AgentCore**: Secure execution environment
  - **Code Interpreter** - Isolated Python sandbox for data analysis
  - **Memory Service** - Persistent context across agent interactions
  - **Observability** - Built-in tracing and monitoring
  - **Identity Management** - Secure authentication and access control

#### Compute & Orchestration
- **AWS Lambda**: Event-driven serverless execution
  - Python 3.13 runtime with AWS Powertools
  - SQS trigger integration for Jira webhook processing
  - 15-minute timeout limit for standard workflows
  - Auto-scaling based on SQS queue depth
  - VPC configuration for secure resource access

- **Amazon ECS Fargate**: Container orchestration for long-running tasks
  - Serverless container execution without EC2 management
  - Custom task definitions with resource allocation
  - Integration with Application Load Balancer
  - Auto-scaling based on CPU/memory utilization
  - CloudWatch Container Insights for monitoring

#### Data & Messaging
- **Amazon SQS**: Asynchronous message processing
  - Standard queues for Jira webhook ingestion
  - Dead letter queues for error handling
  - Message visibility timeout configuration
  - Batch processing for improved throughput

- **Amazon DynamoDB**: NoSQL database for metadata
  - Jira story tracking and status management
  - On-demand billing with auto-scaling
  - Global secondary indexes for query optimization
  - Point-in-time recovery and backup

#### Networking & Security
- **VPC Configuration**: Secure network isolation
  - Private subnets for Lambda and ECS tasks
  - NAT Gateway for outbound internet access
  - Security groups with least-privilege access
  - VPC endpoints for AWS service communication

- **IAM Roles & Policies**: Fine-grained access control
  - Lambda execution roles with minimal permissions
  - ECS task roles for service-specific access
  - Cross-account access for multi-environment deployments

### AI & ML Framework
- **Strands Agents SDK**: Multi-agent workflow orchestration with async execution and tool integration
- **Model Context Protocol (MCP)**: 
  - **Context7 MCP** - Real-time library documentation and code examples
  - **AWS Knowledge MCP** - AWS service documentation and best practices
- **OpenTelemetry**: Distributed tracing and observability with OTLP export

### Advanced Features

#### Intelligent Code Analysis
- **AST-based Code Understanding** - Abstract Syntax Tree analysis for precise code modification
- **Vector Store Integration** - FAISS and Qdrant support for semantic code search
- **Change Manifest System** - Git-based tracking of all code modifications

#### MCP Server Integration
```python
# Context7 MCP for library documentation
context7_mcp = MCPClient(lambda: streamablehttp_client("https://mcp.context7.com/mcp"))

# AWS Documentation MCP for service knowledge
aws_documentation_mcp = MCPClient(lambda: streamablehttp_client("https://knowledge-mcp.global.api.aws"))
```

#### Parallel Agent Execution
```python
# Concurrent review by multiple specialized agents
feedback_results = await asyncio.gather(*[
    agent.invoke_async(review_task) for agent in review_agents.values()
])
```

### Development Tools
- **GitHub Integration**: Automated PR creation and repository management
- **Jira Integration**: Story parsing and requirement extraction
- **Docker**: Containerized deployment

## Quick Start

### Prerequisites
- AWS Account with Bedrock and AgentCore access
- Python 3.13+
- Docker
- AWS CDK

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/nemo-ai-core-agent
cd nemo-ai-core-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure AWS credentials**
```bash
aws configure
```

4. **Deploy infrastructure**
```bash
cdk deploy
```

### Usage

#### Lambda Deployment (< 15 minutes)
```python
# Triggered via SQS message from Jira webhook
{
    "github_link": "https://github.com/user/repo",
    "jira_story": "Create API endpoint for user authentication",
    "jira_story_id": "AUTH-123",
    "is_data_analysis_task": false
}
```

#### ECS Task Execution (Long-running tasks)
```bash
# Set environment variables
export GITHUB_LINK="https://github.com/user/repo"
export JIRA_STORY="Analyze user engagement data and create visualizations"
export JIRA_STORY_ID="DATA-456"
export IS_DATA_ANALYSIS_TASK="true"

# Run ECS task
python ecs_main.py
```

### Workflow Execution Flow

#### Code Development Pipeline
1. **Repository Cloning** - GitHub repository is cloned to `/tmp/{project_name}`
2. **Planning Phase** - Planner agent analyzes Jira story and creates implementation plan
3. **Implementation** - Senior Engineer agent writes code using MCP documentation
4. **Change Detection** - Git manifest captures all modifications
5. **Parallel Review** - 5 specialized agents review code concurrently
6. **Revision** - Senior Engineer addresses review feedback
7. **Validation** - Story Scoring agent validates requirements fulfillment
8. **Documentation** - PR body generation with technical details
9. **GitHub Integration** - Automated PR creation with comprehensive details

#### Data Analytics Pipeline
1. **File Upload** - Data files uploaded to AgentCore Code Interpreter sandbox
2. **Analysis Execution** - Python code execution in secure environment
3. **Visualization Generation** - Charts, graphs, and reports created
4. **Export** - Results exported back to local filesystem
5. **PR Creation** - Analysis results committed to repository

### Key Internal Components

#### Change Manifest System
```python
# Tracks all code modifications with precise line-level changes
change_manifest = get_manifest(project_name=project_name, py_only=True)
# Returns: {"changes": [{"file_path": "...", "change_type": "...", "content": "..."}]}
```

#### Agent Tool Integration
```python
@tool
def execute_python(code: str, description: str = "") -> str:
    """Execute Python code in AgentCore Code Interpreter sandbox"""
    response = code_interpreter_session.client.invoke("executeCode", {
        "code": code, "language": "python", "clearContext": False
    })
```

#### MCP Documentation Lookup
```python
# Automatic library documentation retrieval
# 1. resolve-library-id("boto3") → get library_id  
# 2. get-library-docs(library_id, "S3 client usage") → latest API docs
# 3. AWS Documentation search for best practices
```

## Development & Debugging

### Local Development
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS credentials and configuration

# Run locally with test data
python main.py
```

### Key Configuration Files
- **`.env`** - Environment variables and AWS configuration
- **`otel_config.env`** - OpenTelemetry observability settings
- **`cdk.json`** - AWS CDK deployment configuration
- **`requirements.txt`** - Production dependencies
- **`requirements-dev.txt`** - Development dependencies

### Monitoring & Observability
- **AgentCore Observability** - Built-in tracing for agent execution
- **OpenTelemetry Integration** - Distributed tracing across the workflow
- **CloudWatch Logs** - Comprehensive logging for debugging

### Customization Points

#### Adding New Review Agents
```python
# In workflow.py
new_review_agent = Agent(
    name='new_reviewer',
    model=bedrock_nova_pro_model,
    system_prompt=your_custom_prompt,
    tools=[file_read, shell]
)

# Add to review_agents dictionary
review_agents['new_reviewer'] = new_review_agent
```

## Contributing

This project is part of the AWS AI Agent Global Hackathon 2025. For questions or collaboration opportunities, please reach out through the hackathon platform.

### Architecture Decisions
- **Multi-Agent Design** - Specialized agents for different aspects of code review
- **MCP Integration** - Real-time documentation access for accurate implementations  
- **Processing** - Lambda for quick tasks, ECS for complex analysis
- **Integration** - Integrationg with Jira, Github, Confluence, external MCP Servers, Observability.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built for AWS AI Hackathon 2025**  
*Nemo AI handles the first draft, so your team can focus on what matters: shipping quality features, solving hard problems, and scaling faster.*