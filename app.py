import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import altair as alt

# API Key (Replace with your actual API Key - securely manage this!)
GENAI_API_KEY = "API_KEY"  # Replace with your actual API key
genai.configure(api_key=GENAI_API_KEY)

# Model Configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import altair as alt

# API Key (Replace with your actual API Key - securely manage this!)
# API key loading and configuration
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("API Key not found in Streamlit Secrets.")
    st.stop()
except Exception as e:
    st.error(f"Error configuring API: {e}")
    st.stop()

# Model Configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",  # Or appropriate model
    generation_config=generation_config,
)

# Chat Session (Define the prompt once)
@st.cache_resource  # Cache this to avoid recreating it on every rerun
def create_chat_session():
    return model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "## Improved Prompt for Sentiment Analysis AI Model\n\n**Task:** Analyze the sentiment expressed in the given text and classify it as positive, negative, or neutral. Provide a clear and concise explanation for your classification.\n\n**Input:** [The text to be analyzed]\n\n**Output Format:** (Sentiment - Reason)\n\n**Sentiment Categories:**\n\n*   **Positive:** Expresses favorable opinions, emotions, or attitudes.  Examples include praise, appreciation, excitement, joy, and approval.\n*   **Negative:** Expresses unfavorable opinions, emotions, or attitudes. Examples include criticism, disappointment, anger, sadness, and disapproval.\n*   **Neutral:** Expresses neither positive nor negative sentiment.  Examples include factual statements, objective descriptions, and information without emotional tone.  Ambiguous or mixed sentiment should lean towards neutral unless one sentiment clearly outweighs the other.\n\n**Reasoning Guidelines:**\n\n*   The reason should clearly justify the chosen sentiment category.\n*   Refer to specific words, phrases, or sentence structures in the input text that support your analysis.\n*   Explain *why* those elements indicate the identified sentiment.\n*   Avoid vague or generic explanations like \"the text sounds positive.\" Be specific.\n*   For neutral sentiment, explain why the text lacks clear positive or negative indicators.\n\n**Example 1:**\n\n**Input:** \"The movie was absolutely fantastic! The acting was superb, and the plot was captivating from beginning to end. I highly recommend it.\"\n\n**Output:** (Positive - The text contains strong positive words like \"fantastic,\" \"superb,\" and \"captivating.\"  The phrase \"highly recommend\" explicitly expresses approval. These elements clearly indicate a positive sentiment towards the movie.)\n\n**Example 2:**\n\n**Input:** \"I was extremely disappointed with the service. The staff was rude and unhelpful, and my order was completely wrong. I will never go back.\"\n\n**Output:** (Negative -  Words like \"disappointed,\" \"rude,\" and \"unhelpful\" express negative feelings. The statement \"my order was completely wrong\" indicates a negative experience. The phrase \"I will never go back\" reinforces the negative sentiment.)\n\n**Example 3:**\n\n**Input:** \"The meeting is scheduled for 3 PM tomorrow in conference room B.\"\n\n**Output:** (Neutral - The text provides factual information about a meeting. It does not contain any words or phrases that express positive or negative emotions or opinions.)\n\n**Example 4 (Ambiguous):** \"The movie was long, but it had some interesting moments.\"\n\n**Output:** (Neutral - While \"long\" could be seen as slightly negative, it's balanced by \"interesting moments,\" creating a mixed sentiment.  Without more context, the overall sentiment leans towards neutral as neither positive nor negative clearly outweighs the other.)\n\n**Example 5 (Mixed but leaning):** \"The movie started slow and I almost left, but the ending was surprisingly good. I'm glad I stayed.\"\n\n**Output:** (Positive - Although the initial part of the movie was perceived negatively (\"started slow,\" \"almost left\"), the overall sentiment is positive due to the \"surprisingly good\" ending and the expression of gladness (\"I'm glad I stayed\").  The positive sentiment at the end outweighs the initial negativity.)\n\n\n**Important Considerations for Your Model:**\n\n*   **Context:**  Sentiment can be context-dependent.  Consider providing context to your model if necessary.\n*   **Sarcasm/Irony:**  Train your model to recognize sarcasm and irony, which can invert the apparent sentiment.\n*   **Negation:**  Handle negation words (e.g., \"not,\" \"no,\" \"never\") correctly.\n*   **Intensity:**  Consider the intensity of sentiment (e.g., \"good\" vs. \"amazing\").\n*   **Subjectivity:**  Distinguish between subjective opinions and objective facts.\n\nThis improved prompt should provide a clearer and more comprehensive guideline for your sentiment analysis AI model, leading to better performance and more accurate classifications.",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "Understood. I am ready to analyze sentiment according to your provided guidelines."
                ],
            },
        ]
    )

chat_session = create_chat_session() # Initialise chat session

