#!/usr/bin/env python3
"""
Momo Desktop App - Email Classification & Calendar Integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import webbrowser

# Gmail and Calendar integration
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Google APIs not available. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

# Email classification logic
from main import MomoAgent, EmailInput

class MomoDesktopApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Momo Executive Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize agent
        self.agent = MomoAgent()
        
        # Gmail and Calendar services
        self.gmail_service = None
        self.calendar_service = None
        self.credentials = None
        
        # Data storage
        self.emails = []
        self.classified_emails = []
        
        # Setup UI
        self.setup_ui()
        
        # Auto-refresh emails every 5 minutes
        self.auto_refresh()
    
    def setup_ui(self):
        """Setup the main UI components"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 Momo Executive Assistant", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left sidebar - Controls
        sidebar_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        sidebar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Gmail login button
        self.login_btn = ttk.Button(sidebar_frame, text="Connect Gmail", 
                                   command=self.connect_gmail)
        self.login_btn.pack(fill=tk.X, pady=5)
        
        # Refresh emails button
        self.refresh_btn = ttk.Button(sidebar_frame, text="Refresh Emails", 
                                     command=self.refresh_emails, state='disabled')
        self.refresh_btn.pack(fill=tk.X, pady=5)
        
        # Status label
        self.status_label = ttk.Label(sidebar_frame, text="Status: Not connected", 
                                     foreground='red')
        self.status_label.pack(pady=10)
        
        # Email summary
        summary_frame = ttk.LabelFrame(sidebar_frame, text="Email Summary", padding="5")
        summary_frame.pack(fill=tk.X, pady=10)
        
        self.summary_text = tk.Text(summary_frame, height=8, width=25, wrap=tk.WORD)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Main content area - Email list
        content_frame = ttk.LabelFrame(main_frame, text="Classified Emails", padding="10")
        content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Email treeview
        columns = ('Priority', 'Sender', 'Subject', 'Labels', 'Time')
        self.email_tree = ttk.Treeview(content_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.email_tree.heading('Priority', text='Priority')
        self.email_tree.heading('Sender', text='Sender')
        self.email_tree.heading('Subject', text='Subject')
        self.email_tree.heading('Labels', text='Labels')
        self.email_tree.heading('Time', text='Time')
        
        self.email_tree.column('Priority', width=80)
        self.email_tree.column('Sender', width=150)
        self.email_tree.column('Subject', width=300)
        self.email_tree.column('Labels', width=150)
        self.email_tree.column('Time', width=120)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.email_tree.yview)
        self.email_tree.configure(yscrollcommand=scrollbar.set)
        
        self.email_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click to open email
        self.email_tree.bind('<Double-1>', self.open_email_details)
        
        # Right sidebar - Email details
        details_frame = ttk.LabelFrame(main_frame, text="Email Details", padding="10")
        details_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        
        self.details_text = scrolledtext.ScrolledText(details_frame, width=40, height=30, wrap=tk.WORD)
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add to calendar button
        self.calendar_btn = ttk.Button(details_frame, text="Add Tasks to Calendar", 
                                      command=self.add_to_calendar, state='disabled')
        self.calendar_btn.grid(row=1, column=0, pady=10, sticky=tk.EW)
    
    def connect_gmail(self):
        """Connect to Gmail using OAuth"""
        if not GOOGLE_AVAILABLE:
            messagebox.showerror("Error", "Google APIs not installed. Please install requirements.")
            return
            
        def auth_thread():
            try:
                # Gmail and Calendar scopes
                SCOPES = [
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/calendar'
                ]
                
                creds = None
                # Check if token.json exists
                if os.path.exists('token.json'):
                    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
                
                # If there are no valid credentials, request authorization
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        # You need to create credentials.json from Google Cloud Console
                        if not os.path.exists('credentials.json'):
                            self.root.after(0, lambda: messagebox.showerror(
                                "Error", 
                                "credentials.json not found!\n\n"
                                "Please:\n"
                                "1. Go to Google Cloud Console\n"
                                "2. Create a project and enable Gmail/Calendar APIs\n"
                                "3. Download credentials.json\n"
                                "4. Place it in this folder"
                            ))
                            return
                        
                        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                        creds = flow.run_local_server(port=0)
                    
                    # Save credentials for next run
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())
                
                # Build services
                self.gmail_service = build('gmail', 'v1', credentials=creds)
                self.calendar_service = build('calendar', 'v3', credentials=creds)
                self.credentials = creds
                
                # Update UI
                self.root.after(0, self.on_gmail_connected)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to connect: {str(e)}"))
        
        # Run authentication in separate thread
        threading.Thread(target=auth_thread, daemon=True).start()
        self.status_label.config(text="Status: Connecting...", foreground='orange')
    
    def on_gmail_connected(self):
        """Called when Gmail connection is successful"""
        self.status_label.config(text="Status: Connected ✓", foreground='green')
        self.refresh_btn.config(state='normal')
        self.calendar_btn.config(state='normal')
        self.refresh_emails()
    
    def refresh_emails(self):
        """Fetch and classify emails from Gmail"""
        if not self.gmail_service:
            return
        
        def fetch_thread():
            try:
                # Fetch recent emails
                results = self.gmail_service.users().messages().list(
                    userId='me', maxResults=20, q='is:unread OR newer_than:3d'
                ).execute()
                
                messages = results.get('messages', [])
                self.emails = []
                
                for msg in messages:
                    # Get email details
                    email_data = self.gmail_service.users().messages().get(
                        userId='me', id=msg['id']
                    ).execute()
                    
                    # Extract email info
                    headers = email_data['payload'].get('headers', [])
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                    
                    # Get email body
                    body = self.extract_email_body(email_data['payload'])
                    
                    email_obj = {
                        'id': msg['id'],
                        'sender': sender,
                        'subject': subject,
                        'body': body,
                        'date': date,
                        'raw_data': email_data
                    }
                    
                    self.emails.append(email_obj)
                
                # Classify emails
                self.classify_emails()
                
                # Update UI
                self.root.after(0, self.update_email_display)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch emails: {str(e)}"))
        
        threading.Thread(target=fetch_thread, daemon=True).start()
        self.status_label.config(text="Status: Fetching emails...", foreground='orange')
    
    def extract_email_body(self, payload):
        """Extract email body from Gmail payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = self.decode_base64(data)
                    break
        elif payload['mimeType'] == 'text/plain':
            data = payload['body']['data']
            body = self.decode_base64(data)
        
        return body[:1000]  # Limit body length
    
    def decode_base64(self, data):
        """Decode base64 email content"""
        import base64
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    
    def classify_emails(self):
        """Classify fetched emails using Momo agent"""
        self.classified_emails = []
        
        for email in self.emails:
            email_input = EmailInput(
                sender=email['sender'],
                subject=email['subject'],
                content=email['body']
            )
            
            classification = self.agent.classify_email(email_input)
            
            classified_email = {
                **email,
                'priority_score': classification['priority_score'],
                'labels': classification['labels'],
                'is_important': classification['is_important'],
                'has_tasks': self.detect_tasks(email['body'])
            }
            
            self.classified_emails.append(classified_email)
        
        # Sort by priority
        self.classified_emails.sort(key=lambda x: x['priority_score'], reverse=True)
    
    def detect_tasks(self, content):
        """Detect if email contains tasks or meeting requests"""
        task_keywords = [
            'meeting', 'call', 'schedule', 'appointment', 'deadline',
            'due date', 'task', 'action item', 'follow up', 'reminder'
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in task_keywords)
    
    def update_email_display(self):
        """Update the email treeview with classified emails"""
        # Clear existing items
        for item in self.email_tree.get_children():
            self.email_tree.delete(item)
        
        # Add classified emails
        for email in self.classified_emails:
            priority_text = f"{email['priority_score']:.2f}"
            if email['is_important']:
                priority_text += " ⭐"
            
            labels_text = ", ".join(email['labels'])
            
            # Format date
            try:
                date_obj = datetime.strptime(email['date'][:25], '%a, %d %b %Y %H:%M:%S')
                time_text = date_obj.strftime('%m/%d %H:%M')
            except:
                time_text = "Recent"
            
            # Insert with color coding
            item = self.email_tree.insert('', 'end', values=(
                priority_text,
                email['sender'][:30],
                email['subject'][:50],
                labels_text,
                time_text
            ))
            
            # Color code by priority
            if email['priority_score'] > 0.7:
                self.email_tree.set(item, 'Priority', f"{priority_text} 🔴")
            elif email['priority_score'] > 0.5:
                self.email_tree.set(item, 'Priority', f"{priority_text} 🟡")
        
        # Update summary
        self.update_summary()
        self.status_label.config(text="Status: Connected ✓", foreground='green')
    
    def update_summary(self):
        """Update email summary in sidebar"""
        total = len(self.classified_emails)
        important = len([e for e in self.classified_emails if e['is_important']])
        with_tasks = len([e for e in self.classified_emails if e['has_tasks']])
        
        summary = f"""📧 Total Emails: {total}
