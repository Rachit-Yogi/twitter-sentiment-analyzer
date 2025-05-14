import React, { useState } from 'react';
import axios from 'axios';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import './App.css';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

function App() {
  const [inputMode, setInputMode] = useState('url');
  const [tweetUrl, setTweetUrl] = useState('');
  const [tweetText, setTweetText] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (inputMode === 'url' && !tweetUrl.trim()) {
      setError('Please enter a valid tweet URL');
      return;
    }
    if (inputMode === 'text' && !tweetText.trim()) {
      setError('Please enter tweet text');
      return;
    }
    setError('');
    setResult(null);
    setLoading(true);

    try {
      const endpoint = inputMode === 'url' ? '/analyze' : '/analyze-text';
      const payload = inputMode === 'url' ? { tweetUrl } : { tweetText };
      const response = await axios.post(`http://localhost:5000${endpoint}`, payload, {
        timeout: 20000
      });
      setResult(response.data);
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.code === 'ECONNABORTED'
        ? 'Request timed out. Try pasting the tweet text directly.'
        : 'An error occurred. Please try again.';
      setError(errorMsg);
      if (errorMsg.includes('rate limit exceeded') || errorMsg.includes('timed out')) {
        setInputMode('text');
        setTweetUrl('');
      }
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setTweetUrl('');
    setTweetText('');
    setResult(null);
    setError('');
    setInputMode('url');
  };

  // Pie chart data for Local Model
  const localChartData = result?.local_sentiment
    ? {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [
          {
            data: [
              result.local_sentiment.positive,
              result.local_sentiment.neutral,
              result.local_sentiment.negative,
            ],
            backgroundColor: ['#34D399', '#60A5FA', '#F87171'],
            borderColor: ['#000', '#000', '#000'],
            borderWidth: 1,
          },
        ],
      }
    : null;

  // Pie chart data for Gemini Model
  const geminiChartData = result?.gemini_sentiment?.text_sentiment
    ? {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [
          {
            data: [
              result.gemini_sentiment.text_sentiment.positive,
              result.gemini_sentiment.text_sentiment.neutral,
              result.gemini_sentiment.text_sentiment.negative,
            ],
            backgroundColor: ['#34D399', '#60A5FA', '#F87171'],
            borderColor: ['#000', '#000', '#000'],
            borderWidth: 1,
          },
        ],
      }
    : null;

  const chartOptions = {
    plugins: {
      legend: {
        labels: {
          color: '#fff',
          font: {
            size: 14,
            family: 'Google Sans',
          },
        },
      },
    },
    maintainAspectRatio: false,
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-between p-6">
      <div className="w-full max-w-2xl">
        <h1 className="text-5xl font-bold text-center mb-2 text-white glow-text">
          X Sentiment Analyzer
        </h1>
        <p className="text-center text-gray-400 mb-8">
          Powered by Local & Gemini Model
        </p>

        {/* Input Mode Toggle */}
        <div className="flex justify-center space-x-4 mb-8">
          <button
            onClick={() => setInputMode('url')}
            className={`px-6 py-3 rounded-lg font-medium transition-all border-2 text-black ${
              inputMode === 'url'
                ? 'border-white glow-border bg-white'
                : 'border-gray-600 bg-gray-800 hover:border-gray-400 hover:scale-105'
            }`}
          >
            Tweet URL
          </button>
          <button
            onClick={() => setInputMode('text')}
            className={`px-6 py-3 rounded-lg font-medium transition-all border-2 text-black ${
              inputMode === 'text'
                ? 'border-white glow-border bg-white'
                : 'border-gray-600 bg-gray-800 hover:border-gray-400 hover:scale-105'
            }`}
          >
            Tweet Text
          </button>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="bg-gray-900 p-6 rounded-lg mb-6 border border-gray-700">
          {inputMode === 'url' ? (
            <input
              type="text"
              value={tweetUrl}
              onChange={(e) => setTweetUrl(e.target.value)}
              placeholder="Enter Tweet URL (e.g., https://x.com/user/status/123)"
              className="w-full p-4 rounded-xl bg-black text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-white glow-border text-lg fancy-input mb-4"
              disabled={loading}
            />
          ) : (
            <textarea
              value={tweetText}
              onChange={(e) => setTweetText(e.target.value)}
              placeholder="Paste tweet text here"
              className="w-full p-4 rounded-xl bg-black text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-white glow-border text-lg fancy-input mb-4 resize-none"
              rows="6"
              disabled={loading}
            />
          )}
          <button
            type="submit"
            disabled={loading || (inputMode === 'url' && !tweetUrl.trim()) || (inputMode === 'text' && !tweetText.trim())}
            className={`w-full p-4 rounded-xl font-medium transition-all border-2 text-black ${
              loading || (inputMode === 'url' && !tweetUrl.trim()) || (inputMode === 'text' && !tweetText.trim())
                ? 'border-gray-600 bg-gray-800 cursor-not-allowed'
                : 'border-white glow-border bg-white hover:scale-105'
            }`}
          >
            {loading ? 'Analyzing...' : 'Analyze Sentiment'}
          </button>
        </form>

        {/* Error Message */}
        {error && (
          <p className="mb-6 text-red-400 text-center glow-text">
            {error}
          </p>
        )}

        {/* Results */}
        {result && (
          <div className="bg-gray-900 p-6 rounded-lg border border-gray-700 fade-in">
            <h2 className="text-3xl font-semibold text-center mb-6 text-white glow-text">
              Analysis Results
            </h2>
            <div className="mb-6">
              <p className="text-gray-300 break-words text-center">{result.text}</p>
            </div>

            {/* Sentiment Results */}
            <div className="space-y-8">
              {result.local_sentiment && (
                <div>
                  <h3 className="text-2xl font-medium text-center mb-2 text-white glow-text">
                    Local Model Sentiment
                  </h3>
                  {result.local_overall_sentiment && (
                    <p className="text-3xl font-bold text-center text-white glow-text overall-sentiment mb-4">
                      Overall: {result.local_overall_sentiment}
                    </p>
                  )}
                  <div className="flex justify-center">
                    <div className="w-64 h-64">
                      <Pie data={localChartData} options={chartOptions} />
                    </div>
                  </div>
                </div>
              )}
              {result.gemini_sentiment?.text_sentiment && !result.gemini_sentiment.error && (
                <div>
                  <h3 className="text-2xl font-medium text-center mb-2 text-white glow-text">
                    Gemini Model Sentiment
                  </h3>
                  {result.gemini_overall_sentiment && (
                    <p className="text-3xl font-bold text-center text-white glow-text overall-sentiment mb-4">
                      Overall: {result.gemini_overall_sentiment}
                    </p>
                  )}
                  <div className="flex justify-center">
                    <div className="w-64 h-64">
                      <Pie data={geminiChartData} options={chartOptions} />
                    </div>
                  </div>
                </div>
              )}
              {result.gemini_sentiment?.error && (
                <p className="mt-4 text-yellow-400 text-center glow-text">
                  Gemini Analysis Unavailable: {result.gemini_sentiment.error}
                </p>
              )}
            </div>

            {/* Next Button */}
            <button
              onClick={clearForm}
              className="mt-8 w-full p-4 rounded-xl font-medium transition-all border-2 border-white glow-border bg-white text-black hover:scale-105"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Project Credit Footer */}
      <footer className="mt-8 text-center">
        <p className="text-gray-400 text-lg">
          Project made by{' '}
          <a
            href="https://www.linkedin.com/in/rachit-yogi-71591b290"
            target="_blank"
            rel="noopener noreferrer"
            className="text-white glow-text hover:underline"
          >
            Rachit Yogi
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;