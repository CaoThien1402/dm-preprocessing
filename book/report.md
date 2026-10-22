# Chương 7. Báo cáo: so sánh và thảo luận

> Chương này chiếm **20%** điểm. Mỗi mục cần trích dẫn con số cụ thể từ các chương 1–6 (đã lưu trong `data/processed/results/*.json`), so sánh giữa các kỹ thuật và đưa ra **nhận xét phê bình**, không chỉ mô tả lại kết quả.

## 7.1 Tóm tắt

TODO: 1 đoạn ngắn: dữ liệu, các pipeline đã xây dựng, phát hiện quan trọng nhất của mỗi phần.

## 7.2 Phần (a): Chuỗi thời gian S&P 500

### Điền khoảng trống
TODO: bảng MAE / RMSE / Ljung-Box của 4 phương pháp; phương pháp được chọn và lý do.

### Tính dừng và phân rã
TODO: bảng p-value ADF / KPSS / PP trước và sau biến đổi; so sánh additive, multiplicative, STL qua residual variance ratio; biện luận chu kỳ mùa vụ.

### Dị thường
TODO: số điểm dị thường và độ chồng lấn giữa 3 phương pháp; đối chiếu với sự kiện thực tế.

### Dự báo và Granger
TODO: MAE / RMSE của RF so với baseline; đặc trưng quan trọng; ma trận Granger và hạn chế của diễn giải.

## 7.3 Phần (b): Văn bản IMDB

### Text EDA
TODO: độ dài theo lớp và kết quả Mann-Whitney; TTR; mức độ tuân theo Zipf.

### Chuẩn hóa và tokenization
TODO: bảng thay đổi từ vựng theo từng bước; bảng vocab size / OOV / độ dài token của 4 chiến lược.

### Stop words, stemming, lemmatization
TODO: bảng trước/sau (vocab, MI, Naive Bayes); collision rate và F1 5-fold CV; trả lời: loại stop words có luôn tốt không?

### Biểu diễn văn bản
TODO: bảng số chiều / độ thưa / cosine trong-ngoài lớp / silhouette; so sánh TF-IDF với Sentence Transformer.

## 7.4 Thảo luận chung

TODO: so sánh hai dạng dữ liệu (tiền xử lý chuỗi thời gian vs văn bản), những lựa chọn có rủi ro rò rỉ dữ liệu và cách đã phòng tránh, các quyết định thiết kế quan trọng nhất.

## 7.5 Hạn chế và hướng phát triển

TODO: survivorship bias của dữ liệu S&P 500, giới hạn của mẫu con 10.000 review, các giả định của kiểm định thống kê, ...

## 7.6 Kết luận

TODO.

## Tài liệu tham khảo

TODO: liệt kê bài báo, tài liệu thư viện, nguồn dữ liệu đã dùng.
