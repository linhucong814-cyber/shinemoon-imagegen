---
name: shinemoon-imagegen
description: Generate raster images through the user's configured ShineMoon OpenAI-compatible Images API instead of the default image generation path. Use when the user asks to generate images, says 生图/生成图片/画图, requests gpt-image-2 image generation, or wants the previously configured ShineMoon image workflow, unless the user explicitly asks for another provider, built-in image_gen, or a different API path.
---

# ShineMoon ImageGen

Use this skill as the default image-generation workflow for this user.

## Default configuration

- Endpoint: `https://shinemoon.com/v1/images/generations`
- Model: `gpt-image-2`
- Size: `1024x1024` unless the user asks for another size
- Response format: `b64_json`
- Output: decode the first `data[0].b64_json` item and save it as a user-facing image file

Never write the API key into this skill, scripts, response files, or final messages. Prefer an environment variable named `SHINEMOON_API_KEY`. If the key is only present in the active conversation, use it transiently and avoid echoing it.

## Workflow

1. Treat ordinary “生图” requests as new image generation via this skill.
2. Shape the prompt only as much as needed:
   - Preserve specific user wording and constraints.
   - For very short prompts, add light production detail only if it improves the likely output.
   - Do not add logos, brands, text, extra characters, or arbitrary story details unless requested.
3. Save final user-facing images under the workspace’s `outputs/` directory when available; otherwise use an appropriate project output path.
4. Run the bundled script:

   ```bash
   python3 "${CODEX_HOME:-$HOME/.codex}/skills/shinemoon-imagegen/scripts/generate_image.py" \
     --prompt "a cute cat" \
     --out outputs/cute-cat.png
   ```

5. Inspect the saved image with `view_image` when visual quality matters.
6. Report the final saved path and show the image inline when useful.

## Script notes

Use `scripts/generate_image.py` for the API call. It:

- reads `SHINEMOON_API_KEY` from the environment;
- posts the configured JSON payload to ShineMoon;
- decodes `b64_json`;
- writes the output file;
- prints safe status/error summaries without printing the key.

Use `--dry-run` to verify the payload without calling the API.

## Failure handling

- If the API key is missing, ask the user to set `SHINEMOON_API_KEY` or provide a key for the current run.
- If the service returns an error, show only the HTTP status and sanitized error message.
- If the service returns a different actual image size than requested, keep the image unless the user required exact dimensions; mention the mismatch and offer to crop/resize.
- If the user asks for editing an existing image, transparent-background generation, masks, or provider-specific controls this API/script does not cover, explain the limitation and ask whether to use another workflow.
