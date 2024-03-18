import os
import time
import datetime
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class AgentManager:
    def __init__(self, configManager, controlManager, modelManager, databaseManager, mediaManager):
        self.configManager = configManager
        self.controlManager = controlManager
        self.modelManager = modelManager
        self.databaseManager = databaseManager
        self.mediaManager = mediaManager

        self.agent_livesummary_loop_time_in_min = self.configManager.get_config("agent_livesummary_loop_time_in_min") * 60
        self.agent_livesummary_text_model = self.configManager.get_config("agent_livesummary_text_model")
        self.send_to_email_id = self.configManager.get_config("send_to_email_id")
        self.agent_livesummary_hour_to_send_summary = self.configManager.get_config("agent_livesummary_hour_to_send_summary")
        self.agent_livesummary_sent_email_for_day = self.configManager.get_config("agent_livesummary_sent_email_for_day")

        self.default_system_prompt = """
            You are the user's helper who is inside their desktop.
            You are provided with some or all the following:
            - A running summary of the user's activity
            - Descriptions of their desktop's screenshot
            - Descriptions of their webcam's images 
            - Transcripts of their desktop's audio
            Summarize with cool details. Be precise.
        """
    
    def agent_live_summarizer(self):
        print(f'Live Summarizer\n')

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        to_timestamp, screenshots_description_text_rows, photos_description_text_rows, audio_transcript_text_rows = self.databaseManager.retrieve_all_sources_text_content_for_livesummary(timestamp)
        last_summary = self.databaseManager.retrieve_last_summary_for_livesummary()

        # FIXME: Figure out how to improve this
        len_filter = 100
        screenshots_description_text = '\n'.join(screenshots_description_text_rows[:len_filter])
        photos_description_text = '\n'.join(photos_description_text_rows[:len_filter])
        audio_transcript_text = '\n'.join(audio_transcript_text_rows[:len_filter])

        default_user_prompt = f"Running Summary:\n{last_summary}\nScreenshots Descriptions:\n{screenshots_description_text}\nPhotos Descriptions:\n{photos_description_text}\nAudio Transcripts:\n{audio_transcript_text}"
        print(f"default_user_prompt\n{default_user_prompt}\n")

        # Take all text and summarize
        payload = {
            "model": self.agent_livesummary_text_model,
            "messages": [
                {
                    "role": "system",
                    "content": self.default_system_prompt
                },
                {
                    "role": "user",
                    "content": default_user_prompt
                }
            ],
            "max_tokens": 256,
            "temperature": 0.1
        }
        # print(f"payload: {payload}")
        summarize_text = self.modelManager.send_text_to_llm_api(payload)

        # Save to SQL
        self.databaseManager.save_to_summary_db(timestamp, to_timestamp, timestamp, str(payload), summarize_text)
        
    def agent_day_summary_ping(self):
        print(f'Day Summary Ping\n')
        
        # Get the current time
        current_time = datetime.datetime.now()
        
        # Check if it's 9PM
        if current_time.hour == self.agent_livesummary_hour_to_send_summary and not self.agent_livesummary_sent_email_for_day:
            print(f'Current Hour: {current_time.hour}\n')
            last_summary = self.databaseManager.retrieve_last_summary_for_livesummary()
            self.send_html_email(
                subject="lifelog.ai Summary",
                recipient_email=self.send_to_email_id,
                message=last_summary
            )
            self.agent_livesummary_sent_email_for_day = True
            print("Summary sent!")
        else:            
            print(f'Not the time to send summary\n')

    def send_html_email(self, subject, recipient_email, message):
        # Sender email and password from .env
        sender_email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")
        
        # Load the HTML template
        with open(".\email\email_template.html", "r") as file:
            html_template = file.read()

        # Split the message by line breaks and wrap each paragraph in a <td> tag
        paragraphs = message.split('\n')
        print(f"len of paragraphs: {len(paragraphs)}")
        formatted_message = ''.join(f'<tr><td style="padding: 8px 20px;">{p}</td></tr>' for p in paragraphs if p.strip())
        
        # Replace the placeholder in the template with actual content
        html_content = html_template.format(
            message=formatted_message
        )
        
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Record the MIME types
        part = MIMEText(html_content, 'html')
        
        # Attach parts into message container
        msg.attach(part)
        
        # Set up the SMTP server
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.close()
            
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def agent_loop(self):
        print(f'Agent Loop\n')

        while self.controlManager.is_running():        
            print(f'Running Agent Loop')
            
            self.agent_live_summarizer()
            self.agent_day_summary_ping()
            
            if self.controlManager.stop_event.wait(self.agent_livesummary_loop_time_in_min):
                break