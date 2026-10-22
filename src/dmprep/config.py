"""Cấu hình chung cho toàn bộ đồ án: đường dẫn, seed, tham số dữ liệu.

Mọi notebook đều import từ đây để kết quả nhất quán và tái lập được.
"""

from __future__ import annotations

import json
import os
import random
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Đường dẫn
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = PROCESSED_DIR / "results"

for _d in (RAW_DIR, PROCESSED_DIR, RESULTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Tái lập kết quả
# ---------------------------------------------------------------------------
SEED = 42


def set_seed(seed: int = SEED) -> None:
    """Cố định seed cho random, numpy và (nếu có) torch."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch

        torch.manual_seed(seed)
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# Phần (a): chuỗi thời gian S&P 500
# ---------------------------------------------------------------------------
SP500_HANDLE = "darkmatternet/s-and-p-500-stocks-25-years-of-data-updated-daily"
# Bộ dữ liệu được cập nhật hằng ngày → PHẢI cố định phiên bản và ngày kết thúc,
# nếu không mỗi lần chạy lại sẽ ra kết quả khác. Version 206 là bản mới nhất
# ngày 22/10/2026 (dữ liệu đến 20/10/2026), xác định qua kagglehub.
SP500_VERSION: int | None = 206
TS_START = "2005-01-01"
TS_END = "2025-12-31"

# Chuỗi chính dùng cho phân tích đơn biến
TS_MAIN_TICKER = "AAPL"
# Dataset chỉ có một cột giá đóng cửa `close` (không có `adj_close`), và cột này
# ĐÃ được điều chỉnh chia tách và cổ tức (kiểu "Adj Close" của Yahoo): quanh các
# lần chia tách của AAPL (7:1 ngày 09/06/2014, 4:1 ngày 31/08/2020) giá không có
# bước nhảy giả nào (31/08/2020: +3.4%, không phải -75%).
TS_FIELD = "close"
# Các mã dùng cho Granger causality [Nâng cao] (nhiều ngành khác nhau)
TS_GRANGER_TICKERS = ["AAPL", "MSFT", "JPM", "XOM", "JNJ"]

# ---------------------------------------------------------------------------
# Phần (b): văn bản IMDB
# ---------------------------------------------------------------------------
IMDB_HANDLE = "lakshmi25npathi/imdb-dataset-of-50k-movie-reviews"
IMDB_VERSION: int | None = 1  # dataset tĩnh, chỉ có một phiên bản
# Kích thước mẫu cho các bước nặng (t-SNE, Sentence Transformer, ...)
TEXT_SAMPLE_SIZE = 10_000
TEST_SIZE = 0.2


# ---------------------------------------------------------------------------
# Lưu kết quả số để chương báo cáo tham chiếu lại
# ---------------------------------------------------------------------------
def save_results(name: str, results: dict) -> Path:
    """Ghi dict kết quả (score, p-value, ...) ra data/processed/results/<name>.json."""

    def _to_builtin(x):
        if isinstance(x, (np.integer,)):
            return int(x)
        if isinstance(x, (np.floating,)):
            return float(x)
        if isinstance(x, np.ndarray):
            return x.tolist()
        return str(x)

    path = RESULTS_DIR / f"{name}.json"
    path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=_to_builtin),
        encoding="utf-8",
    )
    return path
