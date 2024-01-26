import sqlite3

class ManageDB:
    def __init__(self, post_db_path):
        self.conn = sqlite3.connect(post_db_path)
        self.cursor = self.conn.cursor()
        self._setup_database()
    
    def _setup_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS frontend_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                domain TEXT,
                frontend_code TEXT
            )
        ''')
        self.conn.commit()

    def _collect_data(self):
        conn = sqlite3.connect("C:/Users/bruker/Desktop/WebScraperDriftDesignV010/updated_website.db")
        cursor = conn.cursor()
        cursor.execute('SELECT category_id, domain FROM html_files')
        result = cursor.fetchall()

        domains = {}
        print("Collected data")
        print(len(result))
        start_index = 5478

        for index, row in enumerate(result):
            if index > start_index:
                category_id, domain_name = row
                if category_id not in domains:
                    domains[category_id] = []
                domains[category_id].append(domain_name)
            else:
                print(index)
        return domains

    def _insert_data(self, post_db_path, category_id, domain, html):
        self.conn = sqlite3.connect(post_db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('INSERT INTO frontend_files (category_id, domain, frontend_code) VALUES (?, ?, ?)', (category_id, domain, html))
        self.conn.commit()
    
    def _close_database(self):
        self.conn.close()
