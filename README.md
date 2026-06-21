# ShineMoon ImageGen Codex Skill

A Codex skill that routes image-generation requests through a ShineMoon OpenAI-compatible Images API endpoint.

It is designed for prompts like “生图：一只可爱的猫”, “generate an image of…”, or “use gpt-image-2 to create…”. The skill calls the configured API, decodes the returned `b64_json`, and saves the final image file locally.

## Features

- Uses `https://shinemoon.com/v1/images/generations`
- Defaults to `gpt-image-2`
- Requests `response_format: "b64_json"`
- Saves decoded images to a chosen output path
- Avoids storing API keys in the skill files
- Includes a reusable Python helper script with safe error summaries

## Install

Copy this folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R shinemoon-imagegen ~/.codex/skills/
```

Then restart or refresh Codex so the skill can be discovered.

## Configure

Set your ShineMoon API key as an environment variable:

```bash
export SHINEMOON_API_KEY="your-api-key"
```

Optional custom API base:

```bash
export SHINEMOON_IMAGE_API_BASE="https://shinemoon.com/v1"
```

Do not commit real API keys. Keep them in environment variables, shell profiles, secret managers, or local ignored files.

## Usage in Codex

Ask Codex to use the skill:

```text
Use $shinemoon-imagegen to generate a cute cat.
```

Or use natural Chinese prompts after the skill is installed:

```text
生图：一只穿粉色蝴蝶结的可爱小猫，柔和摄影风格
```

## Script usage

Dry run:

```bash
python3 scripts/generate_image.py \
  --prompt "a cute cat" \
  --out outputs/cute-cat.png \
  --dry-run
```

Generate an image:

```bash
SHINEMOON_API_KEY="your-api-key" \
python3 scripts/generate_image.py \
  --prompt "a cute cat" \
  --out outputs/cute-cat.png
```

Change size or model:

```bash
python3 scripts/generate_image.py \
  --prompt "a cinematic landscape at sunrise" \
  --size 1536x1024 \
  --model gpt-image-2 \
  --out outputs/landscape.png
```

## Project structure

```text
shinemoon-imagegen/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── generate_image.py
```

## Notes

- The API may return an image whose actual dimensions differ from the requested size. Keep or post-process the result according to your use case.
- This skill covers new image generation. Existing-image edits, masks, and transparent-background workflows may need a different workflow.
- The helper script prints sanitized error summaries and never intentionally prints the API key.

