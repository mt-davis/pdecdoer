import streamlit as st
import os
from typing import List, Dict, Any, Union, Optional

# Constants removed: MOBILE_BREAKPOINT = 768


def set_page_config(
    page_title: str,
    page_icon: str = "🧭",
    layout: str = "wide",
    initial_sidebar_state: str = "expanded"  # Changed from "collapsed" to "expanded"
) -> None:
    """
    Set the page configuration with consistent defaults.
    
    Args:
        page_title: The title of the page
        page_icon: The emoji icon for the page
        layout: Page layout ("wide" or "centered")
        initial_sidebar_state: Initial state of sidebar ("auto", "expanded", "collapsed")
    """
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,
    )

def add_custom_css(padding: Dict[str, str] = None) -> None:
    """
    Add custom CSS with optional custom padding.
    
    Args:
        padding: Dictionary with top, right, bottom, left padding (optional)
    """
    # Default padding 
    default_padding = {
        "top": "1rem",
        "right": "1rem",
        "bottom": "2rem",
        "left": "1rem"
    }
    
    # Use provided padding or defaults
    p = padding or default_padding
    
    # Apply custom CSS
    st.markdown(
        f"""
        <style>
            /* Basic adjustments */
            .block-container {{
                padding-top: {p['top']};
                padding-right: {p['right']};
                padding-left: {p['left']};
                padding-bottom: {p['bottom']};
            }}
            
            /* Hide default Streamlit footer */
            footer {{
                visibility: hidden;
            }}
            
            /* Button styles */
            .standard-button {{
                border-radius: 8px;
                padding: 0.75rem 1rem;
                font-weight: 500;
                margin-bottom: 0.75rem;
            }}
            
            /* Card */
            .enhanced-card {{
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 10px;
                padding: 1rem;
                margin-bottom: 1rem;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            }}
        </style>
        """, 
        unsafe_allow_html=True
    )

def use_is_mobile() -> bool:
    """
    Simplified placeholder function that always returns False since we're removing mobile functionality.
    
    Returns:
        bool: Always False (desktop mode)
    """
    # Always return False - we have removed mobile functionality
    return False

