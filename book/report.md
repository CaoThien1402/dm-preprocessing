# Chương 7. Báo cáo: so sánh và thảo luận

> Chương này so sánh các kỹ thuật tiền xử lý đã cài đặt ở chương 1 đến 6, nêu nhận xét phê bình và các hạn chế. Mọi con số được sinh trực tiếp từ `data/processed/results/*.json`; các giải thích chưa được kiểm chứng riêng được ghi rõ là "giải thích hợp lý".


## 7.1 Tóm tắt

Đồ án xây dựng hai pipeline tiền xử lý hoàn chỉnh, mỗi bước đều được đo bằng thực nghiệm có kiểm định thống kê thay vì áp dụng theo thói quen. **Phần (a)** dùng giá đóng cửa đã điều chỉnh chia tách của AAPL (5.283 phiên, 2005 đến 2025; train 4.226 phiên đến 2021-10-14, test 1.057 phiên) và log-return của 5 mã (AAPL, MSFT, JPM, XOM, JNJ) cho Granger. **Phần (b)** dùng IMDB: 50.000 review, còn 49.578 sau khử trùng lặp (train 39.662, test 9.916).

**Phát hiện chính của phần (a):**
- Nội suy tuyến tính là tốt nhất khi điền khoảng trống MCAR (thắng 29/30 lần, MAE trung bình 0.5430 so với 0.7639 của forward fill), vì giá gần như bước đi ngẫu nhiên; kết luận từ một mặt nạ duy nhất thì ngược lại.
- Giá không dừng; log-return dừng theo cả ba kiểm định ADF, KPSS, PP. AAPL gần như **không có mùa vụ**: không chu kỳ nào trong tuần, tháng, quý, năm có p hoán vị dưới 0.05.
- **Rò rỉ dữ liệu từ bộ làm mượt hai phía là rủi ro lớn nhất**: dùng STL fit trên toàn chuỗi làm đặc trưng thổi phồng R² ngoài mẫu từ 0.44% lên 29.72%.
- Với dữ liệu sạch, Random Forest **không vượt baseline ngây thơ có ý nghĩa thống kê** (MAE 2.2823 so với 2.2808 USD; Diebold–Mariano p = 0.6259).
- Granger: kiểm định F cổ điển cho 19/20 cặp có ý nghĩa nhưng chỉ 5 cạnh sống sót khi dùng sai số chuẩn bền vững và hiệu chỉnh đa kiểm định, với R² riêng phần dưới 0.8%.

**Phát hiện chính của phần (b):**
- Độ dài review không khác nhau giữa hai lớp (Mann-Whitney p = 0.1144). Top-50 từ gần như trùng nhau (46/50), nhưng các từ chức năng như *no*, *just*, *even* lại mang tín hiệu cảm xúc mạnh.
- Chuẩn hóa giảm từ vựng từ 380.597 xuống 99.459; giữ điểm đánh giá kiểu `7/10` cải thiện F1 có ý nghĩa.
- **Loại stop words không luôn tốt**: giúp Naive Bayes (+0.015 F1) nhưng không giúp Logistic Regression. Stemming và lemmatization không giúp ở bất kỳ phương pháp nào.
- TF-IDF với bigram là biểu diễn mạnh nhất trong thí nghiệm (F1 test 0.8941 với 10.000 review huấn luyện); **Sentence Transformer kém hơn** (0.8179), và không biểu diễn được phủ định tốt hơn TF-IDF.

## 7.2 Phần (a): Chuỗi thời gian S&P 500

### Điền khoảng trống

Tạo nhân tạo 5% khoảng trống MCAR (264 điểm) rồi so sánh 5 phương pháp (đề yêu cầu 4 nhóm, trong đó đa thức có bậc 2 và 3). Ljung–Box chạy trên log-return của chuỗi sau khi điền; chuỗi gốc cho Q = 34.92.

| Phương pháp | MAE (1 mặt nạ) | RMSE (1 mặt nạ) | Q Ljung–Box (h=10) | MAE, 30 mặt nạ (TB ± SD) | RMSE, 30 mặt nạ (TB) | Số lần MAE nhỏ nhất |
|---|---|---|---|---|---|---|
| forward fill | 0.7510 | 1.6071 | 28.73 | 0.7639 ± 0.0853 | 1.6060 | 0 |
| tuyến tính | 0.5595 | 1.1198 | 27.87 | 0.5430 ± 0.0644 | 1.1306 | 29 |
| đa thức bậc 2 | 0.5664 | 1.1673 | 32.13 | 0.6236 ± 0.0846 | 1.2981 | 1 |
| đa thức bậc 3 | 0.5345 | 1.1156 | 31.30 | 0.6026 ± 0.0870 | 1.2716 | 0 |
| cubic spline | 0.5367 | 1.1475 | 32.36 | 0.6101 ± 0.0671 | 1.2663 | 0 |

**Nhận xét phê bình.**
- **Nội suy tuyến tính thắng**: MAE trung bình 0.5430, và đa thức bậc 3 kém hơn 11.0%, forward fill kém hơn 40.7%. Lý do có cơ sở lý thuyết: PACF của giá chỉ có lag 1 vượt dải (chương 1), tức giá gần như bước đi ngẫu nhiên, mà với bước đi ngẫu nhiên kỳ vọng của điểm nằm giữa hai điểm đã biết chính là điểm trên đoạn thẳng nối chúng. Các đường cong bậc cao tìm "độ cong" không tồn tại và chỉ thêm phương sai.
- **Một mặt nạ ngẫu nhiên có thể cho kết luận ngược.** Với mặt nạ mặc định, đa thức bậc 3 (0.5345) và cubic spline (0.5367) thấp hơn tuyến tính (0.5595); chỉ khi lặp 30 mặt nạ mới thấy tuyến tính thắng 29/30 lần. Đây là lý do mọi so sánh ở đây đều có độ biến thiên đi kèm.
- **Ljung–Box không phân biệt được các phương pháp.** Mọi p-value đều dưới 0.05, kể cả chuỗi gốc (Q = 34.92), nên tiêu chí hợp lý là độ lệch của Q so với chuỗi gốc (từ 7% đến 20% thấp hơn), một chênh lệch nhỏ.
- **Forward fill là phương pháp duy nhất không dùng thông tin tương lai** (các phương pháp còn lại dùng giá sau khoảng trống), nên là lựa chọn duy nhất hợp lệ khi dự báo thời gian thực dù kém chính xác nhất.
- **Cài đặt:** `interpolate("polynomial", order=3)` của pandas trùng cubic spline (sai khác tối đa 5.7e-14), nên đa thức bậc 2 và 3 được cài thủ công; `interpolate("spline")` mặc định là smoothing spline (không đi qua điểm đã biết) nên không dùng.
- **Hạn chế:** khoảng trống MCAR chủ yếu là điểm đơn lẻ, trong khi dữ liệu thật thường mất thành đoạn dài; chuỗi AAPL thật không có khoảng trống nên bước này chỉ là thí nghiệm có kiểm soát.

