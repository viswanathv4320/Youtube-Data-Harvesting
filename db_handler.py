import mysql.connector

def connect_to_db():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql123",
        database="youtube_data"
    )
    return connection

def create_tables():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        channel_id VARCHAR(255) PRIMARY KEY,
        channel_name VARCHAR(255),
        channel_type VARCHAR(255),
        channel_views BIGINT,
        channel_description TEXT,
        channel_status VARCHAR(255)
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlists (
        playlist_id VARCHAR(255) PRIMARY KEY,
        channel_id VARCHAR(255),
        playlist_name VARCHAR(255),
        FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        video_id VARCHAR(255) PRIMARY KEY,
        playlist_id VARCHAR(255),
        video_name VARCHAR(255),
        video_description TEXT,
        published_date DATETIME,
        view_count BIGINT,
        like_count BIGINT,
        favorite_count BIGINT,
        comment_count BIGINT,
        duration BIGINT,
        thumbnail VARCHAR(255),
        caption_status VARCHAR(255),
        FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE
    )
    """)
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        comment_id VARCHAR(255) PRIMARY KEY,
        video_id VARCHAR(255),
        comment_text TEXT,
        comment_author VARCHAR(255),
        comment_published_date DATETIME,
        FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("All tables created successfully.")

if __name__ == "__main__":
    create_tables()
