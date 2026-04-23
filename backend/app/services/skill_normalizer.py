"""
Skill Normalizer — maps known aliases to canonical skill names.
Applied before every MERGE in graph_builder.py to prevent duplicate nodes.

Example: "ReactJS", "React.js", "react" → "React"
"""

# ── Canonical Alias Map ───────────────────────────────────────────────────────
# Key   = lowercase alias (what might appear in job postings / syllabi)
# Value = canonical name (what gets stored in Neo4j)

SKILL_ALIASES: dict[str, str] = {

    # ── JavaScript / Frontend ─────────────────────────────────────────────────
    "reactjs":                  "React",
    "react.js":                 "React",
    "react js":                 "React",
    "react native":             "React Native",
    "vuejs":                    "Vue.js",
    "vue js":                   "Vue.js",
    "vue":                      "Vue.js",
    "angularjs":                "Angular",
    "angular js":               "Angular",
    "angular 2+":               "Angular",
    "nodejs":                   "Node.js",
    "node js":                  "Node.js",
    "node":                     "Node.js",
    "expressjs":                "Express.js",
    "express js":               "Express.js",
    "express":                  "Express.js",
    "nextjs":                   "Next.js",
    "next js":                  "Next.js",
    "typescript":               "TypeScript",
    "ts":                       "TypeScript",
    "javascript":               "JavaScript",
    "js":                       "JavaScript",
    "es6":                      "JavaScript",
    "ecmascript":               "JavaScript",

    # ── Python ────────────────────────────────────────────────────────────────
    "python3":                  "Python",
    "python 3":                 "Python",
    "python programming":       "Python",
    "py":                       "Python",

    # ── Machine Learning / AI ─────────────────────────────────────────────────
    "ml":                       "Machine Learning",
    "machine learning (ml)":    "Machine Learning",
    "deep learning (dl)":       "Deep Learning",
    "dl":                       "Deep Learning",
    "artificial intelligence":  "AI",
    "generative ai":            "Generative AI",
    "gen ai":                   "Generative AI",
    "genai":                    "Generative AI",
    "llm":                      "Large Language Models",
    "llms":                     "Large Language Models",
    "large language model":     "Large Language Models",
    "transformer":              "Transformer Models",
    "transformers":             "Transformer Models",
    "bert":                     "BERT",
    "gpt":                      "GPT",
    "chatgpt":                  "GPT",
    "rag":                      "RAG",
    "retrieval augmented generation": "RAG",
    "langchain":                "LangChain",
    "lang chain":               "LangChain",
    "vector db":                "Vector Database",
    "vector store":             "Vector Database",
    "vectordb":                 "Vector Database",
    "faiss":                    "FAISS",

    # ── Data Science ──────────────────────────────────────────────────────────
    "data science":             "Data Science",
    "data analysis":            "Data Analysis",
    "data analytics":           "Data Analytics",
    "pandas":                   "Pandas",
    "numpy":                    "NumPy",
    "np":                       "NumPy",
    "matplotlib":               "Matplotlib",
    "scikit learn":             "Scikit-learn",
    "sklearn":                  "Scikit-learn",
    "scikit-learn":             "Scikit-learn",
    "tensorflow":               "TensorFlow",
    "tf":                       "TensorFlow",
    "pytorch":                  "PyTorch",
    "torch":                    "PyTorch",
    "keras":                    "Keras",

    # ── Databases ─────────────────────────────────────────────────────────────
    "sql":                      "SQL",
    "mysql":                    "MySQL",
    "postgresql":               "PostgreSQL",
    "postgres":                 "PostgreSQL",
    "mongo":                    "MongoDB",
    "mongodb":                  "MongoDB",
    "nosql":                    "NoSQL",
    "neo4j":                    "Neo4j",
    "redis":                    "Redis",
    "sqlite":                   "SQLite",
    "oracle db":                "Oracle Database",
    "oracle database":          "Oracle Database",

    # ── Cloud ─────────────────────────────────────────────────────────────────
    "aws":                      "AWS",
    "amazon web services":      "AWS",
    "azure":                    "Microsoft Azure",
    "microsoft azure":          "Microsoft Azure",
    "gcp":                      "Google Cloud Platform",
    "google cloud":             "Google Cloud Platform",
    "google cloud platform":    "Google Cloud Platform",

    # ── DevOps / Infrastructure ───────────────────────────────────────────────
    "docker":                   "Docker",
    "kubernetes":               "Kubernetes",
    "k8s":                      "Kubernetes",
    "ci/cd":                    "CI/CD",
    "cicd":                     "CI/CD",
    "continuous integration":   "CI/CD",
    "jenkins":                  "Jenkins",
    "git":                      "Git",
    "github":                   "Git",
    "gitlab":                   "Git",
    "linux":                    "Linux",
    "unix":                     "Linux",
    "bash":                     "Bash",
    "shell scripting":          "Bash",
    "terraform":                "Terraform",
    "ansible":                  "Ansible",

    # ── Backend / Languages ───────────────────────────────────────────────────
    "java":                     "Java",
    "j2ee":                     "Java EE",
    "jakarta ee":               "Java EE",
    "spring":                   "Spring Framework",
    "spring boot":              "Spring Boot",
    "springboot":               "Spring Boot",
    "c++":                      "C++",
    "cpp":                      "C++",
    "c#":                       "C#",
    "csharp":                   "C#",
    ".net":                     ".NET",
    "dotnet":                   ".NET",
    "golang":                   "Go",
    "go lang":                  "Go",
    "rust lang":                "Rust",
    "php":                      "PHP",
    "ruby":                     "Ruby",
    "ruby on rails":            "Ruby on Rails",
    "rails":                    "Ruby on Rails",
    "scala":                    "Scala",
    "kotlin":                   "Kotlin",
    "swift":                    "Swift",

    # ── Web / APIs ────────────────────────────────────────────────────────────
    "restful api":              "REST API",
    "rest api":                 "REST API",
    "rest":                     "REST API",
    "graphql":                  "GraphQL",
    "html5":                    "HTML",
    "html":                     "HTML",
    "css3":                     "CSS",
    "css":                      "CSS",
    "fastapi":                  "FastAPI",
    "flask":                    "Flask",
    "django":                   "Django",

    # ── Data Structures & Algorithms ──────────────────────────────────────────
    "dsa":                      "Data Structures and Algorithms",
    "data structures":          "Data Structures and Algorithms",
    "algorithms":               "Data Structures and Algorithms",
    "data structures & algorithms": "Data Structures and Algorithms",

    # ── Soft Skills (deduplicate common variants) ─────────────────────────────
    "communication skills":     "Communication",
    "verbal communication":     "Communication",
    "written communication":    "Communication",
    "problem solving":          "Problem Solving",
    "problem-solving":          "Problem Solving",
    "team work":                "Teamwork",
    "team player":              "Teamwork",
    "leadership skills":        "Leadership",
    "project management":       "Project Management",
    "agile methodology":        "Agile",
    "agile/scrum":              "Agile",
    "scrum":                    "Agile",
}


def normalize(skill_name: str) -> str:
    """
    Returns the canonical name for a skill.
    Falls back to the original (title-cased) if no alias found.
    
    Usage:
        normalize("ReactJS")  →  "React"
        normalize("k8s")      →  "Kubernetes"
        normalize("Foobar")   →  "Foobar"
    """
    if not skill_name or not skill_name.strip():
        return skill_name

    cleaned = skill_name.strip()
    lookup  = cleaned.lower()

    return SKILL_ALIASES.get(lookup, cleaned)


def normalize_list(skills: list[str]) -> list[str]:
    """
    Normalizes a list of skill names and removes duplicates
    while preserving order.
    
    Usage:
        normalize_list(["ReactJS", "React", "nodejs"])
        →  ["React", "Node.js"]
    """
    seen    = set()
    result  = []
    for skill in skills:
        canonical = normalize(skill)
        if canonical not in seen:
            seen.add(canonical)
            result.append(canonical)
    return result
