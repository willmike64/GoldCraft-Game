import streamlit as st

def render_town_hub():
    """Render the town hub interface"""
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown("# 🏘️ **GOLD CREEK TOWN**")
    st.markdown("*The bustling heart of the mining frontier*")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏪 General Store")
        st.markdown("Buy supplies and equipment")
        if st.button("🛒 Enter Store"):
            st.info("Store coming soon!")
    
    with col2:
        st.markdown("### 🍺 Saloon")
        st.markdown("Gather information and rumors")
        if st.button("🍻 Enter Saloon"):
            st.info("Saloon coming soon!")
    
    with col3:
        st.markdown("### 🏦 Bank")
        st.markdown("Secure your gold reserves")
        if st.button("💰 Enter Bank"):
            st.info("Bank coming soon!")
    
    st.divider()
    
    st.markdown("### 📰 Town News")
    st.info("🗞️ Latest: New mining claims discovered in the Sierra foothills!")
    
    st.markdown('</div>', unsafe_allow_html=True)