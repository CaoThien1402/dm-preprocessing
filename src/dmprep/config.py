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
# ĐÃ được điều chỉnh chia tách: quanh cả 3 lần chia tách của AAPL trong giai đoạn
# phân tích (2:1 ngày 28/02/2005, 7:1 ngày 09/06/2014, 4:1 ngày 31/08/2020) lợi
# suất ngày lần lượt là +0.8%, +1.6%, +3.4%, không có bước nhảy giả nào (-50%,
# -86%, -75%). Việc cột này có điều chỉnh cả cổ tức hay không KHÔNG kiểm chứng
# được từ dữ liệu (không có giá gốc để đối chiếu), và không ảnh hưởng kết luận.
TS_FIELD = "close"
# Các mã dùng cho Granger causality [Nâng cao] (nhiều ngành khác nhau)
TS_GRANGER_TICKERS = ["AAPL", "MSFT", "JPM", "XOM", "JNJ"]

# Chia train/test THEO THỜI GIAN (không xáo trộn): 80% phiên đầu là train, 20% phiên cuối là test.
# Mọi bước học tham số của phần (a) (chu kỳ STL, số lag p, scaler, mô hình) chỉ được dùng tập train.
TS_TEST_FRAC = 0.2
# Cửa sổ cuốn chiếu (số phiên, khoảng 1 năm) của STL nhân quả ở chương 2: thành phần tại ngày t
# chỉ được tính từ TS_STL_WINDOW phiên kết thúc tại t.
TS_STL_WINDOW = 252


def ts_split_index(n: int) -> int:
    """Chỉ số của phiên test đầu tiên: train = [0, idx), test = [idx, n)."""
    return int(n * (1 - TS_TEST_FRAC))

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
