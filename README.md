# Đồ án Tiền xử lý dữ liệu – Chuỗi thời gian & Văn bản

| | |
|---|---|
| **Sinh viên** | Cao Tiến Thiên |
| **MSSV** | 24127122 |
| **Môn học** | Khai thác dữ liệu và ứng dụng – FIT@HCMUS |
| **Đề bài** | [Tiền xử lý dữ liệu](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/preprocessing/) |
| **Jupyter Book** | https://caothien1402.github.io/dm-preprocessing |

## 1. Mô tả tập dữ liệu

Dữ liệu thô **không** được lưu trong repository. Notebook tự tải về từ Kaggle (qua `kagglehub`) vào `data/raw/` ở lần chạy đầu tiên.

### Phần (a): Chuỗi thời gian – S&P 500

- **Nguồn:** [S&P 500 Stocks: 25 Years of Data (Updated Daily)](https://www.kaggle.com/datasets/darkmatternet/s-and-p-500-stocks-25-years-of-data-updated-daily)
- **Nội dung:** giá OHLCV theo ngày của 503 mã thuộc S&P 500 (thành phần *hiện tại* của chỉ số), từ 03/01/2000. Gồm 2 file: `sp500_stocks.csv` (dạng dài, cột `date, open, high, low, close, volume, symbol`) và `sp500_companies.csv` (metadata: ngành, trụ sở, ngày vào chỉ số).
- **Giá đã điều chỉnh:** dataset chỉ có cột `close` (không có `adj_close`), và cột này đã được điều chỉnh chia tách cổ phiếu và cổ tức. Ví dụ AAPL chia 4:1 ngày 31/08/2020 nhưng giá ngày đó tăng 3.4% chứ không tụt 75%. Vì vậy đồ án dùng `TS_FIELD = "close"`.
- **Sử dụng:** chuỗi giá đóng cửa của `AAPL` giai đoạn 2005–2025 (5.283 phiên) cho phân tích đơn biến; log-return của `AAPL, MSFT, JPM, XOM, JNJ` cho Granger causality.
- **Tái lập:** dataset được cập nhật hằng ngày, nên phiên bản dataset (`SP500_VERSION = 206`, dữ liệu đến 20/10/2026) và ngày kết thúc (`TS_END = 2025-12-31`) được cố định trong [`src/dmprep/config.py`](src/dmprep/config.py).

### Phần (b): Văn bản – IMDB 50K

- **Nguồn:** [IMDB Dataset of 50K Movie Reviews](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews)
- **Nội dung:** 50.000 review phim tiếng Anh, 2 nhãn `positive` / `negative` (cân bằng 25.000 / 25.000), một file `IMDB Dataset.csv` với 2 cột `review, sentiment`. Có 418 review trùng lặp, được loại bỏ trước khi chia train/test ở chương 4.
- **Tái lập:** `IMDB_VERSION = 1` (dataset tĩnh).

## 2. Cấu trúc repository

```text
.
├── README.md
├── pyproject.toml            # khai báo thư viện (quản lý bằng uv)
├── uv.lock                   # phiên bản cụ thể của toàn bộ thư viện
├── .python-version           # Python 3.12
├── src/dmprep/               # mã phụ trợ: cấu hình, tải và đọc dữ liệu
│   ├── config.py
│   └── data.py
├── book/                     # nguồn của Jupyter Book
│   ├── myst.yml              # cấu hình book + mục lục
│   ├── index.md              # trang mở đầu
│   ├── 01_ts_eda.ipynb                 # Phần (a) – EDA chuỗi thời gian
│   ├── 02_ts_preprocessing.ipynb       # Phần (a) – khoảng trống, tính dừng, phân rã
│   ├── 03_ts_features_forecast.ipynb   # Phần (a) – đặc trưng, dị thường, dự báo, Granger
│   ├── 04_text_eda.ipynb               # Phần (b) – Text EDA
│   ├── 05_text_preprocessing.ipynb     # Phần (b) – chuẩn hóa, tokenization, stop words, stemming
│   ├── 06_text_representation.ipynb    # Phần (b) – BoW, TF-IDF, Word2Vec, Sentence Transformer
│   └── report.md             # chương báo cáo: so sánh và thảo luận
├── data/
│   ├── raw/                  # dữ liệu gốc tải từ Kaggle (không commit)
│   └── processed/            # dữ liệu trung gian (không commit) + results/*.json (có commit)
└── .github/workflows/deploy.yml   # tự động build và deploy lên GitHub Pages
```

## 3. Cài đặt môi trường

Dự án dùng [uv](https://docs.astral.sh/uv/) để quản lý Python và thư viện. Phiên bản chính xác của mọi thư viện được khóa trong `uv.lock`.

```bash
# 1. Cài uv (một lần)
#   macOS / Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
#   Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Clone repo và cài toàn bộ thư viện (uv tự cài Python 3.12 nếu cần)
git clone https://github.com/CaoThien1402/dm-preprocessing.git
cd dm-preprocessing
uv sync
```

Jupyter Book 2 cần thêm **Node.js ≥ 20** ([tải tại đây](https://nodejs.org/)).

Ngoài các thư viện đề cho phép, đồ án dùng thêm 3 thư viện vì không có công cụ tương đương trong danh sách:

| Thư viện | Dùng cho | Lý do |
|---|---|---|
| `arch` | Kiểm định Phillips-Perron | `statsmodels` có ADF và KPSS nhưng không có PP |
| `gensim` | Word2Vec | Đề yêu cầu huấn luyện Word2Vec trên chính tập dữ liệu |
| `networkx` | Đồ thị có hướng Granger | Vẽ đồ thị nhân quả [Nâng cao] |

**Kaggle:** dataset công khai thường tải được không cần đăng nhập. Nếu `kagglehub` báo lỗi xác thực, tạo API token tại *kaggle.com → Settings → API → Create New Token* rồi đặt file `kaggle.json` vào `~/.kaggle/` (Windows: `C:\Users\<tên>\.kaggle\`). **Không commit file này.**

Nếu cần file `requirements.txt` cho pip:

```bash
uv export --no-hashes --no-dev --format requirements-txt -o requirements.txt
```

## 4. Chạy notebook và build book

```bash
# Mở JupyterLab để làm việc với notebook
uv run jupyter lab

# Chạy lại TOÀN BỘ notebook theo thứ tự và lưu kết quả vào file .ipynb
uv run jupyter nbconvert --to notebook --execute --inplace book/0*.ipynb

# Xem trước book (tự reload khi sửa file)
cd book
uv run jupyter-book start

# Build HTML tĩnh vào book/_build/html
uv run jupyter-book build --html
```

> Notebook phải được chạy theo thứ tự 01 → 06, vì chương 3 dùng kết quả phân rã của chương 2 và chương 5–6 dùng tập train/test tạo ở chương 4.

## 5. Xuất bản lên GitHub Pages

1. Trên GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Chạy toàn bộ notebook ở máy (lệnh `nbconvert` ở mục 4) để kết quả được lưu trong file `.ipynb`, rồi commit và push lên nhánh `main`.
3. Workflow [`deploy.yml`](.github/workflows/deploy.yml) tự build book từ các notebook đã có kết quả và deploy. CI **không** chạy lại notebook, nên không cần tải dữ liệu hay cài torch trên GitHub.

## 6. Tài nguyên ngoài

- Dữ liệu S&P 500: https://www.kaggle.com/datasets/darkmatternet/s-and-p-500-stocks-25-years-of-data-updated-daily
- Dữ liệu IMDB: https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews
- Mô hình Sentence Transformer: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- Jupyter Book 2 / MyST: https://jupyterbook.org, https://mystmd.org