### Tính dừng và phân rã

| Biến đổi | ADF p | KPSS p | PP p | Kết luận |
|---|---|---|---|---|
| giá gốc | 0.9985 | ≤ 0.01 | 0.9985 | Không dừng |
| log | 0.6508 | ≤ 0.01 | 0.5766 | Không dừng |
| Box–Cox (λ = 0.0550) | 0.7884 | ≤ 0.01 | 0.7442 | Không dừng |
| sai phân bậc 1 | ≈ 0 | 0.0212 | ≈ 0 | Mâu thuẫn |
| sai phân bậc 2 | ≈ 0 | ≥ 0.1 | ≈ 0 | Dừng |
| log-return (log rồi sai phân) | ≈ 0 | ≥ 0.1 | ≈ 0 | Dừng |
| log, có xu hướng tuyến tính (ct) | 0.0372 | ≤ 0.01 | 0.0218 | Mâu thuẫn |

**Nhận xét phê bình (tính dừng).**
- Giá gốc, log và Box–Cox đều **không dừng** với cả ba kiểm định đồng thuận (ADF p = 0.9985). Log và Box–Cox chỉ ổn định phương sai, không loại được xu hướng. Khi cho phép xu hướng tuyến tính (ct), ADF và PP bác bỏ nghiệm đơn vị của log giá ở mức 5% (p = 0.0372 và 0.0218) nhưng KPSS vẫn bác bỏ tính dừng, nên kết luận nhạy với thành phần tất định và ta không khẳng định chắc.
- **Sai phân bậc 1 của giá cho kết quả mâu thuẫn** (KPSS p = 0.0212), vì độ lệch chuẩn của chênh lệch giá nửa sau gấp 11.6 lần nửa đầu. **Sai phân bậc 2 "dừng" nhưng over-differencing** (tự tương quan lag 1 = -0.5003). **Log-return là biến đổi đầu tiên dừng theo cả ba kiểm định** (tỉ số độ lệch chuẩn 0.8308) và là chuỗi dùng cho các chương sau.
- Kết luận này không có nghĩa log-return là "nhiễu trắng": chương 1 cho thấy tự tương quan nhỏ nhưng khác 0 (Ljung–Box p = 7.0e-5) và biến động tụ cụm rất mạnh (Ljung–Box của log-return² có Q = 2189).

**Phân rã và chọn chu kỳ.** Chu kỳ được chọn bằng kiểm định hoán vị độ mạnh mùa vụ F_S trên tập train (null: bước đi ngẫu nhiên có cùng log-return xáo trộn):

| Chu kỳ | F_S quan sát | null: trung bình | null: phân vị 95% | p hoán vị |
|---|---|---|---|---|
| tuần (5) | 0.320 | 0.299 | 0.317 | 0.0588 |
| tháng (21) | 0.312 | 0.315 | 0.350 | 0.5686 |
| quý (63) | 0.294 | 0.323 | 0.387 | 0.9020 |
| năm (252) | 0.349 | 0.340 | 0.459 | 0.4706 |

| Chu kỳ | Cách phân rã | ρ_y | ρ_dt | Biên độ mùa vụ / giá (2 năm đầu) |
|---|---|---|---|---|
| 5 | additive | 0.000252 | 0.9990 | 2.6% |
| 5 | multiplicative | 0.000252 | 0.9970 | 0.1% |
| 5 | STL (log) | 0.000567 | 0.9924 | 5.0% |
| 252 | additive | 0.013360 | 0.9362 | 162.8% |
| 252 | multiplicative | 0.012579 | 0.8815 | 5.5% |
| 252 | STL (log) | 0.012763 | 0.7189 | 36.0% |

**Nhận xét phê bình (phân rã).**
- **Không chu kỳ nào có bằng chứng mùa vụ (p ≥ 0.05)**, kể cả chu kỳ năm. Chu kỳ 5 chỉ là chu kỳ có p nhỏ nhất (0.0588) và khớp với hiệu ứng thứ trong tuần duy nhất có ý nghĩa ở chương 1 (Kruskal–Wallis p = 1.1e-4, η²_H = 0.0037, rất nhỏ). Ngay cả bước đi ngẫu nhiên không có mùa vụ cũng cho F_S ≈ 0.30 đến 0.34, nên **tỉ số phương sai phần dư đứng riêng không chứng minh được mùa vụ**.
- **ρ nhỏ hơn không có nghĩa là mô hình tốt hơn.** STL chu kỳ 252 có ρ_dt thấp nhất (0.7189) chỉ vì thành phần mùa vụ đủ linh hoạt để khớp nhiễu. **Additive không phù hợp** với chuỗi tăng hơn 270 lần: ở chu kỳ 252 thành phần mùa vụ additive lên tới 162.8% giá trong 2 năm đầu, còn multiplicative chỉ 5.5%.
- **Thành phần mùa vụ của STL chu kỳ 5 chủ yếu là nhiễu**: biên độ trong [-0.0514, 0.0392] (cỡ 5%) lớn hơn nhiều lần so với chênh lệch lợi suất trung bình giữa các thứ trong tuần (0.261% và -0.042%), và phình ra theo các giai đoạn biến động mạnh.
- **Rò rỉ của bộ làm mượt hai phía** (mục 7.4): bảng dưới cho thấy fit trên toàn chuỗi làm xu hướng tại t₀ đổi 0.419 chỉ vì dữ liệu sau t₀ đổi, và ngay cả khi fit chỉ trên train, thành phần hai phía vẫn tương quan -0.417 với lợi suất ngày kế tiếp.

