import pymysql

# আপনার দেওয়া TiDB Serverless এর ডিটেইলস
DB_HOST = "gateway03.us-west-2.prod.aws.tidbcloud.com"
DB_PORT = 4000
DB_USER = "2bGjLwWTPbAgMCo.root"
DB_PASS = "cb4PgMb5gfr8HW4t"
DB_NAME = "gajarbotol_db"  # ডাটাবেসের নাম (এটি কোড নিজেই অটোমেটিক তৈরি করে নেবে)

def get_connection():
    try:
        # প্রথমে কোনো ডাটাবেস সিলেক্ট না করেই কানেক্ট করব, যাতে ডাটাবেস না থাকলে তৈরি করা যায়
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
            ssl={"ssl_disabled": False}  # TiDB Serverless এর জন্য SSL বাধ্যতামূলক
        )
        cursor = conn.cursor()
        # ডাটাবেস না থাকলে তা তৈরি করবে
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        # এবার ডাটাবেসটি সিলেক্ট করবে
        conn.select_db(DB_NAME)
        return conn
    except Exception as e:
        print(f"Database Connection Error: {e}")
        raise e

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # ইউজার টেবিল
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            balance INT DEFAULT 0,
            referred_by BIGINT,
            total_refs INT DEFAULT 0,
            bonus_received BOOLEAN DEFAULT FALSE
        )
        """)
        
        # সেটিংস টেবিল
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INT PRIMARY KEY,
            ref_bonus INT,
            min_withdraw INT
        )
        """)
        
        # চ্যানেল টেবিল
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            channel_username VARCHAR(255) PRIMARY KEY
        )
        """)

        # ডিফল্ট সেটিংস ইনসার্ট করা
        cursor.execute("SELECT * FROM settings WHERE id = 1")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO settings (id, ref_bonus, min_withdraw) VALUES (1, 10, 50)")
            
        conn.close()
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Error in init_db: {e}")
        raise e

# গ্লোবাল স্কোপে ট্রাই-এক্সেপ্ট দিয়ে রান করা হচ্ছে, যাতে ডাটাবেস কানেকশনে কোনো কারণে দেরি হলেও Vercel ক্র্যাশ না করে
try:
    init_db()
except Exception as e:
    print(f"Warning: Database initialization failed during import: {e}")
