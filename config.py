"""
config.py
---------

Central configuration for the Concall Analyser project.

Loads environment variables and exposes project-wide constants.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# --------------------------------------------------------------------
# Load .env file
# --------------------------------------------------------------------

load_dotenv(Path(__file__).resolve().parent / ".env")
# --------------------------------------------------------------------
# Project Directories
# --------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_FOLDER = BASE_DIR / "output"

PDF_FOLDER = BASE_DIR / "pdfs"

LOG_FOLDER = BASE_DIR / "logs"

CACHE_FOLDER = BASE_DIR / "cache"

# Create folders automatically
for folder in (
    OUTPUT_FOLDER,
    PDF_FOLDER,
    LOG_FOLDER,
    CACHE_FOLDER,
):
    folder.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------
# API Keys
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# LLM Provider
# --------------------------------------------------------------------

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "openai",
).strip().lower()

# --------------------------------------------------------------------
# OpenAI Configuration
# --------------------------------------------------------------------

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "",
).strip()

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.5",
).strip()

# --------------------------------------------------------------------
# Analysis Settings
# --------------------------------------------------------------------

MAX_QUARTERS = int(
    os.getenv(
        "MAX_QUARTERS",
        "5",
    )
)

MAX_PDF_PAGES = int(
    os.getenv(
        "MAX_PDF_PAGES",
        "80",
    )
)

MAX_TRANSCRIPT_CHARS = int(
    os.getenv(
        "MAX_TRANSCRIPT_CHARS",
        "80000",
    )
)

MAX_OUTPUT_TOKENS = int(
    os.getenv(
        "MAX_OUTPUT_TOKENS",
        "8192",
    )
)

TEMPERATURE = float(
    os.getenv(
        "TEMPERATURE",
        "0.0",
    )
)

# --------------------------------------------------------------------
# Network Settings
# --------------------------------------------------------------------

REQUEST_TIMEOUT = int(
    os.getenv(
        "REQUEST_TIMEOUT",
        "30",
    )
)

DOWNLOAD_RETRIES = int(
    os.getenv(
        "DOWNLOAD_RETRIES",
        "3",
    )
)

RETRY_DELAY = float(
    os.getenv(
        "RETRY_DELAY",
        "2.0",
    )
)

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/136.0 Safari/537.36"
)

# --------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()

# --------------------------------------------------------------------
# Feature Flags
# --------------------------------------------------------------------

ENABLE_CACHE = os.getenv(
    "ENABLE_CACHE",
    "true",
).lower() == "true"

ENABLE_VERBOSE_LOGGING = os.getenv(
    "ENABLE_VERBOSE_LOGGING",
    "false",
).lower() == "true"

# --------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------

if MAX_QUARTERS < 1:
    MAX_QUARTERS = 1

if MAX_QUARTERS > 5:
    MAX_QUARTERS = 5

if MAX_OUTPUT_TOKENS < 1024:
    MAX_OUTPUT_TOKENS = 1024

if MAX_PDF_PAGES < 1:
    MAX_PDF_PAGES = 1

# --------------------------------------------------------------------
# CLI Test
# --------------------------------------------------------------------

if __name__ == "__main__":

    print("Configuration Loaded")
    print("-" * 40)

    print("BASE_DIR            :", BASE_DIR)
    print("OUTPUT_FOLDER       :", OUTPUT_FOLDER)
    print("PDF_FOLDER          :", PDF_FOLDER)
    print("CACHE_FOLDER        :", CACHE_FOLDER)
    print("LOG_FOLDER          :", LOG_FOLDER)

    print()
    print("LLM Provider        :", LLM_PROVIDER)
    print("OpenAI Model        :", OPENAI_MODEL)
    print("Max Quarters        :", MAX_QUARTERS)
    print("Max PDF Pages       :", MAX_PDF_PAGES)
    print("Output Tokens       :", MAX_OUTPUT_TOKENS)

    print()

    print(
        "OpenAI Key          :",
        "Loaded" if OPENAI_API_KEY else "Missing",
    )