# Sentiment Analysis Function
def analyze_sentiment(text):
    """Analyzes the sentiment of a given text using the Gemini model."""
    response = chat_session.send_message(text)
    sentiment = response.text.strip().replace('`', "").replace(". ", "").replace(')', ")")
    sentiment_parts = sentiment.split("-")
    if len(sentiment_parts) >= 2:  # Handle potential errors
        return sentiment_parts[0].strip(), sentiment_parts[1].strip()
    else:
        return "Error", "Could not extract sentiment and reason."


# Streamlit App
st.title("SENTIMENT ANALYSIS App")
st.markdown("From text to emotion: explore sentiment analysis.")

# Input Text Area
text_input = st.text_area("Enter text to analyze:", "This is a great app!")

# Analyze Button
if st.button("Analyze Sentiment"):
    if text_input:
        with st.spinner("Analyzing..."):
            sentiment, reason = analyze_sentiment(text_input)
            st.write(f"**Sentiment:** {sentiment}")
            st.write(f"**Reason:** {reason}")
    else:
        st.warning("Please enter some text to analyze.")


# Bulk Analysis Feature
st.header("Bulk Sentiment Analysis")
bulk_input = st.text_area("Enter multiple sentences (one sentence per line):", "")

if st.button("Analyze Bulk Sentiments"):
    if bulk_input:
        sentences = [line.strip() for line in bulk_input.splitlines() if line.strip()]
        bulk_data = []
        progress_bar = st.progress(0)  # Initialize progress bar
        total_sentences = len(sentences)

        for i, sentence in enumerate(sentences):
            with st.spinner(f"Analyzing: {sentence}"):
                sentiment, reason = analyze_sentiment(sentence)
                bulk_data.append({"Sentence": sentence, "Sentiment": sentiment, "Reason": reason})
                time.sleep(4)  # Respect API limits

            progress_percent = (i + 1) / total_sentences
            progress_bar.progress(progress_percent)

        bulk_df = pd.DataFrame(bulk_data)
        st.dataframe(bulk_df)

        # Sentiment Distribution Chart for Bulk Analysis
        st.header("Sentiment Distribution Chart (Bulk Analysis)")
        try:
            chart = alt.Chart(bulk_df).mark_bar().encode(
                x='Sentiment',
                y='count()',
                tooltip=['Sentiment', 'count()']
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating chart: {e}")
    else:
        st.warning("Please enter some sentences for bulk analysis.")

st.markdown("---")

st.markdown("This Streamlit app uses Gemini to analyze text sentiment. Enter text for single analysis, or multiple sentences for bulk analysis. A chart shows sentiment distribution for bulk input.")

st.markdown("2025 PeterSynaptic. All rights reserved")
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",  # Or appropriate model
    generation_config=generation_config,
)

# Chat Session (Define the prompt once)
@st.cache_resource  # Cache this to avoid recreating it on every rerun
def create_chat_session():
    return model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "## Improved Prompt for Sentiment Analysis AI Model\n\n**Task:** Analyze the sentiment expressed in the given text and classify it as positive, negative, or neutral. Provide a clear and concise explanation for your classification.\n\n**Input:** [The text to be analyzed]\n\n**Output Format:** (Sentiment - Reason)\n\n**Sentiment Categories:**\n\n*   **Positive:** Expresses favorable opinions, emotions, or attitudes.  Examples include praise, appreciation, excitement, joy, and approval.\n*   **Negative:** Expresses unfavorable opinions, emotions, or attitudes. Examples include criticism, disappointment, anger, sadness, and disapproval.\n*   **Neutral:** Expresses neither positive nor negative sentiment.  Examples include factual statements, objective descriptions, and information without emotional tone.  Ambiguous or mixed sentiment should lean towards neutral unless one sentiment clearly outweighs the other.\n\n**Reasoning Guidelines:**\n\n*   The reason should clearly justify the chosen sentiment category.\n*   Refer to specific words, phrases, or sentence structures in the input text that support your analysis.\n*   Explain *why* those elements indicate the identified sentiment.\n*   Avoid vague or generic explanations like \"the text sounds positive.\" Be specific.\n*   For neutral sentiment, explain why the text lacks clear positive or negative indicators.\n\n**Example 1:**\n\n**Input:** \"The movie was absolutely fantastic! The acting was superb, and the plot was captivating from beginning to end. I highly recommend it.\"\n\n**Output:** (Positive - The text contains strong positive words like \"fantastic,\" \"superb,\" and \"captivating.\"  The phrase \"highly recommend\" explicitly expresses approval. These elements clearly indicate a positive sentiment towards the movie.)\n\n**Example 2:**\n\n**Input:** \"I was extremely disappointed with the service. The staff was rude and unhelpful, and my order was completely wrong. I will never go back.\"\n\n**Output:** (Negative -  Words like \"disappointed,\" \"rude,\" and \"unhelpful\" express negative feelings. The statement \"my order was completely wrong\" indicates a negative experience. The phrase \"I will never go back\" reinforces the negative sentiment.)\n\n**Example 3:**\n\n**Input:** \"The meeting is scheduled for 3 PM tomorrow in conference room B.\"\n\n**Output:** (Neutral - The text provides factual information about a meeting. It does not contain any words or phrases that express positive or negative emotions or opinions.)\n\n**Example 4 (Ambiguous):** \"The movie was long, but it had some interesting moments.\"\n\n**Output:** (Neutral - While \"long\" could be seen as slightly negative, it's balanced by \"interesting moments,\" creating a mixed sentiment.  Without more context, the overall sentiment leans towards neutral as neither positive nor negative clearly outweighs the other.)\n\n**Example 5 (Mixed but leaning):** \"The movie started slow and I almost left, but the ending was surprisingly good. I'm glad I stayed.\"\n\n**Output:** (Positive - Although the initial part of the movie was perceived negatively (\"started slow,\" \"almost left\"), the overall sentiment is positive due to the \"surprisingly good\" ending and the expression of gladness (\"I'm glad I stayed\").  The positive sentiment at the end outweighs the initial negativity.)\n\n\n**Important Considerations for Your Model:**\n\n*   **Context:**  Sentiment can be context-dependent.  Consider providing context to your model if necessary.\n*   **Sarcasm/Irony:**  Train your model to recognize sarcasm and irony, which can invert the apparent sentiment.\n*   **Negation:**  Handle negation words (e.g., \"not,\" \"no,\" \"never\") correctly.\n*   **Intensity:**  Consider the intensity of sentiment (e.g., \"good\" vs. \"amazing\").\n*   **Subjectivity:**  Distinguish between subjective opinions and objective facts.\n\nThis improved prompt should provide a clearer and more comprehensive guideline for your sentiment analysis AI model, leading to better performance and more accurate classifications.",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "Understood. I am ready to analyze sentiment according to your provided guidelines."
                ],
            },
        ]
    )