| Cách phân rã | Mức thay đổi của xu hướng tại t₀ khi đổi dữ liệu sau t₀ | Pearson r của (y_t − T_t) với r_(t+1) |
|---|---|---|
| fit trên toàn chuỗi | 0.41906 | (không đo) |
| fit chỉ trên train (hai phía) | 0.00000 | -0.4166 |
| STL nhân quả | 0.00000 | -0.0354 |

### Dị thường

Ba phương pháp chạy trên cùng 5.031 ngày, tham số chỉ học trên train: Z-score trên log-return đã khử mùa vụ, Isolation Forest trên cửa sổ trượt 10 ngày, và ngưỡng 3σ trên phần dư STL.

| Phương pháp | Số ngày gắn cờ | % ngày xét | Train / test | Phủ 10 ngày có log-return lớn nhất |
|---|---|---|---|---|
| Z-score | 72 | 1.43% | 63 / 9 | 9/10 |
| Isolation Forest | 45 | 0.89% | 40 / 5 | 6/10 |
| STL residual | 127 | 2.52% | 104 / 23 | 5/10 |

Jaccard: Z-score với Isolation Forest 0.206, Z-score với STL residual 0.192, Isolation Forest với STL residual 0.089; 46 ngày được ít nhất 2 phương pháp đồng thuận và 10 ngày được cả 3.

**Nhận xét phê bình.**
- **Ba phương pháp định nghĩa "dị thường" khác nhau nên gần như không trùng nhau** (Jaccard tối đa 0.21). Z-score phát hiện tốt nhất các cú sốc lớn (9/10 ngày có |r| lớn nhất); STL residual chỉ bắt 5/10 vì xu hướng robust bám theo chuỗi các cú sốc liên tiếp.
- **Đuôi dày làm mọi ngưỡng "chuẩn" gắn cờ quá nhiều.** Nếu log-return chuẩn thì 3σ chỉ gắn cờ 13.6 ngày; Z-score gắn cờ 72. Quy tắc k·MAD gắn cờ 765 ngày với k = 3 (15.2%) vì σ̂ theo MAD (0.0092) chỉ bằng 0.40 độ lệch chuẩn thật (kurtosis dư 7.41), nên không dùng làm chính.
- **STL điểm cuối nuốt cú sốc của chính ngày đó**, nên phát hiện dị thường dùng STL nhân quả trễ 5 phiên:

| Ngày | Log-return | z (STL điểm cuối) | z (STL trễ 5 phiên) |
|---|---|---|---|
| 2008-09-29 | -19.75% | -3.01 | -8.25 |
| 2013-01-24 | -13.19% | -5.68 | -3.58 |
| 2020-03-16 | -13.77% | -1.63 | -4.30 |
| 2025-04-09 | 14.26% | 0.04 | 8.13 |

- **Nguyên nhân (kiến thức ngoài dữ liệu, chưa kiểm chứng từ nguồn tin):** 12/15 ngày đồng thuận lớn nhất thuộc hai cụm: khủng hoảng tài chính 2008 và đại dịch COVID-19 tháng 3/2020; các ngày còn lại gồm 09/04/2025 (thông báo tạm hoãn thuế đối ứng) và 03/01/2019 (Apple hạ dự báo doanh thu). Phần lớn "dị thường" của AAPL vì vậy là **ngày sốc toàn thị trường**, không phải bất thường riêng của AAPL.
- **Hạn chế:** ngưỡng 3σ cố định với σ vô điều kiện không thích nghi với biến động tụ cụm nên gắn cờ cả cụm khủng hoảng thay vì các cú sốc bất ngờ so với bối cảnh hiện tại.

### Dự báo và Granger

Random Forest dự báo log-return ngày kế tiếp (p = 16 lag chọn từ PACF trên train, 41 đặc trưng, `min_samples_leaf` = 50 chọn bằng `TimeSeriesSplit`); dự báo giá là y_t·exp(r̂). Baseline ngây thơ ŷ_(t+1) = y_t và baseline drift.

| Mô hình | RMSE log-return | MAE (USD) | RMSE (USD) | R²_oos | Đúng chiều | Diebold–Mariano p |
|---|---|---|---|---|---|---|
| naive (r̂ = 0) | 0.01780 | 2.2808 | 3.2263 | 0.00% |  |  |
| drift (trung bình train) | 0.01779 | 2.2747 | 3.2259 | 0.07% | 53.26% | 0.8465 |
| RF: lag | 0.01787 | 2.2963 | 3.2406 | -0.78% | 51.28% | 0.3733 |
| RF: + cửa sổ trượt | 0.01780 | 2.2917 | 3.2282 | -0.01% | 51.84% | 0.9881 |
| RF: + thời gian | 0.01779 | 2.2880 | 3.2236 | 0.12% | 51.75% | 0.8776 |
| RF: + phân rã STL | 0.01776 | 2.2823 | 3.2179 | 0.44% | 51.66% | 0.6259 |

