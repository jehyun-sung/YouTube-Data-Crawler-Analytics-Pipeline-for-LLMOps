import os
import pickle
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# ===== 설정 =====
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_SECRETS_FILE = os.getenv(
    "YOUTUBE_CLIENT_SECRET",
)
TOKEN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.pickle")


def get_authenticated_service():
    """Authenticate and return YouTube API service"""
    if not os.path.exists(CLIENT_SECRETS_FILE):
        raise FileNotFoundError(f"client_secrets.json이 없습니다: {CLIENT_SECRETS_FILE}")

    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not getattr(creds, "valid", False):
        if creds and getattr(creds, "expired", False) and getattr(creds, "refresh_token", None):
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)


def search_videos(youtube, query, max_results=50):
    """Search for videos and return metadata"""
    response = youtube.search().list(
        part='id,snippet',
        q=query,
        type='video',
        maxResults=max_results
    ).execute()

    videos = []
    for item in response.get('items', []):
        videos.append({
            'video_id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'channel': item['snippet']['channelTitle'],
            'description': item['snippet']['description']
        })
    return videos


def get_video_details(youtube, video_id):
    """Get likes/views/comments count"""
    response = youtube.videos().list(
        part='statistics',
        id=video_id
    ).execute()

    if response.get('items'):
        stats = response['items'][0]['statistics']
        return {
            'likes': stats.get('likeCount', 'N/A'),
            'views': stats.get('viewCount', 'N/A'),
            'comments_count': stats.get('commentCount', 'N/A')
        }
    return None


def get_video_transcript(video_id):
    """Get transcript text"""
    try:
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
        except:
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            except:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([item['text'] for item in transcript_data])
        return text
    except Exception as e:
        return f"Transcript not available ({e})"


def main():
    youtube = get_authenticated_service()
    query = "어머니생신선물"
    print(f"🔍 검색어: {query}")

    videos = search_videos(youtube, query, max_results=50)

    all_data = []
    for i, video in enumerate(videos, 1):
        vid = video['video_id']
        print(f"분석 중... ({i}/50): {video['title']}")
        details = get_video_details(youtube, vid)
        transcript = get_video_transcript(vid)

        all_data.append({
            "No": i,
            "Title": video['title'],
            "Channel": video['channel'],
            "Video URL": f"https://www.youtube.com/watch?v={vid}",
            "Description": video['description'],
            "Views": details.get('views', 'N/A') if details else 'N/A',
            "Likes": details.get('likes', 'N/A') if details else 'N/A',
            "Comments Count": details.get('comments_count', 'N/A') if details else 'N/A',
            "Transcript (Preview)": transcript[:200] + "..." if transcript else "N/A"
        })

    df = pd.DataFrame(all_data)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube_videos.xlsx")
    df.to_excel(output_path, index=False)
    print(f"\n✅ 엑셀 저장 완료: {output_path}")


if __name__ == "__main__":
    main()
