# 📦 Hướng Dẫn Push GitHub & Build APK Local

## 🎯 Tổng Quan

Hướng dẫn này giúp bạn:
1. Push code từ Replit lên GitHub
2. Clone về máy local
3. Build APK Android bằng VS Code/Android Studio

---

## 📂 BƯỚC 1: Push Code Lên GitHub

### Option 1: Dùng Replit Git (Dễ nhất)

#### 1.1. Tạo GitHub Repository

1. Vào [GitHub.com](https://github.com) → Click **"New Repository"**
2. Đặt tên: `imageforge-ai-photo-editor`
3. Chọn **Private** (khuyên dùng) hoặc Public
4. **KHÔNG** check "Initialize with README" (đã có sẵn)
5. Click **"Create Repository"**

#### 1.2. Kết Nối Replit với GitHub

**Trong Replit:**

1. Mở **Tools** panel (bên trái)
2. Click vào **Git** (hoặc nhấn Ctrl+Shift+G)
3. Click **"Connect to GitHub"**
4. Authorize Replit → Chọn repo vừa tạo
5. Click **"Connect"**

#### 1.3. Commit & Push

```bash
# Trong Replit Shell
git add .
git commit -m "Initial commit: Flutter app + Flask API complete"
git push origin main
```

**Hoặc dùng UI:**
- Tab Git → Stage all changes
- Write commit message
- Click "Commit & Push"

### Option 2: Dùng Command Line

```bash
# 1. Khởi tạo git (nếu chưa có)
git init

# 2. Add remote (thay YOUR_USERNAME và YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/imageforge-ai-photo-editor.git

# 3. Add files
git add .

# 4. Commit
git commit -m "Initial commit: Flutter app + Flask API"

# 5. Push
git branch -M main
git push -u origin main
```

**Nếu cần xác thực:**
- Username: Tên GitHub của bạn
- Password: Dùng **Personal Access Token** (không phải password)
  - Tạo token: GitHub → Settings → Developer settings → Personal access tokens → Generate new token
  - Scope cần: `repo` (full control)

---

## 💻 BƯỚC 2: Clone Về Máy Local

### 2.1. Cài Đặt Git (nếu chưa có)

**Windows:**
```bash
# Download từ: https://git-scm.com/download/win
```

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt-get install git
```

### 2.2. Clone Repository

```bash
# Mở Terminal/CMD tại thư mục muốn lưu code
cd ~/Projects  # Hoặc thư mục bất kỳ

# Clone repo
git clone https://github.com/YOUR_USERNAME/imageforge-ai-photo-editor.git

# Di chuyển vào project
cd imageforge-ai-photo-editor
```

---

## 📱 BƯỚC 3: Setup Flutter Local

### 3.1. Cài Flutter SDK

**Windows:**
1. Download: https://docs.flutter.dev/get-started/install/windows
2. Giải nén vào `C:\flutter`
3. Thêm vào PATH: `C:\flutter\bin`

**macOS:**
```bash
# Dùng Homebrew
brew install flutter

# Hoặc download manual từ: https://docs.flutter.dev/get-started/install/macos
```

**Linux:**
```bash
# Download từ: https://docs.flutter.dev/get-started/install/linux
sudo snap install flutter --classic
```

### 3.2. Kiểm Tra Flutter

```bash
flutter doctor
```

**Fix các lỗi thường gặp:**

✅ **Android toolchain:**
```bash
# Cài Android Studio: https://developer.android.com/studio
# Mở Android Studio → Settings → SDK Manager
# Install: Android SDK, Android SDK Platform-Tools, Android SDK Build-Tools
```

✅ **Android licenses:**
```bash
flutter doctor --android-licenses
# Nhấn 'y' để accept all
```

✅ **VS Code/Android Studio:**
```bash
# Install Flutter extension trong VS Code
# Hoặc dùng Android Studio với Flutter plugin
```

### 3.3. Setup Project Dependencies

```bash
# Di chuyển vào Flutter app
cd flutter_app

# Install dependencies
flutter pub get

# Verify
flutter doctor -v
```

---

## 🔧 BƯỚC 4: Build APK

### Option 1: Command Line (Nhanh)

```bash
# Di chuyển vào Flutter app
cd flutter_app

# Build APK Release
flutter build apk --release

# APK output:
# build/app/outputs/flutter-apk/app-release.apk
```

**Variations:**

```bash
# Build APK for specific ABI (nhẹ hơn)
flutter build apk --release --target-platform android-arm64

# Build App Bundle (Google Play)
flutter build appbundle --release

# Build Debug APK (for testing)
flutter build apk --debug
```

### Option 2: Android Studio (UI)

1. Mở Android Studio
2. **File** → **Open** → Chọn thư mục `flutter_app`
3. Đợi Gradle sync xong
4. **Build** → **Flutter** → **Build APK**
5. APK ở: `build/app/outputs/flutter-apk/app-release.apk`

### Option 3: VS Code

1. Mở VS Code → Open folder `flutter_app`
2. **Terminal** → New Terminal
3. Run:
   ```bash
   flutter build apk --release
   ```

---

## 🎯 BƯỚC 5: Test APK

### 5.1. Test trên Emulator

```bash
# List emulators
flutter emulators

# Start emulator
flutter emulators --launch <emulator_id>

# Install & run
flutter install
```

### 5.2. Test trên Physical Device

**Android:**
1. Bật **Developer Options** trên điện thoại
2. Bật **USB Debugging**
3. Kết nối USB → Trust computer
4. Transfer file `app-release.apk` vào phone
5. Install APK
6. Hoặc: `flutter install`

**Test checklist:**
- [ ] App mở thành công
- [ ] Home screen hiển thị 11 features
- [ ] Image picker hoạt động
- [ ] API connection OK (test 1 feature)
- [ ] Result hiển thị đúng

---

## 🔐 BƯỚC 6: Security Check

### 6.1. Kiểm Tra Secrets

**⚠️ QUAN TRỌNG:** Đảm bảo KHÔNG commit secrets!

```bash
# Check .gitignore có .env chưa
cat .gitignore | grep .env
# Phải có dòng: .env

# Verify .env không trong Git
git ls-files | grep .env
# Không có output = OK
```

### 6.2. Secrets Cần Thiết

**Backend (.env):**
```
REPLICATE_API_TOKEN=r8_xxx...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...
```

**⚠️ KHÔNG commit những secrets này!**

**Khi teammate clone:**
1. Copy `.env.example` → `.env`
2. Điền secrets riêng của họ
3. KHÔNG share secrets qua Git

---

## 📝 BƯỚC 7: Workflow Development

### 7.1. Khi Code Trên Local

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create branch cho feature mới
git checkout -b feature/new-ai-effect

# 3. Code & test
flutter run

# 4. Commit changes
git add .
git commit -m "Add new AI effect feature"

# 5. Push branch
git push origin feature/new-ai-effect

# 6. Tạo Pull Request trên GitHub
```

### 7.2. Khi Deploy Backend

**Backend vẫn chạy trên Replit Production:**
- URL: `https://aiforce-onenearcelo.replit.app`
- Auto-deploy khi push code lên Replit

**Local development:**
- Run backend local: `python app.py`
- Update Flutter config: `baseUrl = 'http://localhost:5000'`
- Test local trước khi push

---

## 🚀 BƯỚC 8: Release APK

### 8.1. Tăng Version

**File:** `flutter_app/pubspec.yaml`
```yaml
version: 1.0.1+2  # Tăng số này mỗi release
```

### 8.2. Build Signed APK

**Tạo keystore (lần đầu):**
```bash
keytool -genkey -v -keystore ~/release-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias release
```

**File:** `flutter_app/android/key.properties`
```properties
storePassword=your_password
keyPassword=your_password
keyAlias=release
storeFile=/path/to/release-keystore.jks
```

**Build:**
```bash
flutter build apk --release
# Output: app-release.apk (signed)
```

### 8.3. Upload lên GitHub Release

```bash
# Tag version
git tag v1.0.1
git push origin v1.0.1

# GitHub → Releases → Create new release
# Upload app-release.apk
```

---

## 📊 Project Structure Local

```
imageforge-ai-photo-editor/
├── flutter_app/              # Flutter mobile app
│   ├── android/              # Android config
│   ├── ios/                  # iOS config
│   ├── lib/                  # Dart source code
│   ├── pubspec.yaml          # Dependencies
│   └── build/                # Build output (gitignored)
├── app.py                    # Flask backend (chạy trên Replit)
├── routes/                   # API routes
├── utils/                    # Backend utilities
├── static/                   # Web UI
├── .env.example              # Example env vars
├── .gitignore                # Git ignore
└── README.md                 # Documentation
```

---

## ✅ Checklist Trước Khi Build

- [ ] Flutter SDK cài đặt (`flutter doctor`)
- [ ] Android Studio/toolchain setup
- [ ] Git clone project thành công
- [ ] `flutter pub get` chạy OK
- [ ] API URL đã đúng (`api_config.dart`)
- [ ] Test app trên emulator/device
- [ ] Build APK thành công
- [ ] APK install & run OK

---

## 🐛 Troubleshooting

### ❌ "Flutter not found"
```bash
# Thêm Flutter vào PATH
export PATH="$PATH:`pwd`/flutter/bin"  # macOS/Linux
# Hoặc thêm vào System Environment Variables (Windows)
```

### ❌ "Gradle build failed"
```bash
# Clean build
cd flutter_app
flutter clean
flutter pub get
flutter build apk --release
```

### ❌ "Android licenses not accepted"
```bash
flutter doctor --android-licenses
# Nhấn 'y' cho tất cả
```

### ❌ "Cannot connect to backend"
```bash
# Kiểm tra API URL trong api_config.dart
# Phải là: https://aiforce-onenearcelo.replit.app
# Không dùng localhost khi build APK
```

---

## 📚 Tài Liệu Thêm

- 📱 [Flutter Docs](https://docs.flutter.dev)
- 🤖 [Android Studio Setup](https://developer.android.com/studio)
- 🔧 [Flutter Build APK Guide](https://docs.flutter.dev/deployment/android)
- 🐙 [GitHub Docs](https://docs.github.com)

---

## 🎊 Tóm Tắt

**Push GitHub:**
```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/repo.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

**Clone & Build:**
```bash
git clone https://github.com/YOUR_USERNAME/repo.git
cd repo/flutter_app
flutter pub get
flutter build apk --release
```

**APK Output:**
```
flutter_app/build/app/outputs/flutter-apk/app-release.apk
```

---

**🎉 Bây giờ bạn có thể push code lên GitHub và build APK local rồi!**
