# rule.md – Quy tắc làm việc cho Agent trong đồ án Tiền xử lý dữ liệu

> **Đọc toàn bộ file này trước khi làm bất kỳ việc gì trong repo.**
> Thứ tự ưu tiên khi có mâu thuẫn: **(1) đề bài gốc** → **(2) rule.md** → **(3) yêu cầu trong prompt**.
> Khi có điểm chưa rõ hoặc một quyết định ảnh hưởng đến điểm số, **dừng lại và hỏi sinh viên**, không tự đoán.

- Đề bài gốc: https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/preprocessing/
- Hạn nộp: **23:59 thứ Bảy 14/11/2026** (giờ Việt Nam). **Không chấp nhận nộp trễ.**
- Phạm vi đã chọn: **Phần (a) = Chuỗi thời gian** (S&P 500), **Phần (b) = Văn bản** (IMDB 50K). Không làm phần dữ liệu bảng hay ảnh.

---

## 1. Sản phẩm nộp bài (bắt buộc)

1. Chỉ nộp **một link** lên Moodle: trang Jupyter Book trên **GitHub Pages của repository cá nhân**, dạng `<username>.github.io/<repo>`. Link phải hoạt động ổn định đến hết kỳ chấm.
2. Repository là **nơi duy nhất** chứa mã nguồn và nguồn của book. Quy trình làm việc được chấm qua **lịch sử commit**.
3. Book phải **build thành công và chạy sạch từ trang đầu đến trang cuối**. Chương nào lỗi runtime thì **chương đó bị 0 điểm**.
4. `README.md` phải có đủ: họ tên và MSSV, mô tả tập dữ liệu, hướng dẫn cài môi trường và build book, link tài nguyên ngoài.
5. **Không push dữ liệu thô** vào repo. Dữ liệu tải từ Kaggle bằng code nằm trong notebook (hoặc import từ `src/dmprep/`).

## 2. Môi trường và thư viện

- Quản lý môi trường **chỉ bằng uv**. Thêm thư viện bằng `uv add <pkg>`, không dùng `pip install`. Luôn commit `uv.lock`.
- Python 3.12 (theo `.python-version`). Jupyter Book 2 (MyST) cần Node.js ≥ 20.
- **Thư viện được đề cho phép:** numpy, pandas, matplotlib, seaborn, scikit-learn, scipy, statsmodels, nltk hoặc spacy, missingno, imbalanced-learn, thư viện tải dữ liệu từ Hugging Face/Kaggle, TensorFlow/PyTorch.
- Thư viện mà **đề có nhắc đến** trong mô tả kỹ thuật (được dùng): `holidays`, `tokenizers` (HuggingFace), `sentence-transformers`, `wordcloud`.
- Thư viện **ngoài danh sách** đang dùng, cần sinh viên xác nhận với trợ giảng: `gensim` (Word2Vec), `arch` (Phillips-Perron), `networkx` (đồ thị Granger). **Không thêm thư viện mới ngoài các nhóm trên** khi chưa hỏi sinh viên. Nếu thêm, ghi lý do vào README.

## 3. Cấu trúc repo và notebook

- Giữ nguyên cấu trúc: `src/dmprep/` (mã phụ trợ), `book/` (nguồn book, mục lục ở `book/myst.yml`), `data/raw` và `data/processed` (không commit, trừ `data/processed/results/*.json`).
- **Mỗi chương = một notebook.** Thứ tự chạy bắt buộc: 01 → 06 (chương 3 đọc kết quả chương 2, chương 5–6 đọc tập train/test tạo ở chương 4).
- **Mỗi kỹ thuật tiền xử lý phải có đủ 3 ô:**
  1. Markdown **lý thuyết** kèm **công thức toán** (nếu có),
  2. Code cài đặt,
  3. Markdown **phân tích kết quả**.
- **Mọi kết quả số** (score, p-value, statistic, MAE, RMSE, F1, ...) phải được **in ra** và **gán vào biến Python**, đồng thời lưu vào dict `RESULTS` và ghi ra file bằng `config.save_results(...)` ở cuối notebook.
- Mọi đường dẫn lấy từ `dmprep.config` (không hard-code đường dẫn tuyệt đối). Mọi tham số dùng chung (seed, ngày bắt đầu/kết thúc, mã cổ phiếu, cỡ mẫu) đặt trong `config.py`.
- Code sạch: tách hàm khi lặp lại, có comment ngắn giải thích **vì sao**, không in ra DataFrame hay log quá dài.

## 4. Yêu cầu kỹ thuật bắt buộc theo đề

Không được bỏ sót hay thay đổi tham số nào dưới đây. Mục `[Nâng cao]` là điểm thưởng.

### Phần (a) – Chuỗi thời gian (chương 1–3)

