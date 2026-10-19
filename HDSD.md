# 🚀 HƯỚNG DẪN SỬ DỤNG MÔI TRƯỜNG LÀM VIỆC CHUNG (Dành cho M1 & M2)

Chào M1 và M2,
Mình (M3) đã thiết lập xong môi trường code dùng chung trên GitHub (thông qua **Codespaces** / Devcontainer) cho dự án Kappa Foundation. Việc dùng chung môi trường này đảm bảo:
* Mọi người dùng chung một phiên bản thư viện (không bị lỗi "code chạy trên máy tao nhưng lỗi trên máy mày").
* Dễ dàng ráp nối dữ liệu giữa phần Trái phiếu (M1), Cổ phiếu (M2) và Chạy mô hình nhân tố (M3).
* Đảm bảo toàn bộ dự án vượt qua bài kiểm tra tự động (QA Pipeline) trước khi nộp.

Dưới đây là hướng dẫn cụ thể cho từng người:

## 🌟 PHẦN 1: THAO TÁC CƠ BẢN (Cho cả M1 và M2)

**1. Cách truy cập không gian làm việc (Codespaces)**
* Vào trang repo GitHub của nhóm.
* Bấm vào nút màu xanh **Code** -> Chọn tab **Codespaces** -> Bấm vào dấu **+** hoặc bấm vào tên Codespace đã có để mở môi trường VS Code ngay trên trình duyệt (hoặc kết nối qua VS Code app).

**2. Quy trình "Bất di bất dịch" khi làm việc (Git Workflow)**
Mỗi khi bắt đầu hoặc kết thúc công việc, hãy mở Terminal (Ctrl + \`) và gõ các lệnh sau để tránh xung đột file (Conflict):
* **TRƯỚC KHI LÀM:** `git pull origin main` (Để tải code mới nhất của người khác về máy).
* **SAU KHI LÀM XONG:** 
  1. `git add .` (Đưa toàn bộ thay đổi vào hàng đợi).
  2. `git commit -m "Ghi chú công việc bạn vừa làm (VD: M1 update file Excel)"`.
  3. `git push origin main` (Đẩy code lên mạng cho cả nhóm).

**3. Cách tự kiểm tra bài làm của mình (Chạy Pipeline)**
Sau khi cập nhật file Excel (M1) hoặc chạy xong code (M2), hãy gõ lệnh này ở Terminal để xem bài làm của mình có đạt chuẩn chưa:
```bash
python run_pipeline.py
```
* Nếu toàn bộ hiện `[PASS]` và dòng cuối là `VERDICT: GO` -> **Tuyệt vời!**
* Nếu hiện `[FAIL]`, hãy cuộn lên đọc báo lỗi để biết dữ liệu của mình sai ở đâu và sửa lại.

---

## 💼 PHẦN 2: HƯỚNG DẪN RIÊNG CHO M1 (Phụ trách Bond Funding)

**Khu vực hoạt động:** Thư mục `bond_funding/`

* **Nhiệm vụ chính:** Cập nhật và lưu mô hình trái phiếu Excel của bạn vào thư mục này (File gốc hiện tại đang là `Kappa_Bond_Funding_Model.xlsx`).
* **Lưu ý cực kỳ quan trọng:**
  * Không được thay đổi tên các Sheet hoặc tên Cột (Header) quan trọng mà code của M3 đang dùng để tự động đọc dữ liệu.
  * Đảm bảo tính toán tổng dòng tiền bù đắp nợ (Liability) chuẩn xác. Code `qa_checks` sẽ kiểm tra chéo dòng tiền của bạn.
  * Sau khi lưu file Excel mới, nhớ thực hiện lệnh `git add` và `git commit` để đẩy file Excel đó lên GitHub.
  * Cập nhật các file giả định chính sách (nếu có yêu cầu từ đề bài) một cách cẩn thận vì nó ảnh hưởng đến tổng quy mô quỹ (12 triệu USD).

---

## 💻 PHẦN 3: HƯỚNG DẪN RIÊNG CHO M2 (Phụ trách Portfolio Construction)

**Khu vực hoạt động:** Thư mục `portfolio_construction/` (bao gồm `src/`, `notebooks/`, `outputs/`).

* **Nhiệm vụ chính:** Chạy thuật toán tối ưu hóa danh mục, trích xuất dữ liệu, kiểm tra giới hạn (cap 15%/30%) và xuất ra các file dữ liệu chuẩn cho M3.
* **Quy tắc Dữ liệu (Data Rules):**
  * Toàn bộ code của bạn phải chạy **OFFLINE**. Dữ liệu giá cổ phiếu Yahoo Finance phải được lưu sẵn trong thư mục `portfolio_construction/data/raw/` (như file `.zip` hoặc `.pkl` hiện có). Không gọi API tải trực tiếp mỗi khi chạy file!
  * Đầu ra cuối cùng bắt buộc phải được lưu vào thư mục `outputs/`.
* **Handoff cho M3:** Mình (M3) sẽ cần code của bạn xuất ra chính xác file tỷ trọng danh mục (ví dụ `frozen_weights.csv`) và chuỗi lợi suất (`growth_returns.csv`) để mình chạy mô hình Lecture 7 Fama-French. Đảm bảo tổng tỷ trọng cộng lại bằng đúng `1.0`.
* **Về thư viện (Libraries):** Nếu code của M2 cần dùng một thư viện Python mới (ví dụ `scipy`, `cvxpy`, v.v.), hãy báo cho M3 hoặc tự động thêm tên thư viện đó vào file `requirements.txt` ở ngoài cùng nhé.

---
*Nếu trong quá trình thao tác có bất kỳ lỗi nào báo đỏ trên Terminal (đặc biệt là khi chạy `run_pipeline.py`), mọi người cứ copy lỗi gửi lên group để M3 hỗ trợ debug nhé. Chúc mọi người code mượt!* 🚀