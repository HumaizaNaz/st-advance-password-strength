import streamlit as st
import datetime
import random
import string
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import base64

# Page configuration - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Password Strength Meter", 
    page_icon="🔐", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1rem;
    }
    .info-text {
        color: #424242;
    }
    .password-strong {
        color: #2E7D32;
        font-weight: bold;
    }
    .password-moderate {
        color: #F9A825;
        font-weight: bold;
    }
    .password-weak {
        color: #C62828;
        font-weight: bold;
    }
    .history-item {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'tab' not in st.session_state:
    st.session_state.tab = "check"

# Header
st.markdown("<h1 class='main-header'>🔐 Password Strength Meter & Generator</h1>", unsafe_allow_html=True)

# Function to check password strength
def check_strength(password):
    score = 0
    criteria = {
        "length": len(password) >= 8,
        "uppercase": any(c.isupper() for c in password),
        "lowercase": any(c.islower() for c in password),
        "digits": any(c.isdigit() for c in password),
        "special": any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in password)
    }
    
    # Calculate base score
    score = sum(criteria.values())
    
    # Additional checks for better strength assessment
    if len(password) >= 12:
        score += 0.5
    if len(password) >= 16:
        score += 0.5
        
    # Check for common patterns
    if password.lower() in ["password", "123456", "qwerty", "admin"]:
        score = min(score, 1)
    
    return score, criteria

# Function to get strength label
def get_strength_label(score):
    if score >= 5:
        return "🟢 Strong", "password-strong"
    elif score >= 3:
        return "🟡 Moderate", "password-moderate"
    else:
        return "🔴 Weak", "password-weak"

# Function to check if password is a duplicate
def is_duplicate(password):
    if 'history' not in st.session_state or not st.session_state.history:
        return False
    return sum(1 for p in st.session_state.history if p['password'] == password) >= 2

# Function to generate password
def generate_password(length=12, include_upper=True, include_lower=True, include_digits=True, include_special=True):
    chars = ""
    required_chars = []
    
    if include_lower:
        chars += string.ascii_lowercase
        required_chars.append(random.choice(string.ascii_lowercase))
    if include_upper:
        chars += string.ascii_uppercase
        required_chars.append(random.choice(string.ascii_uppercase))
    if include_digits:
        chars += string.digits
        required_chars.append(random.choice(string.digits))
    if include_special:
        special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
        chars += special_chars
        required_chars.append(random.choice(special_chars))
    
    if not chars:
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        required_chars = [
            random.choice(string.ascii_lowercase),
            random.choice(string.ascii_uppercase),
            random.choice(string.digits),
            random.choice("!@#$%^&*")
        ]
    
    # Ensure we don't require more characters than the length
    required_chars = required_chars[:min(len(required_chars), length)]
    
    # Fill the rest with random characters
    password = required_chars.copy()
    while len(password) < length:
        password.append(random.choice(chars))
    
    # Shuffle the password
    random.shuffle(password)
    return ''.join(password[:length])

# Function to hash password for more secure storage
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()[:10]  # Only store partial hash for demo

# Function to create a downloadable link for password history
def get_download_link(history):
    if not history:
        return None
    
    df = pd.DataFrame(history)
    # Replace actual passwords with hashed versions for the export
    df['password'] = df['password'].apply(hash_password)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="password_history.csv">Download Password History</a>'
    return href

# Create tabs
tabs = ["Check Password", "Generate Password", "Password History", "Statistics"]
selected_tab = st.radio("Select Option:", tabs, horizontal=True)

