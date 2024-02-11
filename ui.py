# Import notwendiger Bibliotheken
import streamlit as st
import asyncio
import json
from pydantic import BaseModel
from typing import List
from serp import search_google_web_automation
from my_functions import get_article_from_url, generate_ideas

prompt = "we are in the german market - give all answers in german. Extract 3 - 5 content ideas from the [post], and return the list in json format, [post]: {post}"

# Define die Klasse Ideas
class Ideas(BaseModel):
    ideas: List[str]

# Async-Funktion zur Verarbeitung der Hauptlogik
async def main(search_query, st):
    try:
        # Zeige den Spinner an
        with st.spinner("Wait for the magic!"):
            search_results = search_google_web_automation(search_query, 10)
            all_ideas = []

            # Initialize Progress-Bar
            progress_bar = st.progress(0)
            total_results = len(search_results)

            for index, result in enumerate(search_results):
                try:
                    # Update Progress-Bar
                    progress_bar.progress((index + 1) / total_results)

                    result_url = result["url"]
                    result_content = get_article_from_url(result_url)

                    if result_content:
                        result_prompt = prompt.format(post=result_content)
                        ideas_object = await generate_ideas(result_prompt, Ideas)

                        if ideas_object and ideas_object.ideas:
                            all_ideas.extend(ideas_object.ideas)
                except Exception as e:
                    st.error(f"Error processing search result {result}: {e}")

            # Display URLs and Titles
            st.write("Websites, von denen die Content-Ideen übernommen wurden:")
            for result in search_results:
                st.write(result["url"])

                # Display H-Titles in an expander
                with st.expander(f"Siehe H-Titel für {result['url']}"):
                    for h_title in result.get("htitles", []):
                        st.write(f"{h_title}")

            # Ensure Progress-Bar is filled when process is complete
            progress_bar.progress(100)

            # Display the number of records
            st.write(f"Anzahl der generierten Ideen: {len(all_ideas)}")

            # Convert the Ideas to JSON and display in an expander
            json_output = json.dumps(all_ideas, indent=4)
            with st.expander("Generierte Ideen anzeigen (JSON)"):
                st.json(json_output)

    except Exception as e:
        st.error(f"Error fetching search results: {e}")
        

# Streamlit UI setup
st.title("Content Ideen-Generator")

# User input fields
search_query = st.text_input("Suchanfrage eingeben:", "")

# Button to trigger the process
if st.button("Generiere die Ideen"):
    # Run the main function asynchronously
    asyncio.run(main(search_query, st))
