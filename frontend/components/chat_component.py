import streamlit as st
from app.models.schemas.request import ChatRequest

def chat_interface(api_base: str, jwt_token: str):
    st.header("🤖 AI Chat - Ask about your finances")
    
    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat input
    if prompt := st.chat_input("Ask 'Where am I overspending?' or 'Show my biggest expenses...'"):
        # Add user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Stream AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            response = requests.post(
                f"{api_base}/api/v1/chat/ask",
                json={"question": prompt},
                headers={"Authorization": f"Bearer {jwt_token}"},
                stream=True
            )
            
            for chunk in response.iter_content(chunk_size=100):
                if chunk:
                    full_response += chunk.decode()
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        st.session_state.chat_history.append((prompt, full_response))
    
    # Render chat history
    for question, answer in st.session_state.chat_history[-6:]:  # Last 6 messages
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            st.write(answer)
    
    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# Usage in main Streamlit app:
# if st.session_state.jwt_token:
#     chat_interface(API_BASE, st.session_state.jwt_token)