chat_session = create_chat_session() # Initialise chat session

# Sentiment Analysis Function
def analyze_sentiment(text):
    """Analyzes the sentiment of a given text using the Gemini model."""
    response = chat_session.send_message(text)
    sentiment = response.text.strip().replace('`', "").replace(". ", "").replace(')', ")")
    sentiment_parts = sentiment.split("-")
    if len(sentiment_parts) >= 2:  # Handle potential errors
        return sentiment_parts[0].strip(), sentiment_parts[1].strip()
    else:
        return "Error", "Could not extract sentiment and reason."


# Streamlit App
st.title("SENTIMENT ANALYSIS App")
st.markdown("From text to emotion: explore sentiment analysis.")

# Input Text Area
text_input = st.text_area("Enter text to analyze:", "This is a great app!")

# Analyze Button
if st.button("Analyze Sentiment"):
    if text_input:
        with st.spinner("Analyzing..."):
            sentiment, reason = analyze_sentiment(text_input)
            st.write(f"**Sentiment:** {sentiment}")
            st.write(f"**Reason:** {reason}")
    else:
        st.warning("Please enter some text to analyze.")


# Bulk Analysis Feature
st.header("Bulk Sentiment Analysis")
bulk_input = st.text_area("Enter multiple sentences (one sentence per line):", "")

if st.button("Analyze Bulk Sentiments"):
    if bulk_input:
        sentences = [line.strip() for line in bulk_input.splitlines() if line.strip()]
        bulk_data = []
        progress_bar = st.progress(0)  # Initialize progress bar
        total_sentences = len(sentences)

        for i, sentence in enumerate(sentences):
            with st.spinner(f"Analyzing: {sentence}"):
                sentiment, reason = analyze_sentiment(sentence)
                bulk_data.append({"Sentence": sentence, "Sentiment": sentiment, "Reason": reason})
                time.sleep(4)  # Respect API limits

            progress_percent = (i + 1) / total_sentences
            progress_bar.progress(progress_percent)

        bulk_df = pd.DataFrame(bulk_data)
        st.dataframe(bulk_df)

        # Sentiment Distribution Chart for Bulk Analysis
        st.header("Sentiment Distribution Chart (Bulk Analysis)")
        try:
            chart = alt.Chart(bulk_df).mark_bar().encode(
                x='Sentiment',
                y='count()',
                tooltip=['Sentiment', 'count()']
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating chart: {e}")
    else:
        st.warning("Please enter some sentences for bulk analysis.")

st.markdown("---")

st.markdown("This Streamlit app uses the Gemini AI model to analyze the sentiment of text. Enter text to analyze manually, or enter multiple sentences for bulk sentiment analysis.  The chart displays the distribution of sentiments for bulk sentences entered above.")