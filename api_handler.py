import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from isodate import parse_duration

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_channel_details(channel_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()

    channel = response["items"][0]
    channel_info = {
        "Channel_Name": channel["snippet"]["title"],
        "Channel_Id": channel["id"],
        "Subscription_Count": int(channel["statistics"]["subscriberCount"]),
        "Channel_Views": int(channel["statistics"]["viewCount"]),
        "Channel_Description": channel["snippet"]["description"],
        "Playlist_Id": channel["contentDetails"]["relatedPlaylists"]["uploads"]
    }

    return channel_info


def get_videos_from_playlist(playlist_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults=10000
    )
    response = request.execute()

    videos = []

    for item in response["items"]:
        video_id = item["contentDetails"]["videoId"]
        video_title = item["snippet"]["title"]
        published_at = item["contentDetails"]["videoPublishedAt"]

        videos.append({
            "Video_Id": video_id,
            "Video_Title": video_title,
            "Published_At": published_at
        })
    
    return videos

def get_video_stats(video_ids):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    id_string = ",".join(video_ids[:])

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=id_string,
        maxResults=10000
    )
    response = request.execute()

    video_stats=[]

    for item in response["items"]:
        video_stats.append({
            "Video_Id": item["id"],
            "Video_Name": item["snippet"]["title"],
            "Video_Description": item["snippet"]["description"],
            "Tags": item["snippet"].get("tags",[]),
            "Published_At": item["snippet"]["publishedAt"],
            "View_Count": item["statistics"].get("viewCount", 0),
            "Like_Count": item["statistics"].get("likeCount", 0),
            "Favorite_Count": item["statistics"].get("favoriteCount", 0),
            "Comment_Count": item["statistics"].get("commentCount", 0),
            "Duration": parse_duration(item["contentDetails"]["duration"]).total_seconds(),
            "Caption_Status": item["contentDetails"]["caption"],
            "Thumbnail": item["snippet"]["thumbnails"]["default"]["url"]
        })

    return video_stats

def get_comments(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=1000
        )
        response = request.execute()
    except HttpError as e:
        print(f"Warning: Could not fetch comments for video {video_id}. Reason: {e}")
        return []

    comments = []
    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "Comment_Id": item["id"],
            "Video_Id": video_id,
            "Comment_Text": comment.get("textDisplay",""),
            "Comment_Author": comment.get("authorDisplayName",""),
            "Comment_Published_Date": comment.get("publishedAt", "")
        })
    
    return comments