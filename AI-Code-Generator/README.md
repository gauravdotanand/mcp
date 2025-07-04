# AI Code Generator (Phase 1)

## Overview
A FastAPI backend for generating code using Azure OpenAI models, with support for custom coding approaches and mainframe context.

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables for Azure OpenAI:
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_VERSION` (default: 2023-05-15)

## Running the Server
```bash
uvicorn app.main:app --reload
```

## API Usage
### POST /generate-code
**Request Body:**
```
{
  "prompt": "<task description>",
  "context": "<mainframe context>",
  "coding_approach_samples": ["<sample1>", "<sample2>", ...],
  "coding_approach_sample_ids": [1, 2, 3],
  "extraction_requirements": "Extract account number from columns 10-20",
  "model": "gpt-4"
}
```