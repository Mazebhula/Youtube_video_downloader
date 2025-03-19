from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

def download_youtube_video(url, output_path="videos"):
    try:
        if output_path is None:
            output_path = os.getcwd()
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': False,
            'progress': True,
            'geo_bypass': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'cookiesfrombrowser': ('chrome',),
            'noplaylist': True,
        }#written by ds dzebu

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return {
                'success': True,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 'Unknown'),
                'uploader': info.get('uploader', 'Unknown'),
                'path': output_path
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'})
    
    result = download_youtube_video(url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)