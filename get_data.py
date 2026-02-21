from yt_dlp import YoutubeDL
from datetime import datetime, timedelta
import json
import time
import os
if not os.path.exists("transcripts"):
    os.makedirs("transcripts")
    print("transcripts folder created")
    

CHANNELS = [
    "https://www.youtube.com/@IvanOnTech",
    "https://www.youtube.com/@alessiorastani",
    "https://www.youtube.com/@CoinBureau"
    #"https://www.youtube.com/@coingecko",
    #"https://www.youtube.com/@DataDispatch",
    #"https://www.youtube.com/@FelixFriends",
    #"https://www.youtube.com/@TomNashTV",
    #"https://www.youtube.com/@DavidCarbutt",
    #"https://www.youtube.com/@CTOLARSSON",
    #"https://www.youtube.com/@elliotrades_official"
]

def get_transcript(video_id, lang='en'):
    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "skip_download": True,
        "writeautomaticsub": True,
        "writesubtitles": True,
        "subtitleslangs": ["en"],
        "quiet": True,
        "no_warnings": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print(info)
        # Felirat kinyerése
        subtitles = info.get("automatic_captions", {}).get(lang)

        if not subtitles:
            return None

        sub_url = subtitles[0]["url"]
        data = requests.get(sub_url).json()

        text_parts = []
        for event in data.get("events", []):
            if "segs" in event:
                for seg in event["segs"]:
                    text_parts.append(seg["utf8"])

        transcript=  " ".join(text_parts).replace("\n", " ").strip()
        print(transcript)

        # Thumbnail logika (biztonságosabb indexelés)
        thumbnails = info.get("thumbnails", [])
        smallest_thumbnail = thumbnails[0].get("url") if thumbnails else None
        if len(thumbnails) > 2:
             smallest_thumbnail = sorted(thumbnails, key=lambda t: t.get("width", 0))[2].get("url")

      
        return {
            "video_id": video_id,
            "title": info.get("title"),
            "url": url,
            "duration_minutes": info.get("duration", 0) / 60,
            "channel": info.get("channel"),
            "like_count": info.get("like_count"),
            "thumbnail_url": smallest_thumbnail,
            "channel_id": info.get("channel_id"),
            "channel": info.get("channel"),
            "channel_url: ": info.get("channel_url"),

            "transcript": transcript

        }

def get_recent_videos(channel_link, n_days=4):
    date_after = datetime.utcnow() - timedelta(days=n_days)
    video_ids = []

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"{channel_link}/videos", download=False)

            for entry in info.get("entries", []):
                video_id = entry["id"]
                time.sleep(1)

                with YoutubeDL({"quiet": True}) as ydl_video:
                    vinfo = ydl_video.extract_info(
                        f"https://www.youtube.com/watch?v={video_id}",
                        download=False
                    )

                upload_date = vinfo.get("upload_date")

                if not upload_date:
                    # nincs dátum → nem tudunk dönteni, menjünk tovább
                    continue

                upload_dt = datetime.strptime(upload_date, "%Y%m%d")

                if upload_dt >= date_after:
                    video_ids.append(video_id)
                else:
                    # 🔥 innentől minden régebbi lesz → megállunk
                    break
    # print the actual error
    except Exception as e:
        print(e)
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"{channel_link}/streams", download=False)

            for entry in info.get("entries", []):
                video_id = entry["id"]

                with YoutubeDL({"quiet": True}) as ydl_video:
                    vinfo = ydl_video.extract_info(
                        f"https://www.youtube.com/watch?v={video_id}",
                        download=False
                    )

                upload_date = vinfo.get("upload_date")

                if not upload_date:
                    # nincs dátum → nem tudunk dönteni, menjünk tovább
                    continue

                upload_dt = datetime.strptime(upload_date, "%Y%m%d")

                if upload_dt >= date_after:
                    video_ids.append(video_id)
                else:
                    # 🔥 innentől minden régebbi lesz → megállunk
                    break
    except Exception as e:
        print(e)

    print(f"Collected {len(video_ids)} videos")
    return video_ids

lang = "en"

for channel in CHANNELS:
    print('\n--------')
    print(channel)

    video_ids = get_recent_videos(channel, 10)
    for video_id in video_ids:
        print(video_id)
        time.sleep(2)
        # filenema will be videoid.json
        file_name = f"transcripts/{lang}_{video_id}.json"
        if os.path.exists(file_name):
            print(f"{file_name} already exists")
            continue

        transcript = get_transcript(video_id, lang)
        # write json with  encoding="utf-8" and indednt 4
        print(transcript)
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(transcript, f, ensure_ascii=False, indent=4)
        