⭐ Important: {important}
📅 With Tasks: {with_tasks}

🏷️ Labels:
"""
        
        # Count labels
        label_counts = {}
        for email in self.classified_emails:
            for label in email['labels']:
                label_counts[label] = label_counts.get(label, 0) + 1
        
        for label, count in sorted(label_counts.items()):
            summary += f"  • {label}: {count}\n"
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
    
    def open_email_details(self, event):
        """Show email details when double-clicked"""
        selection = self.email_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = self.email_tree.index(item)
        email = self.classified_emails[index]
        
        details = f"""From: {email['sender']}
Subject: {email['subject']}
Priority: {email['priority_score']:.2f}
Labels: {', '.join(email['labels'])}
Has Tasks: {'Yes' if email['has_tasks'] else 'No'}

Content:
{email['body']}
"""
        
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
    
    def add_to_calendar(self):
        """Add email tasks to Google Calendar"""
        selection = self.email_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an email first")
            return
        
        item = selection[0]
        index = self.email_tree.index(item)
        email = self.classified_emails[index]
        
        if not email['has_tasks']:
            messagebox.showinfo("Info", "This email doesn't appear to contain tasks")
            return
        
        # Create calendar event
        event = {
            'summary': f"Task: {email['subject']}",
            'description': f"From: {email['sender']}\n\n{email['body'][:500]}",
            'start': {
                'dateTime': (datetime.now() + timedelta(days=1)).isoformat(),
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
                'timeZone': 'America/New_York',
            },
        }
        
        try:
            event = self.calendar_service.events().insert(calendarId='primary', body=event).execute()
            messagebox.showinfo("Success", f"Task added to calendar!\nEvent ID: {event['id']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to calendar: {str(e)}")
    
    def auto_refresh(self):
        """Auto-refresh emails every 5 minutes"""
        if self.gmail_service:
            self.refresh_emails()
        
        # Schedule next refresh
        self.root.after(300000, self.auto_refresh)  # 5 minutes
    
    def run(self):
        """Start the desktop application"""
        self.root.mainloop()

def main():
    print("🚀 Starting Momo Desktop App...")
    app = MomoDesktopApp()
    app.run()

if __name__ == "__main__":
    main()