| Mục | Yêu cầu chính xác |
|---|---|
| Dữ liệu | ≥ 2 năm, tần suất ngày |
| EDA | Time plot, nhận diện trend / seasonality / noise; ACF và PACF với lag tối đa `min(10·log10(n), n/5)`; rolling mean và std với cửa sổ 7, 30, 90 ngày (hoặc tương đương, phải giải thích) |
| Khoảng trống | Tạo nhân tạo **5%** khoảng trống theo **MCAR**; 4 phương pháp: forward fill, linear, polynomial **bậc 2 và 3**, cubic spline; mỗi phương pháp tính **MAE, RMSE** và **Ljung-Box** |
| Tính dừng | **ADF, KPSS, PP** trên chuỗi gốc, báo cáo p-value và kết luận; nếu không dừng: differencing bậc 1 và 2, log, Box-Cox; kiểm định lại sau mỗi biến đổi đến khi dừng |
| Phân rã | Additive, Multiplicative (statsmodels), **STL** với chu kỳ phù hợp (phải biện luận); đánh giá bằng **residual variance ratio**; lưu phần deseasonalized và detrended |
| Đặc trưng thời gian | sin/cos(2πt/T) cho **ngày trong tuần** và **tháng trong năm**; ngày lễ bằng thư viện `holidays`; rolling **mean, std, min, max, skewness** với nhiều cửa sổ |
| Dị thường | 3 phương pháp: Z-score trên chuỗi đã deseasonalize; Isolation Forest trên cửa sổ trượt; Autoencoder 1D **hoặc** STL residual thresholding; đánh dấu trên biểu đồ và thảo luận nguyên nhân |
| Ma trận đặc trưng | Lag t−1…t−p với **p chọn từ PACF**; rolling stats nhiều tỉ lệ; đặc trưng thời gian; chuỗi đã phân rã |
| Dự báo | **Random Forest Regressor** dự báo **t+1**, báo cáo **MAE, RMSE trên tập test** |
| [Nâng cao] Granger | Granger causality giữa nhiều biến, **bảng ma trận nhân quả** và **đồ thị có hướng** |

### Phần (b) – Văn bản (chương 4–6)

| Mục | Yêu cầu chính xác |
|---|---|
| Dữ liệu | ≥ 10.000 mẫu, ≥ 2 nhãn |
| Text EDA | Phân phối độ dài (**số từ và số ký tự**) theo nhãn + **Mann-Whitney U**; **word cloud** và bảng **top-50 từ** theo từng lớp; **TTR**; **Zipf** trên log-log |
| Chuẩn hóa | Chữ thường, bỏ HTML, URL, mention, hashtag, ký tự đặc biệt và số (có điều kiện cụ thể), chuẩn hóa khoảng trắng; **sau mỗi bước** báo cáo tỉ lệ thay đổi từ vựng và tác động đến phân phối độ dài |
| Tokenization | 4 chiến lược: word-level (NLTK/spaCy), sentence-level, character-level, **BPE** (thư viện `tokenizers`); báo cáo **kích thước từ vựng, tỉ lệ OOV trên tập test, độ dài chuỗi token trung bình** |
| Stop words | So sánh trước/sau: kích thước từ vựng, **MI trung bình** giữa từ và nhãn, hiệu năng **Naive Bayes**; thảo luận việc loại stop words có luôn tốt không |
| Stemming / Lemma | **Porter, Snowball, WordNet Lemmatizer**; **collision rate**; tác động lên **Logistic Regression 5-fold CV** |
| Vector hóa | **BoW, TF-IDF với n-gram n ∈ {1, 2, 3}, Word2Vec huấn luyện trên chính tập dữ liệu**; mỗi biểu diễn: số chiều, **sparsity ratio**, **cosine similarity cùng lớp và khác lớp**, **t-SNE 2D** tô màu theo nhãn, **silhouette score** |
| [Nâng cao] | Sentence Transformer `all-MiniLM-L6-v2`: so sánh **silhouette của K-Means** và **Linear SVM** giữa TF-IDF và embeddings; giải thích khác biệt ngữ nghĩa |

### Báo cáo (`book/report.md`, 20% điểm)

Phân tích **so sánh** giữa các kỹ thuật, thảo luận, nhận xét phê bình, có trích **con số thật** từ `data/processed/results/*.json`. Không chỉ mô tả lại kết quả.

## 5. Tính chặt chẽ thống kê (tiêu chí "Xuất sắc")

- Mỗi kiểm định phải nêu rõ **H₀, H₁, mức ý nghĩa α = 0.05**, báo cáo **thống kê kiểm định và p-value**, rồi **diễn giải bằng lời**.
- Với n lớn, p-value nhỏ gần như chắc chắn, nên báo cáo thêm **effect size** khi có thể (ví dụ rank-biserial cho Mann-Whitney).
- Khi kiểm định nhiều lần (Granger), nhắc đến hiệu chỉnh đa kiểm định (Bonferroni hoặc FDR).
- Mọi lựa chọn tham số (chu kỳ STL, ngưỡng dị thường, cửa sổ, p) phải có **lý do** ghi trong markdown.

## 6. Chống rò rỉ dữ liệu (data leakage)

