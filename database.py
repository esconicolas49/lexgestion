import sqlite3
from pathlib import Path
import json

DB_PATH = Path(__file__).parent / "data" / "prototype.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT, phone TEXT, notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, client_id INTEGER NOT NULL,
            area TEXT, status TEXT, responsible TEXT, deadline TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(client_id) REFERENCES clients(id)
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, responsible TEXT, due_date TEXT,
            priority TEXT, status TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL, storage_path TEXT NOT NULL,
            case_id INTEGER NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(case_id) REFERENCES cases(id)
        );
        """)

def rows(query, params=()):
    with connect() as con:
        return [dict(r) for r in con.execute(query, params).fetchall()]

def add_client(name, email, phone, notes):
    with connect() as con:
        con.execute("INSERT INTO clients(name,email,phone,notes) VALUES(?,?,?,?)",(name,email,phone,notes))

def get_clients():
    return rows("SELECT id,name,email,phone,notes,created_at FROM clients ORDER BY id DESC")

def add_case(title, client_id, area, status, responsible, deadline):
    with connect() as con:
        con.execute("INSERT INTO cases(title,client_id,area,status,responsible,deadline) VALUES(?,?,?,?,?,?)",(title,client_id,area,status,responsible,deadline))

def get_cases():
    return rows("""SELECT cases.id,cases.title,clients.name AS client, cases.area,cases.status,cases.responsible,cases.deadline
                   FROM cases JOIN clients ON clients.id=cases.client_id ORDER BY cases.id DESC""")

def add_task(title, responsible, due_date, priority, status):
    with connect() as con:
        con.execute("INSERT INTO tasks(title,responsible,due_date,priority,status) VALUES(?,?,?,?,?)",(title,responsible,due_date,priority,status))

def get_tasks():
    return rows("SELECT id,title,responsible,due_date,priority,status FROM tasks ORDER BY due_date ASC")

def save_document(filename, storage_path, case_id):
    with connect() as con:
        con.execute("INSERT INTO documents(filename,storage_path,case_id) VALUES(?,?,?)",(filename,storage_path,case_id))

def get_documents():
    return rows("""SELECT documents.id,documents.filename,cases.title AS case_title,documents.created_at
                   FROM documents JOIN cases ON cases.id=documents.case_id ORDER BY documents.id DESC""")
