import json
import logging
import subprocess
import tempfile
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from parser import extract_clean_text

_ROOT = Path(__file__).resolve().parent
_OUTPUT_DIR = _ROOT / "output"

# ── Logging setup ─────────────────────────────────────────────────
_OUTPUT_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("esg_auditor")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(_OUTPUT_DIR / "app.log", encoding="utf-8")
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(fh)

app = FastAPI(title="ESG PDF Parser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/parse")
async def parse_pdf(file: UploadFile):
    if not file.filename.lower().endswith(".pdf"):
        logger.warning("Rejected non-PDF upload: %s", file.filename)
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    content = await file.read()
    logger.info("API: PDF upload received: %s (%d bytes)", file.filename, len(content))

    tmp_in = None
    tmp_out_path = None

    try:
        # Write uploaded PDF to a temp file
        tmp_in = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp_in.write(content)
        tmp_in.close()
        logger.debug("API: Temp PDF written to %s", tmp_in.name)

        # Prepare output path
        tmp_out_path = tmp_in.name + ".json"

        # Run LiteParse
        logger.info("API: Starting LiteParse...")
        t0 = time.perf_counter()
        result = subprocess.run(
            [
                "liteparse", "parse",
                "--format", "json",
                "-q",
                "-o", tmp_out_path,
                tmp_in.name,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        elapsed = time.perf_counter() - t0

        if result.returncode != 0:
            logger.error("API: LiteParse failed (exit %d): %s", result.returncode, result.stderr.strip())
            raise HTTPException(
                status_code=502,
                detail=f"LiteParse failed: {result.stderr.strip()}",
            )

        logger.info("API: LiteParse finished in %.2fs", elapsed)

        # Read LiteParse JSON output
        out_path = Path(tmp_out_path)
        if not out_path.exists():
            logger.error("API: LiteParse produced no output file")
            raise HTTPException(status_code=502, detail="LiteParse produced no output.")

        with open(out_path, "r", encoding="utf-8") as f:
            liteparse_data = json.load(f)

        # Extract clean text using parser logic
        logger.info("API: Extracting clean text...")
        text, page_count = extract_clean_text(liteparse_data)
        logger.info("API: Extracted %d pages (%d chars)", page_count, len(text))

        return {
            "filename": file.filename,
            "pages": page_count,
            "text": text,
        }

    except subprocess.TimeoutExpired:
        logger.error("API: LiteParse timed out after 120s")
        raise HTTPException(status_code=504, detail="LiteParse timed out.")

    finally:
        # Clean up temp files
        if tmp_in:
            Path(tmp_in.name).unlink(missing_ok=True)
        if tmp_out_path:
            Path(tmp_out_path).unlink(missing_ok=True)
        logger.debug("API: Temp files cleaned up")
