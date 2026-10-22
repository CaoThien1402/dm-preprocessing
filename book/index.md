# Đồ án Tiền xử lý dữ liệu

- **Sinh viên:** Cao Tiến Thiên – MSSV 24127122
- **Môn học:** Khai thác dữ liệu và ứng dụng – Khoa CNTT, Trường ĐH Khoa học Tự nhiên, ĐHQG-HCM
- **Đề bài:** [Tiền xử lý dữ liệu – Course Lab Book](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/preprocessing/)

## Mục tiêu

Cuốn book trình bày EDA chuyên sâu và pipeline tiền xử lý hoàn chỉnh cho hai dạng dữ liệu. Mỗi kỹ thuật đều có phần lý thuyết, cài đặt và đánh giá định lượng bằng kiểm định thống kê hoặc so sánh có kiểm soát.

| Phần | Dạng dữ liệu | Bộ dữ liệu |
|---|---|---|
| (a) | Chuỗi thời gian | [S&P 500 Stocks: 25 Years of Data](https://www.kaggle.com/datasets/darkmatternet/s-and-p-500-stocks-25-years-of-data-updated-daily) |
| (b) | Văn bản | [IMDB Dataset of 50K Movie Reviews](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews) |

## Cấu trúc cuốn book

| Chương | Nội dung | Tiêu chí chấm tương ứng |
|---|---|---|
| [1. EDA chuỗi thời gian](01_ts_eda.ipynb) | Time plot, ACF/PACF, rolling statistics | Nền cho phần (a) |
| [2. Tiền xử lý chuỗi](02_ts_preprocessing.ipynb) | Nội suy khoảng trống, kiểm định tính dừng, phân rã STL | Kiểm định tính dừng và phân rã STL (10%) |
| [3. Đặc trưng & dự báo](03_ts_features_forecast.ipynb) | Đặc trưng thời gian, dị thường, RF Regressor, Granger | Dị thường + ma trận đặc trưng (10%); RF + Granger (10%) |
| [4. Text EDA](04_text_eda.ipynb) | Độ dài, Mann-Whitney U, word cloud, TTR, Zipf | Text EDA kèm Zipf (10%) |
| [5. Tiền xử lý văn bản](05_text_preprocessing.ipynb) | Chuẩn hóa, tokenization, stop words, stemming | Pipeline chuẩn hóa và OOV (10%) |
| [6. Vector hóa văn bản](06_text_representation.ipynb) | BoW, TF-IDF, Word2Vec, Sentence Transformer | Silhouette và Sentence Transformer (10%) |
| [7. Báo cáo](report.md) | So sánh, thảo luận, kết luận | Các chương báo cáo (20%) |

## Tái lập kết quả

Toàn bộ mã nằm trong repository cá nhân; hướng dẫn cài đặt môi trường (uv) và build book có trong `README.md`. Seed ngẫu nhiên, giai đoạn dữ liệu và phiên bản dataset được cố định trong `src/dmprep/config.py`.
