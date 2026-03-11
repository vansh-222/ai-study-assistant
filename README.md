# 🎓 AI Study Assistant

An AI-powered study assistant that extracts text from PDFs and generates **predicted questions**, **flashcards**, **study plans**, and **mock tests** using OpenAI GPT-4.

---

## 🚀 Features

- 📄 Upload PDF and extract text automatically
- 🤖 AI generates study content using GPT-4
- 📝 Predicted exam questions
- 🃏 Flashcards (question + answer)
- 📅 7-day study plan
- 📋 Mock test with MCQs
- 💾 Save all results in MongoDB
- 🎨 Clean React frontend with Tailwind CSS

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React.js + Tailwind CSS |
| Backend | Node.js + Express.js |
| Database | MongoDB + Mongoose |
| AI | OpenAI GPT-4 API |
| PDF Parsing | pdf-parse |
| File Upload | Multer |

---

## 📁 Project Structure

```
ai-study-assistant/
├── client/                  # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadPDF.jsx
│   │   │   ├── Flashcards.jsx
│   │   │   ├── MockTest.jsx
│   │   │   ├── StudyPlan.jsx
│   │   │   └── Questions.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   └── Result.jsx
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
│
├── server/                  # Node.js Backend
│   ├── controllers/
│   │   └── pdfController.js
│   ├── models/
│   │   └── StudyData.js
│   ├── routes/
│   │   └── upload.js
│   ├── utils/
│   │   └── aiHelper.js
│   ├── uploads/             # Temporary PDF storage
│   ├── index.js
│   └── package.json
│
├── .env.example
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Node.js >= 18
- MongoDB (local or Atlas)
- OpenAI API Key

### 1. Clone the repository
```bash
git clone https://github.com/vansh-222/ai-study-assistant.git
cd ai-study-assistant
```

### 2. Setup Backend
```bash
cd server
npm install
cp ../.env.example .env
# Fill in your .env values
npm start
```

### 3. Setup Frontend
```bash
cd client
npm install
npm start
```

### 4. Environment Variables
Create a `.env` file inside the `server/` folder:
```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/ai-study-assistant
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload PDF and get AI-generated study content |
| GET | `/api/results` | Get all saved study results |
| GET | `/api/results/:id` | Get a specific result by ID |

---

## 🎯 How It Works

1. Student uploads a PDF via the frontend
2. Backend extracts text using `pdf-parse`
3. Extracted text is sent to OpenAI GPT-4
4. AI returns JSON with questions, flashcards, study plan & mock test
5. Data is saved in MongoDB
6. Frontend displays all study content beautifully

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

MIT License - feel free to use this project for learning and building!

---

⭐ **Star this repo if it helped you!**