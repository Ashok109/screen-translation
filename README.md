# Dich Man Hinh - Công Cụ Dịch Thuật Màn Hình

Đây là một công cụ dịch thuật mạnh mẽ và linh hoạt, cho phép bạn chụp ảnh một phần hoặc toàn bộ màn hình và dịch văn bản được nhận dạng ngay lập tức. Ứng dụng được xây dựng bằng PyQt5 và hỗ trợ nhiều dịch vụ (trong tương lại :v) OCR và dịch thuật khác nhau.


## Tính Năng Chính

- **Dịch Linh Hoạt:**
    - **Chụp và Dịch (Snip & Translate):** Dùng phím tắt để nhanh chóng chọn một vùng trên màn hình và dịch ngay lập tức.
    - **Dịch Vùng Cố Định:** Chọn một vùng cụ thể để dịch lặp đi lặp lại.
    - **Dịch Toàn Màn Hình:** Chụp và dịch toàn bộ nội dung hiển thị trên màn hình.
- **Tự Động Dịch Thông Minh:**
    - **Dịch Định Kỳ:** Tự động dịch lại vùng đã chọn hoặc toàn màn hình theo một khoảng thời gian tùy chỉnh.
- **Chế độ Dịch Phụ đề (Cải tiến):** Tối ưu hóa đặc biệt cho việc dịch phụ đề.
    - Giảm đáng kể hiện tượng chớp nháy, mang lại trải nghiệm xem mượt mà.
    - Tự động ẩn bản dịch khi không còn phụ đề trên màn hình, tránh che khuất nội dung.
    - Sử dụng bộ lọc thông minh để chỉ dịch khi phát hiện văn bản mới và có ý nghĩa.
- **Đọc văn bản dịch (Text-to-Speech):**
    - Tự động đọc kết quả dịch sau mỗi lần dịch thành công (trừ chế độ toàn màn hình).
    - Có thể bật/tắt dễ dàng trong bảng điều khiển.
- **Lọc Ngôn Ngữ Thông Minh (Tùy chọn):**
    - Tự động phát hiện ngôn ngữ của văn bản gốc để ngăn chặn các bản dịch sai từ kết quả OCR vô nghĩa.
    - Có thể **tắt/bật** bộ lọc này trong bảng điều khiển để dịch mọi văn bản mà OCR nhận dạng được, bất kể ngôn ngữ.
- **Hỗ trợ Đa Ngôn Ngữ Đích:**
    - Dễ dàng chọn ngôn ngữ đích từ danh sách các ngôn ngữ phổ biến.
    - Chuyển sang chế độ tùy chỉnh để nhập bất kỳ mã ngôn ngữ nào bạn muốn dịch sang.
- **Hỗ trợ Đa Dịch Vụ Dịch Thuật:**
    - **Google Translate** (mặc định, không cần API key)
    - **Gemini** (của Google)
    - **OpenRouter** (hỗ trợ nhiều mô hình AI)
    - **API Tùy Chỉnh** (tương thích với định dạng OpenAI)
- **Tùy Chỉnh Cao:**
- **Phím Tắt Toàn Diện:** Tùy chỉnh các phím tắt cho mọi chức năng dịch, bao gồm cả việc bật/tắt nhanh Chế độ Dịch Phụ đề (mặc định `Alt+Ctrl+S`).
- **Ngôn Ngữ OCR (Cải tiến):**
    - Giao diện chọn ngôn ngữ được thiết kế lại với menu thả xuống cho các ngôn ngữ/cặp ngôn ngữ phổ biến (Anh, Nhật, Trung, Hàn, Việt).
    - Dễ dàng chuyển sang chế độ tùy chỉnh để nhập nhiều ngôn ngữ khác theo nhu cầu.
- **Prompt Tùy Chỉnh:** Viết prompt riêng cho các mô hình AI để tinh chỉnh kết quả dịch.
- **Giao Diện Thân Thiện và Tiện Lợi:**
    - Bảng điều khiển nhỏ gọn, có thể di chuyển, mở rộng và luôn nằm trong màn hình.
    - Kết quả dịch được hiển thị ngay tại vị trí của văn bản gốc với tính năng "Lớp phủ thông minh".
    - Cửa sổ lịch sử dịch cho phép xem lại và có nút xóa nhanh.
    - Dễ dàng hủy vùng chọn đã thiết lập.
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

Chạy cập nhật tourh với GPU nvidia: pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

Cập nhật thư viện cần thiết: pip3 install -r requirements.txt

Khởi động ứng dụng: python main.py

---




Cả hai kịch bản sẽ tự động thực hiện tất cả các bước cần thiết:
- Tạo môi trường ảo (`.venv`) để tránh xung đột thư viện.
- **Tự động phát hiện GPU NVIDIA** và cài đặt phiên bản PyTorch (thư viện OCR) phù hợp.
- Cài đặt tất cả các thư viện phụ thuộc khác.
- Khởi chạy ứng dụng.

