import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
import os
import requests

load_dotenv('.env')
groq_api_key = os.getenv("GROQ_API_KEY")
pixabay_api_key = os.getenv("PIXABAY_API_KEY")

def summarize_article(topic, words):
    chat = ChatGroq(temperature=1, model_name="mixtral-8x7b-32768", groq_api_key=groq_api_key)
    prompt = ChatPromptTemplate.from_messages([("human", "Summarize the {topic} in about{words} words if possible else summarize it in max length possible")])
    chain = prompt | chat
    return chain.invoke({"topic": topic, "words": words}).content

def use_prompt_template(text):
    prompt_template = PromptTemplate.from_template(
        "I will be giving you the article find the top 5 most influential words which can be used to find the images relevant for the article, return a python list , containing those words , the article is {article}."
    )
    formatted_output = prompt_template.format(article=text)
    return formatted_output

def use_chat_prompt(formatted_output):
    chat = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")
    prompt_result = chat.invoke(formatted_output)
    return prompt_result.content

def main():
    st.title("Article Summarizer, Meta Keyword Extractor, and Image Finder")

    # Input field for article topic
    topic = st.text_area("Enter the article topic:", key="article_topic_input")

    # Input field for desired word count in summary
    words = st.number_input("Enter the desired word count in the summary:", value=200)

    if st.button("Summarize"):
        if topic.strip() == "":
            st.error("Please enter an article topic.")
        else:
            summary = summarize_article(topic, words)
            st.subheader("Summary:")
            st.write(summary)

    # Input field for news article
    news_article = st.text_area("Enter the news article:", key="news_article_input")

    if st.button("Extract Meta Keywords"):
        if news_article.strip() == "":
            st.error("Please enter a news article.")
        else:
            formatted_output = use_prompt_template(news_article)
            meta_keywords = use_chat_prompt(formatted_output)
            st.subheader("Meta Keywords:")
            st.write(meta_keywords)

    # Automatically find relevant images for top 5 words
    if news_article.strip() != "":
        formatted_output = use_prompt_template(news_article)
        top_words = use_chat_prompt(formatted_output)
        start_index = top_words.find("[")
        end_index = top_words.find("]")
        list_content = top_words[start_index:end_index + 1]
        actual_list = eval(list_content)
        st.subheader("Article related images are :")
        #st.subheader("Images for Top Words:")
        
        for word in actual_list[:5]:
            st.write(word)
            response = requests.get(f"https://pixabay.com/api/?key={pixabay_api_key}&q={word}&per_page=3")
            if response.status_code == 200:
                data = response.json()
                if data["totalHits"] > 0:
                    for hit in data["hits"]:
                        st.image(hit["largeImageURL"], caption=word)
                else:
                    st.write(f"No images found for the word '{word}'.")
            else:
                st.write(f"Error fetching images for the word '{word}'. Please try again later.")

if __name__ == "__main__":
    main()

