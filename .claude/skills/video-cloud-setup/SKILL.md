---
name: video-cloud-setup
description: Set up or troubleshoot the claude.ai/code cloud environment for the easy-video-editing tools - allowed domains (Hugging Face for the speech model), setup script, and "blocked" errors. Use when speech-to-text fails with a 403/blocked error, or the person asks how to set up the cloud for video editing.
---

# Cloud setup for video editing

Explain in simple words. Never ask for passwords or keys in chat.

## Allowed domains (Network access: Limited + "Allow package managers")

Needed only for the speech-to-text model download:
```
huggingface.co
cdn-lfs.hf.co
cdn-lfs-us-1.hf.co
cdn-lfs.huggingface.co
cas-bridge.xethub.hf.co
cas-server.xethub.hf.co
transfer.xethub.hf.co
us.gcp.cdn.hf.co
us.aws.cdn.hf.co
```
Not needed by these tools (leave out unless there's another reason): `github.com`, `objects.githubusercontent.com`, `release-assets.githubusercontent.com` (git already works through the cloud proxy), `fonts.googleapis.com`, `fonts.gstatic.com` (the font comes from apt).
ffmpeg, pip packages and the Montserrat font come through "Allow package managers".

If a download is still blocked, the error names the host: add exactly that host.

## Setup script (so tools are ready at the start of every session)

```bash
#!/usr/bin/env bash
set -e
if [ -f norjaasiahmazneka/.claude/skills/easy-video-editing/scripts/install.sh ]; then
  bash norjaasiahmazneka/.claude/skills/easy-video-editing/scripts/install.sh
fi
```
(The setup script starts in the folder that holds the repositories.)

## Troubleshooting
- "403 Forbidden" / "blocked" during model download -> a Hugging Face host is missing from the list.
- Changes to the environment apply to new sessions; start a new one.
- Use the environment tools (get_environment / update_environment / create_environment) to propose changes; the person approves them.
