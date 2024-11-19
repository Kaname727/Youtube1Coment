import requests
import json
#guiなしのバージョンです
#結果などはターミナルに表示されます
URL = 'https://www.googleapis.com/youtube/v3/'
API_KEY = 'n'  # 自分で取得したApi Keyを入力

def get_comment_count(video_id):
    params = {
        'key': API_KEY,
        'part': 'statistics',
        'id': video_id
    }
    response = requests.get(URL + 'videos', params=params)
    resource = response.json()
    
    if 'items' in resource and resource['items']:
        comment_count = int(resource['items'][0]['statistics']['commentCount'])
        return comment_count
    else:
        print("コメント数を取得できませんでした。")
        return None

def get_all_comments(video_id):
    comments = []
    next_page_token = None

    while True:
        params = {
            'key': API_KEY,
            'part': 'snippet',
            'videoId': video_id,
            'maxResults': 100,
            'pageToken': next_page_token,
            'order': 'time'
        }
        response = requests.get(URL + 'commentThreads', params=params)
        resource = response.json()

        # エラーチェック(削除予定)
        if 'error' in resource:
            print("エラーが発生しました:", resource['error']['message'])
            break

        comments.extend(resource['items'])

        next_page_token = resource.get('nextPageToken')
        if not next_page_token:
            break

    return comments

def retrieve_oldest_comment(video_id):
    # コメント総数を取得
    comment_count = get_comment_count(video_id)
    if comment_count is None:
        return

    print(f"コメント総数: {comment_count}")
    
    # 取得時間を予測
    estimated_time_sec = comment_count / 100
    print(f"予想取得時間: {estimated_time_sec:.2f} 秒（約 {estimated_time_sec / 60:.2f} 分）")

    comments = get_all_comments(video_id)
    if not comments:
        print("コメントがありません。")
        return

    # １コメを表示
    oldest_comment = comments[-1]
    oldest_comment_text = oldest_comment['snippet']['topLevelComment']['snippet']['textDisplay']
    oldest_comment_like_count = oldest_comment['snippet']['topLevelComment']['snippet']['likeCount']
    oldest_comment_reply_count = oldest_comment['snippet']['totalReplyCount']
    oldest_comment_published_at = oldest_comment['snippet']['topLevelComment']['snippet']['publishedAt']

    print("\n１コメ:")
    print(f"コメント内容: {oldest_comment_text}")
    print(f"投稿日: {oldest_comment_published_at}")
    print(f"グッド数: {oldest_comment_like_count}, 返信数: {oldest_comment_reply_count}")

    # 返信を表示
    if 'replies' in oldest_comment:
        for reply in oldest_comment['replies']['comments']:
            reply_text = reply['snippet']['textDisplay']
            reply_like_count = reply['snippet']['likeCount']
            reply_published_at = reply['snippet']['publishedAt']

            print(f"  返信: {reply_text}")
            print(f"  投稿日: {reply_published_at}")
            print(f"  グッド数: {reply_like_count}")



#探したい動画のVideo idを入力(urlではないです)
video_id = 'n'
retrieve_oldest_comment(video_id)