import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the necessary DataFrames
item_similarity_df = pd.read_pickle('item_similarity_df.pkl')
filtered_popular_events = pd.read_csv('C:/Users/CHUKS/Desktop/recommender/filtered_popular_events.csv')
q_events = pd.read_csv('C:/Users/CHUKS/Desktop/recommender/q_events.csv')
predicted_ratings = pd.read_csv('C:/Users/CHUKS/Desktop/recommender/predicted_ratings.csv')

# Create the title of the page
title = """
    <div style="display: flex; justify-content: center; align-items: center; font-size: 50px; font-weight: bold;">
        <span style="color: black;">LaughOutLoud</span>
        <span style="margin-left: 10px;">😂😂</span>
    </div>
    """

#create the about section
st.markdown(title, unsafe_allow_html=True)
st.sidebar.markdown("""
    <style>
        .about-box {
            background-color: #F7F0F0;
            border-radius: 8px;
            padding: 7px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            text-align: center;
        }
        .align-text {
            text-align: left;
        }
    </style>
    <div class="about-box">
        <h2 style="font-size: 25px; font-weight: bold;">About</h2>
    </div>
    <div class="align-text">
        Welcome to the LaughOutLoud😂 Recommender App! This app is designed to provide you with the best comedy events
        and recommendations based on your preferences. Enjoy the laughter and have a great time!
    </div>
    """, unsafe_allow_html=True)

# Filter for the top 10 events based on scores
popular_10_events = q_events.head(10)

# Plotting the top 10 popular events
plt.figure(figsize=(8, 5))
sns.barplot(x=popular_10_events['Rating'], y=popular_10_events['Joke_identifier'], color="#FF4B4B")
plt.title('Trending Comedy Events')
plt.xlabel('Popularity')
plt.ylabel('Comedy Event')

st.markdown("""
    <div style="padding: 20px; background-color: rgba(255, 255, 255, 0.8); box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); margin-top: 20px;">
        """, unsafe_allow_html=True)

st.pyplot(plt)


# Get Recommendations
def recommend_top_events(viewer_id, filtered_train_df, test_df, item_similarity_df, top_10_df, top_n=10):
    
    def format_top_events(top_10_df, top_n):
        top_events = top_10_df.head(top_n)['Joke_identifier'].tolist()
        formatted_events = "\n".join([f"{i+1}. {event}" for i, event in enumerate(top_events)])
        return formatted_events

    viewer_ratings = filtered_popular_events[filtered_popular_events['Viewers_ID'] == viewer_id]
    highly_rated_events = viewer_ratings[viewer_ratings['Rating'] >= 3]['Joke_identifier'] 
    
    if viewer_ratings.empty:
        return format_top_events(top_10_df, top_n)
    
    if highly_rated_events.empty:
        return format_top_events(top_10_df, top_n)

    scores = {}

    my_bar = st.progress(0)
    total_events = len(highly_rated_events)
    
    for idx,event_id in enumerate(highly_rated_events):
        if event_id in item_similarity_df.index:
            # Get similar items and their similarity scores
            similar_items = item_similarity_df.loc[event_id]
            
            for sim_item_id, similarity in similar_items.items():
                predicted_rating = test_df[(test_df['Viewers_ID'] == viewer_id) & (test_df['Joke_identifier'] == sim_item_id)]['Rating'].values
                if len(predicted_rating) > 0:
                    predicted_rating = predicted_rating[0]
                    if sim_item_id not in scores:
                        scores[sim_item_id] = 0
                    scores[sim_item_id] += similarity * predicted_rating
    
        # Update the progress bar
        my_bar.progress((idx + 1) / total_events)
                    
    if not scores:
        return format_top_events(top_10_df, top_n)
    
    # Sort items by their aggregated scores in descending order
    recommended_item_ids = sorted(scores, key=scores.get, reverse=True)[:top_n]
    
    # Create a numbered string of the top N item_ids
    recommended_items = "\n".join([f"{i+1}. {item_id}" for i, item_id in enumerate(recommended_item_ids)])
    
    return recommended_items

st.markdown("</div>", unsafe_allow_html=True)
viewer_id = st.selectbox('Get Recommendation As...', filtered_popular_events['Viewers_ID'].unique())

if st.button("Recommend"):
    with st.spinner("Getting Recommendations For You!!..."):
        top_10_events = recommend_top_events(viewer_id, filtered_popular_events, predicted_ratings, item_similarity_df, q_events)
        st.success("Recommendations Complete!")
        st.write("Top 10 Recommended Events For You:")
        st.text(top_10_events)


