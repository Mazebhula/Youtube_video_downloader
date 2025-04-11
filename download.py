from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

def download_youtube_video(url, output_path="videos", list_formats=False):
    try:
        if output_path is None:
            output_path = os.getcwd()
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Define a list of format strings to try in order
        format_options = [
            'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            'bestvideo+bestaudio/best',
            'best',
            '22/18/17/36'  # Common YouTube format codes (720p, 360p, etc.)
        ]

        ydl_opts = {
            # We'll set format later in the loop
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': False,
            'progress': True,
            'geo_bypass': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'cookiesfrombrowser': ('chrome',),
            'noplaylist': True,
            'ignoreerrors': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash'],
                }
            },
            'socket_timeout': 30,
            'retries': 10,
        }#written by ds dzebu

        if list_formats:
            # Just list available formats without downloading
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                format_list = []
                for f in formats:
                    format_list.append({
                        'format_id': f.get('format_id', 'Unknown'),
                        'extension': f.get('ext', 'Unknown'),
                        'resolution': f.get('resolution', 'Unknown'),
                        'filesize': f.get('filesize', 'Unknown'),
                        'format_note': f.get('format_note', '')
                    })
                return {
                    'success': True,
                    'title': info.get('title', 'Unknown'),
                    'formats': format_list
                }
        
        # Try each format option until one works
        last_error = None
        for format_option in format_options:
            try:
                ydl_opts['format'] = format_option
                print(f"Trying format: {format_option}")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                # If we get here, download was successful
                return {
                    'success': True,
                    'title': info.get('title', 'Unknown'),
                    'duration': info['duration'] if info and 'duration' in info else 'Unknown',
                    'uploader': info.get('uploader', 'Unknown'),
                    'path': output_path
                }
            except yt_dlp.utils.DownloadError as e:
                last_error = str(e)
                print(f"Format {format_option} failed: {last_error}")
                continue  # Try next format
        
        # If we get here, all formats failed
        return {'success': False, 'error': f"All format options failed. Last error: {last_error}"}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    list_formats = request.form.get('list_formats') == 'true'
    
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'})
    
    result = download_youtube_video(url, list_formats=list_formats)
    return jsonify(result)

@app.route('/formats', methods=['POST'])
def list_formats():
    url = request.form.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'})
    
    result = download_youtube_video(url, list_formats=True)
    return jsonify(result)

if __name__ == '__main__':
    import socket
    from werkzeug.serving import is_running_from_reloader
    
    # Try to find an available port starting from 5000
    port = 5000
    max_port = 5050  # Try ports up to 5050
    
    while port <= max_port:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            # If we get here, the port is available
            break
        except OSError:
            port += 1
    
    if port > max_port:
        print("Could not find an available port between 5000 and 5050.")
        exit(1)
    
    print(f"Starting server on port {port}")
    app.run(debug=False, port=port)
