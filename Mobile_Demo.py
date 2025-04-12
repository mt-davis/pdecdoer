import streamlit as st
from components.ui_helpers import (
    set_page_config,
    add_custom_css,
    responsive_layout,
    responsive_columns,
    responsive_container,
    mobile_friendly_button,
    create_navigation_sidebar,
    use_is_mobile,
    show_success,
    bottom_navigation,
    mobile_friendly_text_input,
    mobile_friendly_text_area,
    mobile_friendly_selectbox,
    enhanced_card
)

# Page configuration
set_page_config(
    page_title="Mobile Components Demo",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

add_custom_css(padding={"top": "2rem", "right": "1rem", "left": "1rem", "bottom": "0"})

# Add empty sidebar to maintain consistent page width for demo
create_navigation_sidebar(
    session_key="mobile_demo",
    title="",
    description="This is a sidebar example.",
    hide_on_mobile=True
)

# Main content container
main_container = responsive_container("100%", is_centered=True)

with main_container:
    is_mobile = use_is_mobile()
    
    # Page title
    st.markdown("# 📱 Mobile Components Demo")
    
    st.markdown("This page showcases mobile-friendly components available in the PolicyCompassAI app.")
    st.markdown("**Current device detected:** " + ("📱 Mobile" if is_mobile else "🖥️ Desktop"))
    
    # Demo section: Responsive Layout
    st.markdown("## Responsive Layout Demo")
    
    with responsive_layout() as layout:
        with layout.desktop:
            st.markdown("This content only shows on desktop")
            st.write("Desktop view has more horizontal space for content")
        
        with layout.mobile:
            st.markdown("This content only shows on mobile")
            st.write("Mobile view prioritizes vertical stacking")
    
    # Demo section: Responsive Columns
    st.markdown("## Responsive Columns Demo")
    
    col1, col2 = responsive_columns([1, 1])
    
    with col1:
        st.markdown("### Column 1")
        st.write("This column will stack on mobile")
    
    with col2:
        st.markdown("### Column 2")
        st.write("This column will stack below Column 1 on mobile")
    
    # Demo section: Mobile-Friendly Buttons
    st.markdown("## Mobile-Friendly Buttons")
    
    mobile_friendly_button("Primary Button", key="primary_btn")
    mobile_friendly_button("Secondary Button", type="secondary", key="secondary_btn")
    mobile_friendly_button("Small Button", size="small", key="small_btn")
    
    # Demo section: Card Layout
    st.markdown("## Card Layout Demo")
    
    enhanced_card(
        title="Default Card",
        content="<p>This card adjusts its padding based on device size</p>"
    )
    
    enhanced_card(
        title="Compact Card (Mobile)",
        content="<p>This card uses compact styling on mobile</p>",
        mobile_style="compact"
    )
    
    enhanced_card(
        title="Expanded Card (Mobile)",
        content="<p>This card uses expanded styling on mobile</p>",
        mobile_style="expanded",
        has_hover=False
    )

    # Demo section: Enhanced Form Controls
    st.markdown("## Mobile-Friendly Form Controls")
    
    st.markdown("### Text Input")
    user_input = mobile_friendly_text_input("Enter your name", placeholder="John Doe")
    
    st.markdown("### Text Area")
    user_message = mobile_friendly_text_area("Your message", placeholder="Type your message here...", height=150)
    
    st.markdown("### Select Box")
    user_option = mobile_friendly_selectbox("Select an option", options=["Option 1", "Option 2", "Option 3"])
    
    # Demo section: Bottom Navigation
    st.markdown("## Bottom Navigation")
    
    st.markdown("The bottom navigation bar (visible on mobile only) provides quick access to main app features:")
    
    bottom_navigation([
        {'icon': '📄', 'label': 'Decoder', 'url': '/Decoder'},
        {'icon': '🔍', 'label': 'Compare', 'url': '/Compare_Bills'},
        {'icon': '💬', 'label': 'Chat', 'url': '/Chat_Memory'},
        {'icon': '📊', 'label': 'Impact', 'url': '/Impact_Sim'}
    ])
    
    # Compare mobile/desktop visualization
    st.markdown("## Mobile vs. Desktop Comparison")
    
    with responsive_layout() as layout:
        with layout.desktop:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Desktop View")
                st.markdown("- Wide horizontal layout")
                st.markdown("- Multi-column content")
                st.markdown("- Sidebar navigation visible")
                st.markdown("- Standard form controls")
            with col2:
                st.image("https://via.placeholder.com/400x300?text=Desktop+Layout")
        
        with layout.mobile:
            st.markdown("### Mobile View")
            st.markdown("- Stacked vertical layout")
            st.markdown("- Full-width components")
            st.markdown("- Bottom navigation bar")
            st.markdown("- Touch-optimized controls")
            st.image("https://via.placeholder.com/300x400?text=Mobile+Layout")
    
    # Mobile Design Guidelines
    st.markdown("## 📝 Mobile-First Design Guidelines")
    
    with st.expander("Show Mobile Design Guidelines", expanded=False):
        st.markdown("""
        ### Mobile-First Principles
        
        1. **Design for mobile first**, then enhance for larger screens
        2. **Touch-friendly elements** (min 44×44px touch targets)
        3. **Use stack layout by default** (single-column on mobile)
        4. **Simplified navigation** (bottom nav or hamburger menu)
        5. **Thumb-friendly zones** for important actions
        6. **Responsive typography** (readable on small screens)
        7. **Consider network limitations** (optimize assets)
        8. **Test on real devices** frequently
        """)
    
    # Success message at the bottom
    show_success(
        "PolicyCompassAI is built with a mobile-first approach, ensuring all users have a great experience regardless of device."
    ) 