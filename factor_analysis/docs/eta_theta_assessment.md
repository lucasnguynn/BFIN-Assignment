# Eta vs Theta - Đánh giá ý nghĩa kinh tế của hệ số nhân tố (Workstream 4)

> **TRẠNG THÁI: BẢN KHUNG - CHƯA CÓ KẾT QUẢ HỒI QUY CHÍNH THỨC.**
> Dữ liệu Kenneth French (Mkt-RF, SMB, HML, RF) chưa được tải về (xem `README.md`, bước 2). Mọi mục "KẾT QUẢ" bên dưới
> sẽ được điền từ `factor_analysis/outputs/*.csv` sau khi chạy `run_pipeline.py`. Không con số SMB/HML/alpha nào trong file này được ước lượng hay bịa ra.

## 1. Những gì đã biết chắc (dữ liệu thật, nhưng CHỈ là proxy sơ bộ)
Nguồn: `factor_analysis/outputs/PRELIMINARY_vti_proxy_market_model.csv` - hồi quy lợi suất thô theo VTI, 96 tháng 2015-01..2022-12.
**Đây không phải CAPM/Jensen's alpha**: không trừ lãi suất phi rủi ro, VTI không phải Mkt-RF, chưa có SMB/HML.

| Đối tượng | Beta so với VTI (CI 95%) | R² hiệu chỉnh |
|---|---|---|
| Danh mục tăng trưởng đã đóng băng (Sample MV) | 0.82 (0.73-0.90) | 0.79 |
| Danh mục Min-Variance (bị loại) | 0.71 (0.63-0.79) | 0.77 |
| MSFT | 0.96 (0.76-1.17) | 0.48 |
| PG | 0.39 (0.21-0.57) | 0.15 |

Diễn giải (mức độ tin cậy: trung bình, vì là proxy): danh mục tăng trưởng nhạy với thị trường **thấp hơn 1** (khoảng 0.8): khoảng 80% biến động
tháng được giải thích bởi thị trường rộng; phần còn lại là rủi ro riêng/nhân tố. MSFT gần beta 1 nhưng R² thấp (rủi ro riêng lớn); PG phòng thủ (beta ~0.4, R² 0.15).
Điều này khớp với cấu trúc danh mục: tối đa 15%/cổ phiếu, nhiều mã phòng thủ (PG, KO, JNJ, PFE).

## 2. Giả thuyết cần kiểm định (KHÔNG phải kết quả)
- **SMB (size)**: danh mục toàn large-cap (AAPL, MSFT, JPM, JNJ, PG, KO, CAT, PFE) và 0% IWM => kỳ vọng SMB loading âm hoặc gần 0.
- **HML (value)**: lẫn lộn - AAPL/MSFT là growth (HML âm), PG/KO/JNJ/PFE/JPM/CAT thiên value/defensive (HML dương). Dấu tổng hợp chưa thể đoán; để dữ liệu quyết định.
- **Alpha**: kỳ vọng alpha CAPM dương trong mẫu (xem proxy: intercept dương), và **có khả năng giảm khi thêm SMB/HML** nếu phần "vượt trội" thực ra là phần bù nhân tố.

## 3. Alpha ước lượng cho phép và KHÔNG cho phép kết luận điều gì
1. **Thiên lệch chọn lọc trong mẫu (in-sample selection bias).** Trọng số được tối ưu hóa bằng chính mẫu 2015-2022 (25% trung bình lịch sử riêng từng mã + 75% VTI), cộng với universe 12 mã được chọn hồi tố năm 2026.
   Alpha dương trong mẫu vì thế một phần là **cơ học** (chọn người thắng ex post), không phải kỹ năng.
2. **Alpha không phải kỹ năng**: alpha = phần lợi suất chưa được giải thích bởi *mô hình đã chọn*. Khác mô hình, alpha đổi (sẽ báo cáo `alpha_change_monthly`, `alpha_sign_flip`).
3. **Bất định**: với n=96, SE của alpha hàng tháng rộng; chỉ kết luận khi CI 95% (và SE Newey-West) không chứa 0. Với 8 cổ phiếu + 2 danh mục + VTI x 2 mô hình, có vấn đề **multiple testing** (có ~1/20 kết quả "có ý nghĩa" ngẫu nhiên ở mức 5%).
4. **Dữ liệu**: Adj Close của Yahoo (retrieved 2026) và bản French mới nhất có thể đã được điều chỉnh/revised so với vintage 31/12/2022.
5. **Persistence chưa kiểm định**: không được nói alpha 2015-22 sẽ kéo dài sang 2023-25 trước khi có đánh giá đóng băng (WS6) với tiêu chí khai báo trước.

## 4. Eta (treasurer: Sharpe/lợi suất điều chỉnh rủi ro lịch sử) vs Theta (adviser: nhân tố + alpha bền vững)
| | Eta | Theta |
|---|---|---|
| Logic | chọn tài sản có Sharpe lịch sử cao nhất | chọn theo loading nhân tố và alpha "bền" |
| Điểm mạnh | đơn giản, minh bạch | tách được lợi suất do beta/nhân tố khỏi phần dư |
| Điểm yếu | mẫu nhiễu, Sharpe ước lượng sai số lớn, overfit | alpha phụ thuộc mô hình; persistence chưa được chứng minh; multiple testing |
| Quan hệ với khuyến nghị nhóm | Sample-MV có thành phần "chọn theo lịch sử" nên **gần Eta hơn** mong đợi; nhóm đã shrink 75% về VTI và đặt cap 15%/30% để giảm overfit | nhân tố dùng để **giải thích và giám sát rủi ro**, không dùng alpha làm căn cứ chọn trọng số |

**KẾT QUẢ (điền sau):** bảng `factor_coefficients.csv` (alpha, beta, SE, t, CI, adj R²) và `factor_model_comparison.csv` (đổi alpha CAPM->FF3, F-test SMB+HML, BIC) cho GROWTH, MSFT, PG + 6 mã khác.
Quy tắc điền: mỗi câu kết luận phải trích đúng một ô trong CSV; nếu CI chứa 0 thì ghi "không phân biệt được với 0".

## 5. Bẫy thi (exam traps)
- Dùng **VTI** thay cho **Mkt-RF** hoặc quên trừ **RF** => alpha sai. Phải dùng excess return đúng đơn vị (decimal, French là %/100).
- Nói "alpha dương = có kỹ năng / sẽ outperform". Sai: chỉ là phần dư của mô hình, trong mẫu, chưa kiểm persistence.
- Quên rằng danh mục 2015-22 ở đây là trọng số **cố định** (static exposure), khác danh mục buy-and-hold trôi trọng số của 2023-25.
- Đọc R² cao như "dự báo tốt": R² đo mức giải thích trong mẫu, không phải khả năng dự báo.
- Báo cáo mô hình đa nhân tố khi chưa xác nhận **Lecture 7** dùng FF3 hay mô hình khác.
