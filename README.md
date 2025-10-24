# Smart Attendance System

A face recognition-based attendance system built with Flask and OpenCV that automatically marks student attendance by recognizing faces in real-time.

## 📋 Features

- **Face Recognition**: Automatically detects and recognizes student faces using OpenCV's LBPH (Local Binary Patterns Histograms) algorithm
- **Web Interface**: User-friendly Flask web application with login authentication
- **Student Management**: Add new students to the system by capturing their face data
- **Automatic Attendance**: Mark attendance by scanning faces in real-time
- **CSV Export**: Generate timestamped attendance reports in CSV format
- **Database Integration**: SQLite database to store student information and attendance records

## 🛠️ Technologies Used

- **Python 3.10**
- **Flask** - Web framework
- **OpenCV** - Face detection and recognition
- **SQLite** - Database management
- **Pandas** - Data manipulation and CSV export
- **OpenPyXL** - Excel file handling

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Webcam/Camera access
- pip or pipenv

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart_attendance_system.git
   cd smart_attendance_system
   ```

2. **Install dependencies**

   Using pip:
   ```bash
   pip install -r requirements.txt
   ```

   Using pipenv:
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Initialize the database**
   ```bash
   python -c "import sqlite3; conn = sqlite3.connect('database.db'); conn.execute('CREATE TABLE IF NOT EXISTS students_details (name TEXT, roll_no TEXT)'); conn.close()"
   ```

4. **Create necessary directories**
   ```bash
   mkdir datasets attendance_sheets
   ```

## 🚀 Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Access the web interface**
   - Open your browser and navigate to `http://localhost:5000`
   - Login credentials:
     - Username: `ngit`
     - Password: `password`

3. **Add Students**
   - Click on "Add Student" button
   - Enter student name and roll number
   - Position yourself in front of the camera
   - The system will capture 100 images of your face
   - Wait for the confirmation message

4. **Mark Attendance**
   - Click on "Mark Attendance" button
   - Position yourself in front of the camera
   - The system will recognize your face and mark you as present
   - Attendance sheet will be generated automatically in the `attendance_sheets` folder

## 📁 Project Structure

```
smart_attendance_system/
├── app.py                      # Main Flask application
├── database.db                 # SQLite database
├── requirements.txt            # Python dependencies
├── Pipfile                     # Pipenv configuration
├── datasets/                   # Student face images directory
│   ├── 034/                   # Roll number folders
│   ├── 037/
│   └── ...
├── attendance_sheets/          # Generated attendance CSV files
├── static/                     # Static files (CSS, images)
│   ├── css/
│   └── images/
└── templates/                  # HTML templates
    ├── base.html
    ├── index.html
    ├── login.html
    ├── attendance.html
    └── create__student_db.html
```

## 🔧 Configuration

### Default Credentials
- **Username**: `ngit`
- **Password**: `password`

To change the login credentials, edit the `login()` function in `app.py`:
```python
if username == 'your_username' and password == 'your_password':
```

### Camera Settings
The system uses the default camera (index 0). To use a different camera, modify:
```python
camera = cv2.VideoCapture(0)  # Change index for different camera
```

## 📊 Database Schema

### students_details table
| Column | Type | Description |
|--------|------|-------------|
| name | TEXT | Student's full name |
| roll_no | TEXT | Student's roll number |

## 🎯 How It Works

1. **Training Phase**: When adding a student, the system captures 100 face images from the webcam
2. **Storage**: Images are stored in `datasets/roll_number/` directory
3. **Recognition**: During attendance, the system:
   - Loads all face images from the datasets folder
   - Trains the LBPH face recognizer model
   - Detects faces in real-time using Haar Cascade classifier
   - Matches detected faces with trained data
   - Marks students as present/absent
4. **Export**: Generates a CSV file with attendance records

## ⚠️ Limitations

- Requires good lighting conditions for optimal face recognition
- Single face detection at a time
- Accuracy depends on camera quality and face angle
- No multi-face simultaneous detection in current version

## 🔮 Future Enhancements

- [ ] Multiple face detection in a single frame
- [ ] Attendance viewing dashboard
- [ ] Email notifications for attendance reports
- [ ] Login encryption and secure authentication
- [ ] Subject-wise attendance tracking
- [ ] Automated attendance scheduling with DAGs
- [ ] Improved UI/UX design
- [ ] Real-time video feed during attendance marking

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created as part of MSCS Projects - Smart Attendance System

## 📧 Support

For issues and questions, please open an issue on the GitHub repository.

