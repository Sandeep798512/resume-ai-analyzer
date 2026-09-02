# Fallback Technical, Behavioral & DSA Interview Question Bank with Model Answers

ROLE_INTERVIEW_BANK = {
    "Python Developer": {
        "technical": [
            {
                "question": "Explain Python's GIL (Global Interpreter Lock) and how it impacts multi-threading.",
                "model_answer": "The Global Interpreter Lock (GIL) is a mutex lock used by CPython to ensure that only one native thread executes Python bytecode at a time. Impact: It prevents CPU-bound multi-threading performance gains. Solution: For CPU-bound tasks, use multiprocessing or C-extensions (NumPy). For I/O-bound tasks (network, disk), Python threading or asyncio works efficiently as GIL is released during I/O wait.",
                "key_terms": ["cpython", "mutex", "bytecode", "cpu-bound", "multiprocessing", "i/o-bound", "asyncio"]
            },
            {
                "question": "What is the difference between deepcopy and shallow copy in Python?",
                "model_answer": "A shallow copy (copy.copy()) creates a new collection object but populates it with references to the original child objects. Modifying nested mutable objects affects both copies. A deep copy (copy.deepcopy()) recursively copies all nested objects, creating completely independent data structures.",
                "key_terms": ["shallow copy", "deep copy", "reference", "nested", "recursively", "mutable", "independent"]
            },
            {
                "question": "How do Flask request contexts and application contexts work under the hood?",
                "model_answer": "Flask uses Thread Local / Context Locals (Werkzeug) to manage state. Request Context (g, request) holds data active during an HTTP request. Application Context (current_app) holds application-level config and DB connections. Contexts are automatically pushed when a request enters a Flask WSGI handler and popped when completed.",
                "key_terms": ["request context", "application context", "thread local", "werkzeug", "current_app", "g", "wsgi"]
            },
            {
                "question": "Explain Python decorators and write an example of a timing decorator.",
                "model_answer": "A decorator is a higher-order function that takes another function as an argument and extends its behavior without modifying it explicitly (@wrapper syntax). Standard structure uses functools.wraps to preserve function metadata.",
                "key_terms": ["decorator", "higher-order", "wrapper", "functools.wraps", "arguments", "metadata"]
            },
            {
                "question": "How does WSGI differ from ASGI in Python web framework deployment?",
                "model_answer": "WSGI (Web Server Gateway Interface) is synchronous (one request per thread/worker, e.g., Gunicorn, Flask, Django). ASGI (Asynchronous Server Gateway Interface) supports async/await, WebSockets, HTTP/2, and long-polling (e.g., Uvicorn, FastAPI, Channels).",
                "key_terms": ["wsgi", "asgi", "synchronous", "asynchronous", "gunicorn", "uvicorn", "fastapi", "websockets"]
            }
        ],
        "resume": [
            {
                "question": "Walk me through your backend project architecture and key Python libraries used.",
                "model_answer": "State your project scope clearly using STAR method: 1. Architecture layer (Flask/FastAPI, ORM/SQLite/PostgreSQL, Jinja2/REST endpoints). 2. Explain data flow from HTTP request -> routing -> controller logic -> database query -> response serialization. 3. Mention performance highlights (e.g. indexing, caching, validation).",
                "key_terms": ["architecture", "routing", "controller", "database", "orm", "endpoints", "serialization"]
            },
            {
                "question": "Why did you choose Flask over Django for your application requirements?",
                "model_answer": "Flask is a micro-framework that provides lightweight flexibility without forcing an unneeded monolithic ORM or admin suite. It allows explicitly configuring modules (pypdf, scikit-learn, SQLite, custom CSS) with fast startup times and minimal memory footprint.",
                "key_terms": ["micro-framework", "lightweight", "flexibility", "explicit", "minimal footprint", "decoupled"]
            }
        ],
        "behavioral": [
            {
                "question": "Describe a challenging bug you encountered in Python and how you debugged it.",
                "model_answer": "Structure your answer using STAR: Situation (unhandled exception or memory leak), Task (identifying root cause under deadline), Action (inspecting stack traces, pdb debugger, logging statements), Result (fixed bug, added unit test, deployed cleanly).",
                "key_terms": ["star method", "situation", "task", "action", "result", "root cause", "unit test", "logging"]
            }
        ],
        "dsa": ["Arrays & Two Pointers", "Hash Maps & Sets", "String Manipulation", "Recursion & Backtracking", "Linked Lists"],
        "cs_fundamentals": ["Database Indexing & ACID Principles", "HTTP Protocol & REST API Status Codes", "Process vs Thread Execution"]
    },
    "Backend Developer": {
        "technical": [
            {
                "question": "Explain the difference between SQL (Relational) and NoSQL (Document/Key-Value) databases.",
                "model_answer": "SQL databases (PostgreSQL, MySQL) are structured, table-based, schema-enforced, and strictly ACID compliant, suitable for complex queries and relational integrity. NoSQL databases (MongoDB, Redis) are schema-less, document or key-value based, scaled horizontally, and optimized for unstructured high-throughput data.",
                "key_terms": ["sql", "nosql", "relational", "schema", "acid", "document", "horizontal scaling", "postgresql", "mongodb"]
            },
            {
                "question": "What are database indexes, B-Trees, and how do they impact write performance?",
                "model_answer": "A database index is a data structure (commonly B-Tree or Hash) that speeds up SELECT queries by reducing lookup complexity from O(N) to O(log N). Impact: While reads become drastically faster, INSERT, UPDATE, and DELETE operations become slightly slower because index structures must be re-balanced upon data mutation.",
                "key_terms": ["index", "b-tree", "lookup complexity", "select", "read performance", "write penalty", "re-balance"]
            },
            {
                "question": "How do you design RESTful APIs for scale, idempotency, and versioning?",
                "model_answer": "Use standard HTTP verbs (GET, POST, PUT, DELETE). Implement URI path versioning (/v1/resource). Ensure GET, PUT, and DELETE operations are idempotent (repeating request produces same server state). Use standard HTTP status codes (200, 201, 400, 401, 403, 404, 500) and pagination.",
                "key_terms": ["restful", "idempotent", "http verbs", "versioning", "status codes", "pagination", "json"]
            }
        ],
        "resume": [
            {
                "question": "How did you handle authentication and session security in your application?",
                "model_answer": "Passwords must never be stored in plain text; use PBKDF2 / Bcrypt / SHA256 password hashing (Werkzeug). Use HTTP-only secure session cookies, CSRF protection tokens on POST requests, and rate limiting middleware to prevent brute-force attacks.",
                "key_terms": ["password hashing", "pbkdf2", "werkzeug", "csrf tokens", "session cookies", "rate limiting"]
            }
        ],
        "behavioral": [
            {
                "question": "Tell me about a time when a server or service crashed under load and how you responded.",
                "model_answer": "Explain monitoring log inspection, identifying bottleneck (e.g. database unindexed query or memory leak), applying emergency fix, and adding automated error logging & load testing.",
                "key_terms": ["logs", "bottleneck", "database index", "load testing", "post-mortem", "mitigation"]
            }
        ],
        "dsa": ["Hash Tables & Sets", "Graphs (BFS / DFS)", "Queues & Stacks", "Heaps & Priority Queues"],
        "cs_fundamentals": ["TCP/IP 3-Way Handshake", "ACID Transactions (Atomicity, Consistency, Isolation, Durability)", "System Design Horizontal vs Vertical Scaling"]
    },
    "Software Engineer": {
        "technical": [
            {
                "question": "Explain Object-Oriented Programming (OOP) concepts: Encapsulation, Abstraction, Inheritance, Polymorphism.",
                "model_answer": "1. Encapsulation: Bundling data and methods operating on that data within a class while restricting direct access (private variables). 2. Abstraction: Hiding background complexity and showing only essential interfaces. 3. Inheritance: Deriving child classes from parent classes for code reuse. 4. Polymorphism: Overriding or overloading methods to execute different behavior based on object type.",
                "key_terms": ["encapsulation", "abstraction", "inheritance", "polymorphism", "class", "interface", "code reuse"]
            },
            {
                "question": "What is the difference between stack memory and heap memory allocation?",
                "model_answer": "Stack memory is fast, statically allocated, managed automatically by CPU instructions, and holds primitive variables and function calls (LIFO). Heap memory is dynamic, larger, allocated manually or via runtime garbage collector, and shared globally across threads.",
                "key_terms": ["stack memory", "heap memory", "static allocation", "dynamic allocation", "lifo", "garbage collection"]
            }
        ],
        "resume": [
            {
                "question": "Describe your role and individual technical contributions in your major capstone project.",
                "model_answer": "Explain problem statement, your specific module (e.g. backend algorithm design, database schema, NLP matching engine), technical challenges overcome, and final quantifiable results achieved.",
                "key_terms": ["problem statement", "module", "backend logic", "database schema", "quantifiable results"]
            }
        ],
        "behavioral": [
            {
                "question": "Describe how you manage tight deadlines when building software projects.",
                "model_answer": "Prioritize core MVP (Minimum Viable Product) features first, break down tasks into sub-milestones, maintain clear communication with team members, and write clean testable code.",
                "key_terms": ["mvp", "milestones", "prioritization", "communication", "clean code"]
            }
        ],
        "dsa": ["Binary Trees & BST", "Dynamic Programming", "Sorting & Binary Search", "Graph Traversal"],
        "cs_fundamentals": ["Operating System Paging & Virtual Memory", "OSI 7-Layer Model", "Database Normalization 1NF to 3NF"]
    },
    "AI/ML Engineer": {
        "technical": [
            {
                "question": "What is the difference between L1 (Lasso) and L2 (Ridge) regularization?",
                "model_answer": "L1 Regularization (Lasso) adds absolute sum of weights penalty (|w|), driving less important feature weights to exactly zero, performing feature selection. L2 Regularization (Ridge) adds squared weights penalty (w^2), penalizing large weights smoothly to prevent overfitting without forcing exact zero weights.",
                "key_terms": ["l1 regularization", "l2 regularization", "lasso", "ridge", "overfitting", "penalty", "feature selection"]
            },
            {
                "question": "Explain the Bias-Variance tradeoff in machine learning algorithms.",
                "model_answer": "Bias error comes from overly simplistic assumptions (underfitting, model fails to capture complexity). Variance error comes from sensitivity to small fluctuations in training data (overfitting, model captures noise). Goal: Find optimal model complexity minimizing total generalization error.",
                "key_terms": ["bias", "variance", "underfitting", "overfitting", "model complexity", "tradeoff", "generalization"]
            }
        ],
        "resume": [
            {
                "question": "Walk me through your machine learning pipeline: data cleaning, feature engineering, model selection, evaluation.",
                "model_answer": "Explain step-by-step: 1. Preprocessing (missing values, normalization). 2. Feature Extraction (TF-IDF, n-grams, embeddings). 3. Model Training & Hyperparameter Tuning (Scikit-Learn, PyTorch). 4. Evaluation Metrics (Precision, Recall, F1-Score, ROC-AUC).",
                "key_terms": ["preprocessing", "normalization", "feature extraction", "hyperparameter tuning", "precision", "recall", "f1-score"]
            }
        ],
        "behavioral": [
            {
                "question": "How do you handle dirty, incomplete, or imbalanced datasets in real-world AI projects?",
                "model_answer": "For missing data: impute using mean/median or drop rows. For imbalanced datasets: use SMOTE oversampling, class weighting, or evaluate using Precision-Recall AUC rather than raw Accuracy.",
                "key_terms": ["imputation", "smote", "class weighting", "imbalanced data", "precision-recall"]
            }
        ],
        "dsa": ["Matrix Multiplication & Vector Operations", "Dynamic Programming", "Graph Embeddings", "Searching & Sorting"],
        "cs_fundamentals": ["Probability Distributions & Bayes Theorem", "Vector Calculus & Gradient Optimization", "Model Inference Latency & Quantization"]
    }
}

DEFAULT_INTERVIEW_BANK = ROLE_INTERVIEW_BANK["Software Engineer"]