**Nhận xét phê bình (dự báo).**
- **Kết quả chính: MAE = 2.2823 USD và RMSE = 3.2179 USD**, so với baseline ngây thơ 2.2808 và 3.2263. Không mô hình nào có khác biệt có ý nghĩa với baseline (p từ 0.3733 trở lên). Đó là kết quả trung thực và hợp lý: log-return của AAPL gần như không tự tương quan (chương 1), phù hợp với giả thuyết thị trường hiệu quả dạng yếu. Tỉ lệ đoán đúng chiều của RF (51.66%) còn thấp hơn mô hình luôn dự báo tăng (53.26%).
- **Ablation:** thêm từng nhóm đặc trưng nâng R²_oos từ -0.78% lên 0.44% nhưng mọi chênh lệch nằm trong nhiễu; MDI chia gần đều theo số đặc trưng (lag 48.5%, cửa sổ trượt 36.0%, STL 11.4%, thời gian 4.1%), dấu hiệu của khớp nhiễu.
- **Điểm số "đẹp" có thể là dấu hiệu của lỗi.** Cùng mô hình nhưng dùng STL hai phía fit trên toàn chuỗi làm đặc trưng cho RMSE 2.6827 USD, R²_oos 29.72% và đúng chiều 72.37%, với p của Diebold–Mariano < 1e-8. Kết quả giả hoàn toàn: thành phần STL tại t đã chứa y_(t+1).

**Granger (nâng cao).** BIC của VAR chọn 0 lag nên dùng lag 1 làm trường hợp tối thiểu.

| Cách kiểm định | p thô < 0.05 | Bonferroni < 0.05 | BH (FDR) < 0.05 |
|---|---|---|---|
| F cổ điển | 19 | 15 | 19 |
| Wald HC3 (bền vững) | 11 | 3 | 5 |

**Nhận xét phê bình (Granger).**
- Kiểm định F cổ điển gần như kết luận mọi mã đều "dẫn dắt" mọi mã khác, nhưng nó giả định phương sai sai số không đổi trong khi log-return có biến động tụ cụm. Với sai số chuẩn bền vững HC3 và hiệu chỉnh BH chỉ còn 5 cạnh: AAPL→JNJ, MSFT→JNJ, XOM→AAPL, XOM→MSFT, XOM→JNJ. **R² riêng phần của mọi cặp dưới 0.77%**: có ý nghĩa thống kê nhưng không có ý nghĩa thực tế.
- Granger chỉ đo khả năng dự báo theo thời gian, không phải nhân quả thật; nó bỏ qua tương quan cùng thời điểm (tương quan giữa các mã từ 0.34 đến 0.51) và yếu tố thị trường chung. Chưa kiểm tra độ nhạy theo số lag (AIC chọn 9).

## 7.3 Phần (b): Văn bản IMDB

### Text EDA

Mọi phân tích khám phá chỉ dùng tập train (39.662 review).

| Đại lượng | Trung vị positive / negative | p-value | Rank-biserial | CI 95% (bootstrap) |
|---|---|---|---|---|
| số từ | 173 / 174 | 0.1144 | -0.0092 | [-0.0240; 0.0014] |
| số ký tự | 971 / 973 | 0.4108 | -0.0048 | [-0.0189; 0.0062] |
| số từ (đã bỏ HTML) | 171 / 172 | 0.1468 | -0.0084 | [-0.0234; 0.0026] |

**Nhận xét phê bình.**
- **Hai lớp không khác nhau về độ dài** (mọi p > 0.05; khoảng tin cậy chứa 0 và |rank-biserial| ≤ 0.024), nên độ dài không phải đặc trưng phân biệt. Phân phối lệch phải mạnh (skewness 2.17) nên dùng kiểm định phi tham số; kết luận không đổi sau khi bỏ thẻ HTML (thẻ này có ở 58.4% review).
- **Top-50 từ không phân biệt được cảm xúc**: 46/50 từ chung, và 46/50 từ của mỗi lớp là stop words hoặc `br` (token HTML `br` chiếm 1.73% số token). Log-odds có tiên nghiệm lại cho thấy các từ chức năng mang tín hiệu mạnh: *no* (z = -39.9), *just* (-35.1), *even* (-33.2) nghiêng negative, *and* (+41.9) nghiêng positive.
- **TTR phụ thuộc độ dài văn bản** nên không so sánh được nếu không cố định số token: TTR toàn lớp là 0.01689 (positive) và 0.01638 (negative), nhưng trên cùng 2.293.505 token là 0.02571 và 0.02451. Hai cách đo cho chiều ngược nhau: positive có vốn từ chung rộng hơn nhưng TTR trong từng review (100 token đầu) thấp hơn một chút (rank-biserial -0.0643); cả hai đều nhỏ về thực tế.
- **Zipf chỉ đúng gần đúng:**

| Đoạn fit | Số điểm | s | R² |
|---|---|---|---|
| toàn bộ từ vựng | 108.085 | 1.635 | 0.9774 |
| rank ≥ 10 và freq ≥ 10 (đoạn chính) | 25.748 | 1.365 | 0.9908 |
| rank từ 10 đến 5000 | 4.991 | 1.156 | 0.9977 |

  Hệ số s phụ thuộc mạnh vào đoạn fit (từ 1.16 đến 1.63), và đường log-log hơi cong nên R² cao (0.9908) chưa đủ để khẳng định lũy thừa thuần. 41.3% số types chỉ xuất hiện một lần, 100 từ đầu phủ 51.4% số token.

### Chuẩn hóa và tokenization

| Bước | Từ vựng (số types) | ΔV | Số từ TB |
|---|---|---|---|
| văn bản gốc | 380.597 |  | 231.19 |
| chữ thường | 339.687 | -10.75% | 231.19 |
| bỏ HTML | 317.911 | -6.41% | 228.90 |
| bỏ URL | 317.773 | -0.04% | 228.89 |
| bỏ mention, hashtag | 317.673 | -0.03% | 228.89 |
| bỏ ký tự đặc biệt và số (có điều kiện) | 99.459 | -68.69% | 229.69 |
| chuẩn hóa khoảng trắng | 99.459 | 0.00% | 229.69 |

**Nhận xét phê bình (chuẩn hóa).**
- Bước bỏ ký tự đặc biệt và số làm từ vựng giảm nhiều nhất (-68.69%), nhưng chủ yếu vì **gộp các dạng bề mặt của cùng một từ** ("movie", "movie.", "movie!"), không phải mất thông tin. URL, mention, hashtag chỉ giảm dưới 0.05%. Phân phối độ dài gần như không đổi (số từ TB từ 231.19 xuống 229.69).
- **"Có điều kiện" là có cơ sở thực nghiệm:** giữ điểm đánh giá kiểu `7/10` (có ở 8.68% review) tăng F1 có ý nghĩa (Logistic Regression +0.0029, p = 0.0098; Naive Bayes +0.0041, p = 0.0024). Mức tăng nhỏ vì chỉ có một thiểu số review chứa điểm.

