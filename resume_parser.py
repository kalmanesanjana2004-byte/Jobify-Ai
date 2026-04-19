"""
Resume Parser Module
Handles PDF text extraction and text preprocessing for the Job Recommendation System.
"""

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


# Comprehensive skill dictionary for extraction
KNOWN_SKILLS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "ruby", "php",
    "swift", "kotlin", "rust", "go", "scala", "r", "matlab", "perl", "dart",
    "objective-c", "solidity", "abap", "bash", "powershell", "sql", "html", "css",
    "sass", "less", "graphql", "xml", "json", "yaml",

    # Web Frameworks & Libraries
    "react", "angular", "vue.js", "vue", "next.js", "nuxt.js", "svelte", "django",
    "flask", "spring boot", "spring", "express.js", "express", "node.js", "nodejs",
    "rails", "ruby on rails", "laravel", "asp.net", "fastapi", "gin",
    "jquery", "bootstrap", "tailwind", "material ui", "webpack", "vite",

    # Data Science & ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "pandas", "numpy", "scipy", "matplotlib", "seaborn",
    "nlp", "natural language processing", "computer vision", "opencv",
    "spacy", "nltk", "hugging face", "transformers", "bert", "gpt",
    "reinforcement learning", "neural networks", "cnn", "rnn", "lstm",
    "random forest", "xgboost", "lightgbm", "catboost",
    "data mining", "data analysis", "data visualization", "statistics",
    "a/b testing", "hypothesis testing", "regression", "classification",
    "clustering", "dimensionality reduction", "feature engineering",
    "model deployment", "mlops", "yolo", "object detection", "segmentation",
    "sentiment analysis", "text classification", "image processing",

    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra",
    "dynamodb", "oracle", "sql server", "sqlite", "neo4j", "firebase",
    "snowflake", "bigquery", "data warehousing", "etl",

    # Cloud & DevOps
    "aws", "azure", "google cloud", "gcp", "docker", "kubernetes",
    "jenkins", "terraform", "ansible", "ci/cd", "github actions",
    "gitlab ci", "circleci", "nginx", "apache", "linux", "unix",
    "microservices", "serverless", "lambda", "vmware", "vagrant",
    "prometheus", "grafana", "datadog", "splunk", "elk stack",

    # Tools & Platforms
    "git", "github", "gitlab", "bitbucket", "jira", "confluence",
    "slack", "trello", "notion", "figma", "adobe xd", "sketch",
    "photoshop", "illustrator", "after effects", "premiere pro",
    "wordpress", "shopify", "salesforce", "sap", "power bi", "tableau",
    "looker", "excel", "google analytics", "postman", "swagger",

    # Mobile Development
    "react native", "flutter", "swiftui", "uikit", "jetpack compose",
    "android sdk", "xcode", "ios", "android", "mobile development",
    "app store", "google play", "cocoapods", "gradle",

    # Testing
    "selenium", "cypress", "jest", "mocha", "pytest", "unittest",
    "testng", "junit", "karma", "jasmine", "testing", "tdd", "bdd",
    "api testing", "load testing", "performance testing", "qa",

    # Security
    "cybersecurity", "penetration testing", "ethical hacking",
    "network security", "web security", "owasp", "burp suite",
    "metasploit", "nmap", "wireshark", "kali linux", "siem",
    "firewall", "vpn", "encryption", "ssl/tls", "iso 27001",
    "incident response", "vulnerability assessment",

    # Methodologies & Practices
    "agile", "scrum", "kanban", "waterfall", "devops", "ci/cd",
    "rest apis", "restful", "soap", "microservices", "mvc", "mvvm",
    "design patterns", "solid", "clean code", "code review",
    "pair programming", "tdd", "bdd",

    # Other Technical Skills
    "blockchain", "smart contracts", "web3", "defi", "nft",
    "iot", "embedded systems", "rtos", "arm", "microcontrollers",
    "robotics", "ros", "slam", "sensor fusion",
    "game development", "unity", "unreal engine",
    "data modeling", "system design", "api design",
    "technical writing", "documentation",

    # Soft Skills & Business
    "project management", "product management", "leadership",
    "communication", "teamwork", "problem solving", "critical thinking",
    "presentation", "negotiation", "stakeholder management",
    "user research", "wireframing", "prototyping", "usability testing",
    "seo", "content marketing", "email marketing", "social media marketing",
    "copywriting", "brand design", "financial modeling", "accounting",
    "data strategy", "roadmap planning",

    # Certifications & Standards
    "pmp", "csm", "aws certified", "azure certified", "google certified",
    "ceh", "oscp", "cissp", "ccna", "ccnp",
]


def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    if PdfReader is None:
        raise ImportError("PyPDF2 is not installed. Please install it: pip install PyPDF2")

    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {str(e)}")


def clean_text(text):
    """
    Clean and preprocess text:
    - Convert to lowercase
    - Remove special characters (keep letters, numbers, spaces)
    - Remove extra whitespace
    - Tokenize
    - Remove stopwords
    - Lemmatize
    """
    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # Remove phone numbers
    text = re.sub(r'\b\d{10,}\b', '', text)

    # Remove special characters but keep spaces and basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s\+\#\.]', ' ', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenize
    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words and len(t) > 1]

    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]

    return ' '.join(tokens)


def extract_skills(text, skill_list=None):
    """
    Extract known skills from text.
    Returns a list of matched skills.
    """
    if skill_list is None:
        skill_list = KNOWN_SKILLS

    if not text:
        return []

    text_lower = text.lower()
    found_skills = []

    for skill in skill_list:
        skill_lower = skill.lower()
        # Use word boundary matching for short skills to avoid false positives
        if len(skill_lower) <= 2:
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        else:
            if skill_lower in text_lower:
                found_skills.append(skill)

    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for s in found_skills:
        s_lower = s.lower()
        if s_lower not in seen:
            seen.add(s_lower)
            unique_skills.append(s)

    return unique_skills


def process_resume(file_path):
    """
    Full pipeline: extract text from PDF, clean it, and extract skills.
    Returns (raw_text, cleaned_text, skills_list)
    """
    raw_text = extract_text_from_pdf(file_path)
    cleaned = clean_text(raw_text)
    skills = extract_skills(raw_text)
    return raw_text, cleaned, skills


def process_manual_input(skills_text, experience_text="", qualifications_text=""):
    """
    Process manually entered user data.
    Returns (combined_text, cleaned_text, skills_list)
    """
    combined = f"{skills_text} {experience_text} {qualifications_text}".strip()
    cleaned = clean_text(combined)
    skills = extract_skills(combined)
    return combined, cleaned, skills