*Lưu ý: Lần chạy đầu tiên có thể mất vài phút để tải và cài đặt các thư viện.*

## Đóng Gói Thành File Thực Thi (.exe) (Tùy chọn KHÔNG ỔN ĐỊNH)

Dự án đã được cấu hình sẵn để bạn có thể tự đóng gói thành một tệp `.exe` duy nhất để dễ dàng phân phối và sử dụng.

1.  **Chạy file `build.bat`:**
    - Di chuyển đến thư mục dự án.
    - **Nhấp đúp** vào file `build.bat`.
2.  Kịch bản sẽ tự động cài đặt các thư viện cần thiết (bao gồm `pyinstaller`) và bắt đầu quá trình đóng gói. Quá trình này có thể mất từ 5-15 phút.
3.  Sau khi hoàn tất, bạn sẽ tìm thấy tệp `DichManHinh.exe` trong một thư mục mới có tên là `dist`.

**Lưu ý quan trọng khi chạy file `.exe`:**
- Lần đầu tiên bạn chạy file `.exe` và thực hiện một thao tác dịch, ứng dụng sẽ cần tải về các mô hình ngôn ngữ OCR cần thiết. Quá trình này yêu cầu kết nối internet và có thể mất vài phút.
- Các mô hình sẽ được lưu vào thư mục `model_dump` nằm cùng cấp với file `.exe`, và sẽ được tái sử dụng cho những lần chạy sau.

## Hướng Dẫn Sử Dụng

### Giao Diện Chính
- Khi khởi động, một bong bóng nhỏ với chữ "V" sẽ xuất hiện.
- **Nhấp chuột** vào bong bóng để mở rộng bảng điều khiển đầy đủ.
- **Nhấn và kéo** bong bóng để di chuyển nó đến vị trí khác trên màn hình.

### Các Chức Năng Dịch
- **New Selection (Vùng chọn mới):** Nhấp để vẽ một hình chữ nhật trên khu vực bạn muốn dịch. Vùng này sẽ được lưu lại cho các chế độ tự động.
- **Unselect Region (Hủy vùng chọn):** Nhấp để xóa vùng chọn hiện tại.
- **Translate Full Screen (Dịch toàn màn hình):** Dịch toàn bộ nội dung hiển thị.
- **Snip & Translate (Chụp và Dịch nhanh):** Sử dụng phím tắt (mặc định là `+`) để nhanh chóng chọn một vùng và dịch ngay lập tức mà không lưu lại vùng chọn.

### Bảng Điều Khiển
- **Display (Hiển thị):**
    - **Font Size (Cỡ chữ):** Điều chỉnh kích thước chữ của kết quả dịch (đặt là 0 để tự động).
    - **Smart Overlay (Lớp phủ thông minh):** Bật/tắt chế độ che văn bản gốc bằng màu nền đã phân tích.
- **Auto Translate (Tự động dịch):**
    - **Translate periodically (Dịch định kỳ):** Bật để tự động dịch lại vùng chọn/toàn màn hình cuối cùng.
    - **Subtitle mode (Chế độ phụ đề):** Bật để kích hoạt chế độ dịch phụ đề thông minh.
    - **Interval (s) (Chu kỳ (giây)):** Đặt khoảng thời gian chung cho cả hai chế độ tự động dịch.
- **History (Lịch sử):**
    - **Show History (Hiện lịch sử):** Mở cửa sổ xem lại lịch sử dịch. Cửa sổ này có nút `X` để xóa nhanh toàn bộ lịch sử.
- **Configuration (Cấu hình):**
    - **OCR Language:** Chọn ngôn ngữ/cặp ngôn ngữ phổ biến từ menu thả xuống, hoặc tích vào ô "Tùy chỉnh" để nhập các mã ngôn ngữ khác.
    - **Destination Language:** Chọn ngôn ngữ đích từ menu thả xuống, hoặc tích vào ô "Tùy chỉnh" để nhập mã ngôn ngữ bất kỳ.
    - **Translator:** Chọn dịch vụ dịch thuật bạn muốn sử dụng.
    - **API Keys & Models:** Nhập thông tin API key và tên model tương ứng với dịch vụ bạn chọn.
- **Image Preprocessing (Tiền xử lý ảnh):**
    - **Enable Language Filter:** Bật/tắt tính năng lọc ngôn ngữ thông minh.
- **Custom Prompt:**
    - **Use Custom Prompt:** Bật tính năng này để sử dụng prompt của riêng bạn cho các dịch vụ AI.
    - **Hộp văn bản:** Viết prompt của bạn. Sử dụng `{text}` để chèn văn bản gốc và `{dest_lang}` để chèn ngôn ngữ đích.
- **Apply & Save Changes:** Nhấp vào nút này để lưu tất cả các thay đổi cấu hình và áp dụng chúng ngay lập tức.


### © 2025 ViVuCloud. Nếu bạn chia sẽ vui lòng giữ nguyên thông tin tác giả
### Nếu cần hỗ trợ bạn vui lòng liên hệ: https://www.facebook.com/VivuCloud
