import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from pathlib import Path
import bcrypt
import config

class Database:
    def __init__(self, db_url=None):
        self.db_url = db_url or config.DATABASE_URL
        self.is_postgres = self.db_url.startswith('postgresql://')
        
        if not self.is_postgres:
            db_path = self.db_url.replace('sqlite:///', '')
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            self.db_path = db_path
        
        self.init_tables()
    
    def get_connection(self):
        if self.is_postgres:
            return psycopg2.connect(self.db_url)
        else:
            return sqlite3.connect(self.db_path)
    
    def init_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.is_postgres:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_vip BOOLEAN DEFAULT FALSE,
                    vip_expire TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    age INTEGER,
                    gender TEXT,
                    constitution TEXT,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_log (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    ip TEXT,
                    user_agent TEXT,
                    UNIQUE(user_id, date),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registration_log (
                    id SERIAL PRIMARY KEY,
                    ip TEXT NOT NULL,
                    date TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    UNIQUE(ip, date)
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_vip BOOLEAN DEFAULT 0,
                    vip_expire TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    age INTEGER,
                    gender TEXT,
                    constitution TEXT,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    ip TEXT,
                    user_agent TEXT,
                    UNIQUE(user_id, date),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registration_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT NOT NULL,
                    date TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    UNIQUE(ip, date)
                )
            """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, password, email, ip):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            if self.is_postgres:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, email)
                    VALUES (%s, %s, %s) RETURNING id
                """, (username, password_hash.decode('utf-8'), email if email else None))
                user_id = cursor.fetchone()[0]
            else:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, email)
                    VALUES (?, ?, ?)
                """, (username, password_hash, email if email else None))
                user_id = cursor.lastrowid
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            if self.is_postgres:
                cursor.execute("""
                    INSERT INTO registration_log (ip, date, count)
                    VALUES (%s, %s, 1)
                    ON CONFLICT(ip, date) DO UPDATE SET count = registration_log.count + 1
                """, (ip, today))
            else:
                cursor.execute("""
                    INSERT INTO registration_log (ip, date, count)
                    VALUES (?, ?, 1)
                    ON CONFLICT(ip, date) DO UPDATE SET count = count + 1
                """, (ip, today))
            
            conn.commit()
            conn.close()
            
            return True, "注册成功", user_id
            
        except (sqlite3.IntegrityError, psycopg2.IntegrityError) as e:
            if 'username' in str(e):
                return False, "用户名已存在", None
            return False, "注册失败", None
        except Exception as e:
            return False, f"注册失败: {str(e)}", None
    
    def verify_user(self, username, password):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.is_postgres:
                cursor.execute("""
                    SELECT id, username, password_hash, email
                    FROM users WHERE username = %s
                """, (username,))
            else:
                cursor.execute("""
                    SELECT id, username, password_hash, email
                    FROM users WHERE username = ?
                """, (username,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return False, "用户名或密码错误", None
            
            if self.is_postgres:
                user_id, username, password_hash, email = row
            else:
                user_id, username, password_hash, email = row
            
            password_hash_bytes = password_hash.encode('utf-8') if isinstance(password_hash, str) else password_hash
            
            if bcrypt.checkpw(password.encode('utf-8'), password_hash_bytes):
                return True, "登录成功", {
                    'id': user_id,
                    'username': username,
                    'email': email
                }
            else:
                return False, "用户名或密码错误", None
                
        except Exception as e:
            return False, f"登录失败: {str(e)}", None
    
    def update_last_login(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.is_postgres:
            cursor.execute("""
                UPDATE users SET last_login = %s WHERE id = %s
            """, (datetime.now(), user_id))
        else:
            cursor.execute("""
                UPDATE users SET last_login = ? WHERE id = ?
            """, (datetime.now(), user_id))
        
        conn.commit()
        conn.close()
    
    def check_ip_register_limit(self, ip, max_per_day=3):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if self.is_postgres:
            cursor.execute("""
                SELECT count FROM registration_log
                WHERE ip = %s AND date = %s
            """, (ip, today))
        else:
            cursor.execute("""
                SELECT count FROM registration_log
                WHERE ip = ? AND date = ?
            """, (ip, today))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] >= max_per_day:
            return False
        return True
    
    def get_profile(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.is_postgres:
            cursor.execute("""
                SELECT age, gender, constitution, location, created_at, updated_at
                FROM profiles WHERE user_id = %s
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT age, gender, constitution, location, created_at, updated_at
                FROM profiles WHERE user_id = ?
            """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'age': row[0],
                'gender': row[1],
                'constitution': row[2],
                'location': row[3],
                'created_at': row[4],
                'updated_at': row[5]
            }
        return None
    
    def save_profile(self, user_id, age, gender, constitution, location):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.is_postgres:
            cursor.execute("SELECT id FROM profiles WHERE user_id = %s", (user_id,))
        else:
            cursor.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,))
        
        existing = cursor.fetchone()
        
        if existing:
            if self.is_postgres:
                cursor.execute("""
                    UPDATE profiles
                    SET age=%s, gender=%s, constitution=%s, location=%s, updated_at=%s
                    WHERE user_id=%s
                """, (age, gender, constitution, location, datetime.now(), user_id))
            else:
                cursor.execute("""
                    UPDATE profiles
                    SET age=?, gender=?, constitution=?, location=?, updated_at=?
                    WHERE user_id=?
                """, (age, gender, constitution, location, datetime.now(), user_id))
        else:
            if self.is_postgres:
                cursor.execute("""
                    INSERT INTO profiles (user_id, age, gender, constitution, location)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, age, gender, constitution, location))
            else:
                cursor.execute("""
                    INSERT INTO profiles (user_id, age, gender, constitution, location)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, age, gender, constitution, location))
        
        conn.commit()
        conn.close()
    
    def check_daily_limit(self, user_id, limit):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if self.is_postgres:
            cursor.execute("""
                SELECT count FROM usage_log
                WHERE user_id = %s AND date = %s
            """, (user_id, today))
        else:
            cursor.execute("""
                SELECT count FROM usage_log
                WHERE user_id = ? AND date = ?
            """, (user_id, today))
        
        row = cursor.fetchone()
        
        if row:
            count = row[0]
            if count >= limit:
                conn.close()
                return False, count
            count += 1
        else:
            count = 1
        
        conn.close()
        return True, count
    
    def log_usage(self, user_id, ip, user_agent):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if self.is_postgres:
            cursor.execute("""
                INSERT INTO usage_log (user_id, date, count, ip, user_agent)
                VALUES (%s, %s, 1, %s, %s)
                ON CONFLICT(user_id, date) DO UPDATE SET
                    count = usage_log.count + 1,
                    ip = %s,
                    user_agent = %s
            """, (user_id, today, ip, user_agent, ip, user_agent))
        else:
            cursor.execute("""
                INSERT INTO usage_log (user_id, date, count, ip, user_agent)
                VALUES (?, ?, 1, ?, ?)
                ON CONFLICT(user_id, date) DO UPDATE SET
                    count = count + 1,
                    ip = ?,
                    user_agent = ?
            """, (user_id, today, ip, user_agent, ip, user_agent))
        
        conn.commit()
        conn.close()
    
    def get_today_usage(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if self.is_postgres:
            cursor.execute("""
                SELECT count FROM usage_log
                WHERE user_id = %s AND date = %s
            """, (user_id, today))
        else:
            cursor.execute("""
                SELECT count FROM usage_log
                WHERE user_id = ? AND date = ?
            """, (user_id, today))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else 0
    
    def save_conversation(self, user_id, user_message, ai_response):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.is_postgres:
            cursor.execute("""
                INSERT INTO conversations (user_id, user_message, ai_response)
                VALUES (%s, %s, %s)
            """, (user_id, user_message, ai_response))
        else:
            cursor.execute("""
                INSERT INTO conversations (user_id, user_message, ai_response)
                VALUES (?, ?, ?)
            """, (user_id, user_message, ai_response))
        
        conn.commit()
        conn.close()
    
    def get_conversations(self, user_id, limit=20):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.is_postgres:
            cursor.execute("""
                SELECT user_message, ai_response, timestamp
                FROM conversations
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT user_message, ai_response, timestamp
                FROM conversations
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'user_message': row[0],
            'ai_response': row[1],
            'timestamp': row[2]
        } for row in reversed(rows)]
