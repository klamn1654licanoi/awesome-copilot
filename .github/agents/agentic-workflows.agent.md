# Agentic Workflows Agent

## Overview

This agent defines guidelines for agentic and multi-step workflow tasks
within the awesome-copilot project. It helps Copilot understand how to
plan, execute, and validate multi-step operations.

## Guidelines

- Break complex tasks into clearly defined, sequential steps.
- Validate inputs and outputs at each step before proceeding.
- Prefer idempotent operations where possible.
- Log meaningful progress messages at each stage.
- Handle errors gracefully and provide actionable feedback.
- Avoid side effects outside the declared scope of the workflow.
- Use existing project scripts (e.g., `scripts/`) as building blocks.
- Prefer reading configuration from files over hardcoded values.
- Always clean up temporary resources after workflow completion.
- Document any assumptions made during workflow execution.

## Workflow Structure

Each agentic workflow should follow this structure:

1. **Input validation** — confirm required parameters are present and valid.
2. **Planning** — outline the steps to be taken.
3. **Execution** — carry out each step, checking for errors.
4. **Verification** — confirm the expected outcome was achieved.
5. **Reporting** — summarise what was done and any warnings.

## Examples

- Validating all contributor entries and reporting issues.
- Checking instruction files for required sections and formatting.
- Generating summary reports from structured JSON data.
