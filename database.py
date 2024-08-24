import sqlite3
from datetime import datetime, timedelta, date

class Database:
    def __init__(self, db_name='expense_tracker.db'):
        self.conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.add_columns()
        self.insert_categories()
        self.update_date_format()
        self.rename_item_type_to_tag()
    
    def rename_item_type_to_tag(self):
        self.cursor.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'item_type' in columns:
            self.cursor.execute("ALTER TABLE transactions RENAME COLUMN item_type TO tag")
        self.conn.commit()

    def add_transaction(self, amount, category, date, type, store_name, item, tags, quantity=1):
        date_obj = self._parse_date(date)
        self.cursor.execute('''
            INSERT INTO transactions (item, tag, quantity, category, date, type, store_name, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item, ','.join(tags), float(quantity), category, date_obj, type, store_name, float(amount)))
        self.conn.commit()

    def get_transactions(self):
        self.cursor.execute('''
            SELECT item, tag, amount, category, store_name, date
            FROM transactions
            ORDER BY date DESC
        ''')
        return self.cursor.fetchall()

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
                date DATE NOT NULL,
                type TEXT NOT NULL,
                store_name TEXT,
                amount REAL NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                date DATE NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                date DATE NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                date DATE NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                note TEXT NOT NULL,
                color TEXT DEFAULT '#3DD56D'
            )
        ''')
        
        # Add color column to existing notes table if it doesn't exist
        self.cursor.execute("PRAGMA table_info(notes)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'color' not in columns:
            self.cursor.execute("ALTER TABLE notes ADD COLUMN color TEXT DEFAULT '#3DD56D'")
        
        self.conn.commit()

    def add_columns(self):
        for table in ['transactions', 'balances', 'loans', 'savings']:
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns = [column[1] for column in self.cursor.fetchall()]
            if 'date' not in columns:
                self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN date DATE")
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

    def update_date_format(self):
        for table in ['transactions', 'balances', 'loans', 'savings']:
            self.cursor.execute(f"SELECT id, date FROM {table}")
            rows = self.cursor.fetchall()
            for row in rows:
                id, old_date = row
                if isinstance(old_date, str):
                    try:
                        new_date = datetime.strptime(old_date, '%d-%m-%Y').date()
                    except ValueError:
                        try:
                            new_date = datetime.strptime(old_date, '%Y-%m-%d').date()
                        except ValueError:
                            continue
                    self.cursor.execute(f"UPDATE {table} SET date = ? WHERE id = ?", (new_date, id))
        self.conn.commit()

    def get_transaction_for_this_month(self):
        current_date = datetime.now()
        start_date = current_date.replace(day=1).date()
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        self.cursor.execute('''
        SELECT item, category, amount, date
        FROM transactions
        WHERE date BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        return self.cursor.fetchall()

    def get_balance(self):
        self.cursor.execute('SELECT amount FROM balances ORDER BY date DESC LIMIT 1')
        result = self.cursor.fetchone()
        return result[0] if result else 0
    
    def get_loan(self):
        return 13000
    def get_savings(self):
        return 8000

    def get_categories(self):
        self.cursor.execute('SELECT name FROM categories')
        return [category[0] for category in self.cursor.fetchall()]

    def get_expenses_by_category(self, start_date, end_date):
        start_date = self._parse_date(start_date)
        end_date = self._parse_date(end_date)
        self.cursor.execute('''
            SELECT category, SUM(amount)
            FROM transactions
            WHERE type = 'expense' AND date BETWEEN ? AND ?
            GROUP BY category
        ''', (start_date, end_date))
        return self.cursor.fetchall()

    def get_cumulative_spending(self, year, month):
        start_date = date(year, month, 1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        self.cursor.execute('''
            SELECT strftime('%d', date) as day, SUM(amount) OVER (ORDER BY date) as cumulative_total
            FROM transactions
            WHERE date BETWEEN ? AND ?
            GROUP BY day
            ORDER BY day
        ''', (start_date, end_date))
        return self.cursor.fetchall()

    def get_monthly_spending(self, year, month):
        start_date = date(year, month, 1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        self.cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as total_spending
            FROM transactions
            WHERE date BETWEEN ? AND ?
        ''', (start_date, end_date))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def _parse_date(self, date_input):
        if isinstance(date_input, str):
            try:
                return datetime.strptime(date_input, '%d-%m-%Y').date()
            except ValueError:
                return datetime.strptime(date_input, '%Y-%m-%d').date()
        elif isinstance(date_input, datetime):
            return date_input.date()
        elif isinstance(date_input, date):
            return date_input
        else:
            raise ValueError("Invalid date type. Use string, datetime, or date object.")

    def close(self):
        self.conn.close()

    def get_notes(self, date):
        self.cursor.execute('SELECT id, note, color FROM notes WHERE date = ?', (date,))
        return [{'id': row[0], 'text': row[1], 'color': row[2]} for row in self.cursor.fetchall()]

    def add_note(self, date, text, color="#3DD56D"):
        self.cursor.execute('INSERT INTO notes (date, note, color) VALUES (?, ?, ?)', (date, text, color))
        self.conn.commit()
    
    def delete_note(self, note_id):
        self.cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        self.conn.commit()
    

    def has_note(self, date):
        self.cursor.execute('SELECT COUNT(*) FROM notes WHERE date = ?', (date,))
        return self.cursor.fetchone()[0] > 0
    
    def get_dates_with_notes(self):
        self.cursor.execute('SELECT DISTINCT date FROM notes')
        return [row[0] for row in self.cursor.fetchall()]


    def get_expenses_by_month(self, months):
        self.cursor.execute('''
            SELECT strftime('%Y-%m-01', date) as Month, SUM(amount) as Expenses
            FROM transactions
            WHERE date >= date('now', 'start of month', '-' || ? || ' months')
            GROUP BY Month
            ORDER BY Month DESC
        ''', (months,))
        return self.cursor.fetchall()

    def get_expenses_by_category_and_month(self, start_date, end_date):
        self.cursor.execute('''
            SELECT 
                strftime('%Y-%m', date) as Month,
                category,
                SUM(amount) as Expenses
            FROM transactions
            WHERE date BETWEEN ? AND ?
            GROUP BY Month, category
            ORDER BY Month, Expenses DESC
        ''', (start_date, end_date))
        return self.cursor.fetchall()
    
    def get_transactions_with_tags(self, start_date, end_date):
        self.cursor.execute('''
            SELECT strftime('%Y-%m', date) as Month, tag, amount
            FROM transactions
            WHERE date BETWEEN ? AND ?
        ''', (start_date, end_date))
        return self.cursor.fetchall() 
    def get_expenses_by_tag(self, months):
        self.cursor.execute('''
            SELECT tag, amount
            FROM transactions
            WHERE date >= date('now', '-' || ? || ' months')
        ''', (months,))
        transactions = self.cursor.fetchall()
        
        tag_expenses = {}
        for tag, amount in transactions:
            if tag:
                for t in tag.split(','):
                    t = t.strip()
                    tag_expenses[t] = tag_expenses.get(t, 0) + amount
        
        return sorted(tag_expenses.items(), key=lambda x: x[1], reverse=True)
    
    def get_daily_spending(self, start_date, end_date):
        self.cursor.execute('''
            SELECT date, SUM(amount) as total_amount
            FROM transactions
            WHERE date BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date
        ''', (start_date, end_date))
        return self.cursor.fetchall()