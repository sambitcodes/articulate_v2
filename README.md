# articulAIte - AI-Powered Assistant

An advanced Streamlit-based web application that leverages LangChain and Groq API to provide comprehensive career development assistance across four specialized domains.

## 🌟 Features Overview

### 📄 Tab 1: CV Analysis & Interview Preparation
- **Upload and analyze** your CV/Resume (PDF, DOCX, or TXT)
- **Get personalized interview questions** based on your experience
- **Receive skill highlighting suggestions** for interviews
- **Add job descriptions** for targeted preparation
- **Chat-enabled** for deep-dive discussions with career coach

**Supported Models:**
- Groq Compound (Default - for company-specific web research)
- OpenAI GPT-OSS-120B
- Llama 3.3 70B
- Kimi K2 Instruct
- Groq Compound Mini (latency-optimized version)

### 💻 Tab 2: Code Explainer & Problem Solver
- **Line-by-line code explanations** for any programming language
- **Error detection and fixing** with detailed explanations
- **Code optimization suggestions** for performance and readability
- **Coding problem solutions** with step-by-step guidance
- **Interactive chat** for technical discussions

**Supported Models:**
- Groq Compound (Default - for code execution and iterative debugging)
- OpenAI GPT-OSS-120B
- Llama 4 Maverick 17B
- Kimi K2 Instruct
- Groq Compound Mini (latency-optimized version)

### 📝 Tab 3: Article Generator
- **Create well-researched articles** on any topic
- **Control word count** (100-5000 words)
- **Choose writing styles**: Academic, Casual, Professional, Technical, Journalistic, Creative
- **Manage creativity levels** for different tones
- **Get publication-ready formatted content**

**Supported Models:**
- Groq Compound (Default - with web search and synthesis)
- Groq Compound Mini (latency-optimized version)
- OpenAI GPT-OSS-120B
- Llama 3.3 70B
- Kimi K2 Instruct

### 📚 Tab 4: Study Plan Generator
- **Create personalized study plans** for any subject
- **Get week-by-week learning schedules** with realistic timelines
- **Find recommended resources and materials**
- **Receive time estimates and progress tracking metrics**
- **Chat with study mentor** for customization

