import os
import sqlite3

# region DatabaseManager
class DatabaseManager:
    def __init__(self, db_path, sql_folder_path):
        self.db_path = db_path
        self.sql_folder_path = sql_folder_path

    def initialize_db(self):
        print(f'Initializing DB...')

        if not os.path.exists(self.sql_folder_path):
            os.makedirs(self.sql_folder_path)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS screenshots 
        (timestamp TEXT, image_path TEXT, ocr_text TEXT, description_text TEXT)
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS photos
        (timestamp TEXT, image_path TEXT, description_text TEXT)
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS audio
        (timestamp TEXT, audio_path TEXT, transcript_text TEXT)
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS summary
        (timestamp TEXT, content_text TEXT)
        ''')
        conn.commit()
        conn.close()

        print(f'Initialized!\n')

    def save_to_screenshot_db(self, timestamp, image_path, ocr_text, description_text):
        print(f'Saving to Screenshots DB...')

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO screenshots VALUES (?, ?, ?, ?)", (timestamp, image_path, ocr_text, description_text))
        conn.commit()
        conn.close()

        print(f'Saved!\n')

    def save_to_photo_db(self, timestamp, image_path, description_text):
        print(f'Saving to Photos DB...')

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO photos VALUES (?, ?, ?)", (timestamp, image_path, description_text))
        conn.commit()
        conn.close()

        print(f'Saved!\n')

    def save_to_summary_db(self, timestamp, content_text):
        print(f'Saving to Summary DB...')

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO summary VALUES (?, ?)", (timestamp, content_text))
        conn.commit()
        conn.close()

        print(f'Saved!\n')

    def retrieve_image_paths_from_db(self, table_name):
        print(f'Retrieving image paths from {table_name}...')

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"SELECT image_path FROM {table_name} WHERE api_response IS NULL OR api_response = '' OR LENGTH(api_response)=0")
        rows = c.fetchall()
        conn.close()

        print(f'Retrieved!\n')

        return [row[0] for row in rows]

    def retrieve_contents_from_db(self, table_name):
        print(f'Retrieving contents from {table_name}...')

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"SELECT content FROM {table_name} WHERE content IS NOT NULL OR content != '' OR LENGTH(content)>0")
        rows = c.fetchall()
        conn.close()

        print(f'Retrieved!\n')

        return [row[0] for row in rows]

    def update_api_response(self, table_name, filepath, response, content):
        print(f'Updating {table_name}...')

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"UPDATE {table_name} SET api_response = ? WHERE image_path = ?", (response, filepath))
        c.execute(f"UPDATE {table_name} SET content = ? WHERE image_path = ?", (content, filepath))
        conn.commit()
        conn.close()

        print(f'Updated!\n')
# endregion