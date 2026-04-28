🧠 Harmony AI

A Multi-Modal AI System for Emotional, Physical & Social Well-being

🚀 Overview

I built Harmony AI as a modular AI system that integrates:

🧠 Emotional intelligence (chatbot + sentiment analysis)
🩺 Physical health detection (skin analysis via images)
🚨 Social safety (real-time SOS gesture recognition)

Each module is independently executable and designed to be scalable into production services.

🎥 Demo
🔗 Live Demo / Video Walkthrough

Demo link https://drive.google.com/drive/folders/1U7Hn9t8m47F8B79jV7y6IzSizO6BJf3y?usp=sharing 

📸 Screenshots
🧠 Chatbot Interface
<img width="1919" height="1024" alt="image" src="https://github.com/user-attachments/assets/5b2bf7b8-bb44-4cbf-9af8-bf27e4727ab6" />


🩺 Skin Detection Output
<img width="1919" height="1020" alt="image" src="https://github.com/user-attachments/assets/b46d6fd4-40e3-4c0e-a6f7-2922d2add796" />

🚨 SOS Gesture Detection
<img width="1919" height="1018" alt="image" src="https://github.com/user-attachments/assets/14c80aac-62f2-4957-a328-f14533160f6c" />


🧩 System UI (if applicable)

🧩 System Architecture
                ┌────────────────────┐
                │   User Interface   │
                └────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Chat Module  │ │ Skin Module  │ │ Gesture Mod  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
 NLP Pipeline     CNN Pipeline     CV Pipeline
       │                │                │
       └──────────┬─────┴─────┬──────────┘
                  ▼           ▼
         Response Engine / Alert System
🗂️ Project Structure
Harmony-AI/
│── chatbot.py
│── skin_detector.py
│── detector.py
│── main.py
│── ui.py
│── requirements.txt
│── assets/              # Store screenshots here

⚙️ Core Modules
🧠 Chatbot
NLP-based interaction
Sentiment-aware responses
Context handling
🩺 Skin Detection
Image preprocessing
CNN-based classification
Prediction output
🚨 Gesture Detection
Real-time video processing
Hand landmark detection
SOS gesture classification
🛠️ Tech Stack
Python
OpenCV, MediaPipe
TensorFlow / PyTorch
NLP libraries (Transformers / NLTK)
📦 Installation
git clone https://github.com/your-username/harmony-ai.git
cd harmony-ai

pip install -r requirements.txt
▶️ Usage
python main.py

Or run modules individually:

python chatbot.py
python skin_detector.py
python detector.py
📊 Results & Outputs
🔗 Sample Outputs
<img width="1919" height="1018" alt="image" src="https://github.com/user-attachments/assets/14c80aac-62f2-4957-a328-f14533160f6c" />

📈 Model Performance

Note: Metrics are based on current prototype evaluation and limited testing. Full benchmark evaluation is in progress.

Module	Metric	Value
Chatbot	Sentiment Accuracy	~82% (on sample test set)
Skin Detection	Classification Accuracy	~78% (dataset-dependent)
Gesture System	Detection Latency	~70–90 ms per frame
🔐 Production Considerations
Designed with modular architecture, allowing each service to scale independently
Codebase is structured to support containerization (Docker-ready)
Supports near real-time inference for gesture and image processing
Requires a dedicated API layer (FastAPI/Flask) for production deployment
Logging, monitoring, and model versioning are not yet implemented
🐳 Deployment (Planned)
docker build -t harmony-ai .
docker run -p 8000:8000 harmony-ai

Note: Containerization structure is planned; production-ready Docker setup is not fully implemented yet.

🚧 Limitations
No API layer (currently script-based execution)
Model performance heavily dependent on dataset quality
Limited real-world validation and testing
No real-time alert integration (SMS/GPS)
No CI/CD pipeline or monitoring
🔮 Future Work
Develop FastAPI-based backend for service exposure
Integrate real-time alert system (Twilio/GPS APIs)
Improve model accuracy with larger datasets
Add logging, monitoring, and model versioning (MLOps)
Build a web-based dashboard (React + backend API)
👨‍💻 Author

Ayush Saxena

📜 License

MIT License

⚠️ Disclaimer

This project is not a substitute for professional medical or psychological advice.
