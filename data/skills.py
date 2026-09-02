# Enhanced Structured Skill Dictionary for ResumeAI V2

SKILLS_DB = {
    "Programming": [
        "python", "java", "c", "c++", "c#", "javascript", "typescript",
        "go", "golang", "php", "ruby", "rust", "kotlin", "swift", "r", "scala"
    ],
    "Web": [
        "html", "html5", "css", "css3", "bootstrap", "tailwind", "tailwind css",
        "react", "react.js", "reactjs", "next.js", "vue", "vue.js", "angular",
        "jinja2", "jquery"
    ],
    "Backend": [
        "node.js", "nodejs", "express", "express.js", "flask", "django",
        "fastapi", "rest api", "restful api", "graphql", "microservices",
        "servlet", "jsp", "spring boot", "gRPC"
    ],
    "Database": [
        "mysql", "postgresql", "postgres", "mongodb", "sqlite", "sqlite3",
        "redis", "oracle", "sql server", "mssql", "cassandra", "dynamodb",
        "neo4j", "sql", "nosql"
    ],
    "AI/ML": [
        "machine learning", "ml", "deep learning", "nlp", "natural language processing",
        "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
        "sklearn", "opencv", "transformers", "huggingface", "spacy", "nltk",
        "neural networks", "cnn", "rnn", "lstm", "generative ai", "llm", "bert"
    ],
    "Data": [
        "pandas", "numpy", "scipy", "data analysis", "data science",
        "data engineering", "power bi", "tableau", "spark", "hadoop", "etl"
    ],
    "Cloud": [
        "aws", "amazon web services", "azure", "gcp", "google cloud",
        "serverless", "s3", "ec2", "lambda"
    ],
    "DevOps": [
        "docker", "kubernetes", "k8s", "linux", "bash", "shell scripting",
        "ci/cd", "jenkins", "gitlab ci", "github actions", "terraform", "ansible"
    ],
    "CS Fundamentals": [
        "data structures", "algorithms", "dsa", "dbms", "operating systems",
        "computer networks", "object-oriented programming", "oop", "system design",
        "software engineering", "compiler design"
    ],
    "Tools": [
        "git", "github", "gitlab", "postman", "jira", "maven", "gradle",
        "webpack", "npm", "pip", "conda", "vscode"
    ],
    "Soft Skills": [
        "communication", "leadership", "teamwork", "problem solving",
        "critical thinking", "time management", "adaptability", "collaboration",
        "creativity", "project management", "decision making", "analytical thinking"
    ]
}

# Alias map to normalize variations into display canonical names
SKILL_DISPLAY_MAP = {
    "python": "Python",
    "java": "Java",
    "c": "C",
    "c++": "C++",
    "c#": "C#",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "go": "Go",
    "golang": "Go",
    "php": "PHP",
    "ruby": "Ruby",
    "rust": "Rust",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "r": "R",
    "scala": "Scala",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "flask": "Flask",
    "django": "Django",
    "fastapi": "FastAPI",
    "rest api": "REST API",
    "restful api": "REST API",
    "graphql": "GraphQL",
    "microservices": "Microservices",
    "jinja2": "Jinja2",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "sqlite": "SQLite",
    "sqlite3": "SQLite",
    "redis": "Redis",
    "oracle": "Oracle",
    "sql": "SQL",
    "nosql": "NoSQL",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "opencv": "OpenCV",
    "data structures": "Data Structures",
    "algorithms": "Algorithms",
    "dsa": "DSA",
    "dbms": "DBMS",
    "operating systems": "Operating Systems",
    "computer networks": "Computer Networks",
    "object-oriented programming": "OOP",
    "oop": "OOP",
    "system design": "System Design",
    "git": "Git",
    "github": "GitHub",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "linux": "Linux",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "postman": "Postman",
    "jira": "Jira",
    "ci/cd": "CI/CD",
    "communication": "Communication",
    "leadership": "Leadership",
    "teamwork": "Teamwork",
    "problem solving": "Problem Solving",
    "critical thinking": "Critical Thinking",
    "time management": "Time Management",
    "project management": "Project Management"
}