# Check Password Tab
if selected_tab == "Check Password":
    st.markdown("<h2 class='sub-header'>Check Password Strength</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        password = st.text_input("Enter a password to check its strength", type="password")
        account_name = st.text_input("Enter the account name (optional)")
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("💾 Save Password", use_container_width=True):
            if password:
                if not account_name:
                    account_name = "Unnamed Account"
                score, _ = check_strength(password)
                strength_label, _ = get_strength_label(score)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                st.session_state.history.append({
                    "account": account_name,
                    "password": password,
                    "strength": strength_label,
                    "score": score,
                    "timestamp": timestamp
                })
                st.success(f"✅ Password for '{account_name}' saved successfully!")
            else:
                st.warning("⚠️ Please enter a password to save.")
    
    if password:
        score, criteria = check_strength(password)
        strength_label, css_class = get_strength_label(score)
        
        st.markdown(f"<h3>Strength: <span class='{css_class}'>{strength_label}</span></h3>", unsafe_allow_html=True)
        
        # Progress bar with color
        if score >= 5:
            bar_color = "green"
        elif score >= 3:
            bar_color = "orange"
        else:
            bar_color = "red"
            
        progress_value = min(1.0, max(0.0, score / 6))  # Scale to 0-1 range
        st.progress(progress_value)
        
        # Display criteria in a more organized way
        st.markdown("<h3>Strength Criteria:</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        criteria_list = list(criteria.items())
        half = len(criteria_list) // 2
        
        for i, (key, met) in enumerate(criteria_list):
            if i < half:
                with col1:
                    st.write(f"{'✅' if met else '❌'} {key.capitalize()}")
            else:
                with col2:
                    st.write(f"{'✅' if met else '❌'} {key.capitalize()}")
        
        if is_duplicate(password):
            st.warning("⚠️ This password has been used multiple times before!")
            
        # Password suggestions if weak
        if score < 3:
            st.markdown("<h3>Suggestions to improve:</h3>", unsafe_allow_html=True)
            suggestions = []
            if not criteria["length"]:
                suggestions.append("• Make your password at least 8 characters long")
            if not criteria["uppercase"]:
                suggestions.append("• Add uppercase letters (A-Z)")
            if not criteria["lowercase"]:
                suggestions.append("• Add lowercase letters (a-z)")
            if not criteria["digits"]:
                suggestions.append("• Add numbers (0-9)")
            if not criteria["special"]:
                suggestions.append("• Add special characters (!@#$%^&*)")
                
            for suggestion in suggestions:
                st.markdown(suggestion)
            
            st.markdown("Or use our password generator to create a strong password!")

# Generate Password Tab
elif selected_tab == "Generate Password":
    st.markdown("<h2 class='sub-header'>🔑 Generate a Secure Password</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        length = st.slider("Password Length", min_value=8, max_value=32, value=12)
        
        col_a, col_b = st.columns(2)
        with col_a:
            include_upper = st.checkbox("Include Uppercase Letters", value=True)
            include_lower = st.checkbox("Include Lowercase Letters", value=True)
        with col_b:
            include_digits = st.checkbox("Include Digits", value=True)
            include_special = st.checkbox("Include Special Characters", value=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚡ Generate Password", use_container_width=True):
            generated_password = generate_password(length, include_upper, include_lower, include_digits, include_special)
            st.session_state.generated_password = generated_password
    
    if 'generated_password' in st.session_state:
        st.markdown("<h3>Generated Password:</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.code(st.session_state.generated_password, language=None)
            
            # Show strength of generated password
            score, criteria = check_strength(st.session_state.generated_password)
            strength_label, css_class = get_strength_label(score)
            st.markdown(f"Strength: <span class='{css_class}'>{strength_label}</span>", unsafe_allow_html=True)
        
        with col2:
            if st.button("Save This Password"):
                account_name = st.text_input("Account name:", value="Generated Password")
                if st.button("Confirm Save"):
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.history.append({
                        "account": account_name,
                        "password": st.session_state.generated_password,
                        "strength": strength_label,
                        "score": score,
                        "timestamp": timestamp
                    })
                    st.success(f"✅ Password saved successfully!")

# Password History Tab
elif selected_tab == "Password History":
    st.markdown("<h2 class='sub-header'>📜 Password History</h2>", unsafe_allow_html=True)
    
    if st.session_state.history:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🗑️ Clear History"):
                st.session_state.history = []
                st.success("History cleared successfully!")
            
            download_link = get_download_link(st.session_state.history)
            if download_link:
                st.markdown(download_link, unsafe_allow_html=True)
        
        # Display history in a more organized way
        for i, entry in enumerate(st.session_state.history[::-1]):
            if entry['strength'].startswith("🟢"):
                bg_color = "#E8F5E9"  # Light green
            elif entry['strength'].startswith("🟡"):
                bg_color = "#FFF8E1"  # Light yellow
            else:
                bg_color = "#FFEBEE"  # Light red
                
            st.markdown(f"""
            <div class='history-item' style='background-color: {bg_color};'>
                <strong>{entry['account']}</strong> - {entry['strength']}<br>
                <small>{entry['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                # Show password on demand
                if st.button(f"Show Password #{i+1}"):
                    st.code(entry['password'], language=None)
            with col2:
                # Delete individual entry
                if st.button(f"Delete #{i+1}"):
                    st.session_state.history.remove(entry)
                    st.success("Entry deleted!")
                    st.experimental_rerun()
    else:
        st.info("No passwords saved yet.")

# Statistics Tab
elif selected_tab == "Statistics":
    st.markdown("<h2 class='sub-header'>📊 Password Statistics</h2>", unsafe_allow_html=True)
    
    if st.session_state.history:
        # Extract data for analysis
        scores = [entry.get('score', 0) for entry in st.session_state.history]
        strengths = [entry['strength'] for entry in st.session_state.history]
        
        # Calculate average score
        avg_score = sum(scores) / len(scores)
        st.metric("Average Password Strength", f"{avg_score:.2f}/6")
        
        # Count by strength category
        strength_counts = {
            "Strong": sum(1 for s in strengths if s.startswith("🟢")),
            "Moderate": sum(1 for s in strengths if s.startswith("🟡")),
            "Weak": sum(1 for s in strengths if s.startswith("🔴"))
        }
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#2E7D32', '#F9A825', '#C62828']
        wedges, texts, autotexts = ax.pie(
            strength_counts.values(), 
            labels=strength_counts.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        ax.set_title('Password Strength Distribution')
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        st.pyplot(fig)
        
        # Password length distribution
        password_lengths = [len(entry['password']) for entry in st.session_state.history]
        
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.hist(password_lengths, bins=range(min(password_lengths), max(password_lengths) + 2), alpha=0.7, color='#1976D2')
        ax2.set_xlabel('Password Length')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Password Length Distribution')
        ax2.grid(axis='y', alpha=0.75)
        
        # Add a vertical line for recommended minimum length
        ax2.axvline(x=8, color='red', linestyle='--', label='Minimum Recommended (8)')
        ax2.axvline(x=12, color='green', linestyle='--', label='Strong Recommended (12)')
        ax2.legend()
        
        st.pyplot(fig2)
        
        # Password creation timeline
        if len(st.session_state.history) > 1:
            try:
                # Convert timestamps to datetime objects
                timestamps = [datetime.datetime.strptime(entry['timestamp'], "%Y-%m-%d %H:%M:%S") for entry in st.session_state.history]
                
                # Create a timeline of password creation
                fig3, ax3 = plt.subplots(figsize=(10, 6))
                ax3.plot(timestamps, scores, marker='o', linestyle='-', color='#0D47A1')
                ax3.set_xlabel('Date')
                ax3.set_ylabel('Password Strength Score')
                ax3.set_title('Password Strength Over Time')
                ax3.grid(True, alpha=0.3)
                
                # Rotate date labels for better readability
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                st.pyplot(fig3)
            except Exception as e:
                st.error(f"Error creating timeline: {e}")
    else:
        st.info("No password data available for statistics. Save some passwords first!")

# Add a sidebar with tips
with st.sidebar:
    st.markdown("## 📝 Password Tips")
    st.markdown("""
    ### Strong Password Guidelines:
    - Use at least 12 characters
    - Mix uppercase and lowercase letters
    - Include numbers and special characters
    - Avoid common words or patterns
    - Don't reuse passwords across sites
    
    ### Common Password Mistakes:
    - Using personal information
    - Using dictionary words
    - Simple character substitutions
    - Using keyboard patterns (qwerty)
    - Writing passwords down
    
    ### Password Manager Benefits:
    - Store complex passwords securely
    - Generate strong unique passwords
    - Auto-fill credentials
    - Sync across devices
    """)
    
    # Add a fun fact about passwords
    password_facts = [
        "The most common password is still '123456'",
        "It would take a computer about 7 quintillion years to crack a 12-character password with numbers, upper and lowercase letters, and symbols",
        "The average person has 100 passwords",
        "59% of people use the same password for multiple accounts",
        "Password managers can help you create and store strong, unique passwords",
        "Two-factor authentication adds an extra layer of security beyond just passwords",
        "Passwords like 'qwerty' and 'password' can be cracked instantly",
        "A 12-character password is 62 trillion times stronger than a 6-character password"
    ]
    
    st.markdown("### 💡 Did You Know?")
    st.info(random.choice(password_facts))