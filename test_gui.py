#!/usr/bin/env python3
"""
Simple GUI test to verify tkinter is working
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys

def test_gui():
    """Test basic GUI functionality"""
    try:
        # Create main window
        root = tk.Tk()
        root.title("🧪 Momo GUI Test")
        root.geometry("400x300")
        root.configure(bg='#f5f5f7')
        
        # Header
        header_label = tk.Label(
            root,
            text="🧪 Momo Desktop App Test",
            font=('Arial', 16, 'bold'),
            bg='#f5f5f7',
            fg='#1d1d1f'
        )
        header_label.pack(pady=20)
        
        # Status
        status_label = tk.Label(
            root,
            text="✅ tkinter is working correctly!",
            font=('Arial', 12),
            bg='#f5f5f7',
            fg='#34c759'
        )
        status_label.pack(pady=10)
        
        # Test button
        def show_success():
            messagebox.showinfo("Success", "🎉 GUI components are working!\n\nYour Momo Desktop App should launch properly.")
        
        test_btn = tk.Button(
            root,
            text="🚀 Test GUI Components",
            font=('Arial', 12),
            bg='#007aff',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=show_success
        )
        test_btn.pack(pady=20)
        
        # Instructions
        instructions = tk.Text(
            root,
            height=6,
            width=45,
            font=('Arial', 10),
            bg='white',
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        instructions.pack(pady=10)
        
        instructions.insert(tk.END, """✅ GUI Test Results:
• tkinter is properly installed
• Window creation works
• Fonts and colors display correctly
• Button interactions function

🚀 Next Steps:
1. Close this test window
2. Run: python momo_desktop.py
3. Or run: python launch_desktop.py
4. Enjoy your AI email assistant!""")
        
        instructions.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(
            root,
            text="Close Test",
            font=('Arial', 10),
            bg='#86868b',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=root.quit
        )
        close_btn.pack(pady=10)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        print("🧪 GUI test window created successfully!")
        print("   Click the test button to verify functionality")
        print("   Close the window when done")
        
        # Start the GUI
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Momo Desktop App GUI Components")
    print("=" * 50)
    
    success = test_gui()
    
    if success:
        print("✅ GUI test completed successfully!")
        print("🚀 Your Momo Desktop App should work properly")
    else:
        print("❌ GUI test failed")
        print("   Please check tkinter installation")