**Supported Models:**
- Groq Compound Mini (Default - for latency-sensitive tasks)
- OpenAI GPT-OSS-120B
- Llama 3.3 70B 
- Kimi K2 Instruct

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Groq API key (get one from https://console.groq.com)
- Git (for version control)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/articulAIte.git
cd articulAIte
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_groq_api_key_here
```

5. **Run the application:**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📁 Project Structure

```
articulAIte/
├── app.py                          # Main Streamlit application entry point
├── config.py                       # Configuration, models, and constants
├── requirements.txt                # Python dependencies
├── .env.example                    # Example environment file
├── .gitignore                      # Git ignore patterns
├── README.md                       # This file
│
├── utils/                          # Utility functions
│   ├── __init__.py                # Package initializer
│   ├── file_handler.py            # PDF/DOCX/TXT file processing
│   └── chat_history.py            # Chat history management
│
└── tabs/                           # Tab implementations
    ├── __init__.py                # Package initializer
    ├── cv_interview.py            # CV Analysis & Interview Prep tab
    ├── code_explainer.py          # Code Explainer & Problem Solver tab
    ├── article_generator.py       # Article Generator tab
    └── study_plan.py              # Study Plan Generator tab
```

## 🔒 Security & Deployment

### Local Development
```bash
# Create .env file with your API key
GROQ_API_KEY=your_key_here

# Never commit .env to version control
```

### Streamlit Cloud Deployment

1. **Push code to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy to Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repository, branch, and `app.py`
   - Click "Deploy"

3. **Add API Key as Secret**
   - Go to app settings in Streamlit Cloud
   - Navigate to "Secrets"
   - Add your API key:
   ```
   GROQ_API_KEY = "your_groq_api_key"
   ```

### Environment Variables
- **Local**: Use `.env` file (added to `.gitignore`)
- **Cloud**: Use Streamlit Cloud Secrets management
- **Never**: Commit API keys to version control

## 💬 Chat System

Each tab features a **persistent chat system** that:
- ✅ Maintains conversation history during session
- ✅ Provides context-aware responses
- ✅ Allows follow-up questions on generated content
- ✅ Supports natural conversation flow
- ✅ Respects user privacy (no external storage)

## 🎯 Usage Examples

### Example 1: CV & Interview Tab
1. Upload your resume (PDF, DOCX, or TXT)
2. Optionally paste a job description
3. Click "Generate Interview Questions"
4. Chat with career coach to:
   - Practice answering specific questions
   - Get advice on particular experiences
   - Learn how to present your skills
   - Discuss company culture fit

### Example 2: Code Explainer Tab
1. Paste Python, JavaScript, Java, or other code
2. Click "Explain Code" for detailed breakdown
3. Ask follow-up questions about:
   - Specific lines or functions
   - Algorithm complexity
   - Best practices
   - Alternative implementations

### Example 3: Article Generator Tab
1. Enter topic (e.g., "Machine Learning in Healthcare")
2. Set word count (e.g., 2000 words)
3. Choose style (e.g., "Technical") and creativity level
4. Generate article
5. Chat to:
   - Expand specific sections
   - Change the tone
   - Add more examples
   - Refine content

### Example 4: Study Plan Tab
1. Enter subject (e.g., "Data Structures & Algorithms")
2. Set duration (e.g., 8 weeks)
3. Select learning methods
4. Generate plan
5. Chat to:
   - Adjust pace for your schedule
   - Get resource recommendations
   - Clarify difficult topics
   - Customize for your goals

## ⚙️ Configuration

### Models Configuration
Edit `config.py` to customize:
- Available models for each tab
- Default models
- Temperature ranges
- System prompts

### File Upload Settings
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ["pdf", "docx", "txt"]
```

### Chat Settings
```python
CHAT_MAX_HISTORY = 50  # Maximum messages in history
CHAT_MESSAGE_MAX_LENGTH = 4000  # Max message length
```

## 🛠️ API Configuration

### Groq API Models
The app uses the following Groq models:

| Model | Use Case | Speed | Quality |
|-------|----------|-------|---------|
| Groq Compound | Web search + code | ⚡ | ⭐⭐⭐⭐⭐ |
| Groq Compound Mini | Latency-optimized | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| Llama 3.3 70B | Advanced reasoning | ⚡⚡ | ⭐⭐⭐⭐ |
| Llama 4 Maverick 17B | Complex reasoning | ⚡⚡ | ⭐⭐⭐⭐ |
| GPT-OSS-120B | Complex tasks | ⚡ | ⭐⭐⭐⭐ |
| Kimi K2 Instruct | Natural language | ⚡ | ⭐⭐⭐⭐⭐ |

### Rate Limiting
- Standard Groq API rate limits apply
- Exponential backoff for retries
- Graceful error messages

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
**Solution:**
- Local: Create `.env` file with `GROQ_API_KEY=your_key`
- Cloud: Add to App settings → Secrets

### Models not loading
**Solution:**
- Verify API key is valid
- Check internet connectivity
- Ensure model names match Groq API documentation
- Verify account has access to requested models

### File upload errors
**Solution:**
- Check file size (max 10MB)
- Verify file type (PDF, DOCX, or TXT)
- Ensure file is not corrupted
- Try re-uploading

### Chat not working
**Solution:**
- Refresh the page
- Clear browser cache
- Check Streamlit version
- Verify API key permissions

## 📊 Performance Considerations

- **Streaming responses**: Long responses stream for better UX
- **Caching**: Streamlit caches expensive operations
- **Session state**: Efficient session management
- **Error handling**: Graceful degradation on API failures

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


## 🆘 Support

- **Issues**: Create a GitHub issue for bugs
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: Check README and config files
- **Groq Docs**: https://console.groq.com/docs

## 🔮 Future Enhancements

Potential features for future versions:
- ✨ Database storage for persistent chat history
- ✨ User authentication and profiles
- ✨ Export to PDF/DOCX
- ✨ Team collaboration features
- ✨ Analytics dashboard
- ✨ Integration with more AI providers
- ✨ Advanced RAG capabilities
- ✨ Voice input/output support

## 📞 Contact

For questions or suggestions:
- Email: sambitmaths123@gmail.com
- GitHub: @sambitcodes

---

**articulAIte** - Empower Your Love for learningwith AI 🚀

Made with ❤️ using Streamlit, LangChain, and Groq