- Chuỗi thời gian: chia train/test **theo thời gian**, không xáo trộn. Đặc trưng cửa sổ chỉ dùng thông tin đến thời điểm t (`.shift(1)` khi cần). Không fit scaler hoặc mô hình trên tập test. Có **baseline ngây thơ** (ŷ₍t+1₎ = y_t) để so sánh.
- Văn bản: dùng tập train/test cố định tạo ở chương 4 (khử trùng lặp **trước** khi chia). Từ vựng, BPE, Word2Vec, TF-IDF **chỉ fit trên train**; OOV đo trên test. Cross-validation dùng `StratifiedKFold` với seed cố định.

## 7. Tái lập kết quả

- Seed = `config.SEED` cho mọi thao tác ngẫu nhiên (`random_state`, `np.random.default_rng`, torch).
- Dataset S&P 500 được **cập nhật hằng ngày**, nên phải cố định `SP500_VERSION` và `TS_END` trong `config.py`.
- Dữ liệu giá: kiểm tra cột giá có **điều chỉnh chia tách cổ phiếu** hay không (ví dụ AAPL chia 4:1 ngày 31/08/2020). Nếu chưa điều chỉnh, các bước nhảy giả sẽ làm hỏng kiểm định và bị phát hiện thành dị thường sai. Ghi rõ lựa chọn trong notebook.
- Bước nặng (t-SNE, cosine giữa các cặp, Sentence Transformer) chạy trên **mẫu phân tầng** `config.TEXT_SAMPLE_SIZE`. Giữ thời gian chạy mỗi notebook hợp lý (mục tiêu < 15 phút trên CPU laptop).
- Notebook được commit **kèm output** (CI không chạy lại notebook). Chạy lại toàn bộ bằng:
  `uv run jupyter nbconvert --to notebook --execute --inplace book/0*.ipynb`

## 8. Git và GitHub

- Commit **nhỏ, thường xuyên**, message rõ ràng (ví dụ `feat(ch2): add stationarity tests ADF/KPSS/PP`). Không gộp cả tuần làm việc vào một commit.
- **Không bao giờ commit:** `data/raw/*`, file parquet lớn, `kaggle.json`, `.env`, token hay mật khẩu.
- **Không** `push --force`, không viết lại lịch sử, không xóa nhánh.
- **Phải hỏi sinh viên trước khi:** tạo repo GitHub, push, đổi cài đặt GitHub Pages, xóa file, thêm thư viện mới, đổi bộ dữ liệu hoặc đổi cấu trúc chương.
- Sau mỗi lần push, kiểm tra workflow `deploy.yml` thành công và link Pages mở được.

## 9. Trung thực học thuật

Vi phạm sẽ dẫn đến **điểm 0 toàn môn**.

- **Tuyệt đối không bịa số liệu.** Mọi con số trong markdown và `report.md` phải khớp với output thật của notebook. Nếu output thay đổi, cập nhật lại phần phân tích.
- Kết quả bất ngờ hoặc "xấu" vẫn báo cáo trung thực và giải thích, không chỉnh sửa để đẹp hơn.
- Không sao chép nguyên văn notebook hay bài viết của người khác. Tài liệu tham khảo phải ghi nguồn trong `report.md`.
- Đề cho phép dùng AI, nhưng **sinh viên phải hiểu mọi thứ** vì có **thi vấn đáp**. Sau mỗi phần việc, agent phải giải thích ngắn gọn bằng tiếng Việt: đã làm gì, vì sao, kết quả có ý nghĩa gì, và những câu hỏi giảng viên có thể hỏi.

## 10. Ngôn ngữ và trình bày

- Nội dung book (markdown, báo cáo) viết bằng **tiếng Việt**; thuật ngữ chuyên môn giữ tiếng Anh trong ngoặc khi lần đầu xuất hiện, ví dụ "tính dừng (stationarity)".
- Biểu đồ có tiêu đề, nhãn trục, chú thích; dùng `plt.show()` để hiển thị trong book.
- Bảng so sánh dùng `pandas.DataFrame` (hiển thị gọn), làm tròn hợp lý (3–4 chữ số).

## 11. Định nghĩa "hoàn thành"

Một chương chỉ được coi là xong khi:

- [ ] Đủ mọi yêu cầu của chương trong mục 4, không còn `TODO`
- [ ] Mỗi kỹ thuật có đủ lý thuyết, công thức, code và phân tích
- [ ] Notebook chạy từ đầu đến cuối không lỗi, đã lưu output
- [ ] `RESULTS` đã ghi ra `data/processed/results/<chương>.json`
- [ ] Phân tích trích đúng con số thật
- [ ] Đã commit

Trước khi nộp (muộn nhất ngày 12/11/2026, chừa 2 ngày dự phòng):

- [ ] Clone repo vào thư mục mới, `uv sync`, chạy lại toàn bộ notebook, build book: không lỗi
- [ ] Link GitHub Pages mở được, đủ 7 chương, mục lục đúng
- [ ] README đủ họ tên, MSSV, mô tả dữ liệu, hướng dẫn cài và build, link tài nguyên
- [ ] Repo ở chế độ **public**
