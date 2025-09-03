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
        self.root.title("🤖 Momo Executive Assistant")
        self.root.geometry("1400x900")
        
        # Modern gradient background
        self.root.configure(bg='#667eea')
        
        # Configure modern styling
        self.setup_styles()
        
        # Initialize agent
        self.agent = MomoAgent()
        
        # Gmail and Calendar services
        self.gmail_service = None
        self.calendar_service = None
        self.credentials = None
        
        # Data storage
        self.emails = []
        self.classified_emails = []
        self.selected_email = None
        
        # Setup UI
        self.setup_ui()
        
        # Auto-refresh emails every 5 minutes
        self.auto_refresh()
    
    def setup_styles(self):
        """Configure modern styling for the app"""
        style = ttk.Style()
        
        # Configure modern theme
        style.theme_use('clam')
        
        # Modern button styles
        style.configure('Modern.TButton',
                       background='#007bff',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.map('Modern.TButton',
                 background=[('active', '#0056b3'),
                           ('pressed', '#004085')])
        
        # Primary button style
        style.configure('Primary.TButton',
                       background='#28a745',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.map('Primary.TButton',
                 background=[('active', '#218838'),
                           ('pressed', '#1e7e34')])
        
        # Secondary button style
        style.configure('Secondary.TButton',
                       background='#6c757d',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(12, 6))
        
        style.map('Secondary.TButton',
                 background=[('active', '#545b62'),
                           ('pressed', '#495057')])
        
        # Modern frame styles
        style.configure('Card.TFrame',
                       background='white',
                       relief='flat',
                       borderwidth=1)
        
        # Modern label styles
        style.configure('Title.TLabel',
                       background='white',
                       foreground='#333',
                       font=('Arial', 20, 'bold'))
        
        style.configure('Heading.TLabel',
                       background='white',
                       foreground='#333',
                       font=('Arial', 14, 'bold'))
        
        style.configure('Status.TLabel',
                       background='white',
                       font=('Arial', 12))
        
        # Treeview styling
        style.configure('Modern.Treeview',
                       background='white',
                       foreground='#333',
                       fieldbackground='white',
                       borderwidth=0,
                       font=('Arial', 11))
        
        style.configure('Modern.Treeview.Heading',
                       background='#f8f9fa',
                       foreground='#495057',
                       font=('Arial', 11, 'bold'),
                       borderwidth=1,
                       relief='solid')
    
    def setup_ui(self):
        """Setup the main UI components with modern web app styling"""
        
        # Main container with padding
        main_container = tk.Frame(self.root, bg='#667eea', padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header card
        header_frame = tk.Frame(main_container, bg='white', relief='flat', bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Add rounded corners effect with padding
        header_inner = tk.Frame(header_frame, bg='white', padx=24, pady=24)
        header_inner.pack(fill=tk.BOTH, expand=True)
        
        # Header content
        header_top = tk.Frame(header_inner, bg='white')
        header_top.pack(fill=tk.X)
        
        # Title
        title_label = tk.Label(header_top, text="🤖 Momo Executive Assistant", 
                              font=('Arial', 20, 'bold'), bg='white', fg='#333')
        title_label.pack(side=tk.LEFT)
        
        # Status and buttons container
        header_controls = tk.Frame(header_top, bg='white')
        header_controls.pack(side=tk.RIGHT)
        
        # Status indicator
        self.status_label = tk.Label(header_controls, text="● Not Connected", 
                                    font=('Arial', 12), bg='white', fg='#721c24')
        self.status_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Connect button
        self.login_btn = tk.Button(header_controls, text="Connect Gmail",
                                  command=self.connect_gmail,
                                  bg='#007bff', fg='white', font=('Arial', 11, 'bold'),
                                  relief='flat', padx=20, pady=8, cursor='hand2')
        self.login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        self.refresh_btn = tk.Button(header_controls, text="Refresh Emails",
                                    command=self.refresh_emails, state='disabled',
                                    bg='#6c757d', fg='white', font=('Arial', 11, 'bold'),
                                    relief='flat', padx=20, pady=8, cursor='hand2')
        self.refresh_btn.pack(side=tk.LEFT)
        
        # Dashboard container
        dashboard = tk.Frame(main_container, bg='#667eea')
        dashboard.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid for 3-column layout
        dashboard.grid_columnconfigure(0, weight=0, minsize=300)  # Sidebar
        dashboard.grid_columnconfigure(1, weight=1, minsize=400)  # Main content
        dashboard.grid_columnconfigure(2, weight=0, minsize=350)  # Details
        dashboard.grid_rowconfigure(0, weight=1)
        
        # Left sidebar - Stats and summary
        self.setup_sidebar(dashboard)
        
        # Main content - Email list
        self.setup_main_content(dashboard)
        
        # Right sidebar - Email details and AI summary
        self.setup_details_panel(dashboard)
    
    def setup_sidebar(self, parent):
        """Setup the left sidebar with stats and summary"""
        sidebar_card = tk.Frame(parent, bg='white', relief='flat', bd=0)
        sidebar_card.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        sidebar = tk.Frame(sidebar_card, bg='white', padx=24, pady=24)
        sidebar.pack(fill=tk.BOTH, expand=True)
        
        # Quick Stats
        stats_label = tk.Label(sidebar, text="📊 Quick Stats", 
                              font=('Arial', 14, 'bold'), bg='white', fg='#333')
        stats_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Stats container
        stats_frame = tk.Frame(sidebar, bg='#f8f9fa', relief='flat', bd=1)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        stats_inner = tk.Frame(stats_frame, bg='#f8f9fa', padx=15, pady=15)
        stats_inner.pack(fill=tk.BOTH, expand=True)
        
        self.stats_total = tk.Label(stats_inner, text="📧 Total: 0", 
                                   font=('Arial', 11), bg='#f8f9fa', fg='#333')
        self.stats_total.pack(anchor=tk.W, pady=2)
        
        self.stats_important = tk.Label(stats_inner, text="⭐ Important: 0", 
                                       font=('Arial', 11), bg='#f8f9fa', fg='#333')
        self.stats_important.pack(anchor=tk.W, pady=2)
        
        self.stats_tasks = tk.Label(stats_inner, text="📅 With Tasks: 0", 
                                   font=('Arial', 11), bg='#f8f9fa', fg='#333')
        self.stats_tasks.pack(anchor=tk.W, pady=2)
        
        # Daily Briefing
        briefing_label = tk.Label(sidebar, text="🤖 Daily Briefing", 
                                 font=('Arial', 14, 'bold'), bg='white', fg='#333')
        briefing_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Briefing container
        briefing_frame = tk.Frame(sidebar, bg='#e3f2fd', relief='flat', bd=1)
        briefing_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        briefing_inner = tk.Frame(briefing_frame, bg='#e3f2fd', padx=16, pady=16)
        briefing_inner.pack(fill=tk.BOTH, expand=True)
        
        self.briefing_text = tk.Text(briefing_inner, height=8, wrap=tk.WORD,
                                    bg='#e3f2fd', fg='#333', relief='flat', bd=0,
                                    font=('Arial', 11), cursor='arrow')
        self.briefing_text.pack(fill=tk.BOTH, expand=True)
        self.briefing_text.insert(1.0, "Connect Gmail to see your daily email briefing")
        self.briefing_text.config(state='disabled')
        
        # Labels section
        labels_label = tk.Label(sidebar, text="🏷️ Labels", 
                               font=('Arial', 14, 'bold'), bg='white', fg='#333')
        labels_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.labels_frame = tk.Frame(sidebar, bg='white')
        self.labels_frame.pack(fill=tk.X)
    
    def setup_main_content(self, parent):
        """Setup the main content area with email list"""
        content_card = tk.Frame(parent, bg='white', relief='flat', bd=0)
        content_card.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        content = tk.Frame(content_card, bg='white', padx=24, pady=24)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Header
        content_header = tk.Label(content, text="📧 Classified Emails", 
                                 font=('Arial', 14, 'bold'), bg='white', fg='#333')
        content_header.pack(anchor=tk.W, pady=(0, 15))
        
        # Email list container
        list_container = tk.Frame(content, bg='white')
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure treeview with modern styling
        columns = ('Priority', 'Sender', 'Subject', 'Labels', 'Time')
        self.email_tree = ttk.Treeview(list_container, columns=columns, show='headings', 
                                      height=20, style='Modern.Treeview')
        
        # Configure columns
        self.email_tree.heading('Priority', text='Priority')
        self.email_tree.heading('Sender', text='Sender')
        self.email_tree.heading('Subject', text='Subject')
        self.email_tree.heading('Labels', text='Labels')
        self.email_tree.heading('Time', text='Time')
        
        self.email_tree.column('Priority', width=80, anchor='center')
        self.email_tree.column('Sender', width=150)
        self.email_tree.column('Subject', width=300)
        self.email_tree.column('Labels', width=150)
        self.email_tree.column('Time', width=100, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.email_tree.yview)
        self.email_tree.configure(yscrollcommand=scrollbar.set)
        
        self.email_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.email_tree.bind('<<TreeviewSelect>>', self.on_email_select)
        
        # Loading message
        self.email_tree.insert('', 'end', values=('', '', 'Connect Gmail to see your emails', '', ''))
    
    def setup_details_panel(self, parent):
        """Setup the right details panel with AI summary"""
        details_card = tk.Frame(parent, bg='white', relief='flat', bd=0)
        details_card.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        details = tk.Frame(details_card, bg='white', padx=24, pady=24)
        details.pack(fill=tk.BOTH, expand=True)
        
        # AI Summary header
        summary_header = tk.Frame(details, bg='white')
        summary_header.pack(fill=tk.X, pady=(0, 15))
        
        summary_title = tk.Label(summary_header, text="🤖 AI Email Summary", 
                                font=('Arial', 14, 'bold'), bg='white', fg='#333')
        summary_title.pack(side=tk.LEFT)
        
        # AI status indicator
        self.ai_status = tk.Label(summary_header, text="✨ AI Ready", 
                                 font=('Arial', 10, 'bold'), bg='#d4edda', fg='#155724',
                                 padx=8, pady=4, relief='flat')
        self.ai_status.pack(side=tk.RIGHT)
        
        # Summary container
        summary_container = tk.Frame(details, bg='#f8f9fa', relief='flat', bd=1)
        summary_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        summary_inner = tk.Frame(summary_container, bg='#f8f9fa', padx=20, pady=20)
        summary_inner.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder content
        placeholder_icon = tk.Label(summary_inner, text="📧", font=('Arial', 48), 
                                   bg='#f8f9fa', fg='#6c757d')
        placeholder_icon.pack(pady=(20, 10))
        
        placeholder_title = tk.Label(summary_inner, text="Select an Email", 
                                    font=('Arial', 16, 'bold'), bg='#f8f9fa', fg='#495057')
        placeholder_title.pack(pady=(0, 8))
        
        placeholder_text = tk.Label(summary_inner, 
                                   text="Click on any email to get a simple AI summary\nexplaining what it's about in plain English.",
                                   font=('Arial', 11), bg='#f8f9fa', fg='#6c757d',
                                   justify=tk.CENTER)
        placeholder_text.pack()
        
        # Summary text area (initially hidden)
        self.summary_text = tk.Text(summary_inner, wrap=tk.WORD, height=12,
                                   bg='white', fg='#333', relief='flat', bd=1,
                                   font=('Arial', 12), padx=15, pady=15)
        
        # Action buttons
        actions_frame = tk.Frame(details, bg='white')
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.calendar_btn = tk.Button(actions_frame, text="📅 Add to Calendar",
                                     command=self.add_to_calendar, state='disabled',
                                     bg='#28a745', fg='white', font=('Arial', 11, 'bold'),
                                     relief='flat', padx=15, pady=8, cursor='hand2')
        self.calendar_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        self.regenerate_btn = tk.Button(actions_frame, text="🔄 Regenerate Summary",
                                       command=self.regenerate_summary, state='disabled',
                                       bg='#6c757d', fg='white', font=('Arial', 11, 'bold'),
                                       relief='flat', padx=15, pady=8, cursor='hand2')
        self.regenerate_btn.pack(side=tk.LEFT)
        
        # Email details section
        details_section = tk.Frame(details, bg='white')
        details_section.pack(fill=tk.X, pady=(15, 0))
        
        details_title = tk.Label(details_section, text="📋 Full Email Details", 
                                font=('Arial', 12, 'bold'), bg='white', fg='#495057')
        details_title.pack(anchor=tk.W, pady=(0, 8))
        
        # Details text area
        details_container = tk.Frame(details_section, bg='#f8f9fa', relief='flat', bd=1)
        details_container.pack(fill=tk.X)
        
        self.details_text = tk.Text(details_container, height=8, wrap=tk.WORD,
                                   bg='#f8f9fa', fg='#333', relief='flat', bd=0,
                                   font=('Arial', 10), padx=15, pady=15)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        self.details_text.insert(1.0, "Select an email to view full details")
        self.details_text.config(state='disabled')
    
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
        self.update_status_connected()
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
        self.status_label.config(text="● Fetching emails...", fg='#856404')
    
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
        
        if not self.classified_emails:
            self.email_tree.insert('', 'end', values=('', '', 'No emails found', '', ''))
            return
        
        # Add classified emails
        for email in self.classified_emails:
            # Priority with color indicators
            priority_score = email['priority_score']
            if priority_score > 0.7:
                priority_text = f"🔴 {priority_score:.2f}"
            elif priority_score > 0.5:
                priority_text = f"🟡 {priority_score:.2f}"
            else:
                priority_text = f"🟢 {priority_score:.2f}"
            
            if email['is_important']:
                priority_text += " ⭐"
            
            # Sender (truncated)
            sender = email['sender'].split('<')[0].strip()[:25]
            
            # Subject with task indicator
            subject = email['subject'][:45]
            if email['has_tasks']:
                subject = f"📅 {subject}"
            
            # Labels (truncated)
            labels_text = ", ".join(email['labels'][:2])  # Show max 2 labels
            if len(email['labels']) > 2:
                labels_text += "..."
            
            # Format date
            try:
                date_obj = datetime.strptime(email['date'][:25], '%a, %d %b %Y %H:%M:%S')
                time_text = date_obj.strftime('%m/%d %H:%M')
            except:
                time_text = "Recent"
            
            # Insert email
            self.email_tree.insert('', 'end', values=(
                priority_text,
                sender,
                subject,
                labels_text,
                time_text
            ))
        
        # Update sidebar stats and summary
        self.update_sidebar_stats()
        self.update_status_connected()
    
    def update_sidebar_stats(self):
        """Update the sidebar statistics"""
        total = len(self.classified_emails)
        important = len([e for e in self.classified_emails if e['is_important']])
        with_tasks = len([e for e in self.classified_emails if e['has_tasks']])
        
        # Update stats labels
        self.stats_total.config(text=f"📧 Total: {total}")
        self.stats_important.config(text=f"⭐ Important: {important}")
        self.stats_tasks.config(text=f"📅 With Tasks: {with_tasks}")
        
        # Update daily briefing
        self.update_daily_briefing()
        
        # Update labels
        self.update_labels_display()
    
    def update_daily_briefing(self):
        """Update the daily briefing with AI summary"""
        if not self.classified_emails:
            briefing = "Connect Gmail to see your daily email briefing"
        else:
            total = len(self.classified_emails)
            high_priority = len([e for e in self.classified_emails if e['priority_score'] > 0.7])
            with_tasks = len([e for e in self.classified_emails if e['has_tasks']])
            
            briefing = f"📊 Daily Email Briefing\n\n"
            briefing += f"You have {total} emails today. "
            
            if high_priority > 0:
                briefing += f"{high_priority} require immediate attention. "
            
            if with_tasks > 0:
                briefing += f"{with_tasks} contain tasks or meetings. "
            
            if high_priority == 0 and with_tasks == 0:
                briefing += "Your inbox looks manageable today!"
            
            # Add top senders
            senders = {}
            for email in self.classified_emails:
                sender = email['sender'].split('<')[0].strip()
                senders[sender] = senders.get(sender, 0) + 1
            
            if senders:
                top_sender = max(senders.items(), key=lambda x: x[1])
                briefing += f"\n\nMost emails from: {top_sender[0]} ({top_sender[1]} emails)"
        
        self.briefing_text.config(state='normal')
        self.briefing_text.delete(1.0, tk.END)
        self.briefing_text.insert(1.0, briefing)
        self.briefing_text.config(state='disabled')
    
    def update_labels_display(self):
        """Update the labels display in sidebar"""
        # Clear existing labels
        for widget in self.labels_frame.winfo_children():
            widget.destroy()
        
        if not self.classified_emails:
            no_labels = tk.Label(self.labels_frame, text="No labels yet", 
                               font=('Arial', 10), bg='white', fg='#999',
                               style='italic')
            no_labels.pack(pady=10)
            return
        
        # Count labels
        label_counts = {}
        for email in self.classified_emails:
            for label in email['labels']:
                label_counts[label] = label_counts.get(label, 0) + 1
        
        # Display top labels
        for label, count in sorted(label_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            label_frame = tk.Frame(self.labels_frame, bg='white', relief='flat', bd=1)
            label_frame.pack(fill=tk.X, pady=2)
            
            label_inner = tk.Frame(label_frame, bg='#f8f9fa', padx=8, pady=4)
            label_inner.pack(fill=tk.X)
            
            label_name = tk.Label(label_inner, text=label, 
                                 font=('Arial', 10), bg='#f8f9fa', fg='#495057')
            label_name.pack(side=tk.LEFT)
            
            label_count = tk.Label(label_inner, text=str(count), 
                                  font=('Arial', 10, 'bold'), bg='#007bff', fg='white',
                                  padx=6, pady=2, relief='flat')
            label_count.pack(side=tk.RIGHT)
    
    def update_status_connected(self):
        """Update status to show connected state"""
        self.status_label.config(text="● Connected ✓", fg='#155724')
        self.refresh_btn.config(state='normal', bg='#007bff')
    
    def on_email_select(self, event):
        """Handle email selection in the treeview"""
        selection = self.email_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        try:
            index = self.email_tree.index(item)
            if index < len(self.classified_emails):
                email = self.classified_emails[index]
                self.selected_email = email
                self.show_email_details(email)
                self.generate_ai_summary(email)
        except (IndexError, tk.TclError):
            pass
    
    def show_email_details(self, email):
        """Show email details in the details panel"""
        details = f"""From: {email['sender']}
Subject: {email['subject']}
Date: {email['date']}
Priority Score: {email['priority_score']:.2f}
Labels: {', '.join(email['labels'])}
Has Tasks: {'Yes' if email['has_tasks'] else 'No'}

Content:
{email['body']}
"""
        
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
        self.details_text.config(state='disabled')
        
        # Enable action buttons
        self.calendar_btn.config(state='normal' if email['has_tasks'] else 'disabled')
        self.regenerate_btn.config(state='normal')
    
    def generate_ai_summary(self, email):
        """Generate AI summary for the selected email"""
        # Clear placeholder and show loading
        for widget in self.summary_text.master.winfo_children():
            widget.destroy()
        
        # Loading indicator
        loading_frame = tk.Frame(self.summary_text.master, bg='#f8f9fa')
        loading_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        loading_spinner = tk.Label(loading_frame, text="🔄", font=('Arial', 32), 
                                  bg='#f8f9fa', fg='#007bff')
        loading_spinner.pack(pady=(20, 10))
        
        loading_text = tk.Label(loading_frame, text="Generating AI summary...", 
                               font=('Arial', 12), bg='#f8f9fa', fg='#007bff')
        loading_text.pack()
        
        # Generate summary in background
        def generate_summary():
            try:
                # Use the agent to generate summary (simplified version)
                summary = f"This email from {email['sender']} is about {email['subject']}. "
                if email['has_tasks']:
                    summary += "It contains actionable tasks or meeting requests. "
                if email['priority_score'] > 0.7:
                    summary += "This is a high-priority email that requires immediate attention."
                elif email['priority_score'] > 0.5:
                    summary += "This is a medium-priority email."
                else:
                    summary += "This is a low-priority email."
                
                # Update UI in main thread
                self.root.after(0, lambda: self.show_ai_summary(summary))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_summary_error(str(e)))
        
        threading.Thread(target=generate_summary, daemon=True).start()
    
    def show_ai_summary(self, summary):
        """Show the generated AI summary"""
        # Clear loading indicator
        for widget in self.summary_text.master.winfo_children():
            widget.destroy()
        
        # Summary header
        header_frame = tk.Frame(self.summary_text.master, bg='#f8f9fa')
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        ai_badge = tk.Label(header_frame, text="✨ AI SUMMARY", 
                           font=('Arial', 10, 'bold'), bg='#007bff', fg='white',
                           padx=12, pady=6, relief='flat')
        ai_badge.pack(side=tk.LEFT)
        
        word_count = tk.Label(header_frame, text=f"{len(summary.split())} words", 
                             font=('Arial', 10, 'bold'), bg='rgba(0,123,255,0.1)', fg='#007bff',
                             padx=8, pady=4, relief='flat')
        word_count.pack(side=tk.RIGHT)
        
        # Summary content
        summary_frame = tk.Frame(self.summary_text.master, bg='white', relief='flat', bd=1)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        summary_text = tk.Text(summary_frame, wrap=tk.WORD, height=8,
                              bg='white', fg='#333', relief='flat', bd=0,
                              font=('Arial', 13), padx=18, pady=18)
        summary_text.pack(fill=tk.BOTH, expand=True)
        summary_text.insert(1.0, summary)
        summary_text.config(state='disabled')
        
        # Footer
        footer_frame = tk.Frame(self.summary_text.master, bg='#f8f9fa')
        footer_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        footer_text = tk.Label(footer_frame, text="Generated with AI • Conversational summary", 
                              font=('Arial', 9), bg='#f8f9fa', fg='#6c757d')
        footer_text.pack()
    
    def show_summary_error(self, error):
        """Show error message when summary generation fails"""
        # Clear loading indicator
        for widget in self.summary_text.master.winfo_children():
            widget.destroy()
        
        error_frame = tk.Frame(self.summary_text.master, bg='#f8f9fa')
        error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        error_icon = tk.Label(error_frame, text="⚠️", font=('Arial', 32), 
                             bg='#f8f9fa', fg='#dc3545')
        error_icon.pack(pady=(20, 10))
        
        error_text = tk.Label(error_frame, text=f"Failed to generate summary:\n{error}", 
                             font=('Arial', 11), bg='#f8f9fa', fg='#dc3545',
                             justify=tk.CENTER)
        error_text.pack()
    
    def regenerate_summary(self):
        """Regenerate AI summary for the selected email"""
        if self.selected_email:
            self.generate_ai_summary(self.selected_email)
    
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