"""
Extract email template HTML for easy copy-paste to Supabase Dashboard
"""
import re
from pathlib import Path

def extract_sections(content):
    """Extract subject and HTML from markdown template"""
    # Extract subject
    subject_match = re.search(r'## Subject\s*```\s*(.+?)\s*```', content, re.DOTALL)
    subject = subject_match.group(1).strip() if subject_match else "No subject found"
    
    # Extract HTML
    html_match = re.search(r'## HTML\s*```html\s*(.+?)\s*```', content, re.DOTALL)
    html = html_match.group(1).strip() if html_match else "No HTML found"
    
    return subject, html

def print_template(name, filename, supabase_type, subject, html):
    """Print template in copy-paste friendly format"""
    print(f"\n{'='*80}")
    print(f"{name}")
    print(f"{'='*80}")
    print(f"File: {filename}")
    print(f"Supabase Template Type: {supabase_type}")
    print(f"\n{'-'*80}")
    print("SUBJECT:")
    print(f"{'-'*80}")
    print(subject)
    print(f"\n{'-'*80}")
    print("HTML (Copy everything below this line):")
    print(f"{'-'*80}")
    print(html)
    print(f"\n{'='*80}\n")

def main():
    templates_dir = Path("frontend/templates/authentication")
    
    # Templates that map to Supabase built-in types
    templates = [
        ("01-confirmation.md", "Confirmation (Email Verification)", "Confirmation"),
        ("02-magic-link.md", "Magic Link (Passwordless Login)", "Magic Link"),
        ("03-password-reset.md", "Password Reset", "Recovery"),
        ("05-email-changed.md", "Email Change Notification", "Email Change"),
    ]
    
    print("\n" + "="*80)
    print(" SUPABASE EMAIL TEMPLATES - READY FOR UPLOAD")
    print("="*80)
    print("\nInstructions:")
    print("1. Go to: https://supabase.com/dashboard -> Your Project -> Authentication -> Email Templates")
    print("2. Select the template type shown below")
    print("3. Copy the SUBJECT and paste into 'Subject Line' field")
    print("4. Copy the HTML and paste into 'Email Body' field")
    print("5. Click 'Save'")
    print("\n" + "="*80)
    
    for filename, name, supabase_type in templates:
        file_path = templates_dir / filename
        
        if not file_path.exists():
            print(f"\nWarning: {filename} not found, skipping...")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        subject, html = extract_sections(content)
        print_template(name, filename, supabase_type, subject, html)
    
    print("\n" + "="*80)
    print("All templates extracted!")
    print("="*80)
    print("\nNote: Custom templates (welcome, security alerts, etc.) are not")
    print("supported by Supabase's built-in email templates and must be sent")
    print("via your application backend using Supabase's email service or a")
    print("third-party service like SendGrid/Mailgun.")
    print("\n")

if __name__ == "__main__":
    main()