| Chiến lược | Từ vựng (train) | OOV token (test) | OOV types (test) | Độ dài TB / review (test) |
|---|---|---|---|---|
| word-level | 130.522 | 0.7105% | 25.64% | 266.07 |
| word-level, từ tần suất ≥ 5 | 37.851 | 1.5583% | 48.47% | 266.07 |
| sentence-level | 475.126 | 96.7223% | 98.39% | 12.34 |
| character-level | 154 | 0.0001% | 3.85% | 1293.11 |
| BPE (30.000) | 30.000 | 0.0006% |  | 280.27 |

**Nhận xét phê bình (tokenization).**
- **BPE gần như không có OOV vì rơi về mảnh từ và ký tự** (0.0006%), trong khi word-level để lọt 0.71% token (25.6% số types), và cắt từ hiếm (tần suất ≥ 5) làm OOV tăng gấp 2.2 lần để đổi lấy từ vựng nhỏ hơn 71%.
- **Character-level có từ vựng nhỏ nhất (154) nhưng chuỗi dài nhất** (gấp 4.9 lần word-level). **Sentence-level không dùng được làm từ vựng rời rạc**: 96.7% câu test chưa từng thấy.
- **BPE là thỏa hiệp tốt:** từ vựng nhỏ hơn word-level 4.4 lần mà chuỗi chỉ dài hơn 5.3%.

### Stop words, stemming, lemmatization

| Chính sách | Từ vựng (mọi từ) | Từ / review | Tổng MI (nat) | F1 Naive Bayes | p | F1 Logistic Regression | p |
|---|---|---|---|---|---|---|---|
| giữ tất cả | 99.459 | 229.7 | 3.351 | 0.8428 ± 0.0049 |  | 0.8988 ± 0.0024 |  |
| bỏ stop words, giữ phủ định | 99.300 | 121.6 | 3.245 | 0.8572 ± 0.0042 | 0.0004 | 0.9000 ± 0.0027 | 0.5220 |
| bỏ stop words NLTK | 99.263 | 118.7 | 3.210 | 0.8578 ± 0.0040 | 0.0002 | 0.8998 ± 0.0030 | 0.5471 |

**Loại stop words có luôn tốt không? Không.**
- Stop words là 198 từ của NLTK, chỉ chiếm 0.2% số từ khác nhau nhưng gần một nửa số token (từ / review giảm từ 229.7 xuống 118.7), và **mang 4.49% tổng thông tin tương hỗ** (các từ có MI cao nhất: no, just, why, don, any).
- **Tác dụng phụ thuộc bộ phân loại:** Naive Bayes được lợi rõ (+0.0151, p = 0.0002) còn Logistic Regression thì không (+0.0011, p = 0.5471). Giải thích hợp lý (chưa kiểm chứng riêng): Naive Bayes giả định các từ độc lập và đếm các từ rất phổ biến nhiều lần nên bị nhiễu bởi chúng, còn Logistic Regression tự giảm trọng số.
- **Giữ phủ định:** hai cách bỏ stop words không khác nhau có ý nghĩa (p = 0.2574), nên ta chọn cách giữ nhiều thông tin hơn. **Minh bạch về quy trình:** quy tắc gốc (F1 cao nhất) sẽ chọn "bỏ stop words NLTK"; bước tinh chỉnh ưu tiên giữ phủ định được thêm sau khi xem kết quả CV và đã được công bố trong notebook.

| Phương pháp | Từ vựng sau gộp | Collision rate | Token bị đổi | Nhóm xung đột cảm xúc | F1 LR (CV) | Chênh | p |
|---|---|---|---|---|---|---|---|
| không xử lý | 99.300 | 0.00% | 0.00% | 0 | 0.9000 ± 0.0027 |  |  |
| Porter | 71.586 | 27.91% | 45.76% | 79 | 0.8972 ± 0.0023 | -0.0028 | 0.1686 |
| Snowball | 62.364 | 37.20% | 45.22% | 82 | 0.8970 ± 0.0030 | -0.0030 | 0.1285 |
| WordNet (danh từ) | 90.507 | 8.85% | 10.10% | 22 | 0.8983 ± 0.0022 | -0.0018 | 0.2950 |
| WordNet (động từ rồi danh từ) | 81.489 | 17.94% | 22.55% | 54 | 0.8969 ± 0.0019 | -0.0032 | 0.0529 |

**Nhận xét phê bình (stemming).**
- Snowball gộp mạnh nhất (collision rate 37.20%), WordNet danh từ nhẹ nhất (8.85%); các stemmer gộp sai (Porter: *general, generous, generation* về `gener`) và làm mất tín hiệu: 79 đến 82 nhóm gộp lẫn từ nghiêng positive với từ nghiêng negative (ví dụ *liked* và *like*).
- **Không phương pháp nào cải thiện F1** (mọi chênh lệch âm, p từ 0.0529 đến 0.2950), nên pipeline cuối không dùng stemming. Với 39.662 review và `min_df=5` độ thưa không còn là điểm nghẽn chính (giải thích hợp lý, không kiểm chứng riêng).

**Đánh giá cuối trên tập test** (một lần, không dùng để chọn gì):

| Văn bản đầu vào | F1 test Naive Bayes | F1 test Logistic Regression |
|---|---|---|
| văn bản gốc | 0.8493 | 0.8985 |
| chỉ chuẩn hóa (5.1) | 0.8525 | 0.9011 |
| pipeline đầy đủ | 0.8628 | 0.9004 |

### Biểu diễn văn bản

Mọi thứ cần học (từ vựng, IDF, Word2Vec) chỉ fit trên train; hình học đo trên toàn bộ tập test (9.916 review).

