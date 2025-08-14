from api_handler import get_channel_details, get_videos_from_playlist, get_video_stats, get_comments

channel_id = "UCMiJRAwDNSNzuYeN2uWa0pA"
channel_data = get_channel_details(channel_id)

if channel_data:
    for key, value in channel_data.items():
        print(f"{key}: {value}")
    
    playlist_id = channel_data["Playlist_Id"]
    videos = get_videos_from_playlist(playlist_id)

    video_ids = [v["Video_Id"] for v in videos]
    stats = get_video_stats(video_ids)

    for video in stats[:3]:
        print(video)

    sample_video_id = stats[0]["Video_Id"]
    comments = get_comments(sample_video_id)

    for c in comments[:3]:
        print(c)