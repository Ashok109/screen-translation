# Dich Man Hinh - Công Cụ Dịch Thuật Màn Hình

Đây là một công cụ dịch thuật mạnh mẽ và linh hoạt, cho phép bạn chụp ảnh một phần hoặc toàn bộ màn hình và dịch văn bản được nhận dạng ngay lập tức. Ứng dụng được xây dựng bằng PyQt5 và hỗ trợ nhiều dịch vụ (trong tương lại :v) OCR và dịch thuật khác nhau.


## Tính Năng Chính

- **Dịch Linh Hoạt:**
    - **Chụp và Dịch (Snip & Translate):** Dùng phím tắt để nhanh chóng chọn một vùng trên màn hình và dịch ngay lập tức.
    - **Dịch Vùng Cố Định:** Chọn một vùng cụ thể để dịch lặp đi lặp lại.
    - **Dịch Toàn Màn Hình:** Chụp và dịch toàn bộ nội dung hiển thị trên màn hình.
- **Tự Động Dịch:** Tự động dịch lại vùng đã chọn theo một khoảng thời gian tùy chỉnh, lý tưởng cho việc theo dõi nội dung động như game hoặc video.
- **Hỗ trợ Đa Dịch Vụ Dịch Thuật:**
    - **Google Translate** (mặc định, không cần API key)
    - **Gemini** (của Google)
    - **OpenRouter** (hỗ trợ nhiều mô hình AI)
    - **API Tùy Chỉnh** (tương thích với định dạng OpenAI)
- **Tùy Chỉnh Cao:**
    - **Phím Tắt:** Tùy chỉnh các phím tắt cho mọi chức năng dịch.
    - **Ngôn Ngữ OCR:** Cấu hình nhiều ngôn ngữ để nhận dạng văn bản (ví dụ: `en,ja,ko`).
    - **Prompt Tùy Chỉnh:** Viết prompt riêng cho các mô hình AI để tinh chỉnh kết quả dịch.
- **Giao Diện Thân Thiện:**
    - Bảng điều khiển nhỏ gọn, có thể di chuyển và mở rộng.
    - Kết quả dịch được hiển thị ngay tại vị trí của văn bản gốc.
    - Thay đổi cấu hình và áp dụng ngay lập tức mà không cần khởi động lại.

## Hướng Dẫn Cài Đặt và Chạy Ứng Dụng

