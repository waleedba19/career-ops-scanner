#!/bin/bash
# ============================================================
# setup_model_release.sh — One-time: upload Ollama model to GitHub Release
# After this, every GitHub Actions run downloads from the release (permanent)
#
# Usage:
#   1. Make sure Ollama is installed locally: curl -fsSL https://ollama.com/install.sh | sh
#   2. Pull the model: ollama pull qwen2.5:7b-instruct-q3_K_M
#   3. Run this script: bash setup_model_release.sh
#
# Requires: gh CLI authenticated, jq
# ============================================================

set -euo pipefail

MODEL_TAG="qwen2.5:7b-instruct-q3_K_M"
RELEASE_TAG="models-v1"
ASSET_NAME="ollama-qwen2.5-7b.tar.gz"
REPO="waleedba19/career-ops-scanner"

echo "=== CareerOps Model Release Setup ==="
echo ""

# 1. Check prerequisites
echo "[1/5] Checking prerequisites..."
if ! command -v ollama &>/dev/null; then
    echo "ERROR: ollama not installed. Run: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi
if ! command -v gh &>/dev/null; then
    echo "ERROR: gh CLI not installed. Run: https://cli.github.com/"
    exit 1
fi
if ! gh auth status &>/dev/null; then
    echo "ERROR: gh not authenticated. Run: gh auth login"
    exit 1
fi
if ! command -v jq &>/dev/null; then
    echo "WARNING: jq not found, will use basic JSON parsing"
fi
echo "  OK — ollama, gh, all ready"

# 2. Check model is pulled
echo ""
echo "[2/5] Checking if model is pulled locally..."
if ! ollama list 2>/dev/null | grep -q "qwen2.5:7b"; then
    echo "  Model not found. Pulling ${MODEL_TAG} (~3.5GB)..."
    ollama pull "${MODEL_TAG}"
fi
echo "  OK — model is ready locally"

# 3. Find model files
echo ""
echo "[3/5] Locating model files..."
OLLAMA_DIR="${OLLAMA_DIR:-$HOME/.ollama}"
MODEL_DIR="${OLLAMA_DIR}/models"

if [ ! -d "${MODEL_DIR}/manifests" ]; then
    echo "ERROR: Model directory not found at ${MODEL_DIR}"
    echo "Expected: ${MODEL_DIR}/manifests/ exists"
    exit 1
fi

# Get model size
MODEL_SIZE=$(du -sh "${MODEL_DIR}" 2>/dev/null | cut -f1)
echo "  Model directory: ${MODEL_DIR}"
echo "  Model size: ${MODEL_SIZE}"

# 4. Compress
echo ""
echo "[4/5] Compressing model files..."
TARFILE="/tmp/${ASSET_NAME}"
rm -f "${TARFILE}"

cd "${OLLAMA_DIR}"
tar -czf "${TARFILE}" models/
cd - >/dev/null

TAR_SIZE=$(du -sh "${TARFILE}" 2>/dev/null | cut -f1)
echo "  Compressed: ${TARFILE} (${TAR_SIZE})"

# 5. Upload to GitHub Release
echo ""
echo "[5/5] Uploading to GitHub Release..."

# Delete existing release if present
gh release delete "${RELEASE_TAG}" --repo "${REPO}" --yes --cleanup-tag 2>/dev/null || true

# Create release
gh release create "${RELEASE_TAG}" \
    --repo "${REPO}" \
    --title "Ollama Model: qwen2.5:7b" \
    --notes "Permanent storage for the Ollama model used by CareerOps scanner.
    
Model: qwen2.5:7b-instruct-q3_K_M
Size: ~${TAR_SIZE}

This release is downloaded automatically by the GitHub Actions workflow.
Do NOT delete this release — it prevents the 3.5GB model from being re-downloaded on every run." \
    "${TARFILE}#ollama-qwen2.5-7b.tar.gz"

rm -f "${TARFILE}"

echo ""
echo "=== DONE ==="
echo ""
echo "The model is now permanently stored in GitHub Release '${RELEASE_TAG}'."
echo "Every GitHub Actions run will download it from there (~30 sec instead of ~3 min)."
echo ""
echo "The release never expires. To update the model later:"
echo "  1. Pull new model: ollama pull qwen2.5:7b-instruct-q3_K_M"
echo "  2. Re-run this script: bash setup_model_release.sh"
