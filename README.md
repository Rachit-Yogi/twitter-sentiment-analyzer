
# X Sentiment Analyzer

A web application to analyze the sentiment of X posts using a Local machine learning model and Google's Gemini 2.0 Flash model. Built with a React frontend and Flask backend, it features a sleek black-and-white UI with Google Sans font, glowing text, and pie chart visualizations.

## 📖 Overview

The X Sentiment Analyzer allows users to input text from X posts and analyze their sentiment (Positive, Neutral, Negative) using two models:

- **Local Model**: A pre-trained machine learning model for sentiment analysis.
- **Gemini 2.0 Flash**: Google's latest free-tier model for advanced sentiment analysis.

> ❌ Due to persistent Twitter API rate limit and authentication issues, the app currently supports only text input mode.

The project was developed by **Rachit Yogi** as a demonstration of dual-model sentiment analysis with a modern UI.

## ✨ Features

- 🔁 **Dual-Model Sentiment Analysis**
- 🎨 **Modern UI**: Black-and-white theme, Google Sans font, glowing text, and animations
- 📊 **Visualization**: Pie charts with Chart.js
- 🔎 **Overall Sentiment**: Dominant sentiment from both models
- 🧼 **User-Friendly**: Simple interface with reset functionality
- 👤 **Credits**: Rachit Yogi (LinkedIn linked in footer)

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/x-sentiment-analyzer.git
cd x-sentiment-analyzer
```

### 2. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `/backend` and add your key:

```
GOOGLE_API_KEY=your-api-key-here
```

> ⚠️ **Note**: `model.pkl` and `vectorizer.pkl` are not included due to file size. Contact [Rachit Yogi](https://www.linkedin.com/in/rachit-yogi-71591b290) to get the files or replace with your own models.

### 3. Setup Frontend

```bash
cd ../frontend
npm install
```

---

## 🚀 Usage

### Run Backend

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

Starts Flask on: `http://localhost:5000`

### Run Frontend

```bash
cd frontend
npm start
```

Starts React on: `http://localhost:3000`

### Analyze Sentiment

1. Go to `http://localhost:3000`
2. Input any X post text (e.g., _“Elon’s doing it again 🚀🔥”_)
3. Click **Analyze Sentiment**
4. View the pie charts and final sentiment results

---

## 🖼️ Screenshots

> _Placeholder text — Replace with real screenshots_

- **Input Dashboard**





- **Dual-Model Analysis Results**

---

## 📁 Project Structure

```
x-sentiment-analyzer/
├── backend/
│   ├── app.py              # Flask server
│   ├── requirements.txt    # Python dependencies
│   └── .env                # API key
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # UI styling
│   │   └── index.js        # React root
│   ├── package.json
│   └── package-lock.json
├── presentation/
│   └── X_Sentiment_Analyzer_Presentation.tex
├── .gitignore
└── README.md
```

---

## 🧪 Challenges Faced

- ❌ **Twitter API Rate Limits**: Disabled URL-based input mode.
- 🔄 **Gemini API Access**: Free-tier access to Gemini 2.5 Pro paused. Using Gemini 2.0 Flash instead.

---

## 📈 Future Enhancements

- 🔗 Reinstate **URL-based tweet analysis** (pending X API fixes)
- ⚡ Upgrade to **Gemini 2.5 Pro**
- 🖼️ Support **Multimodal input** (images, videos)
- ☁️ Deploy on **Heroku / Vercel / AWS**
- 📬 Add **feedback-driven model improvement**

---

## 📚 References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Docs](https://reactjs.org/)
- [Gemini API Docs](https://ai.google.dev/)
- [Chart.js](https://www.chartjs.org/)
- [Google AI Blog, Feb 2025](https://ai.google.dev/)
- [Ars Technica, Mar 2025](https://arstechnica.com/)
- [@OfficialLoganK on X, May 13, 2025](https://x.com)

---

## 👤 Author

**Rachit Yogi**  
📎 [LinkedIn](https://www.linkedin.com/in/rachit-yogi-71591b290)  
🧠 Passionate about AI, ML, and building intelligent interfaces.

