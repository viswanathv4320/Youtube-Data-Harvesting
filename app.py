# import streamlit as st
# import time
# from api_handler import get_channel_details, get_videos_from_playlist, get_video_stats, get_comments
# from db_inserter import insert_channel, insert_playlist, insert_videos, insert_comments

# st.title("YouTube Data Harvesting App")

# st.sidebar.button("Home")

# data_collection_clicked = st.sidebar.button("Data Collection")
# if "channel_data" not in st.session_state:
#     st.session_state.channel_data = None

# if data_collection_clicked:
#     channel_id = st.text_input("Enter Youtube Channel ID")
#     fetch_clicked = st.button("Fetch Channel Data")

#     if fetch_clicked:
#         with st.spinner("Fetching..."):
#             time.sleep(1)
#             data = get_channel_details(channel_id)
#             st.session_state.channel_data = data
#             st.success("Channel data fetched!")
#     if st.session_state.channel_data:
#         st.subheader("Channel Details:")
#         st.json(st.session_state.channel_data)

import streamlit as st
import time
from api_handler import get_channel_details, get_videos_from_playlist, get_video_stats, get_comments
from db_inserter import insert_channel, insert_playlist, insert_videos, insert_comments
from db_handler import connect_to_db
import pandas as pd

def get_channel_count():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM channels")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

def wipe_database():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    cursor.execute("DELETE FROM comments")
    cursor.execute("DELETE FROM videos")
    cursor.execute("DELETE FROM playlists")
    cursor.execute("DELETE FROM channels")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    conn.commit()
    cursor.close()
    conn.close()

st.set_page_config(layout="wide")
st.title("YouTube Data Harvesting")

# Initializing session state
if "page" not in st.session_state:
    st.session_state.page = "home"
if "channel_data" not in st.session_state:
    st.session_state.channel_data = None

# Sidebar navigation
with st.sidebar:
    st.markdown("## Navigation")
    if st.button("Home"):
        st.session_state.page = "home"
    if st.button("Data Collection"):
        st.session_state.page = "collect"
    if st.button("Migrate to SQL"):
        st.session_state.page = "migrate"
    if st.button("Data Visualization"):
        st.session_state.page = "visualize"

# ----------------- PAGE: HOME -----------------
if st.session_state.page == "home":
    st.subheader("Welcome to the YouTube Data Harvesting App!")
    st.markdown("""
    - Fetch data from the YouTube API using a Channel ID
    - View channel details
    - Migrate the data (channels, playlists, videos, comments) into a MySQL database
    - Analyze the data via SQL queries
    
    """)

# ----------------- PAGE: DATA COLLECTION -----------------
elif st.session_state.page == "collect":
    st.subheader("Collect Channel Data")

    channel_id = st.text_input("Enter YouTube Channel ID")
    if st.button("Fetch Channel Data"):
        with st.spinner("Fetching data from YouTube API..."):
            time.sleep(0.5)
            
            #  Fetching channel details
            channel_data = get_channel_details(channel_id)
            video_data = get_videos_from_playlist(channel_data["Playlist_Id"])
            
            # Storing all data in session state
            st.session_state.channel_data = channel_data
            st.session_state.video_data = video_data

            st.success("All data fetched successfully!")

    if st.session_state.channel_data:
        
        # -------- Channel Details ----------
        st.subheader("Channel Details")
        ch = st.session_state.channel_data
        st.markdown(f"""
        **Channel Name:** {ch["Channel_Name"]}  
        **Channel ID:** `{ch["Channel_Id"]}`  
        **Subscribers:** {ch["Subscription_Count"]}  
        **Total Views:** {ch["Channel_Views"]}  
        **Playlist ID:** `{ch["Playlist_Id"]}`  
        **Description:**  
         {ch["Channel_Description"]}
        """)

        # --------- Video Details -----------
        if "video_data" in st.session_state:
            st.subheader("Video Details")
            st.dataframe(st.session_state.video_data)

# ----------------- PAGE: MIGRATE TO SQL -------------------
elif st.session_state.page == "migrate":
    st.subheader("Migrate Data to MySQL")

    if st.session_state.channel_data:
        if st.button("Store All Data in MySQL"):
            with st.spinner("Inserting data into MySQL..."):
                # Channel
                insert_channel(st.session_state.channel_data)

                # Playlist
                playlist_id = st.session_state.channel_data["Playlist_Id"]
                channel_id = st.session_state.channel_data["Channel_Id"]
                playlist_name = "Uploads"
                insert_playlist(playlist_id, channel_id, playlist_name)

                # Videos
                video_list = get_videos_from_playlist(playlist_id)
                video_ids = [video["Video_Id"] for video in video_list]
                video_stats = get_video_stats(video_ids)
                insert_videos(video_stats, playlist_id)

                # Comments
                for video_id in video_ids:
                    comments = get_comments(video_id)
                    insert_comments(comments, video_id)

                st.success("All data stored in MySQL!")
    else:
        st.warning("Please fetch channel data first from the 'Data Collection' tab.")