def responsive_container(width: str, is_centered: bool = True) -> st.container:
    """
    Create a container with custom width.
    
    Args:
        width: Container width (e.g., "100%", "500px")
        is_centered: Whether to center the container
    
    Returns:
        st.container: Streamlit container
    """
    if is_centered and width != "100%":
        # Centered container with custom width
        return st.container().markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <div style="width: {width};">
            """,
            unsafe_allow_html=True
        )
    else:
        # Full width or non-centered container
        return st.container()

def create_navigation_sidebar(
    session_key: str,
    title: str,
    description: str = "",
    hide_on_mobile: bool = False  # Parameter kept for compatibility, but not used
) -> None:
    """
    Create a consistent navigation sidebar.
    
    Args:
        session_key: Unique key for the session state
        title: Sidebar title
        description: Optional sidebar description
        hide_on_mobile: Parameter kept for compatibility, but not used
    """
    with st.sidebar:
        st.title("🧭 PolicyCompassAI")
        st.header(title)
        
        if description:
            st.caption(description)
        
        st.divider()
        
        # Common navigation links
        st.button("🏠 Home", key=f"{session_key}_home")
        st.button("📄 Policy Decoder", key=f"{session_key}_decoder")
        st.button("💬 Policy Chat", key=f"{session_key}_chat")
        st.button("📊 Impact Simulator", key=f"{session_key}_simulator")
        st.button("👤 My Profile", key=f"{session_key}_profile")
        st.button("⚙️ Settings", key=f"{session_key}_settings")

def mobile_friendly_button(
    label: str,
    key: str,
    type: str = "primary",
    use_container_width: bool = False,
    size: str = "normal"  # Added for compatibility with Mobile_Demo.py
) -> bool:
    """
    Create a standard button with appropriate styling.
    
    Args:
        label: Button label
        key: Unique key for the button
        type: Button type ("primary", "secondary", "danger")
        use_container_width: Whether to use the full container width
        size: Size of the button (added for compatibility)
    
    Returns:
        bool: True if button was clicked, False otherwise
    """
    button_styles = {
        "primary": {"bg": "primary", "fg": "white"},
        "secondary": {"bg": "secondary", "fg": "white"},
        "danger": {"bg": "error", "fg": "white"}
    }
    style = button_styles.get(type, button_styles["primary"])
    
    return st.button(
        label,
        key=key,
        type=style["bg"],
        use_container_width=use_container_width
    )

def mobile_friendly_text_input(
    label: str,
    key: str = None,
    value: str = "",
    placeholder: str = "",
    max_chars: Optional[int] = None,
    help: str = "",
    **kwargs  # Added for compatibility
) -> str:
    """
    Create a standard text input.
    
    Args:
        label: Input label
        key: Unique key for the input
        value: Default value (optional)
        placeholder: Placeholder text (optional)
        max_chars: Maximum number of characters (optional)
        help: Help text (optional)
        **kwargs: Additional arguments for compatibility
    
    Returns:
        str: Input value
    """
    return st.text_input(
        label=label,
        key=key,
        value=value,
        placeholder=placeholder,
        max_chars=max_chars,
        help=help
    )

def mobile_friendly_selectbox(
    label: str,
    options: List[Any],
    key: str = None,
    index: int = 0,
    help: str = "",
    **kwargs  # Added for compatibility
) -> Any:
    """
    Create a standard select box.
    
    Args:
        label: Select box label
        options: List of options
        key: Unique key for the select box
        index: Default selected index (optional)
        help: Help text (optional)
        **kwargs: Additional arguments for compatibility
    
    Returns:
        Any: Selected option
    """
    return st.selectbox(
        label=label,
        options=options,
        key=key,
        index=index,
        help=help
    )

def mobile_friendly_text_area(
    label: str,
    key: str = None,
    value: str = "",
    placeholder: str = "",
    height: Optional[int] = None,
    help: str = "",
    **kwargs  # Added for compatibility
) -> str:
    """
    Create a standard text area.
    
    Args:
        label: Text area label
        key: Unique key for the text area
        value: Default value (optional)
        placeholder: Placeholder text (optional)
        height: Height in pixels (optional)
        help: Help text (optional)
        **kwargs: Additional arguments for compatibility
    
    Returns:
        str: Text area value
    """
    return st.text_area(
        label=label,
        key=key,
        value=value,
        placeholder=placeholder,
        height=height,
        help=help
    )

def enhanced_card(
    title: str = "",
    is_mobile: bool = False,  # Kept for compatibility but not used
    padding: str = "1rem",
    content: str = None,  # Added for compatibility with enhanced_card call
    mobile_style: str = "normal",  # Added for compatibility
    has_hover: bool = True  # Added for compatibility
) -> st.container:
    """
    Create an enhanced card container with optional title.
    
    Args:
        title: Card title (optional)
        is_mobile: Kept for compatibility but not used
        padding: Padding for the card content
        content: Card content (HTML string) - added for compatibility
        mobile_style: Style for mobile - added for compatibility
        has_hover: Whether to add hover effects - added for compatibility
    
    Returns:
        st.container: Streamlit container for the card content
    """
    card_container = st.container()
    
    with card_container:
        if content:
            # If content is provided directly (new style)
            html = f"""
            <div class="enhanced-card" style="padding: {padding};">
            {"<h4>" + title + "</h4>" if title else ""}
            {content}
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
        else:
            # Original style (container returned for content)
            st.markdown(
                f"""
                <div class="enhanced-card" style="padding: {padding};">
                {"<h4>" + title + "</h4>" if title else ""}
                """,
                unsafe_allow_html=True
            )
    
    # Return the container to add content
    return card_container

def bottom_navigation(items: List[Dict[str, str]]) -> None:
    """
    Simplified function for compatibility - does nothing.
    Bottom navigation was mobile-specific so it's now a no-op.
    
    Args:
        items: List of navigation items with 'icon', 'label', and 'url'
    """
    # Bottom navigation was mobile-specific, now a no-op function
    pass

