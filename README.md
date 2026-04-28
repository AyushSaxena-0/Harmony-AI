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

🩺 Skin Detection Output

🚨 SOS Gesture Detection

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

Add output samples or logs

[Sample Outputs Link](https://your-results-link.com)
📈 Model Performance (Replace with real data)
Module	Metric	Value
Chatbot	Sentiment Acc	XX%
Skin Detection	Accuracy	XX%
Gesture System	Latency	XX ms
🔐 Production Considerations
Modular architecture for scaling
Can be containerized (Docker-ready structure)
Supports real-time inference
Requires proper API layer for deployment
🐳 Deployment (Planned)
docker build -t harmony-ai .
docker run -p 8000:8000 harmony-ai
🚧 Limitations
No API layer yet
Dataset dependency
Limited real-world validation
No alert integration (SMS/GPS)
🔮 Future Work
FastAPI backend
Real-time alert system
Model optimization
Web dashboard
MLOps pipeline
👨‍💻 Author

Ayush Saxena

📜 License

MIT License

⚠️ Disclaimer

This project is not a substitute for professional medical or psychological advice.
