import tkinter as tk
from tkinter import messagebox
import requests
import json
import os

# guiありのバージョンです
# 結果は選択した形式で保存されます
# apiは設定.jsonに保存されています
URL = 'https://www.googleapis.com/youtube/v3/'

# 保存先
SETTINGS_FILE = "設定.json"  # 設定を保存
RESULT_FILE_TXT = "１コメ.txt"  # txt形式の保存
RESULT_FILE_JSON = "１コメ.json"  # json形式の保存

def lak():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)
            return settings.get("api_key", "")
    return ""

def sak(api_key):
    settings = {"api_key": api_key}
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)

def gcc(video_id):
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
        messagebox.showerror("エラー", "コメント数を取得できませんでした。")
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

        if 'error' in resource:
            messagebox.showerror("エラー", f"エラーが発生しました: {resource['error']['message']}")
            break

        comments.extend(resource['items'])

        next_page_token = resource.get('nextPageToken')
        if not next_page_token:
            break

    return comments

def retrieve_oldest_comment(video_id):
    # コメント総数を取得
    comment_count = gcc(video_id)
    if comment_count is None:
        return

    print(f"コメント総数: {comment_count}")
    
    # 取得時間を予測
    estimated_time_sec = comment_count / 100
    print(f"予想取得時間: {estimated_time_sec:.2f} 秒（約 {estimated_time_sec / 60:.2f} 分）")

    comments = get_all_comments(video_id)
    if not comments:
        messagebox.showinfo("情報", "コメントがありません。")
        return

    # 最初のコメントを表示
    oldest_comment = comments[-1]
    oldest_comment_text = oldest_comment['snippet']['topLevelComment']['snippet']['textDisplay']
    oldest_comment_like_count = oldest_comment['snippet']['topLevelComment']['snippet']['likeCount']
    oldest_comment_reply_count = oldest_comment['snippet']['totalReplyCount']
    oldest_comment_published_at = oldest_comment['snippet']['topLevelComment']['snippet']['publishedAt']

    print("\n最初のコメント:")
    print(f"コメント内容: {oldest_comment_text}")
    print(f"投稿日: {oldest_comment_published_at}")
    print(f"グッド数: {oldest_comment_like_count}, 返信数: {oldest_comment_reply_count}")

    replies_data = []
    if 'replies' in oldest_comment:
        for reply in oldest_comment['replies']['comments']:
            reply_text = reply['snippet']['textDisplay']
            reply_like_count = reply['snippet']['likeCount']
            reply_published_at = reply['snippet']['publishedAt']

            replies_data.append({
                "返信内容": reply_text,
                "いいね数": reply_like_count,
                "投稿日": reply_published_at
            })
            print(f"  返信: {reply_text}")
            print(f"  投稿日: {reply_published_at}")
            print(f"  グッド数: {reply_like_count}")

    result_data = {
        "最初のコメント": {
            "コメント内容": oldest_comment_text,
            "いいね数": oldest_comment_like_count,
            "返信数": oldest_comment_reply_count,
            "投稿日": oldest_comment_published_at
        },
        "返信": replies_data
    }
    # txt
    if save_option.get() == "TXT":
        with open(RESULT_FILE_TXT, "w", encoding="utf-8") as txt_file:
            txt_file.write(f"最初のコメント:\n")
            txt_file.write(f"コメント内容: {oldest_comment_text}\n")
            txt_file.write(f"いいね数: {oldest_comment_like_count}\n")
            txt_file.write(f"返信数: {oldest_comment_reply_count}\n")
            txt_file.write(f"投稿日: {oldest_comment_published_at}\n\n")
            txt_file.write("返信:\n")
            for reply in replies_data:
                txt_file.write(f"  返信内容: {reply['返信内容']}\n")
                txt_file.write(f"  いいね数: {reply['いいね数']}\n")
                txt_file.write(f"  投稿日: {reply['投稿日']}\n")
        messagebox.showinfo("成功", f"結果は'{RESULT_FILE_TXT}'に保存されました。")
    elif save_option.get() == "JSON":
        with open(RESULT_FILE_JSON, "w", encoding="utf-8") as json_file:
            json.dump(result_data, json_file, ensure_ascii=False, indent=4)
        messagebox.showinfo("成功", f"結果は'{RESULT_FILE_JSON}'に保存されました。")

def on_submit():
    video_id = video_id_entry.get().strip()
    api_key = api_key_entry.get().strip()

    if not video_id or not api_key:
        messagebox.showerror("エラー", "APIキーと動画IDを入力してください。")
        return

    sak(api_key)

    global API_KEY
    API_KEY = api_key

    comment_count = gcc(video_id)
    if comment_count is None:
        return

    estimated_time_sec = comment_count / 100
    comment_info_label.config(text=f"コメント総数: {comment_count}\n予想取得時間: {estimated_time_sec:.2f} 秒（約 {estimated_time_sec / 60:.2f} 分）")

    retrieve_oldest_comment(video_id)

# GUI
root = tk.Tk()
root.title("YouTube 1コメ取得ツール")
root.geometry("500x350")  # ウィンドウサイズを拡張

api_key_label = tk.Label(root, text="APIキー:")
api_key_label.pack(pady=5)
api_key_entry = tk.Entry(root, width=40)
api_key_entry.pack(pady=5)

video_id_label = tk.Label(root, text="動画ID:")
video_id_label.pack(pady=5)
video_id_entry = tk.Entry(root, width=40)
video_id_entry.pack(pady=5)

comment_info_label = tk.Label(root, text="", justify=tk.LEFT)
comment_info_label.pack(pady=10)
#json
save_option = tk.StringVar(value="JSON")  
save_option_label = tk.Label(root, text="保存形式:")
save_option_label.pack(pady=5)
save_option_frame = tk.Frame(root)
save_option_frame.pack()
save_option_json = tk.Radiobutton(save_option_frame, text="JSON", variable=save_option, value="JSON")
save_option_json.pack(side=tk.LEFT, padx=5)
save_option_txt = tk.Radiobutton(save_option_frame, text="TXT", variable=save_option, value="TXT")
save_option_txt.pack(side=tk.LEFT, padx=5)

submit_button = tk.Button(root, text="コメント取得", command=on_submit)
submit_button.pack(pady=20)

api_key = lak()
api_key_entry.insert(0, api_key)

root.mainloop()