def setup_page_config(title, sidebar_state="expanded"):
    """Set up consistent page configuration across all pages"""
    st.set_page_config(
        page_title=f"PolicyCompassAI - {title}",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state=sidebar_state
    )
    
    # Apply custom CSS
    apply_custom_css()
    
    # Add header
    st.markdown(f"<h1 class='page-title'>{title}</h1>", unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

def apply_custom_css():
    """Apply consistent styling across all pages - removed mobile-specific CSS"""
    st.markdown("""
    <style>
        /* Custom color scheme */
        :root {
            --primary-color: #4B6A9B;
            --secondary-color: #3A5276;
            --accent-color: #61A0FF;
            --background-color: #FFFFFF;
            --card-background: #F8F9FA;
            --success-color: #28A745;
            --error-color: #DC3545;
            --warning-color: #FFC107;
            --info-color: #17A2B8;
            --text-color: #333333;
            --text-muted: #6C757D;
            --border-radius: 8px;
            --box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        /* Improved Sidebar Structure */
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 1px solid #eaeaea;
        }
        
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0 !important;
        }
        
        section[data-testid="stSidebar"] > div {
            padding: 0 0.5rem !important;
        }
        
        /* Force the automatic navigation to appear below our custom branding */
        section[data-testid="stSidebar"] > div > div:has([data-testid="stSidebarNav"]) {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* Style Streamlit's navigation */
        [data-testid="stSidebarNav"] {
            background-color: transparent;
            padding-top: 0;
            margin-top: 0;
        }
        
        [data-testid="stSidebarNav"] > ul {
            padding-left: 0;
            border-top: 1px solid rgba(75, 106, 155, 0.1);
            padding-top: 0.75rem;
            margin-top: 0;
        }
        
        /* Style the navigation links */
        [data-testid="stSidebarNav"] a {
            margin-bottom: 0.25rem;
            padding: 0.5rem 0.5rem 0.5rem 1rem !important;
            border-radius: 4px;
            transition: all 0.2s ease;
        }
        
        [data-testid="stSidebarNav"] a:hover {
            background-color: rgba(75, 106, 155, 0.1) !important;
        }
        
        [data-testid="stSidebarNav"] span {
            font-size: 1rem;
            font-weight: 500;
            color: var(--primary-color);
        }
        
        /* Style active page */
        [data-testid="stSidebarNav"] a[aria-selected="true"] {
            background-color: rgba(75, 106, 155, 0.15) !important;
            border-left: 3px solid var(--primary-color) !important;
        }
        
        /* Typography */
        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
        }
        
        h1.page-title {
            color: var(--primary-color);
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        
        h2, h3, h4 {
            color: var(--primary-color);
            font-weight: 600;
            margin-top: 1rem;
        }
        
        .section-divider {
            margin: 1.5rem 0;
            border: none;
            height: 1px;
            background-color: #f0f0f0;
        }
        
        /* Card styling */
        .card {
            background-color: var(--card-background);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            box-shadow: var(--box-shadow);
            margin-bottom: 1.5rem;
        }
        
        /* Button styling */
        .stButton button {
            border-radius: var(--border-radius);
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Primary button */
        .primary-btn {
            background-color: var(--primary-color) !important;
            color: white !important;
            border: none !important;
        }
        
        /* Success message styling */
        .success-box {
            background-color: rgba(40, 167, 69, 0.1);
            border-left: 4px solid var(--success-color);
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
        }
        
        /* Error message styling */
        .error-box {
            background-color: rgba(220, 53, 69, 0.1);
            border-left: 4px solid var(--error-color);
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
        }
        
        /* Info message styling */
        .info-box {
            background-color: rgba(23, 162, 184, 0.1);
            border-left: 4px solid var(--info-color);
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
        }
        
        /* Improved responses */
        .ai-response {
            background-color: var(--card-background);
            padding: 1.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            border-left: 4px solid var(--primary-color);
            margin: 1rem 0;
        }
        
        /* Form styling */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb] {
            border-radius: var(--border-radius);
            border: 1px solid #E0E0E0;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 1px var(--primary-color);
        }
        
        /* File uploader styling */
        .stFileUploader div[data-testid="stFileUploadDropzone"] {
            background-color: rgba(75, 106, 155, 0.05);
            border: 2px dashed var(--primary-color);
            border-radius: var(--border-radius);
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] hr {
            margin: 1rem 0;
            border: none;
            height: 1px;
            background-color: #eaeaea;
        }
        
        /* Sidebar header */
        section[data-testid="stSidebar"] h3 {
            color: #4B6A9B;
            font-size: 1.2rem;
            margin-bottom: 1rem;
            padding: 0.5rem 0;
        }
        
        /* Sidebar buttons */
        section[data-testid="stSidebar"] button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        
        /* Hide fullscreen button for cleaner UI */
        button[title="View fullscreen"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

def sidebar_navigation():
    """Create a custom navigation sidebar with branding"""
    with st.sidebar:
        # Add company logo using native image support
        # The SVG data URI approach ensures we don't need external files
        logo_svg = '''
        <svg width="70" height="70" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="90" fill="#4B6A9B" />
            <path d="M150 80 L120 140 L80 110 L40 150" stroke="#FFFFFF" stroke-width="8" stroke-linecap="round" />
            <circle cx="70" cy="65" r="20" fill="#61A0FF" />
            <path d="M70 120 Q100 80 130 120" stroke="#FFFFFF" stroke-width="6" fill="none" stroke-linecap="round" />
        </svg>
        '''
        
        # Center the logo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f'<div style="text-align: center; min-height: 70px; display: flex; justify-content: center; align-items: center;">{logo_svg}</div>', unsafe_allow_html=True)
        
        # Company name and version directly with Streamlit
        st.markdown("<h2 style='text-align: center; color: #4B6A9B; margin-bottom: 0; font-size: 1.5rem; font-weight: 700;'>Policy<span style='color: #3A5276;'>Compass</span>AI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #6c757d; margin-top: 0.3rem;'>v1.0.0 Beta</p>", unsafe_allow_html=True)
        
        # Divider line
        st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 0.5rem;'>", unsafe_allow_html=True)
        
        # MOVED: API Keys section - now before the automatic navigation
        with st.expander("🔑 API Keys", expanded=False):
            st.markdown("#### API Keys Status")
            
            # Check which keys are present
            openai_key_set = "✅" if st.session_state.get("openai_key") else "❌"
            anthropic_key_set = "✅" if st.session_state.get("anthropic_key") else "❌"
            propublica_key_set = "✅" if st.session_state.get("propublica_key") else "❌"
            tts_key_set = "✅" if st.session_state.get("tts_key") else "❌"
            
            st.markdown(f"OpenAI: {openai_key_set}")
            st.markdown(f"Anthropic: {anthropic_key_set}")
            st.markdown(f"ProPublica: {propublica_key_set}")
            st.markdown(f"TTS/ElevenLabs: {tts_key_set}")
            
            if st.button("Manage API Keys", key="manage_apis", use_container_width=True):
                # Use the new navigation target
                st.switch_page("pages/9_⚙️_Settings.py")
        
        # MOVED: Settings section - now before the automatic navigation
        with st.expander("⚙️ Help & About", expanded=False):
            st.markdown("""
            **PolicyCompassAI** is a civic education platform that helps users understand complex policy documents through AI-powered analysis.
            """)
            
            if st.button("Settings", key="goto_settings", use_container_width=True):
                st.switch_page("pages/9_⚙️_Settings.py")
                
            if st.button("Report Issues", key="report_issues", use_container_width=True):
                st.markdown("Please report issues on our GitHub repository.")
        
        # Add another divider before the automatic navigation
        st.markdown("<hr style='margin-top: 0.75rem; margin-bottom: 0.75rem;'>", unsafe_allow_html=True)
        
        # Add some space before the navigation (which Streamlit adds automatically)
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        
        # CSS to style the "Pages" section in the navigation
        st.markdown("""
        <style>
        /* Style for automatic navigation heading (Pages) */
        section[data-testid="stSidebar"] .css-16idsys p {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--primary-color);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Add some space after the navigation
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

def card(content, title=None):
    """Display content in a card with optional title"""
    card_content = f"<div class='card'>"
    if title:
        card_content += f"<h3>{title}</h3>"
    card_content += f"{content}</div>"
    st.markdown(card_content, unsafe_allow_html=True)

def success_box(message):
    """Display a success message box"""
    st.markdown(f"<div class='success-box'>{message}</div>", unsafe_allow_html=True)

def error_box(message):
    """Display an error message box"""
    st.markdown(f"<div class='error-box'>{message}</div>", unsafe_allow_html=True)

def info_box(message):
    """Display an info message box"""
    st.markdown(f"<div class='info-box'>{message}</div>", unsafe_allow_html=True)

def ai_response(content):
    """Format AI response with consistent styling"""
    return f"""
    <div class='ai-response'>
        <p style="font-size: 16px; color: var(--text-color);">{content}</p>
    </div>
    """

def primary_button(label, on_click=None, key=None):
    """Create a styled primary button"""
    button_html = f"""
    <button class="primary-btn" style="background-color: var(--primary-color); color: white; 
    border: none; padding: 0.5rem 1rem; border-radius: var(--border-radius); 
    font-weight: 500; cursor: pointer; width: 100%;">{label}</button>
    """
    if on_click:
        return st.button(label, on_click=on_click, key=key)
    return st.button(label, key=key)

def setup_page():
    """Set up page configuration and custom CSS"""
    st.set_page_config(
        page_title="PolicyCompassAI",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS for a cleaner UI and mobile optimizations
    st.markdown("""
    <style>
        /* General UI improvements */
        .block-container {padding-top: 1rem; padding-bottom: 1rem;}
        h1, h2, h3 {color: #2c3e50;}
        .stButton>button {border-radius: 0.5rem; margin-top: 0.5rem; margin-bottom: 0.5rem;}
        .stExpander {border-radius: 0.5rem; border: 1px solid #f0f2f6;}
        
        /* Improved sidebar and navigation */
        .css-1d391kg, .css-163ttbj, .css-1cypcdb {
            background-color: #f8f9fa;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 1px solid #e9ecef;
            min-width: 280px;
            width: auto !important;
        }
        
        section[data-testid="stSidebar"] .css-pkbazv {
            padding-top: 3rem;
        }
        
        /* Sidebar navigation links */
        .css-wjbhl0, .css-qrbaxs {
            font-size: 16px;
            padding: 0.75rem 1rem !important;
            margin: 0.25rem 0 !important;
            border-radius: 0.5rem;
            transition: all 0.2s ease;
        }
        
        .css-wjbhl0:hover, .css-qrbaxs:hover {
            background-color: rgba(75, 106, 155, 0.1);
        }
        
        /* Improve readability/sizing for mobile */
        @media (max-width: 768px) {
            .block-container {
                padding-top: 0.5rem;
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
            
            /* Ensure sidebar is usable on mobile */
            section[data-testid="stSidebar"] {
                min-width: 240px !important;
                width: 75vw !important;
                max-width: 330px !important;
            }
            
            /* Improved navigation touch targets for mobile */
            .css-wjbhl0, .css-qrbaxs {
                padding: 1rem !important;  /* Larger padding for better touch targets */
                margin: 0.5rem 0 !important;
            }
            
            /* Make buttons more touch-friendly */
            .stButton>button {
                min-height: 44px;  /* Minimum touch target size */
                padding: 0.5rem 1rem;
                font-size: 16px;
            }
            
            /* Ensure form elements are touch-friendly */
            input, select, textarea {
                min-height: 44px !important;
                font-size: 16px !important;
            }
            
            /* Adjust spacing between elements */
            .stExpander, .stTextInput, .stSelectbox, .stTextArea {
                margin-bottom: 1rem !important;
            }
            
            /* Full width selects and buttons on mobile */
            div[data-baseweb="select"] {
                width: 100% !important;
            }
        }
        
        /* Card styling */
        .policy-card {
            border: 1px solid #e6e6e6;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .policy-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Hide fullscreen button for cleaner UI */
        button[title="View fullscreen"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

def responsive_layout(mobile_content=None, desktop_content=None):
    """
    Simplified compatibility function that always returns desktop content.
    
    Args:
        mobile_content: Content for mobile devices (ignored)
        desktop_content: Content for desktop devices
    
    Returns:
        The desktop content or a dummy object for dot notation access
    """
    if desktop_content is not None:
        return desktop_content
    
    # If no specific desktop content, return mobile content for compatibility
    if mobile_content is not None:
        return mobile_content
    
    # Create a dummy object with desktop/mobile attributes for dot notation access
    class ResponsiveLayoutDummy:
        def __init__(self):
            self.desktop = st.container()
            self.mobile = None
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    return ResponsiveLayoutDummy()

def responsive_columns(num_cols_desktop=3, num_cols_mobile=1):
    """
    Creates columns based only on desktop setting, ignoring mobile setting.
    
    Args:
        num_cols_desktop (int): Number of columns for desktop view
        num_cols_mobile (int): Number of columns for mobile view (ignored)
    
    Returns:
        list: List of column objects
    """
    return st.columns(num_cols_desktop)

def responsive_container(content=None, max_width_desktop=800, max_width_mobile=None, padding_mobile=1, is_centered=True, width="100%"):
    """
    Compatibility wrapper for both old and new responsive_container implementations.
    
    Args:
        content: Function that renders the content
        max_width_desktop: Maximum width for desktop
        max_width_mobile: Maximum width for mobile (ignored)
        padding_mobile: Padding size on mobile (ignored)
        is_centered: Whether to center the container (for old implementation)
        width: Container width (for old implementation)
    
    Returns:
        A container for the content
    """
    # Detect which version of the function is being called
    if content is not None:
        # New version with content as function
        with st.container():
            # Create a centered column with max width
            _, col, _ = st.columns([1, 3, 1])
            with col:
                if callable(content):
                    content()
    else:
        # Old version returning a container
        if is_centered and width != "100%":
            # Centered container with custom width
            return st.container().markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <div style="width: {width};">
                """,
                unsafe_allow_html=True
            )
        else:
            # Full width or non-centered container
            return st.container()

def mobile_friendly_button(label, on_click=None, key=None, help=None, type="primary"):
    """Creates a mobile-friendly button with appropriate sizing
    
    Args:
        label (str): Button label
        on_click (function, optional): Function to call when clicked
        key (str, optional): Unique key for the button
        help (str, optional): Help text
        type (str, optional): Button type ("primary", "secondary", etc.)
    
    Returns:
        bool: True if button was clicked, False otherwise
    """
    import streamlit as st
    
    is_mobile = use_is_mobile()
    
    # Add custom CSS for mobile buttons
    if is_mobile:
        st.markdown("""
        <style>
        .stButton > button {
            height: 48px !important;
            min-width: 44px !important;
            width: 100% !important;
            padding: 8px 16px !important;
            font-size: 1rem !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Create the button with specified parameters
    return st.button(
        label=label,
        on_click=on_click,
        key=key,
        help=help,
        type=type
    )

# New function for bottom navigation on mobile
def bottom_navigation(items):
    """Creates a mobile-friendly bottom navigation bar
    
    Args:
        items (list): List of dictionaries with 'icon', 'label', and 'url' keys
    
    Example:
        bottom_navigation([
            {'icon': '📄', 'label': 'Decoder', 'url': '/Decoder'},
            {'icon': '🔍', 'label': 'Compare', 'url': '/Compare_Bills'},
            {'icon': '💬', 'label': 'Chat', 'url': '/Chat_Memory'}
        ])
    """
    is_mobile = use_is_mobile()
    
    if is_mobile:
        num_items = len(items)
        item_width = 100 / num_items
        
        nav_html = f"""
        <style>
        .bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 60px;
            background-color: white;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            display: flex;
            z-index: 1000;
        }}
        
        .bottom-nav-item {{
            width: {item_width}%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            color: var(--text-color);
            font-size: 0.7rem;
            padding: 8px 0;
        }}
        
        .bottom-nav-icon {{
            font-size: 1.5rem;
            margin-bottom: 4px;
        }}
        
        .page-padding-bottom {{
            padding-bottom: 70px;
        }}
        </style>
        
        <div class="bottom-nav">
        """
        
        for item in items:
            icon = item.get('icon', '📌')
            label = item.get('label', 'Page')
            url = item.get('url', '/')
            
            nav_html += f"""
            <a href="{url}" class="bottom-nav-item">
                <div class="bottom-nav-icon">{icon}</div>
                <div>{label}</div>
            </a>
            """
        
        nav_html += "</div>"
        
        # Add padding to page bottom
        nav_html += """
        <style>
        .main .block-container {
            padding-bottom: 70px;
        }
        </style>
        """
        
        st.markdown(nav_html, unsafe_allow_html=True)

# Enhanced mobile-friendly form elements
def mobile_friendly_text_input(label, **kwargs):
    """Create a mobile-friendly text input
    
    Args:
        label (str): Input label
        **kwargs: Additional parameters to pass to st.text_input
    
    Returns:
        The value of the text input
    """
    is_mobile = use_is_mobile()
    
    if is_mobile:
        st.markdown("""
        <style>
        .mobile-input .stTextInput > div > div > input {
            min-height: 48px !important;
            font-size: 16px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="mobile-input">', unsafe_allow_html=True)
            value = st.text_input(label, **kwargs)
            st.markdown('</div>', unsafe_allow_html=True)
            return value
    else:
        return st.text_input(label, **kwargs)

def mobile_friendly_text_area(label, **kwargs):
    """Create a mobile-friendly text area
    
    Args:
        label (str): Text area label
        **kwargs: Additional parameters to pass to st.text_area
    
    Returns:
        The value of the text area
    """
    is_mobile = use_is_mobile()
    
    if is_mobile:
        st.markdown("""
        <style>
        .mobile-textarea .stTextArea > div > div > textarea {
            min-height: 120px !important;
            font-size: 16px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="mobile-textarea">', unsafe_allow_html=True)
            value = st.text_area(label, **kwargs)
            st.markdown('</div>', unsafe_allow_html=True)
            return value
    else:
        return st.text_area(label, **kwargs)

def mobile_friendly_selectbox(label, options, **kwargs):
    """Create a mobile-friendly selectbox
    
    Args:
        label (str): Selectbox label
        options (list): Options to display
        **kwargs: Additional parameters to pass to st.selectbox
    
    Returns:
        The selected value
    """
    is_mobile = use_is_mobile()
    
    if is_mobile:
        st.markdown("""
        <style>
        .mobile-select .stSelectbox > div > div {
            min-height: 48px !important;
        }
        .mobile-select .stSelectbox > div > div > div {
            font-size: 16px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="mobile-select">', unsafe_allow_html=True)
            value = st.selectbox(label, options, **kwargs)
            st.markdown('</div>', unsafe_allow_html=True)
            return value
    else:
        return st.selectbox(label, options, **kwargs)

# Enhanced card with optional hover and shadow effects for mobile
def enhanced_card(content, title=None, mobile_style='compact', has_hover=True):
    """Display content in a card with responsive mobile styling
    
    Args:
        content (str): HTML content to display in the card
        title (str, optional): Card title
        mobile_style (str): Style for mobile: 'compact', 'normal', or 'expanded'
        has_hover (bool): Whether to add hover effects
    """
    is_mobile = use_is_mobile()
    
    # Adjust padding based on mobile style
    mobile_padding = "0.75rem" if mobile_style == 'compact' else "1.25rem" if mobile_style == 'normal' else "1.5rem"
    hover_class = "card-hover" if has_hover else ""
    
    # Define CSS classes
    st.markdown(f"""
    <style>
    .enhanced-card {{
        background-color: var(--card-background);
        border-radius: var(--border-radius);
        padding: {'' if is_mobile else '1.5rem'};
        padding: {mobile_padding if is_mobile else '1.5rem'};
        box-shadow: var(--box-shadow);
        margin-bottom: 1.25rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    
    .card-hover:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Create the card
    card_content = f"<div class='enhanced-card {hover_class}'>"
    if title:
        card_content += f"<h3>{title}</h3>"
    card_content += f"{content}</div>"
    
    st.markdown(card_content, unsafe_allow_html=True)

# For compatibility with Mobile_Demo.py
def show_success(message: str) -> None:
    """
    Display a success message.
    
    Args:
        message: The success message to display
    """
    st.success(message)

# Enhanced locale support
def get_user_locale():
    """Get the user's locale from Streamlit context if available"""
    try:
        return st.context.locale
    except (AttributeError, ImportError):
        # Fallback for older Streamlit versions
        return "en-US"

# Helper for colored badges
def create_badge(text, color="blue"):
    """Create a colored badge using Streamlit's new badge directive
    
    Args:
        text: The text to display in the badge
        color: Badge color (blue, green, red, yellow, gray, etc.)
    """
    st.markdown(f":{color}-badge[{text}]")

# Enhanced error handling with search links
def show_error_with_help(error_message):
    """Display an error message with helpful search links
    
    Args:
        error_message: The error message to display
    """
    try:
        st.exception(error_message)
    except Exception:
        # Fallback for older Streamlit versions
        st.error(error_message)
        st.markdown(f"[Search Google for this error](https://www.google.com/search?q={error_message.replace(' ', '+')})")
        st.markdown(f"[Ask ChatGPT about this error](https://chat.openai.com/new?q=Help+with+this+error+{error_message.replace(' ', '+')})")
