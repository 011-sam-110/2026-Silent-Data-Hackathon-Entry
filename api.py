import json
import subprocess
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from parser import extract_clean_text

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
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    content = await file.read()
    tmp_in = None
    tmp_out = None

    try:
        # Write uploaded PDF to a temp file
        tmp_in = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp_in.write(content)
        tmp_in.close()

        # Prepare output path
        tmp_out_path = tmp_in.name + ".json"

        # Run LiteParse
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

        if result.returncode != 0:
            raise HTTPException(
                status_code=502,
                detail=f"LiteParse failed: {result.stderr.strip()}",
            )

        # Read LiteParse JSON output
        out_path = Path(tmp_out_path)
        if not out_path.exists():
            raise HTTPException(status_code=502, detail="LiteParse produced no output.")

        with open(out_path, "r", encoding="utf-8") as f:
            liteparse_data = json.load(f)

        # Extract clean text using parser logic
        text, page_count = extract_clean_text(liteparse_data)

        return {
            "filename": file.filename,
            "pages": page_count,
            "text": text,
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="LiteParse timed out.")

    finally:
        # Clean up temp files
        if tmp_in:
            Path(tmp_in.name).unlink(missing_ok=True)
        if tmp_out_path:
            Path(tmp_out_path).unlink(missing_ok=True)
