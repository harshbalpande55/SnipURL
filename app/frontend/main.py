import streamlit as st
import requests
from config import get_settings

def call_generate_url(link):
    response = requests.request("POST", url=get_settings().base_url+"/url", json= {'target_url': link})
    if response.ok:
        st.text_input("Shortend URL",response.json()['url'])

def main():
    st.header("Url Shortner")
    link_text = st.text_input('Enter long URL')
    st.button("Generate Shortend URL",on_click=call_generate_url(link_text))
        
if __name__ == "__main__":
    main()