| Biểu diễn | Số chiều | Độ thưa | Cohen d (cosine cùng lớp / khác lớp) | Silhouette (nhãn cảm xúc) | F1 test, Linear SVM (10.000 review) |
|---|---|---|---|---|---|
| BoW (1-gram) | 32.951 | 0.997056 | 0.0832 ± 0.0100 | 0.0060 | 0.8780 |
| TF-IDF (1-gram) | 32.951 | 0.997056 | 0.1242 ± 0.0081 | 0.0025 | 0.8854 |
| TF-IDF (1-2 gram) | 143.441 | 0.999052 | 0.1309 ± 0.0061 | 0.0014 | 0.8941 |
| TF-IDF (1-3 gram) | 158.199 | 0.999122 | 0.1306 ± 0.0057 | 0.0014 | 0.8949 |
| Word2Vec (trung bình) | 100 | 0.000000 | 0.1905 ± 0.0160 | 0.0713 | 0.8805 |
| Sentence Transformer | 384 | 0 | 0.1016 ± 0.0131 | 0.0157 | 0.8179 |

**Nhận xét phê bình.**
- **Không biểu diễn nào tách cảm xúc trong không gian không giám sát:** mọi Cohen d dưới 0.2 và silhouette gần 0 (cao nhất Word2Vec: 0.0713). Độ giống nhau giữa hai review chủ yếu do chủ đề quyết định. Silhouette thấp **không có nghĩa bài toán khó**: bộ phân loại có nhãn vẫn đạt F1 trên 0.88, vì nó tìm được hướng phân tách mà khoảng cách không giám sát không thấy. Cosine thô không so sánh được giữa các biểu diễn (nền từ 0.015 với TF-IDF đến 0.927 với Word2Vec) nên so bằng Cohen d.
- **Đánh đổi số chiều và độ thưa:** TF-IDF có 32.951 đến 158.199 chiều và trên 99.7% phần tử bằng 0; thêm trigram gần như không đổi gì (chỉ thêm 14.758 chiều). Word2Vec chỉ 100 chiều, dày đặc, nắm đồng nghĩa (*terrible* gần *horrible*) nhưng cũng đặt *good* gần *bad*, vì tương đồng của nó là về ngữ cảnh chứ không phải cực tính.
- **TF-IDF với bigram mạnh nhất với bộ phân loại tuyến tính**; bigram tốt hơn unigram có ý nghĩa (McNemar p = 1.7e-6), trigram không thêm gì.

**So sánh TF-IDF với Sentence Transformer (nâng cao).**
- Với cùng 10.000 review huấn luyện, Sentence Transformer có F1 test 0.8179 so với 0.8854 (TF-IDF 1-gram) và 0.8941 (1-2 gram); McNemar p < 1e-8 theo chiều bất lợi cho embedding.
- **Cắt văn bản chỉ giải thích một phần:** 41.0% review dài hơn 256 token bị cắt. Khoảng cách F1 là 4.0 điểm ở review không bị cắt nhưng 10.9 điểm ở review bị cắt (gấp 2.7 lần) và vẫn có ý nghĩa ở review ngắn (McNemar p < 1e-8).
- **Các cụm tự nhiên của embedding không ứng với cảm xúc:** K-Means (k = 2) có silhouette cụm 0.0526 (cao hơn TF-IDF: 0.0025) nhưng ARI so với nhãn chỉ 0.0171.
- **Phủ định:** cả hai biểu diễn đều coi "not good" gần "good", trong khi embedding nhận ra đồng nghĩa tốt hơn hẳn (ví dụ minh họa, không phải kiểm định):

| Cặp câu | cosine TF-IDF | cosine Sentence Transformer |
|---|---|---|
| good so với not good | 0.852 | 0.819 |
| good so với great | 0.320 | 0.905 |
| good so với terrible | 0.214 | 0.706 |

  Vậy giả thuyết "embedding ngữ nghĩa nắm được phủ định mà TF-IDF bỏ lỡ" **không được ủng hộ** ở đây; embedding chỉ nắm được "cùng chủ đề và cùng nhóm nghĩa".

## 7.4 Thảo luận chung

### So sánh hai dạng dữ liệu

| | Chuỗi thời gian (AAPL) | Văn bản (IMDB) |
|---|---|---|
| Rủi ro tiền xử lý lớn nhất | rò rỉ thông tin tương lai qua bộ làm mượt hai phía và đặc trưng cửa sổ | rò rỉ qua trùng lặp giữa train và test, và qua việc fit từ vựng/vectorizer trên cả test |
| Bằng chứng định lượng | R² ngoài mẫu 0.44% (đúng) so với 29.72% (rò rỉ) | 422 review trùng theo khóa chuẩn hóa; sau khử, giao train/test bằng 0 |
| Bước "kinh điển" không giúp | mùa vụ, đặc trưng thời gian, Random Forest so với baseline ngây thơ | stemming, và stop words với Logistic Regression |
| Bước có cơ sở dữ liệu rõ | log-return (dừng), STL nhân quả, nội suy tuyến tính | giữ điểm đánh giá và phủ định, TF-IDF với bigram |
| Tín hiệu dự đoán | rất yếu (hiệu quả thị trường dạng yếu) | mạnh (F1 trên 0.90) |

### Những lựa chọn có rủi ro rò rỉ và cách đã phòng tránh

| Rủi ro | Nơi xảy ra | Cách phòng tránh | Bằng chứng |
|---|---|---|---|
| Xáo trộn thời gian | chia train/test | chia theo thời gian (80/20), không xáo trộn | train 4.226 phiên đến 2021-10-14, test 1.057 phiên |
| Bộ làm mượt hai phía (STL) | đặc trưng phân rã | STL nhân quả cuốn chiếu (cửa sổ 252) cho đặc trưng; fit chỉ trên train cho phân tích | xu hướng đổi 0.419 (toàn chuỗi) so với 0 (nhân quả); r = -0.417 so với -0.035 |
| Chọn tham số bằng dữ liệu test | số lag p, chu kỳ STL, ngưỡng dị thường | PACF và kiểm định chu kỳ chỉ trên train; tham số dị thường học trên train | p = 16 từ PACF của train; kiểm tra tự động: số ô đặc trưng đổi khi phá dữ liệu tương lai = 0 |
| Trùng lặp review | chia văn bản | khử trùng lặp theo khóa chuẩn hóa trước khi chia | 422 bản bị loại; giao train/test = 0 |
| EDA nhìn thấy test | chương 4 | chia trước, EDA chỉ trên train | mọi thống kê EDA tính trên 39.662 review train |
| Fit vectorizer, BPE, Word2Vec trên test | chương 5 và 6 | chỉ fit trên train; trong CV, vectorizer nằm trong pipeline fit lại từng fold | OOV đo trên test; test chỉ dùng cho đánh giá cuối |
| Chọn mô hình theo điểm test | stop words, stemming | quy tắc chọn dựa trên CV trên train; test chỉ chấm một lần ở 5.5 | bảng F1 test không tham gia lựa chọn |

