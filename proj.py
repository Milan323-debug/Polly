from flask import Flask, request, jsonify, render_template, send_from_directory
import boto3
from flask_cors import CORS

app = Flask(__name__, static_folder='', template_folder='')
CORS(app)

# Amazon Polly client setup
polly_client = boto3.client(
    'polly',
    region_name='us-east-1',
    aws_access_key_id='paste the aws access id',
    aws_secret_access_key='paste the secret key'
)

@app.route('/')
def index():
    # Serve the HTML file
    return render_template('index2.html')

@app.route('/convert', methods=['POST'])
def convert_to_speech():
    try:
        data = request.json  # Read JSON data sent by the front-end
        text = data.get('text', '')
        voice = data.get('voice', 'Joanna')  # Default to 'Joanna'
        speed = data.get('speed', 'medium')  # Default to 'medium'
        volume = data.get('volume', '0.5')  # Default to 0.5 (50%)

        if not text:
            return jsonify({'error': 'Text input is required!'}), 400

        # Validate and convert volume to a valid SSML value
        volume_percent = float(volume) * 100
        if volume_percent <= 0:
            ssml_volume = "silent"
        elif volume_percent < 50:
            ssml_volume = "x-soft"
        elif volume_percent < 75:
            ssml_volume = "soft"
        elif volume_percent <= 100:
            ssml_volume = "medium"
        else:
            ssml_volume = "loud"

        # Construct SSML with valid Polly attributes
        ssml_text = f"""
        <speak>
            <prosody rate="{speed}" volume="{ssml_volume}">{text}</prosody>
        </speak>
        """

        # Call Amazon Polly with SSML
        response = polly_client.synthesize_speech(
            TextType='ssml',
            Text=ssml_text,
            OutputFormat='mp3',
            VoiceId=voice
        )

        # Return the audio stream
        audio_stream = response['AudioStream'].read()
        return audio_stream, 200, {
            'Content-Type': 'audio/mpeg',
            'Content-Disposition': 'inline; filename="speech.mp3"'
        }

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve static files (like CSS)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('', filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

