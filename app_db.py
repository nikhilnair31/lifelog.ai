import os
import sqlite3

# region DatabaseManager
class DatabaseManager:
    def __init__(self):
        self.db_path = 'data/sql/data.db'
        self.sql_folder_path = 'data/sql/'

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
        (timestamp TEXT, from_timestamp TEXT, to_timestamp TEXT, payload TEXT, content_text TEXT)
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
    def save_to_audio_db(self, timestamp, audio_path, transcript_text):
        print(f'Saving to Audio DB...')

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO audio VALUES (?, ?, ?)", (timestamp, audio_path, transcript_text))
        conn.commit()
        conn.close()

        print(f'Saved!\n')
    def save_to_summary_db(self, timestamp, from_timestamp, to_timestamp, payload, content_text):
        print(f'Saving to Summary DB...')

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO summary VALUES (?, ?, ?, ?, ?)", (timestamp, from_timestamp, to_timestamp, payload, content_text))
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
    
    def retrieve_contents_for_livesummary(self, current_timestamp):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if the summary table is empty
        cursor.execute("SELECT * FROM summary")
        summary_rows = cursor.fetchall()

        # If summary table is empty
        if not summary_rows:
            cursor.execute("SELECT MIN(timestamp) FROM (SELECT MIN(timestamp) AS timestamp FROM screenshots UNION ALL SELECT MIN(timestamp) AS timestamp FROM audio UNION ALL SELECT MIN(timestamp) AS timestamp FROM photos)")
            to_timestamp = cursor.fetchone()[0]

            cursor.execute("SELECT description_text FROM screenshots")
            screenshots_description_text_rows = cursor.fetchall()
            cursor.execute("SELECT description_text FROM photos")
            photos_description_text_rows = cursor.fetchall()
            cursor.execute("SELECT transcript_text FROM audio")
            audio_transcript_text_rows = cursor.fetchall()
        else:
            # Get the last timestamp from the summary table
            cursor.execute("SELECT to_timestamp FROM summary ORDER BY to_timestamp DESC LIMIT 1")
            to_timestamp = cursor.fetchone()[0]

            # Pull rows less than current timestamp and greater than last timestamp
            cursor.execute("SELECT description_text FROM screenshots WHERE timestamp > ? AND timestamp < ?", (to_timestamp, current_timestamp))
            screenshots_description_text_rows = cursor.fetchall()
            cursor.execute("SELECT description_text FROM photos WHERE timestamp > ? AND timestamp < ?", (to_timestamp, current_timestamp))
            photos_description_text_rows = cursor.fetchall()
            cursor.execute("SELECT transcript_text FROM audio WHERE timestamp > ? AND timestamp < ?", (to_timestamp, current_timestamp))
            audio_transcript_text_rows = cursor.fetchall()

        conn.commit()
        conn.close()

        screenshots_description_text_rows = [row[0] for row in screenshots_description_text_rows]
        photos_description_text_rows = [row[0] for row in photos_description_text_rows]
        audio_transcript_text_rows = [row[0] for row in audio_transcript_text_rows]

        return to_timestamp, screenshots_description_text_rows, photos_description_text_rows, audio_transcript_text_rows

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