### Các quyết định thiết kế quan trọng nhất
1. **Dự báo log-return thay vì giá**, vì giá không dừng và Random Forest không ngoại suy (giá test tối đa vượt xa giá train).
2. **STL nhân quả cho đặc trưng, STL fit trên train cho phân tích**; STL trễ 5 phiên cho phát hiện dị thường.
3. **Khóa chuẩn hóa để khử trùng lặp** và chia train/test trước mọi phân tích văn bản.
4. **Quy tắc chọn đặt trước, dựa trên cross-validation và kiểm định t ghép cặp có hiệu chỉnh**, kèm công bố rõ chỗ quy tắc được tinh chỉnh (stop words).
5. **Báo cả effect size và độ biến thiên** (Cohen d, rank-biserial, η²_H, R² riêng phần) vì với n lớn p-value nhỏ gần như chắc chắn.
6. **Kiểm định bền vững khi giả định bị vi phạm** (HC3 cho Granger khi có biến động tụ cụm).

### Bài học chung
- **Điểm số đẹp bất thường là dấu hiệu cần nghi ngờ**: R² 29.72% là kết quả của rò rỉ, còn kết quả đúng là 0.44%.
- **Phức tạp hơn không có nghĩa là tốt hơn**: nội suy tuyến tính thắng đa thức, TF-IDF thắng Sentence Transformer, không xử lý thắng stemming, naive ngang Random Forest.
- **Ý nghĩa thống kê khác ý nghĩa thực tế**: Granger có 19/20 cặp "có ý nghĩa" nhưng R² riêng phần dưới 0.77%.
- **Hiệu ứng của một bước tiền xử lý phụ thuộc mô hình phía sau** (stop words giúp Naive Bayes, không giúp Logistic Regression), nên không thể đánh giá tiền xử lý độc lập với bài toán.

## 7.5 Hạn chế và hướng phát triển

**Dữ liệu và phạm vi.**
- **Survivorship bias:** dataset chỉ chứa các mã hiện thuộc S&P 500; 293/503 mã được thêm vào chỉ số sau 2005 và chỉ 382/500 mã có đủ lịch sử. Kết quả mô tả riêng AAPL, một "người sống sót" rất thành công (CAGR 30.9%), không suy rộng được cho thị trường. Cột giá `close` đã điều chỉnh chia tách; việc điều chỉnh cổ tức không kiểm chứng được.
- **Chỉ một mã và một giai đoạn kiểm tra:** tập test (từ 2021-10-14) chỉ gồm một chế độ thị trường nên kết quả dự báo chưa chắc tổng quát; cần walk-forward nhiều cửa sổ và nhiều mã.
- **Mẫu con 10.000 review** để huấn luyện bộ phân loại ở chương 6 làm F1 thấp hơn so với dùng toàn bộ train (TF-IDF 1-2 gram: 0.9129 so với 0.8941); các so sánh giữa biểu diễn chỉ đúng ở cỡ dữ liệu này.

**Phương pháp và thống kê.**
- **Giả định của kiểm định:** t hiệu chỉnh trên 5-fold CV chỉ là xấp xỉ; các cặp review dùng chung tài liệu nên không báo p-value cho cosine; Levene và Ljung–Box giả định độc lập trong khi log-return có biến động tụ cụm; số chuỗi xáo trộn cho kiểm định mùa vụ chỉ là 50 nên độ phân giải của p khoảng 0.02.
- **Đa kiểm định:** ta hiệu chỉnh đầy đủ cho Granger, chỉ nhắc Bonferroni cho các tương quan Spearman, và không hiệu chỉnh xuyên suốt mọi chương; nhiều kết luận phụ thuộc vào ngưỡng 0.05 mong manh (ví dụ p = 0.0529 của WordNet động từ rồi danh từ).
- **Quy tắc chọn stop words được tinh chỉnh sau khi xem kết quả CV** (đã công bố); lần chạy đầu của chương 5 đã in F1 test của quy tắc gốc nhưng quyết định dựa trên CV.
- **Sentence Transformer chưa được tinh chỉnh**, cắt ở 256 token và chỉ kết hợp với bộ phân loại tuyến tính; chia review thành nhiều đoạn, fine-tuning hoặc mô hình lớn hơn có thể thu hẹp khoảng cách.
- **Granger** chỉ thử một số lag; **dị thường** dùng ngưỡng cố định không thích nghi với biến động tụ cụm (hướng phát triển: ngưỡng điều kiện theo biến động, ví dụ mô hình GARCH).
- **Nguyên nhân các ngày dị thường** là kiến thức ngoài dữ liệu, chưa đối chiếu nguồn tin.

**Hướng phát triển.** Walk-forward với nhiều mã; mô hình biến động có điều kiện; đặc trưng mức độ vĩ mô; fine-tuning embedding và chia đoạn cho review dài; thử bộ phân loại phi tuyến trên TF-IDF.

## 7.6 Kết luận

