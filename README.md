# Đồ án Tiền xử lý dữ liệu – Chuỗi thời gian & Văn bản

| | |
|---|---|
| **Sinh viên** | Cao Tiến Thiên |
| **MSSV** | 24127122 |
| **Môn học** | Khai thác dữ liệu và ứng dụng – FIT@HCMUS |
| **Đề bài** | [Tiền xử lý dữ liệu](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/preprocessing/) |
| **Jupyter Book** | https://caothien1402.github.io/dm-preprocessing |

## Tóm tắt kết quả

Hai pipeline tiền xử lý hoàn chỉnh, mỗi bước được đo bằng thực nghiệm có kiểm định thống kê và có biện pháp chống rò rỉ dữ liệu. Phân tích so sánh đầy đủ nằm ở chương 7 của book ([`book/report.md`](book/report.md)); mọi con số trong đó được sinh từ `data/processed/results/*.json`.

| Phần | Phát hiện chính |
|---|---|
| (a) Chuỗi thời gian | Nội suy tuyến tính thắng đa thức và spline khi điền khoảng trống MCAR (29/30 lần); giá không dừng, log-return dừng (ADF, KPSS, PP); AAPL gần như không có mùa vụ |
| (a) Rò rỉ dữ liệu | STL hai phía fit trên toàn chuỗi làm R² ngoài mẫu vọt từ 0.44% lên 29.72% (kết quả giả); đặc trưng STL nhân quả cho kết quả đúng |
| (a) Dự báo | Random Forest không vượt baseline ngây thơ có ý nghĩa (Diebold–Mariano p = 0.6259); Granger: F cổ điển 19/20 cặp, kiểm định bền vững HC3 chỉ còn 5 cạnh |
| (b) Văn bản | Giữ điểm đánh giá `7/10` và từ phủ định có cơ sở thực nghiệm; loại stop words chỉ giúp Naive Bayes; stemming không giúp |
| (b) Biểu diễn | TF-IDF với bigram mạnh nhất (F1 test 0.8941 với 10.000 review huấn luyện); Sentence Transformer kém hơn (0.8179) và không nắm phủ định tốt hơn TF-IDF |

## 1. Mô tả tập dữ liệu

Dữ liệu thô **không** được lưu trong repository. Notebook tự tải về từ Kaggle (qua `kagglehub`) vào `data/raw/` ở lần chạy đầu tiên.

### Phần (a): Chuỗi thời gian – S&P 500

