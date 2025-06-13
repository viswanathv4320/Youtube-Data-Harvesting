import mysql.connector
from datetime import datetime

def connect_to_db():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql123",
        database="youtube_data"
    )
    return connection

def insert_channel(channel_data):
    conn = connect_to_db()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO channels (channel_id, channel_name, channel_type, channel_views, channel_description, channel_status)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        channel_name = VALUES(channel_name),
        channel_type = VALUES(channel_type),
        channel_views = VALUES(channel_views),
        channel_description = VALUES(channel_description),
        channel_status = VALUES(channel_status)
    """
    values = (
        channel_data["Channel_Id"],
        channel_data["Channel_Name"],
        "Unknown",  # channel_type placeholder
        channel_data["Channel_Views"],
        channel_data["Channel_Description"],
        "Active"    # channel_status placeholder
    )

    cursor.execute(insert_query,values)
    conn.commit()
    cursor.close()
    conn.close()

def insert_playlist(playlist_id, channel_id, playlist_name):
    conn = connect_to_db()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO playlists (playlist_id, channel_id, playlist_name)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
        playlist_name = VALUES(playlist_name)
    """

    cursor.execute(insert_query, (playlist_id, channel_id, playlist_name))
    conn.commit()
    cursor.close()
    conn.close()

def insert_videos(video_list, playlist_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO videos (video_id, playlist_id, video_name, video_description, published_date,
                        view_count, like_count, favorite_count, comment_count, duration,
                        thumbnail, caption_status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        video_name = VALUES(video_name),
        view_count = VALUES(view_count),
        like_count = VALUES(like_count),
        comment_count = VALUES(comment_count)
    """
    
    for video in video_list:
        published_at = video["Published_At"]
        published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        values = (
            video["Video_Id"],
            playlist_id,
            video["Video_Name"],
            video["Video_Description"],
            published_at,
            video["View_Count"],
            video["Like_Count"],
            video["Favorite_Count"],
            video["Comment_Count"],
            video["Duration"],
            video["Thumbnail"],
            video["Caption_Status"]
        )
        cursor.execute(insert_query, values)

    conn.commit()
    cursor.close()
    conn.close()

def insert_comments(comment_list, video_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO comments (comment_id, video_id, comment_text, comment_author, comment_published_date)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        comment_text = VALUES(comment_text),
        comment_author = VALUES(comment_author)
    """

    for comment in comment_list:
        published_at = comment["Comment_Published_Date"]
        published_dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        values = (
            comment["Comment_Id"],
            video_id,
            comment["Comment_Text"],
            comment["Comment_Author"],
            published_dt
        )
        cursor.execute(insert_query, values)

    conn.commit()
    cursor.close()
    conn.close()
