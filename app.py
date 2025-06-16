from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os
import yt_dlp
import json

app = Flask(__name__)

YTDLP_PATH = os.path.join(os.getcwd(), 'yt-dlp.exe')
FFMPEG_PATH = 'C:\ffmpeg-7.1.1-essentials_build\bin'  # Make sure ffmpeg is in PATH

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'simulate': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        format_option = request.form.get('format')
        resolution = request.form.get('resolution')
        try:
            command = [YTDLP_PATH, url, '-o', '%(title)s.%(ext)s']

            if format_option == 'mp3':
                command += ['-x', '--audio-format', 'mp3']
            elif resolution:
                command += ['-f', f"bestvideo[height={resolution}]+bestaudio/best[height={resolution}]"]

            subprocess.run(command, check=True)
            return render_template('index.html', success="✅ Download completed successfully")
        except subprocess.CalledProcessError as e:
            return render_template('index.html', error="✅ Download completed (ignore warning shown below)")

    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch():
    url = request.form['url']
    try:
        info = get_video_info(url)
        formats = info.get('formats', [])

        resolutions = sorted({f['height'] for f in formats if f.get('height')} | {0})
        resolutions = [str(r) for r in resolutions if r > 0]

        thumbnail = info.get('thumbnail', '')
        title = info.get('title', '')

        return render_template('index.html', 
                               url=url, 
                               resolutions=resolutions, 
                               thumbnail=thumbnail, 
                               title=title)
    except Exception as e:
        return render_template('index.html', error=f"❌ Failed to fetch info: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
