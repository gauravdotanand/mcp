import streamlit as st
import requests
import json
from typing import Optional, List
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

def init_session_state():
    """Initialize session state variables"""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'samples' not in st.session_state:
        st.session_state.samples = []

def make_api_request(endpoint: str, method: str = "GET", data: dict = None, headers: dict = None) -> Optional[dict]:
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if st.session_state.api_key:
            default_headers["X-API-Key"] = st.session_state.api_key
        
        if headers:
            default_headers.update(headers)
        
        if method == "GET":
            response = requests.get(url, headers=default_headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=default_headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=default_headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API server. Please make sure the FastAPI server is running.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def login_page():
    """Login page with API key input or user registration"""
    st.title("🤖 AI Code Generator")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔑 Login with API Key", "👤 Create New User"])
    
    with tab1:
        st.header("Login")
        api_key = st.text_input("Enter your API Key:", type="password")
        
        if st.button("Login"):
            if api_key:
                st.session_state.api_key = api_key
                # Test the API key
                user_info = make_api_request("/users/me")
                if user_info:
                    st.session_state.user_info = user_info
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid API key. Please try again.")
            else:
                st.error("Please enter an API key.")
    
    with tab2:
        st.header("Create New User")
        username = st.text_input("Username:")
        email = st.text_input("Email:")
        
        if st.button("Create User"):
            if username and email:
                user_data = {"username": username, "email": email}
                result = make_api_request("/users", method="POST", data=user_data)
                if result:
                    st.success("User created successfully!")
                    st.info(f"Your API Key: {result['api_key']}")
                    st.warning("Please save this API key - you won't be able to see it again!")
                else:
                    st.error("Failed to create user. Please try again.")
            else:
                st.error("Please fill in all fields.")

def load_samples():
    """Load user's coding approach samples"""
    samples = make_api_request("/coding-approach-samples")
    if samples:
        st.session_state.samples = samples

def main_app():
    """Main application interface"""
    st.title("🤖 AI Code Generator")
    
    # Sidebar with user info
    with st.sidebar:
        st.header("👤 User Info")
        if st.session_state.user_info:
            st.write(f"**Username:** {st.session_state.user_info['username']}")
            st.write(f"**Email:** {st.session_state.user_info['email']}")
        
        if st.button("Logout"):
            st.session_state.api_key = None
            st.session_state.user_info = None
            st.session_state.samples = []
            st.rerun()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🚀 Generate Code", "📚 Manage Samples", "📊 System Status"])
    
    with tab1:
        code_generation_tab()
    
    with tab2:
        sample_management_tab()
    
    with tab3:
        system_status_tab()

def code_generation_tab():
    """Code generation interface"""
    st.header("🚀 Generate Code")
    
    # Load samples if not loaded
    if not st.session_state.samples:
        load_samples()
    
    # Input form
    with st.form("code_generation_form"):
        prompt = st.text_area("Task Description:", placeholder="Describe what code you want to generate...")
        
        col1, col2 = st.columns(2)
        with col1:
            context = st.text_area("Mainframe Context (Optional):", placeholder="Provide mainframe screen context...")
            model = st.selectbox("Model:", ["gpt-4", "gpt-4o", "gpt-3.5-turbo"])
        
        with col2:
            extraction_requirements = st.text_area("Extraction Requirements (Optional):", placeholder="e.g., Extract account number from columns 10-20")
            
            # Sample selection
            if st.session_state.samples:
                st.write("**Select Coding Approach Samples:**")
                selected_sample_ids = []
                for sample in st.session_state.samples:
                    if st.checkbox(f"{sample['title']} (ID: {sample['id']})"):
                        selected_sample_ids.append(sample['id'])
            else:
                st.write("No samples available. Create some in the 'Manage Samples' tab.")
                selected_sample_ids = []
        
        # Direct code samples
        st.write("**Or provide direct code samples:**")
        direct_samples = st.text_area("Direct Code Samples (Optional):", placeholder="Paste your code samples here, separated by '---'")
        
        submitted = st.form_submit_button("Generate Code")
        
        if submitted and prompt:
            with st.spinner("Generating code..."):
                # Prepare request data
                request_data = {
                    "prompt": prompt,
                    "model": model
                }
                
                if context:
                    request_data["context"] = context
                if extraction_requirements:
                    request_data["extraction_requirements"] = extraction_requirements
                if selected_sample_ids:
                    request_data["coding_approach_sample_ids"] = selected_sample_ids
                if direct_samples:
                    request_data["coding_approach_samples"] = [s.strip() for s in direct_samples.split("---") if s.strip()]
                
                # Make API request
                result = make_api_request("/generate-code", method="POST", data=request_data)
                
                if result:
                    st.success("Code generated successfully!")
                    st.code(result["generated_code"], language="python")
                    
                    # Download button
                    st.download_button(
                        label="Download Generated Code",
                        data=result["generated_code"],
                        file_name="generated_code.py",
                        mime="text/plain"
                    )
                else:
                    st.error("Failed to generate code. Please try again.")

def sample_management_tab():
    """Sample management interface"""
    st.header("📚 Manage Coding Approach Samples")
    
    # Load samples
    if st.button("🔄 Refresh Samples"):
        load_samples()
    
    # Create new sample
    with st.expander("➕ Add New Sample"):
        with st.form("add_sample_form"):
            title = st.text_input("Sample Title:")
            code_sample = st.text_area("Code Sample:", height=200)
            max_length = st.number_input("Max Sample Length (tokens):", value=1000, min_value=100, max_value=5000)
            
            if st.form_submit_button("Add Sample"):
                if title and code_sample:
                    sample_data = {
                        "title": title,
                        "code_sample": code_sample,
                        "max_sample_length": max_length
                    }
                    
                    result = make_api_request("/coding-approach-samples", method="POST", data=sample_data)
                    if result:
                        st.success("Sample added successfully!")
                        load_samples()  # Refresh the list
                    else:
                        st.error("Failed to add sample.")
                else:
                    st.error("Please fill in all required fields.")
    
    # Display existing samples
    if st.session_state.samples:
        st.write(f"**Your Samples ({len(st.session_state.samples)}):**")
        
        for sample in st.session_state.samples:
            with st.expander(f"📄 {sample['title']} (ID: {sample['id']})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Style:** {sample.get('coding_style_summary', 'Not analyzed')}")
                    st.write(f"**Created:** {sample['created_at']}")
                    
                    if sample.get('truncated_code_sample'):
                        st.write("**Code (Truncated):**")
                        st.code(sample['truncated_code_sample'], language="python")
                    else:
                        st.write("**Code:**")
                        st.code(sample['code_sample'], language="python")
                
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_{sample['id']}"):
                        if make_api_request(f"/coding-approach-samples/{sample['id']}", method="DELETE"):
                            st.success("Sample deleted!")
                            load_samples()
                            st.rerun()
                        else:
                            st.error("Failed to delete sample.")
    else:
        st.info("No samples found. Create your first sample above!")

def system_status_tab():
    """System status and monitoring"""
    st.header("📊 System Status")
    
    # API Status
    st.subheader("🔌 API Status")
    if make_api_request("/users/me"):
        st.success("✅ API Server: Connected")
    else:
        st.error("❌ API Server: Disconnected")
    
    # User Info
    if st.session_state.user_info:
        st.subheader("👤 User Information")
        st.write(f"**Username:** {st.session_state.user_info['username']}")
        st.write(f"**Email:** {st.session_state.user_info['email']}")
        st.write(f"**Status:** {'🟢 Active' if st.session_state.user_info['is_active'] else '🔴 Inactive'}")
        st.write(f"**Member Since:** {st.session_state.user_info['created_at']}")
    
    # Sample Statistics
    if st.session_state.samples:
        st.subheader("📈 Sample Statistics")
        st.write(f"**Total Samples:** {len(st.session_state.samples)}")
        
        # Style analysis
        styles = {}
        for sample in st.session_state.samples:
            style = sample.get('coding_style_summary', 'Unknown')
            styles[style] = styles.get(style, 0) + 1
        
        if styles:
            st.write("**Coding Styles:**")
            for style, count in styles.items():
                st.write(f"  • {style}: {count}")
    
    # Usage Tips
    st.subheader("💡 Usage Tips")
    st.markdown("""
    - **Token Optimization**: The system automatically truncates long code samples to save tokens
    - **Smart Selection**: Only the most relevant samples are sent to the LLM
    - **Embedding Search**: Uses semantic similarity to find the best code samples
    - **Mainframe Context**: Provide mainframe screen data for specialized code generation
    """)

def main():
    """Main application"""
    st.set_page_config(
        page_title="AI Code Generator",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Check if user is logged in
    if st.session_state.api_key and st.session_state.user_info:
        main_app()
    else:
        login_page()

if __name__ == "__main__":
    main() 