# ----------------- PAGE: DATA VISUALIZATION -------------------
elif st.session_state.page == "visualize":

    st.subheader("Channels in Database")
    channel_count = get_channel_count()
    st.metric(label="Total Channels", value=channel_count)

    st.subheader("Select the Questions to get Insights")

    option = st.selectbox("",
        ("Q1. What are the names of all the videos and their corresponding channels?",
         "Q2. Which channels have the most number of videos, and how many videos do they have?",
         "Q3. What are the top 10 most viewed videos and their respective channels?",
         "Q4. How many comments were made on each video, and what are their corresponding video names?",
         "Q5. Which videos have the highest number of likes, and what are their corresponding channel names?", 
         "Q6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
         "Q7. What is the total number of views for each channel, and what are their corresponding channel names?",
         "Q8. What are the names of all the channels that have published videos in the year 2025?",
         "Q9. What is the average duration of all videos in each channel, and what are their corresponding channel names?",
         "Q10. Which videos have the highest number of comments, and what are their corresponding channel names?"),
         index=None,
         placeholder="Select question"
    )

    if option:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        if option == "Q1. What are the names of all the videos and their corresponding channels?":
            query = """
            SELECT videos.video_name, channels.channel_name
            FROM videos
            JOIN playlists ON videos.playlist_id = playlists.playlist_id
            JOIN channels ON playlists.channel_id = channels.channel_id;
            """

        elif option == "Q2. Which channels have the most number of videos, and how many videos do they have?":
            query = """
            SELECT channels.channel_name, COUNT(videos.video_id) AS video_count
            FROM videos
            JOIN playlists ON videos.playlist_id = playlists.playlist_id
            JOIN channels ON playlists.channel_id = channels.channel_id
            GROUP BY channels.channel_name
            ORDER BY video_count DESC;
            """

        elif option == "Q3. What are the top 10 most viewed videos and their respective channels?":
            query = """
            SELECT videos.video_name, channels.channel_name, videos.view_count
            FROM videos
            JOIN playlists ON videos.playlist_id = playlists.playlist_id
            JOIN channels ON playlists.channel_id = channels.channel_id
            ORDER BY videos.view_count DESC
            LIMIT 10;
            """

        elif option == "Q4. How many comments were made on each video, and what are their corresponding video names?":
            query = """
            SELECT videos.video_name, COUNT(comments.comment_id) AS comment_count
            FROM comments
            JOIN videos ON comments.video_id = videos.video_id
            GROUP BY videos.video_name
            ORDER BY comment_count DESC;
            """

        elif option == "Q5. Which videos have the highest number of likes, and what are their corresponding channel names?":
            query = """
            SELECT videos.video_name, channels.channel_name, videos.like_count
            FROM videos
            JOIN playlists ON videos.playlist_id = playlists.playlist_id
            JOIN channels ON playlists.channel_id = channels.channel_id
            ORDER BY videos.like_count DESC;
            """

        elif option == "Q6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?":
            query = """
            SELECT videos.video_name, videos.like_count
            FROM videos
            ORDER BY videos.like_count DESC
            LIMIT 50;
            """

        elif option == "Q7. What is the total number of views for each channel, and what are their corresponding channel names?":
            query = """
            SELECT channels.channel_name, channels.channel_views
            FROM channels;
            """

        elif option == "Q8. What are the names of all the channels that have published videos in the year 2025?":
            query = """
            SELECT DISTINCT channels.channel_name
            FROM videos
            JOIN playlists ON videos.playlist_id = playlists.playlist_id
            JOIN channels ON playlists.channel_id = channels.channel_id
            WHERE YEAR(videos.published_date) = 2025;
            """

        elif option == "Q9. What is the average duration of all videos in each channel, and what are their corresponding channel names?":
            query = """
            SELECT channels.channel_name, AVG(videos.duration) AS avg_duration
            FROM videos
            JOIN playlists ON videos.playlist_id = playlists.playlist_id
            JOIN channels ON playlists.channel_id = channels.channel_id
            GROUP BY channels.channel_name;
            """
        
        elif option == "Q10. Which videos have the highest number of comments, and what are their corresponding channel names?":
            query = """
            SELECT channels.channel_name, videos.video_name, COUNT(comments.comment_id) AS comment_count
            FROM comments
            JOIN videos ON comments.video_id = videos.video_id
            JOIN playlists ON videos.playlist_id = playlists.playlist_id
            JOIN channels ON playlists.channel_id = channels.channel_id
            GROUP BY videos.video_name, channels.channel_name
            ORDER BY comment_count DESC;
            """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        st.dataframe(df)

        cursor.close()
        conn.close()

    st.markdown("---")
    st.subheader("Clearing Database")

    if st.button("Clear ALL Channel Data from MySQL"):
        wipe_database()