- **Nguồn:** [S&P 500 Stocks: 25 Years of Data (Updated Daily)](https://www.kaggle.com/datasets/darkmatternet/s-and-p-500-stocks-25-years-of-data-updated-daily)
- **Nội dung:** giá OHLCV theo ngày của 503 mã thuộc S&P 500 (thành phần *hiện tại* của chỉ số), từ 03/01/2000. Gồm 2 file: `sp500_stocks.csv` (dạng dài, cột `date, open, high, low, close, volume, symbol`) và `sp500_companies.csv` (metadata: ngành, trụ sở, ngày vào chỉ số).
- **Giá đã điều chỉnh:** dataset chỉ có cột `close` (không có `adj_close`), và cột này đã được điều chỉnh chia tách cổ phiếu. Cả 3 lần chia tách của AAPL trong giai đoạn phân tích (2:1 ngày 28/02/2005, 7:1 ngày 09/06/2014, 4:1 ngày 31/08/2020) đều không tạo bước nhảy giả: lợi suất ngày lần lượt là +0.8%, +1.6%, +3.4%. Vì vậy đồ án dùng `TS_FIELD = "close"`. (Cột này có điều chỉnh cả cổ tức hay không thì không kiểm chứng được từ dữ liệu.)
- **Sử dụng:** chuỗi giá đóng cửa của `AAPL` giai đoạn 2005–2025 (5.283 phiên) cho phân tích đơn biến, chia theo thời gian: train 4.226 phiên (đến 14/10/2021), test 1.057 phiên; log-return của `AAPL, MSFT, JPM, XOM, JNJ` cho Granger causality.
- **Tái lập:** dataset được cập nhật hằng ngày, nên phiên bản dataset (`SP500_VERSION = 206`, dữ liệu đến 20/10/2026) và ngày kết thúc (`TS_END = 2025-12-31`) được cố định trong [`src/dmprep/config.py`](src/dmprep/config.py).
- **Lưu ý:** dataset chỉ chứa các mã hiện thuộc S&P 500 nên có survivorship bias (293/503 mã được thêm vào chỉ số sau 2005); kết quả mô tả riêng AAPL.

### Phần (b): Văn bản – IMDB 50K

- **Nguồn:** [IMDB Dataset of 50K Movie Reviews](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews)
- **Nội dung:** 50.000 review phim tiếng Anh, 2 nhãn `positive` / `negative` (cân bằng 25.000 / 25.000), một file `IMDB Dataset.csv` với 2 cột `review, sentiment`. Có 418 review trùng chính xác (422 nếu so theo khóa chuẩn hóa: bỏ thẻ HTML, chữ thường, gộp khoảng trắng), không có nhãn mâu thuẫn; chúng được loại bỏ trước khi chia train/test ở chương 4, còn lại 49.578 review (train 39.662, test 9.916).
- **Tái lập:** `IMDB_VERSION = 1` (dataset tĩnh).

## 2. Cấu trúc repository

```text
.
├── README.md
├── pyproject.toml            # khai báo thư viện (quản lý bằng uv)
├── uv.lock                   # phiên bản cụ thể của toàn bộ thư viện
├── .python-version           # Python 3.12
├── src/dmprep/               # mã phụ trợ: cấu hình, tải và đọc dữ liệu
│   ├── config.py             # đường dẫn, seed, phiên bản dataset, tham số dùng chung
│   └── data.py               # tải dữ liệu Kaggle, đọc S&P 500 và IMDB
├── book/                     # nguồn của Jupyter Book
│   ├── myst.yml              # cấu hình book + mục lục
│   ├── index.md              # trang mở đầu
│   ├── 01_ts_eda.ipynb                 # Phần (a) – EDA chuỗi thời gian
│   ├── 02_ts_preprocessing.ipynb       # Phần (a) – khoảng trống, tính dừng, phân rã
│   ├── 03_ts_features_forecast.ipynb   # Phần (a) – đặc trưng, dị thường, dự báo, Granger
│   ├── 04_text_eda.ipynb               # Phần (b) – Text EDA, khử trùng lặp, chia train/test
│   ├── 05_text_preprocessing.ipynb     # Phần (b) – chuẩn hóa, tokenization, stop words, stemming
│   ├── 06_text_representation.ipynb    # Phần (b) – BoW, TF-IDF, Word2Vec, Sentence Transformer
│   └── report.md             # chương 7: so sánh, thảo luận, hạn chế, tài liệu tham khảo
├── data/
│   ├── raw/                  # dữ liệu gốc tải từ Kaggle (không commit)
│   └── processed/            # dữ liệu trung gian (không commit) + results/*.json (có commit)
└── .github/workflows/deploy.yml   # tự động build và deploy lên GitHub Pages
```

### Luồng dữ liệu giữa các chương

Các chương phải chạy theo thứ tự 01 → 06 vì chương sau đọc file do chương trước tạo ra (trong `data/processed/`, không commit):

| Chương | Đọc | Ghi |
|---|---|---|
| 01 | `data/raw/sp500/` (tự tải) | `results/01_ts_eda.json` |
| 02 | dữ liệu S&P 500 | `ts_decomposed_train.parquet` (STL fit trên train), `ts_decomposed.parquet` (STL nhân quả), `results/02_*.json` |
| 03 | `ts_decomposed.parquet`, `results/02_*.json` | `results/03_*.json` |
| 04 | `data/raw/imdb/` (tự tải) | `imdb_split.parquet` (train/test đã khử trùng lặp), `results/04_*.json` |
| 05 | `imdb_split.parquet` | `imdb_clean.parquet` (cột `clean` và `light`), `results/05_*.json` |
| 06 | `imdb_clean.parquet`; tải mô hình `all-MiniLM-L6-v2` từ Hugging Face | `results/06_*.json` |

### Tham số dùng chung (`src/dmprep/config.py`)

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `SEED` | 42 | seed cho mọi thao tác ngẫu nhiên |
| `SP500_VERSION`, `IMDB_VERSION` | 206, 1 | cố định phiên bản dataset Kaggle |
| `TS_START`, `TS_END` | 2005-01-01, 2025-12-31 | giai đoạn phân tích chuỗi thời gian |
| `TS_MAIN_TICKER`, `TS_FIELD` | AAPL, close | chuỗi đơn biến chính |
| `TS_GRANGER_TICKERS` | AAPL, MSFT, JPM, XOM, JNJ | các mã cho Granger causality |
| `TS_TEST_FRAC` | 0.2 | tỉ lệ test của chuỗi thời gian (chia theo thời gian) |
| `TS_STL_WINDOW` | 252 | cửa sổ cuốn chiếu của STL nhân quả |
| `TEST_SIZE` | 0.2 | tỉ lệ test của văn bản (chia phân tầng) |
| `TEXT_SAMPLE_SIZE` | 10.000 | cỡ mẫu có nhãn dùng để huấn luyện bộ phân loại ở chương 6 |

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

**Dữ liệu tải tự động khi chạy:** NLTK (`punkt`, `stopwords`, `wordnet`) ở chương 5; mô hình `sentence-transformers/all-MiniLM-L6-v2` (khoảng 90 MB) từ Hugging Face ở chương 6, cần Internet ở lần chạy đầu tiên. Cảnh báo "unauthenticated requests to the HF Hub" là vô hại.

Nếu cần file `requirements.txt` cho pip:

```bash
uv export --no-hashes --no-dev --format requirements-txt -o requirements.txt
```

## 4. Chạy notebook và build book

```bash
# Mở JupyterLab để làm việc với notebook
uv run jupyter lab

# Chạy lại TOÀN BỘ notebook theo thứ tự và lưu kết quả vào file .ipynb.
# BẮT BUỘC có --ExecutePreprocessor.timeout=-1: mặc định nbconvert dừng mỗi ô sau 30 giây,
# trong khi có ô chạy nhiều phút (huấn luyện Word2Vec, mã hóa Sentence Transformer).
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 book/0*.ipynb

# Xem trước book (tự reload khi sửa file)
cd book
uv run jupyter-book start

# Build HTML tĩnh vào book/_build/html
uv run jupyter-book build --html
```

> Notebook phải được chạy theo thứ tự 01 → 06 (xem bảng luồng dữ liệu ở mục 2). Chạy lại toàn bộ ước tính khoảng một giờ trên máy 16 CPU; chương 5 và 6 lâu nhất (mỗi chương hơn 10 phút, trong đó mã hóa Sentence Transformer khoảng 7 phút). Mọi kết quả ngẫu nhiên đều dùng `config.SEED`, nên chạy lại cho cùng kết quả.

**Khi đổi phiên bản dataset** (`SP500_VERSION`, `IMDB_VERSION`) hoặc `TS_END`: phải xóa `data/raw/sp500/`, `data/processed/sp500_long.parquet` (và `data/raw/imdb/` với IMDB), vì bộ nhớ đệm không gắn với phiên bản và sẽ lặng lẽ dùng dữ liệu cũ.

## 5. Xuất bản lên GitHub Pages

1. Trên GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Chạy toàn bộ notebook ở máy (lệnh `nbconvert` ở mục 4) để kết quả được lưu trong file `.ipynb`, rồi commit và push lên nhánh `main`.
3. Workflow [`deploy.yml`](.github/workflows/deploy.yml) tự build book từ các notebook đã có kết quả và deploy. CI **không** chạy lại notebook, nên không cần tải dữ liệu hay cài torch trên GitHub.

## 6. Quy trình làm việc và tái lập

- **Git:** commit nhỏ theo từng mục kỹ thuật (mỗi commit là một trạng thái notebook đã chạy được, không lỗi, có output thật), push thẳng lên `main`; sau mỗi lần push kiểm tra workflow deploy và các trang Pages. Không commit `data/raw/`, file parquet, `kaggle.json`.
- **Chống rò rỉ dữ liệu:** chuỗi thời gian chia theo thời gian, đặc trưng chỉ dùng thông tin đến thời điểm hiện tại (có kiểm tra tự động), STL nhân quả cho đặc trưng; văn bản khử trùng lặp trước khi chia, mọi từ vựng/vectorizer/BPE/Word2Vec chỉ fit trên train, EDA chỉ trên train, test chỉ dùng để đánh giá. Chi tiết và bằng chứng định lượng ở mục 7.4 của báo cáo.
- **Kiểm tra số liệu:** sau mỗi chương, các con số trong phân tích được tính lại độc lập từ dữ liệu gốc bằng mã riêng và đối chiếu với file kết quả; chương 7 được sinh trực tiếp từ các file kết quả.
- **Sử dụng công cụ AI:** đồ án được thực hiện với sự hỗ trợ của trợ lý lập trình AI (Claude Code) để viết và chạy mã; các lựa chọn thiết kế, kết quả và giải thích được sinh viên xem xét và chịu trách nhiệm.

## 7. Tài nguyên ngoài

- Dữ liệu S&P 500: https://www.kaggle.com/datasets/darkmatternet/s-and-p-500-stocks-25-years-of-data-updated-daily
- Dữ liệu IMDB: https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews
- Mô hình Sentence Transformer: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- Jupyter Book 2 / MyST: https://jupyterbook.org, https://mystmd.org
- Tài liệu tham khảo học thuật (kiểm định, mô hình, phương pháp): xem cuối chương 7 ([`book/report.md`](book/report.md)).
