import pymysql

# আপনার দেওয়া TiDB Serverless এর ডিটেইলস
DB_HOST = "gateway03.us-west-2.prod.aws.tidbcloud.com"
DB_PORT = 4000
DB_USER = "2bGjLwWTPbAgMCo.root"
DB_PASS = "cb4PgMb5gfr8HW4t"
DB_NAME = "test"  # TiDB এর ডিফল্ট ডাটাবেস নাম

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"ssl_disabled": False} # TiDB Serverless এর জন্য SSL প্রয়োজন
    )

def init_db():
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

    # ডিফল্ট সেটিংস ইনসার্ট (যদি না থাকে)
    cursor.execute("SELECT * FROM settings WHERE id = 1")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO settings (id, ref_bonus, min_withdraw) VALUES (1, 10, 50)")
        
    conn.close()

# অ্যাপ চালু হওয়ার সাথে সাথে টেবিল তৈরি হয়ে যাবে
init_db()