### Yêu Cầu Hệ Thống
- Python 3.x
- Git (tùy chọn, để tải dự án)
- **Đối với người dùng GPU NVIDIA:** Cần cài đặt [NVIDIA Driver](https://www.nvidia.com/Download/index.aspx) mới nhất.

### Bước 1: Tải Dự Án
- **Cách 1 (Dùng Git):** `git clone https://github.com/caotranquochoai/screen-translation`
- **Cách 2 (Tải ZIP):** Tải file ZIP của dự án từ GitHub và giải nén.

### Bước 2: Chạy Cài Đặt Tự Động
Sau khi tải dự án, bạn có hai lựa chọn để cài đặt và chạy ứng dụng.

---

#### **Lựa chọn 1: Dùng PowerShell (Khuyến nghị)**
Đây là phương pháp đáng tin cậy nhất để đảm bảo GPU được nhận diện chính xác.

1.  **Cho phép thực thi Script (Chỉ làm một lần duy nhất có thể bỏ qua nếu chạy bước 2 không lỗi :v):**
    - Mở **Windows PowerShell** với quyền **Administrator**.
    - Chạy lệnh sau và nhấn `Y` (Yes) nếu được hỏi:
      ```powershell
      Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
      ```
    - Bạn có thể đóng cửa sổ Administrator sau khi lệnh chạy xong.

2.  **Chạy file `run.ps1`:**
    - Di chuyển đến thư mục dự án.
    - **Chuột phải** vào file `run.ps1` và chọn **"Run with PowerShell"**.

---

#### **Lựa chọn 2: Dùng file Batch (Đơn giản)**
Phương pháp này đơn giản hơn nhưng có thể không nhận diện được GPU trên một số máy.
Nếu máy bạn không có GPU hoặc GPU AMD hãy chạy file này.

1.  **Chạy file `run.bat`:**
    - Di chuyển đến thư mục dự án.
    - **Nhấp đúp** vào file `run.bat`.

---
#### **Lựa chọn 3: Chạy thủ công **

Tạo môi trường ảo: python -m venv .venv

Truy cập môi trường ảo: .venv\Scripts\activate

Chạy cập nhật tourh với cpu: pip install torch torchvision torchaudio

Chạy cập nhật tourh với GPU nvidia: pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

Cập nhật thư viện cần thiết: pip3 install -r requirements.txt

Khởi động ứng dụng: python main.py

---




Cả hai kịch bản sẽ tự động thực hiện tất cả các bước cần thiết:
- Tạo môi trường ảo (`.venv`) để tránh xung đột thư viện.
- **Tự động phát hiện GPU NVIDIA** và cài đặt phiên bản PyTorch (thư viện OCR) phù hợp.
- Cài đặt tất cả các thư viện phụ thuộc khác.
- Khởi chạy ứng dụng.

*Lưu ý: Lần chạy đầu tiên có thể mất vài phút để tải và cài đặt các thư viện.*

## Hướng Dẫn Sử Dụng

### Giao Diện Chính
- Khi khởi động, một bong bóng nhỏ với chữ "V" sẽ xuất hiện.
- **Nhấp chuột** vào bong bóng để mở rộng bảng điều khiển đầy đủ.
- **Nhấn và kéo** bong bóng để di chuyển nó đến vị trí khác trên màn hình.

### Các Chức Năng Dịch
- **New Selection:** Nhấp vào đây để mở cửa sổ chọn vùng. Vẽ một hình chữ nhật trên khu vực bạn muốn dịch. Vùng này sẽ được lưu lại cho các lần dịch sau và cho chế độ tự động dịch.
- **Translate Full Screen:** Dịch toàn bộ màn hình.
- **Phím Tắt `+` (mặc định):** Kích hoạt chế độ "Snip". Vẽ một vùng và ứng dụng sẽ dịch ngay lập tức mà không lưu lại vùng chọn.
### Các phím tắt bản dịch có thể tùy chỉnh trong file json
- ** Mặc định: ** phím (`) kéo thả để dịch, phím (+) khi chọn xong vùng dịch nhấn để dịch, tổ hợp: alt + ctrl +f để dịch toàn bộ màn, phím (-) để xóa bản dịch
### Bảng Điều Khiển
- **Display:**
    - **Font Size:** Điều chỉnh kích thước chữ của kết quả dịch (đặt là 0 để tự động).
- **Auto Translate:**
    - **Enabled:** Bật/tắt chế độ tự động dịch cho vùng đã chọn (`New Selection`).
    - **Interval (s):** Đặt khoảng thời gian (giây) giữa các lần tự động dịch.
- **Configuration:**
    - **OCR Langs:** Nhập các mã ngôn ngữ bạn muốn OCR nhận dạng, cách nhau bởi dấu phẩy (ví dụ: `en,ja,ch_sim`), bạn có thể vào https://www.jaided.ai/easyocr để lấy đầy đủ mã ngôn ngữ được hỗ trợ.
    - **Translator:** Chọn dịch vụ dịch thuật bạn muốn sử dụng.
    - **API Keys & Models:** Nhập thông tin API key và tên model tương ứng với dịch vụ bạn chọn.
- **Custom Prompt:**
    - **Use Custom Prompt:** Bật tính năng này để sử dụng prompt của riêng bạn cho các dịch vụ AI.
    - **Hộp văn bản:** Viết prompt của bạn. Sử dụng `{text}` để chèn văn bản gốc và `{dest_lang}` để chèn ngôn ngữ đích.
- **Apply & Save Changes:** Nhấp vào nút này để lưu tất cả các thay đổi cấu hình và áp dụng chúng ngay lập tức.


### © 2025 ViVuCloud. Nếu bạn chia sẽ vui lòng giữ nguyên thông tin tác giả
### Nếu cần hỗ trợ bạn vui lòng liên hệ: https://www.facebook.com/VivuCloud
