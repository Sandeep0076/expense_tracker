import sqlite3
from datetime import datetime, timedelta
import random

class Database:
    def __init__(self, db_name='expense_tracker.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.add_columns()
        self.insert_categories()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                item_type TEXT,
                quantity REAL DEFAULT 1,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                store_name TEXT,
                amount REAL NOT NULL
            )
        ''')
        self.conn.commit()
    def insert_categories(self):
        categories = [
            'Housing', 'Utilities', 'Transportation', 'Groceries', 'Healthcare', 'Insurance',
            'Savings and Investments', 'Debt Repayment', 'Personal Care', 'Entertainment and Leisure',
            'Income', 'Other'
        ]
        self.cursor.executemany('''
            INSERT OR IGNORE INTO categories (name) VALUES (?)
        ''', [(category,) for category in categories])
        self.conn.commit()

    def add_columns(self):
        self.cursor.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'item_type' not in columns:
            self.cursor.execute("ALTER TABLE transactions ADD COLUMN item_type TEXT")
        if 'quantity' not in columns:
            self.cursor.execute("ALTER TABLE transactions ADD COLUMN quantity REAL DEFAULT 1")
        self.conn.commit()

    def add_transaction(self, amount, category, date, type, store_name, item, item_type, quantity=1):
        self.cursor.execute('''
            INSERT INTO transactions (item, item_type, quantity, category, date, type, store_name, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item, item_type, quantity, category, date, type, store_name, amount))
        self.conn.commit()

    def get_transactions(self):
        self.cursor.execute('''
            SELECT item, item_type, amount, category, store_name, date
            FROM transactions
            ORDER BY date DESC
        ''')
        return self.cursor.fetchall()

    def get_categories(self):
        self.cursor.execute('SELECT name FROM categories')
        return [category[0] for category in self.cursor.fetchall()]  
    def get_balance(self):
        self.cursor.execute('''
            SELECT COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE -amount END), 0)
            FROM transactions
        ''')
        return self.cursor.fetchone()[0]
    
    def get_loan(self):
        return 9000

    def get_savings(self):
        return 1500

    def get_expenses_by_category(self, start_date, end_date):
        self.cursor.execute('''
            SELECT category, SUM(amount)
            FROM transactions
            WHERE type = 'expense' AND date BETWEEN ? AND ?
            GROUP BY category
        ''', (start_date, end_date))
        return self.cursor.fetchall()

    def get_monthly_expenses(self, year, month):
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-31"
        self.cursor.execute('''
            SELECT date, SUM(amount)
            FROM transactions
            WHERE type = 'expense' AND date BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date
        ''', (start_date, end_date))
        return self.cursor.fetchall()
    
    def populate_with_artificial_data(self):
        self.cursor.execute("SELECT COUNT(*) FROM transactions")
        if self.cursor.fetchone()[0] > 0:
            return

        categories = [
            'Housing', 'Utilities', 'Transportation', 'Groceries', 'Healthcare',
            'Insurance', 'Savings and Investments', 'Debt Repayment',
            'Personal Care', 'Entertainment and Leisure'
        ]
        stores = ['Amazon', 'Walmart', 'Target', 'Costco', 'Safeway', 'CVS', 'Home Depot']
        items = ['Groceries', 'Electronics', 'Clothes', 'Books', 'Furniture', 'Medicine', 'Tools']
        item_types = ['Fruits', 'Vegetables', 'Meat', 'Dairy', 'Electronics', 'Household', 'Personal']
        current_date = datetime.now()
        
        for i in range(30):
            date = (current_date - timedelta(days=i)).strftime('%Y-%m-%d')
            
            for _ in range(random.randint(1, 3)):
                amount = round(random.uniform(10, 200), 2)
                category = random.choice(categories)
                store_name = random.choice(stores)
                item = random.choice(items)
                item_type = random.choice(item_types)
                quantity = random.randint(1, 5)
                self.add_transaction(amount, category, date, 'expense', store_name, item, item_type, quantity)
            
            if random.random() < 0.2:
                amount = round(random.uniform(500, 3000), 2)
                self.add_transaction(amount, 'Income', date, 'income', 'Employer', 'Salary', 'Wages', 1)

        self.conn.commit()

    def clear_all_data(self):
        self.cursor.execute("DELETE FROM transactions")
        self.conn.commit()
        
    def list_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        return [table[0] for table in tables]
    
    def update_transaction_categories(self):
        category_mapping = {
            'Rent': 'Housing',
            'Entertainment': 'Entertainment and Leisure'
        }
        for old_category, new_category in category_mapping.items():
            self.cursor.execute('''
                UPDATE transactions
                SET category = ?
                WHERE category = ?
            ''', (new_category, old_category))
        self.conn.commit()

    def close(self):
        self.conn.close()