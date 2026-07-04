# 🎤 AI Mock Interview App

An AI-powered mock interview application built using **Streamlit**, **Groq API**, and **JSON**. The app simulates realistic interview experiences by asking role-specific questions, evaluating user responses, and providing constructive feedback to help users improve their interview skills.

---

## 🚀 Features

- 🤖 AI-powered mock interview sessions
- 🔑 Bring Your Own Groq API Key
- 💬 Interactive chat-based interview experience
- 📋 Role-specific interview questions
- 🧠 AI-generated feedback on every response
- ⭐ Performance evaluation and improvement suggestions
- 📂 JSON-based question and interview management
- ⚡ Fast responses powered by Groq's Llama models
- 🎨 Clean and intuitive Streamlit interface

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Groq API
- JSON

---

## 📂 Project Structure

```text
.
├── app.py
├── interview_questions.json
├── requirements.txt
├── README.md
└── .env (optional)
```

> Modify the project structure above if your repository contains additional files.

---

## ▶️ Running the Application

Launch the Streamlit application:

```bash
streamlit run app.py
```

---

## 💡 How It Works

1. Enter your Groq API key.
2. Select your desired interview role or domain.
3. The AI begins asking interview questions one at a time.
4. Respond to each question naturally.
5. Receive AI-generated feedback and suggestions after each answer.
6. Continue until the interview is complete.

---

## 🔄 Workflow

```text
User
 │
 ▼
Enter Groq API Key
 │
 ▼
Choose Interview Role
 │
 ▼
Load Questions (JSON)
 │
 ▼
AI Conducts Interview
 │
 ▼
User Answers
 │
 ▼
Groq AI Evaluation
 │
 ▼
Feedback & Suggestions
```

---

## 💬 Sample Interview Roles

- Software Engineer
- Data Analyst
- Data Scientist
- Frontend Developer
- Backend Developer
- Full Stack Developer
- Product Manager
- Business Analyst
- Marketing Executive
- Human Resources

---

## ✨ Key Highlights

- Personalized interview experience
- Realistic AI-generated interview questions
- Constructive feedback for every response
- Lightweight and responsive Streamlit interface
- Easily extensible by updating the JSON question bank
- Supports multiple interview domains

---

## 🔒 Security

Users provide their own Groq API key during runtime. The application uses the key only for the active session and does **not** store API credentials.

---

## 🌟 Future Enhancements

- Voice-based interviews
- Resume-based personalized questions
- Difficulty level selection
- Technical coding interviews
- Behavioral interview mode
- Interview scorecard with detailed analytics
- PDF report generation
- Interview history dashboard

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Built with ❤️ using **Python**, **Streamlit**, **Groq API**, and **JSON**.
