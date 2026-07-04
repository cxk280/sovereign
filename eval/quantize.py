"""Quantize a merged HF model to GGUF via llama.cpp — the lifecycle's quant step.

Wraps llama.cpp's ``convert_hf_to_gguf.py`` + ``llama-quantize`` into one call so
model preparation is reproducible. Not run in CI (needs llama.cpp + a model on
disk); it's a documented, runnable command path, mirroring how ``rag.ingest`` is
runnable-but-not-CI. For the vLLM/GPU path, AWQ is used instead (see docs).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

VALID_QUANTS = {"Q4_K_M", "Q5_K_M", "Q8_0"}


def quantize_to_gguf(
    model_dir: str | Path,
    out_dir: str | Path,
    quant: str = "Q4_K_M",
    llama_cpp_dir: str | Path = "llama.cpp",
) -> Path:
    if quant not in VALID_QUANTS:
        raise ValueError(f"unsupported quant {quant!r}; choose one of {sorted(VALID_QUANTS)}")

    llama = Path(llama_cpp_dir)
    convert = llama / "convert_hf_to_gguf.py"
    quantize_bin = llama / "build" / "bin" / "llama-quantize"
    if not convert.exists() or not quantize_bin.exists():
        raise RuntimeError(
            f"llama.cpp not found under {llama}/. Clone and build it first: "
            "git clone https://github.com/ggerganov/llama.cpp && cmake -B build llama.cpp && "
            "cmake --build build -j"
        )

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    f16 = out / "model-f16.gguf"
    quantized = out / f"model-{quant}.gguf"

    subprocess.run(
        ["python", str(convert), str(model_dir), "--outfile", str(f16), "--outtype", "f16"],
        check=True,
    )
    subprocess.run([str(quantize_bin), str(f16), str(quantized), quant], check=True)
    return quantized