Tiền xử lý tốt không phải là áp dụng nhiều kỹ thuật mà là **chọn kỹ thuật bằng bằng chứng và kiểm soát rò rỉ**. Với chuỗi thời gian, thay vì điểm số cao, kết quả đáng tin nhất là dự báo ngày kế tiếp không vượt baseline ngây thơ (R² ngoài mẫu 0.44%), và bài học lớn nhất là một đặc trưng phân rã tưởng vô hại có thể thổi phồng R² lên 29.72%. Với văn bản, các bước mang tính miền (giữ điểm đánh giá, giữ phủ định) và biểu diễn TF-IDF với bigram có bằng chứng tốt, trong khi stemming không giúp, loại stop words chỉ giúp một mô hình và embedding ngữ nghĩa không hơn TF-IDF cho cảm xúc. Mọi con số trong báo cáo được sinh từ các file kết quả của notebook và đã được tính lại độc lập bằng mã riêng ở từng chương.

## Tài liệu tham khảo

**Dữ liệu và đề bài**
- Dark Matter Net. *S&P 500 Stocks: 25 Years of Data (Updated Daily)*, Kaggle, phiên bản 206. https://www.kaggle.com/datasets/darkmatternet/s-and-p-500-stocks-25-years-of-data-updated-daily
- Lakshmipathi N. *IMDB Dataset of 50K Movie Reviews*, Kaggle, phiên bản 1. https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews
- Đề bài: *Tiền xử lý dữ liệu*, Course Lab Book, Khai thác dữ liệu và ứng dụng, FIT@HCMUS. https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/preprocessing/

**Chuỗi thời gian**
- Dickey, D. A., Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association*, 74(366), 427–431.
- Phillips, P. C. B., Perron, P. (1988). Testing for a unit root in time series regression. *Biometrika*, 75(2), 335–346.
- Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., Shin, Y. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root. *Journal of Econometrics*, 54, 159–178.
- Ljung, G. M., Box, G. E. P. (1978). On a measure of lack of fit in time series models. *Biometrika*, 65(2), 297–303.
- Cleveland, R. B., Cleveland, W. S., McRae, J. E., Terpenning, I. (1990). STL: A seasonal-trend decomposition procedure based on loess. *Journal of Official Statistics*, 6(1), 3–73.
- Hyndman, R. J., Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3rd ed.). OTexts (độ mạnh mùa vụ).
- Liu, F. T., Ting, K. M., Zhou, Z.-H. (2008). Isolation Forest. *IEEE International Conference on Data Mining (ICDM)*, 413–422.
- Breiman, L. (2001). Random Forests. *Machine Learning*, 45, 5–32.
- Diebold, F. X., Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics*, 13(3), 253–263.
- Newey, W. K., West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703–708.
- Granger, C. W. J. (1969). Investigating causal relations by econometric models and cross-spectral methods. *Econometrica*, 37(3), 424–438.
- MacKinnon, J. G., White, H. (1985). Some heteroskedasticity-consistent covariance matrix estimators with improved finite sample properties. *Journal of Econometrics*, 29, 305–325.
- Benjamini, Y., Hochberg, Y. (1995). Controlling the false discovery rate: a practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society, Series B*, 57(1), 289–300.

**Văn bản**
- Zipf, G. K. (1949). *Human Behavior and the Principle of Least Effort*. Addison-Wesley.
- Monroe, B. L., Colaresi, M. P., Quinn, K. M. (2008). Fightin' words: lexical feature selection and evaluation for identifying the content of political conflict. *Political Analysis*, 16(4), 372–403.
- Porter, M. F. (1980). An algorithm for suffix stripping. *Program*, 14(3), 130–137.
- Fellbaum, C. (ed.) (1998). *WordNet: An Electronic Lexical Database*. MIT Press.
- Sennrich, R., Haddow, B., Birch, A. (2016). Neural machine translation of rare words with subword units. *Proceedings of ACL*, 1715–1725.
- Mikolov, T., Chen, K., Corrado, G., Dean, J. (2013). Efficient estimation of word representations in vector space. arXiv:1301.3781.
- Reimers, N., Gurevych, I. (2019). Sentence-BERT: sentence embeddings using Siamese BERT-networks. *Proceedings of EMNLP-IJCNLP*, 3982–3992.
- Wang, W., Wei, F., Dong, L., Bao, H., Yang, N., Zhou, M. (2020). MiniLM: deep self-attention distillation for task-agnostic compression of pre-trained transformers. *NeurIPS 33*. Mô hình `sentence-transformers/all-MiniLM-L6-v2`: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- van der Maaten, L., Hinton, G. (2008). Visualizing data using t-SNE. *Journal of Machine Learning Research*, 9, 2579–2605.
- Rousseeuw, P. J. (1987). Silhouettes: a graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics*, 20, 53–65.
- Hubert, L., Arabie, P. (1985). Comparing partitions. *Journal of Classification*, 2, 193–218.

**Thống kê chung**
- Mann, H. B., Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *Annals of Mathematical Statistics*, 18(1), 50–60.
- McNemar, Q. (1947). Note on the sampling error of the difference between correlated proportions or percentages. *Psychometrika*, 12(2), 153–157.
- Nadeau, C., Bengio, Y. (2003). Inference for the generalization error. *Machine Learning*, 52, 239–281.
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum.
- Tomczak, M., Tomczak, E. (2014). The need to report effect size estimates revisited. *Trends in Sport Sciences*, 21(1), 19–25.

**Phần mềm**
- Pedregosa, F. et al. (2011). Scikit-learn: machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
- Seabold, S., Perktold, J. (2010). statsmodels: econometric and statistical modeling with Python. *Proceedings of the 9th Python in Science Conference*.
- Řehůřek, R., Sojka, P. (2010). Software framework for topic modelling with large corpora. *Proceedings of the LREC Workshop on New Challenges for NLP Frameworks*, 45–50 (gensim).
- Bird, S., Klein, E., Loper, E. (2009). *Natural Language Processing with Python*. O'Reilly (NLTK).
- Sheppard, K. *arch: ARCH models and unit-root tests in Python* (kiểm định Phillips–Perron).
- Hugging Face *tokenizers*, *sentence-transformers*, `holidays`, `wordcloud`, `networkx`, `kagglehub`, `uv`, Jupyter Book 2 / MyST (tài liệu chính thức của từng thư viện).
