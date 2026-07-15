"""db.py — 数据库连接与初始化"""
import sqlite3
import os
import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database")
DB_PATH = os.path.join(DB_DIR, "finderos.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    with get_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, salt TEXT NOT NULL, role_id INTEGER DEFAULT NULL,
            is_enabled INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id))""")
        conn.execute("""CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '', is_system INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS functions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
            module TEXT DEFAULT '', icon TEXT DEFAULT '', route_path TEXT DEFAULT '',
            parent_id INTEGER DEFAULT NULL, sort_order INTEGER DEFAULT 0,
            is_enabled INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES functions(id))""")
        conn.execute("""CREATE TABLE IF NOT EXISTS menus (
            id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
            path TEXT DEFAULT '', icon TEXT DEFAULT '', sort_order INTEGER DEFAULT 0,
            parent_id INTEGER DEFAULT NULL, is_enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES menus(id))""")
        conn.execute("""CREATE TABLE IF NOT EXISTS role_functions (
            role_id INTEGER NOT NULL, function_id INTEGER NOT NULL,
            PRIMARY KEY (role_id, function_id),
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (function_id) REFERENCES functions(id) ON DELETE CASCADE)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS role_menus (
            role_id INTEGER NOT NULL, menu_id INTEGER NOT NULL,
            PRIMARY KEY (role_id, menu_id),
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS fingerprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fingerprint TEXT NOT NULL,
            user_agent TEXT DEFAULT '', platform TEXT DEFAULT '',
            screen_w INTEGER DEFAULT 0, screen_h INTEGER DEFAULT 0,
            url TEXT DEFAULT '', referrer TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS watch_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT DEFAULT '',
            base_url TEXT NOT NULL, method TEXT DEFAULT 'GET', headers TEXT DEFAULT '{}',
            params_template TEXT DEFAULT '', status INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS model_engines (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, model_name TEXT NOT NULL,
            api_key TEXT DEFAULT '', api_url TEXT DEFAULT '', is_default INTEGER DEFAULT 0,
            status INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS digital_employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT DEFAULT '',
            avatar TEXT DEFAULT 'robot', system_prompt TEXT DEFAULT '', model_id INTEGER DEFAULT 0,
            status INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES model_engines(id))""")
        conn.execute("""CREATE TABLE IF NOT EXISTS data_warehouse (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, url TEXT DEFAULT '',
            summary TEXT DEFAULT '', content TEXT DEFAULT '', source_name TEXT DEFAULT '',
            source_id INTEGER DEFAULT 0, keyword TEXT DEFAULT '',
            is_deep_collected INTEGER DEFAULT 0, deep_data TEXT DEFAULT '{}',
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_id) REFERENCES watch_sources(id))""")
        conn.execute("""CREATE TABLE IF NOT EXISTS user_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            title TEXT DEFAULT 'New Chat', messages TEXT DEFAULT '[]',
            model_id INTEGER DEFAULT 0, employee_id INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id))""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_functions_parent ON functions(parent_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_functions_code ON functions(code)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_menus_parent ON menus(parent_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_menus_code ON menus(code)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role_functions_role ON role_functions(role_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role_functions_func ON role_functions(function_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role_menus_role ON role_menus(role_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role_menus_menu ON role_menus(menu_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fingerprints_fp ON fingerprints(fingerprint)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_data_warehouse_keyword ON data_warehouse(keyword)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_conversations_user ON user_conversations(user_id)")
        conn.commit()
        print(f"[DB] Database initialized: {DB_PATH}")


def seed_default_data():
    import hashlib, secrets
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys=OFF")

        existing = conn.execute("SELECT COUNT(*) as cnt FROM roles").fetchone()
        if existing["cnt"] == 0:
            conn.execute("INSERT INTO roles (id, name, description, is_system) VALUES (1, 'Admin', 'System administrator', 1)")
            conn.execute("INSERT INTO roles (id, name, description, is_system) VALUES (2, 'User', 'Regular user', 1)")
            print("[Seed] Roles created")

        existing_admin = conn.execute("SELECT COUNT(*) as cnt FROM users WHERE username = ?", ("admin",)).fetchone()
        if existing_admin["cnt"] == 0:
            salt = secrets.token_bytes(16)
            client_hash = hashlib.sha256(b"admin888").hexdigest()
            dk = hashlib.pbkdf2_hmac("sha256", client_hash.encode(), salt, 100000)
            conn.execute("INSERT INTO users (username, password_hash, salt, role_id) VALUES (?, ?, ?, 1)",
                        ("admin", dk.hex(), salt.hex()))
            print("[Seed] Admin user created (admin/admin888)")

        existing_funcs = conn.execute("SELECT COUNT(*) as cnt FROM functions").fetchone()
        if existing_funcs["cnt"] == 0:
            funcs = [
                (1,"user:view","User View","User Management","","",None,1,1),
                (2,"user:edit","User Edit","User Management","","",None,2,1),
                (3,"role:view","Role View","Role Management","","",None,3,1),
                (4,"role:edit","Role Edit","Role Management","","",None,4,1),
                (5,"func:view","Function View","Function Management","","",None,5,1),
                (6,"func:edit","Function Edit","Function Management","","",None,6,1),
                (7,"menu:view","Menu View","Menu Management","","",None,7,1),
                (8,"menu:edit","Menu Edit","Menu Management","","",None,8,1),
            ]
            conn.executemany("INSERT INTO functions (id,code,name,module,icon,route_path,parent_id,sort_order,is_enabled) VALUES (?,?,?,?,?,?,?,?,?)", funcs)
            print("[Seed] Functions created")

        existing_menus = conn.execute("SELECT COUNT(*) as cnt FROM menus").fetchone()
        if existing_menus["cnt"] == 0:
            menus = [
                (1,"dashboard","Dashboard","/admin","layui-icon-console",1,None,1),
                (2,"user","Users","/admin/user","layui-icon-user",2,None,1),
                (3,"role","Roles","/admin/role","layui-icon-group",3,None,1),
                (4,"function","Functions","/admin/function","layui-icon-template-1",4,None,1),
                (5,"menu_mgr","Menus","/admin/menu","layui-icon-list",5,None,1),
                (6,"warehouse","Data Warehouse","/admin/warehouse","layui-icon-read",6,None,1),
                (7,"watch","Watch","/admin/watch","layui-icon-search",7,None,1),
                (8,"watch_src","Watch Sources","/admin/watch-source","layui-icon-url",8,None,1),
                (9,"model","Models","/admin/model","layui-icon-engine",9,None,1),
                (10,"employee","Employees","/admin/employee","layui-icon-diamond",10,None,1),
            ]
            conn.executemany("INSERT INTO menus (id,code,name,path,icon,sort_order,parent_id,is_enabled) VALUES (?,?,?,?,?,?,?,?)", menus)
            print("[Seed] Menus created")

        existing_rf = conn.execute("SELECT COUNT(*) as cnt FROM role_functions").fetchone()
        if existing_rf["cnt"] == 0:
            func_ids = conn.execute("SELECT id FROM functions WHERE is_enabled = 1").fetchall()
            conn.executemany("INSERT INTO role_functions (role_id, function_id) VALUES (1, ?)",
                           [(row["id"],) for row in func_ids])
            print("[Seed] Role-function mappings created")

        existing_rm = conn.execute("SELECT COUNT(*) as cnt FROM role_menus").fetchone()
        if existing_rm["cnt"] == 0:
            menu_ids = conn.execute("SELECT id FROM menus WHERE is_enabled = 1").fetchall()
            conn.executemany("INSERT INTO role_menus (role_id, menu_id) VALUES (1, ?)",
                           [(row["id"],) for row in menu_ids])
            print("[Seed] Role-menu mappings created")

        existing_sources = conn.execute("SELECT COUNT(*) as cnt FROM watch_sources").fetchone()
        if existing_sources["cnt"] == 0:
            sources = [
                ("Baidu Search","Baidu search engine","https://www.baidu.com/s","GET","{}","wd={keyword}&pn={page}"),
                ("Bing Search","Microsoft Bing search","https://cn.bing.com/search","GET","{}","q={keyword}&first={page}"),
                ("Sogou Search","Sogou search engine","https://www.sogou.com/web","GET","{}","query={keyword}&page={page}"),
                ("Zhihu Search","Zhihu Q&A platform","https://www.zhihu.com/search","GET","{}","q={keyword}&type=content"),
                ("GitHub Search","GitHub repositories","https://api.github.com/search/repositories","GET","{}","q={keyword}&page={page}"),
                ("CSDN Search","CSDN tech blog","https://so.csdn.net/so/search","GET","{}","q={keyword}&t=all"),
                ("Douban Search","Douban books/movies","https://www.douban.com/search","GET","{}","q={keyword}"),
                ("Weibo Search","Sina Weibo","https://s.weibo.com/weibo","GET","{}","q={keyword}&page={page}"),
                ("Baidu Baike","Baidu encyclopedia","https://baike.baidu.com/search","GET","{}","word={keyword}"),
                ("Douyin Search","Douyin videos","https://www.douyin.com/search","GET","{}","keyword={keyword}"),
            ]
            conn.executemany("INSERT INTO watch_sources (name,description,base_url,method,headers,params_template) VALUES (?,?,?,?,?,?)", sources)
            print("[Seed] Watch sources created (10)")

        existing_models = conn.execute("SELECT COUNT(*) as cnt FROM model_engines").fetchone()
        if existing_models["cnt"] == 0:
            models = [
                ("Tongyi Qianwen","qwen-turbo","sk-xxx","https://dashscope.aliyuncs.com/api/v1",1),
                ("Wenxin Yiyan","ernie-bot","ak-xxx","https://aip.baidubce.com/rpc/2.0",0),
                ("DeepSeek Chat","deepseek-chat","sk-xxx","https://api.deepseek.com/v1",0),
                ("GPT-4o","gpt-4o","sk-xxx","https://api.openai.com/v1",0),
                ("Claude 3.5","claude-3-5-sonnet","sk-xxx","https://api.anthropic.com/v1",0),
                ("Zhipu GLM","glm-4","ak-xxx","https://open.bigmodel.cn/api/paas/v4",0),
            ]
            conn.executemany("INSERT INTO model_engines (name,model_name,api_key,api_url,is_default) VALUES (?,?,?,?,?)", models)
            print("[Seed] Model engines created (6)")

        existing_emp = conn.execute("SELECT COUNT(*) as cnt FROM digital_employees").fetchone()
        if existing_emp["cnt"] == 0:
            emps = [
                ("General Assistant","All-purpose AI assistant for Q&A, writing, coding","robot","You are a professional AI assistant.",1),
                ("Data Analyst","Data analysis and visualization expert","chart","You are a data analysis expert.",1),
                ("Code Assistant","Programming help for multiple languages","laptop","You are a programming expert.",1),
                ("Writing Expert","Content writing and text polishing","pen","You are a writing expert.",1),
                ("Legal Advisor","Legal consultation and risk assessment","scales","You are a legal advisor. Answers are for reference only.",1),
                ("Finance Advisor","Financial analysis and investment advice","money","You are a financial advisor. Answers are for reference only.",1),
                ("Product Manager","Product requirements and competitive analysis","clipboard","You are a product manager.",1),
                ("UI Designer","Interface design and user experience","palette","You are a UI/UX designer.",1),
                ("DevOps Expert","Server ops, Docker, K8s, CI/CD","wrench","You are a DevOps expert.",1),
                ("Security Expert","Cybersecurity and penetration testing","lock","You are a security expert. Answers are for reference only.",1),
                ("Academic Assistant","Paper writing and literature review","book","You are an academic assistant.",1),
                ("Translator","Multi-language translation support","globe","You are a professional translator.",2),
            ]
            conn.executemany("INSERT INTO digital_employees (name,description,avatar,system_prompt,model_id) VALUES (?,?,?,?,?)", emps)
            print("[Seed] Digital employees created (12)")

        existing_dw = conn.execute("SELECT COUNT(*) as cnt FROM data_warehouse").fetchone()
        if existing_dw["cnt"] == 0:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = [
                ("SCU Introduction","https://www.scu.edu.cn","Sichuan University overview","Sichuan University is a key university under the Ministry of Education.","Baidu",1,"SCU"),
                ("CDUT Overview","https://www.cdut.edu.cn","Chengdu University of Technology","CDUT is a multi-disciplinary university focusing on geology and energy.","Baidu",1,"CDUT"),
                ("UESTC Info","https://www.uestc.edu.cn","University of Electronic Science and Technology","UESTC is a national key university in Chengdu.","Bing",1,"UESTC"),
                ("SWJTU Profile","https://www.swjtu.edu.cn","Southwest Jiaotong University","SWJTU is a national key university under the Ministry of Education.","Bing",1,"SWJTU"),
                ("AI Report 2024","https://arxiv.org/abs/2401.00001","AI development trends 2024","Comprehensive review of AI advances in 2023-2024.","Zhihu",1,"AI"),
                ("Python Tutorial","https://docs.python.org/zh-cn/3/tutorial/","Python official tutorial","Python is a widely used high-level programming language.","CSDN",1,"Python"),
                ("Docker Guide","https://docs.docker.com/get-started/","Docker getting started","Docker is an open-source containerization platform.","CSDN",1,"Docker"),
                ("React Docs","https://react.dev/learn","React official documentation","React is a JavaScript library for building user interfaces.","GitHub",1,"React"),
                ("ML Algorithms","https://scikit-learn.org/stable/","scikit-learn documentation","scikit-learn is the most important ML library in Python.","GitHub",1,"ML"),
                ("Cybersecurity","https://www.freebuf.com","FreeBuf security portal","Cybersecurity protects hardware, software and data.","Baidu",1,"Security"),
                ("Blockchain","https://ethereum.org/zh-cn/","Ethereum documentation","Blockchain is a distributed database technology.","Bing",1,"Blockchain"),
                ("Cloud Computing","https://aws.amazon.com/cn/what-is-cloud-computing/","AWS cloud guide","Cloud computing delivers resources over the internet.","Baidu",1,"Cloud"),
                ("Hadoop","https://hadoop.apache.org/","Apache Hadoop docs","Hadoop is an open-source distributed computing framework.","GitHub",1,"BigData"),
                ("IoT Tech","https://iot.eclipse.org/","Eclipse IoT projects","IoT connects physical devices via sensors and networks.","Baidu",1,"IoT"),
                ("5G Technology","https://www.3gpp.org/technologies/5g-overview","3GPP 5G overview","5G features high speed, low latency, and massive connections.","Bing",1,"5G"),
                ("PyTorch","https://pytorch.org/tutorials/","PyTorch tutorials","PyTorch is a deep learning framework by Facebook.","GitHub",1,"PyTorch"),
                ("NLP Survey","https://huggingface.co/docs/transformers/","Hugging Face docs","NLP enables computers to understand human language.","Zhihu",1,"NLP"),
                ("Computer Vision","https://pytorch.org/vision/stable/index.html","PyTorch Vision docs","Computer vision extracts information from images.","CSDN",1,"CV"),
                ("DB Optimization","https://dev.mysql.com/doc/refman/8.0/en/optimization.html","MySQL optimization","Database optimization improves query performance.","Baidu",1,"DB"),
                ("Microservices","https://microservices.io/patterns/","Microservices patterns","Microservices architecture splits apps into small services.","CSDN",1,"Microservices"),
                ("Git Tutorial","https://git-scm.com/book/zh/v2","Git official book","Git is a distributed version control system.","GitHub",1,"Git"),
                ("Linux Admin","https://www.linuxfoundation.org/","Linux Foundation","Linux is an open-source Unix-like operating system.","Baidu",1,"Linux"),
                ("API Design","https://restfulapi.net/","RESTful API guide","RESTful API uses HTTP methods for resource operations.","CSDN",1,"API"),
                ("Scrum Guide","https://scrumguides.org/scrum-guide.html","Official Scrum Guide","Scrum is an iterative incremental development framework.","Bing",1,"Scrum"),
                ("Pentest","https://www.offensive-security.com/","Offensive Security","Penetration testing is a practical security skill.","Baidu",1,"Pentest"),
                ("AI Ethics","https://oecd.ai/en/","OECD AI Policy Observatory","AI ethics covers fairness, privacy, and accountability.","Zhihu",1,"AI Ethics"),
                ("Quantum Computing","https://qiskit.org/learn/","IBM Qiskit tutorials","Quantum computing uses quantum mechanics for computation.","GitHub",1,"Quantum"),
                ("Edge Computing","https://www.lfedge.org/","LF Edge","Edge computing moves computation to network edges.","Bing",1,"Edge"),
                ("Digital Twin","https://www.digitaltwinconsortium.org/","Digital Twin Consortium","Digital twins are virtual replicas of physical objects.","Baidu",1,"Digital Twin"),
                ("Rust Language","https://www.rust-lang.org/zh-CN/learn","Rust official tutorial","Rust is a systems programming language focused on safety.","GitHub",1,"Rust"),
                ("Go Language","https://go.dev/learn/","Go official learning","Go is an open-source programming language by Google.","GitHub",1,"Go"),
                ("Kubernetes","https://kubernetes.io/zh-cn/docs/home/","K8s official docs","Kubernetes automates container deployment and scaling.","CSDN",1,"K8s"),
                ("DevOps","https://www.atlassian.com/devops","Atlassian DevOps","DevOps bridges development and operations.","Bing",1,"DevOps"),
                ("Frontend Perf","https://web.dev/performance/","Google Web Dev","Frontend optimization improves user experience.","CSDN",1,"Frontend"),
                ("Backend Arch","https://microservices.io/patterns/","Architecture patterns","Backend patterns include monolith, microservices, event-driven.","Baidu",1,"Backend"),
                ("Software Testing","https://testing.googleblog.com/","Google Testing Blog","Testing ensures software quality.","GitHub",1,"Testing"),
                ("CI/CD","https://docs.github.com/en/actions","GitHub Actions docs","CI/CD automates build, test and deploy pipelines.","GitHub",1,"CI/CD"),
                ("Data Warehouse","https://www.kimballgroup.com/","Kimball Group","Data warehouses support analytical decision making.","Baidu",1,"DWH"),
                ("ETL Process","https://www.talend.com/learning-center/what-is-etl/","Talend ETL"," ETL extracts, transforms and loads data.","Bing",1,"ETL"),
                ("Data Viz","https://www.tableau.com/learn/whitepapers/visual-best-practices","Tableau best practices","Data visualization turns data into charts and graphs.","CSDN",1,"Viz"),
                ("Model Deploy","https://www.mlflow.org/docs/latest/deployment/index.html","MLflow deployment","ML model deployment puts models into production.","GitHub",1,"MLOps"),
                ("AI Agents","https://docs.langchain.com/docs/modules/agents/","LangChain Agent docs","AI agents autonomously plan and execute tasks.","Zhihu",1,"Agent"),
                ("LLM Fine-tune","https://huggingface.co/docs/transformers/training","Transformers training","Fine-tuning adapts pre-trained models to specific tasks.","GitHub",1,"LLM"),
                ("Knowledge Graph","https://neo4j.com/use-cases/knowledge-graph/","Neo4j knowledge graphs","Knowledge graphs represent entities and relationships.","Baidu",1,"KG"),
                ("Recommend Sys","https://github.com/microsoft/recommenders","Microsoft RecBole","Recommendation systems predict user preferences.","GitHub",1,"RecSys"),
                ("Speech Recognition","https://github.com/openai/whisper","OpenAI Whisper","Speech recognition converts audio to text.","GitHub",1,"ASR"),
                ("Image Generation","https://stability.ai/stable-diffusion","Stable Diffusion","Image generation AI creates images from text.","Baidu",1,"ImageGen"),
                ("Autonomous Driving","https://www.autoware.org/","Autoware platform","Self-driving cars use sensors and algorithms.","Bing",1,"AutoDrive"),
                ("Smart Customer Service","https://www.dialogflow.com/","Dialogflow","Chatbots use NLP to answer customer questions.","CSDN",1,"Chatbot"),
                ("Smart Contracts","https://docs.soliditylang.org/zh/latest/","Solidity docs","Smart contracts are self-executing blockchain programs.","GitHub",1,"SmartContract"),
                ("Metaverse","https://www.metaversestandards.org/","Metaverse Standards","The metaverse is a shared 3D virtual space.","Zhihu",1,"Metaverse"),
                ("Xinchuang","https://www.iscas.ac.cn/","ISCAS","Xinchuang is China IT self-reliance initiative.","Baidu",1,"Xinchuang"),
                ("Smart City","https://www.ibm.com/topics/smart-city","IBM Smart City","Smart cities use IoT and AI for urban management.","Bing",1,"SmartCity"),
            ]
            for item in data:
                conn.execute("INSERT INTO data_warehouse (title,url,summary,content,source_name,source_id,keyword,collected_at) VALUES (?,?,?,?,?,?,?,?)",
                           (item[0], item[1], item[2], item[3], item[4], item[5], item[6], now))
            print("[Seed] Data warehouse created (55 items)")

        conn.commit()
        conn.execute("PRAGMA foreign_keys=ON")
