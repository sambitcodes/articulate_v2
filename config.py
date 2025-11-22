"""
Configuration and constants for articulAIte application
"""

# Groq Models Configuration
CV_INTERVIEW_MODELS = {
    "Groq Compound (Best)": "groq/compound",
    "Groq Compound Mini (Web Research)": "groq/compound-mini",
    "Kimi K2 Instruct": "moonshotai/Kimi-K2-Instruct-0905",
    "GPT-OSS-120B": "openai/gpt-oss-120b",
    "Llama 3.3 ": "llama-3.3-70b-versatile" 
}

CODE_EXPLAINER_MODELS = {
    "Groq Compound (Best)": "groq/compound",
    "Groq Compound Mini (Code Execution)": "groq/compound-mini",
    "Kimi K2 Instruct": "moonshotai/Kimi-K2-Instruct-0905",
    "GPT-OSS-120B": "openai/gpt-oss-120b",
    "Llama 4 Maverick": "Meta Llama-4 Maverick-17B-128E-Instruct"
}

ARTICLE_GENERATOR_MODELS = {
    "Groq Compound (Best)": "groq/compound",
    "Groq Compound Mini (Web Research)": "groq/compound-mini",
    "Kimi K2 Instruct": "moonshotai/Kimi-K2-Instruct-0905",
    "OpenAI GPT-OSS-120B": "openai/gpt-oss-120b",
    "Llama 3.3 70B": "llama-3.3-70b-versatile"
}

STUDY_PLAN_MODELS = {
    "Groq Compound Mini (Best)": "groq/compound-mini",
    "Kimi K2 Instruct": "moonshotai/Kimi-K2-Instruct-0905",
    "OpenAI GPT-OSS-120B": "openai/gpt-oss-120b",
    "Llama 3.3 70B": "llama-3.3-70b-versatile"
}

# Default Models
DEFAULT_CHAT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_CV_MODEL = "qwen-3-32b"
DEFAULT_CODE_MODEL = "qwen-3-32b"
DEFAULT_ARTICLE_MODEL = "groq/compound"
DEFAULT_STUDY_MODEL = "llama-3.3-70b-versatile"

# File Upload Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ["pdf", "docx", "txt"]

# Article Generation Settings
ARTICLE_MIN_WORDS = 100
ARTICLE_MAX_WORDS = 5000
ARTICLE_DEFAULT_WORDS = 1500

WRITING_STYLES = [
    "Academic",
    "Casual",
    "Professional",
    "Technical",
    "Journalistic",
    "Creative"
]

CREATIVITY_LEVELS = ["Low", "Medium", "High"]

# Study Plan Settings
STUDY_MIN_WEEKS = 1
STUDY_MAX_WEEKS = 52

# Chat Configuration
CHAT_MAX_HISTORY = 50
CHAT_MESSAGE_MAX_LENGTH = 4000

# Timeout Configuration (seconds)
API_TIMEOUT = 60
FILE_UPLOAD_TIMEOUT = 30

# System Prompts
SYSTEM_PROMPTS = {
    "cv_interview": """You are an expert career coach and interview preparation specialist. 
Your role is to:
1. Analyze resumes/CVs thoroughly
2. Generate targeted interview questions based on experience
3. Provide suggestions for highlighting skills
4. Give company-specific interview preparation advice
5. Help practice answers to common and role-specific questions

Be encouraging, detailed, and practical in your responses.""",
    
    "code_explainer": """You are an expert software developer and code mentor.
Your role is to:
1. Provide line-by-line code explanations
2. Identify and fix errors
3. Suggest optimizations and best practices
4. Explain complex algorithms and data structures
5. Help debug and troubleshoot issues

Be thorough, educational, and provide examples when helpful.""",
    
    "article_generator": """You are a professional writer and researcher.
Your role is to:
1. Create well-researched, engaging articles
2. Research topics thoroughly using available information
3. Ensure factual accuracy and credibility
4. Format content for various platforms
5. Adapt tone and style to match requirements

Produce high-quality, publication-ready content.""",
    
    "study_plan": """You are an experienced educator and learning specialist.
Your role is to:
1. Create personalized study plans
2. Break down complex subjects into digestible lessons
3. Recommend quality learning resources
4. Provide realistic time estimates
5. Include progress tracking metrics

Be encouraging and create realistic, achievable plans."""
}

# Rate Limiting
RATE_LIMIT_CALLS = 10
RATE_LIMIT_WINDOW = 60  # seconds

# Error Messages
ERROR_MESSAGES = {
    "api_key_missing": "GROQ_API_KEY not configured.",
    "file_too_large": "File exceeds maximum size limit (10MB).",
    "invalid_file_type": "Invalid file type. Supported: PDF, DOCX, TXT",
    "api_error": "An error occurred with the API.",
    "timeout": "Request timed out.",
    "rate_limit": "Rate limit exceeded."
}
