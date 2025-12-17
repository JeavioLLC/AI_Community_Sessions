# Google ADK

A collection of AI agent projects built with Google's Agent Development Kit (ADK), created for the Jeavio AI Community sessions.

## Projects

### 📽️ [BookMyShow](/bookmyshow)

A movie ticket booking agent that demonstrates progressive agent development:

- **Part 1** - Basic agent setup
- **Part 2** - Adding tools
- **Part 3** - Implementing callbacks
- **Part 4** - Agent handoff patterns
- **Part 5** - Complete multi-agent system with showtime and seat agents

👉 See [bookmyshow/README.md](/bookmyshow/README.md) for setup and usage instructions.

### 🧮 [Math Problem Solver](/math-problem-solver)

An intelligent math solving pipeline featuring:

- **Reasoner Agent** - Breaks down and solves math problems
- **Verifier Agent** - Validates solutions
- **Fixer Agent** - Corrects errors in solutions

👉 See [math-problem-solver/README.md](/math-problem-solver/README.md) for setup and usage instructions.

## Getting Started

### Prerequisites

- Python 3.10+
- Google ADK and other Dependencies (`pip install -r requirements.txt`)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd AI_Community_Sessions
```

2. Navigate to a project and follow its README for specific setup instructions.

## Project Structure

```
AI_Community_Sessions/
├── bookmyshow/           # Movie booking agent
│   ├── part1_agent/      # Basic agent
│   ├── part2_tool/       # Agent with tools
│   ├── part3_callback/   # Agent with callbacks
│   ├── part4_handoff/    # Multi-agent handoff
│   └── part5_final/      # Complete implementation
│
└── math-problem-solver/  # Math solving pipeline
    └── math_solver_pipeline/
        ├── reasoner_agent/
        └── math_loop/
            ├── verifier_agent/
            └── fixer_agent/
```

