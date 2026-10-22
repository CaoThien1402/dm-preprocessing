"""Tải và đọc dữ liệu từ Kaggle.

Dữ liệu thô KHÔNG được push lên repository: lần chạy đầu tiên sẽ tải về qua
`kagglehub` và sao chép vào `data/raw/` (thư mục này nằm trong .gitignore).
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pandas as pd

from . import config

# ---------------------------------------------------------------------------
# Tải dữ liệu
# ---------------------------------------------------------------------------


def download_dataset(handle: str, dest: Path, version: int | None = None) -> Path:
    """Tải dataset Kaggle về `dest` (bỏ qua nếu đã có file CSV ở đó).

    Dataset công khai thường tải được không cần đăng nhập. Nếu kagglehub báo lỗi
    xác thực, đặt biến môi trường KAGGLE_USERNAME / KAGGLE_KEY hoặc tạo file
    ~/.kaggle/kaggle.json (KHÔNG commit file này).
    """
    dest.mkdir(parents=True, exist_ok=True)
    if any(dest.rglob("*.csv")):
        return dest

    import kagglehub

    full_handle = f"{handle}/versions/{version}" if version is not None else handle
    cache = Path(kagglehub.dataset_download(full_handle))
    for f in cache.rglob("*"):
        if f.is_file():
            target = dest / f.relative_to(cache)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
    return dest


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """'Adj Close' -> 'adj_close', 'Date' -> 'date', ..."""
    df = df.copy()
    df.columns = [re.sub(r"[^0-9a-z]+", "_", str(c).strip().lower()).strip("_") for c in df.columns]
    return df


# ---------------------------------------------------------------------------
# Phần (a): S&P 500
# ---------------------------------------------------------------------------
_TICKER_CANDIDATES = ("ticker", "symbol", "name", "stock")


def load_sp500(
    tickers: list[str] | None = None,
    start: str | None = config.TS_START,
    end: str | None = config.TS_END,
) -> pd.DataFrame:
    """Đọc dữ liệu OHLCV dạng dài (long format): mỗi dòng = (date, ticker).

    Hàm tự nhận diện cấu trúc file:
    - một (hoặc vài) file CSV lớn có cột ticker/symbol, hoặc
    - mỗi mã một file CSV, tên file chính là mã cổ phiếu.
    Các file không có cột ngày (ví dụ metadata công ty) sẽ bị bỏ qua.
    """
    root = download_dataset(config.SP500_HANDLE, config.RAW_DIR / "sp500", config.SP500_VERSION)
    cache = config.PROCESSED_DIR / "sp500_long.parquet"

    if cache.exists():
        df = pd.read_parquet(cache)
    else:
        frames = []
        for path in sorted(root.rglob("*.csv")):
            header = _normalize_columns(pd.read_csv(path, nrows=5))
            if "date" not in header.columns:
                continue  # file metadata, không phải giá
            part = _normalize_columns(pd.read_csv(path))
            ticker_col = next((c for c in _TICKER_CANDIDATES if c in part.columns), None)
            if ticker_col is None:
                part["ticker"] = path.stem.upper()
            elif ticker_col != "ticker":
                part = part.rename(columns={ticker_col: "ticker"})
            frames.append(part)
        if not frames:
            raise FileNotFoundError(f"Không tìm thấy file giá có cột 'date' trong {root}")
        df = pd.concat(frames, ignore_index=True)
        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce").dt.tz_localize(None).dt.normalize()
        df["ticker"] = df["ticker"].astype(str).str.upper()
        df = df.dropna(subset=["date"]).sort_values(["ticker", "date"]).reset_index(drop=True)
        df.to_parquet(cache, index=False)

    if tickers is not None:
        df = df[df["ticker"].isin([t.upper() for t in tickers])]
    if start is not None:
        df = df[df["date"] >= pd.Timestamp(start)]
    if end is not None:
        df = df[df["date"] <= pd.Timestamp(end)]
    return df.reset_index(drop=True)


def to_wide(df_long: pd.DataFrame, field: str = config.TS_FIELD) -> pd.DataFrame:
    """Chuyển long -> wide: index = date, mỗi cột = một ticker."""
    return df_long.pivot_table(index="date", columns="ticker", values=field).sort_index()


def load_main_series(ticker: str = config.TS_MAIN_TICKER, field: str = config.TS_FIELD) -> pd.Series:
    """Chuỗi đơn biến dùng xuyên suốt phần (a): giá `field` của `ticker`, index = ngày giao dịch."""
    df = load_sp500(tickers=[ticker])
    if df.empty:
        raise ValueError(f"Không có dữ liệu cho mã {ticker}")
    if field not in df.columns:
        raise KeyError(f"Không có cột '{field}'. Các cột hiện có: {list(df.columns)}")
    s = df.set_index("date")[field].sort_index()
    s = s[~s.index.duplicated(keep="last")]
    s.name = ticker
    return s


# ---------------------------------------------------------------------------
# Phần (b): IMDB
# ---------------------------------------------------------------------------


def load_imdb() -> pd.DataFrame:
    """Đọc IMDB 50K. Trả về DataFrame với cột `review` (str), `sentiment` (str), `label` (0/1)."""
    root = download_dataset(config.IMDB_HANDLE, config.RAW_DIR / "imdb", config.IMDB_VERSION)
    csvs = sorted(root.rglob("*.csv"), key=lambda p: p.stat().st_size, reverse=True)
    if not csvs:
        raise FileNotFoundError(f"Không tìm thấy file CSV trong {root}")
    df = _normalize_columns(pd.read_csv(csvs[0]))
    if not {"review", "sentiment"} <= set(df.columns):
        raise ValueError(f"Thiếu cột review/sentiment, các cột hiện có: {list(df.columns)}")
    df["label"] = (df["sentiment"].str.lower() == "positive").astype(int)
    return df[["review", "sentiment", "label"]]
