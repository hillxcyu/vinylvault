import requests

url = "http://127.0.0.1:8000/api/chat-album"
payload = {
    "artist": "Tame Impala",
    "albumTitle": "Currents",
    "message": "Tell me about the recording gear and synth pedals used on this album!"
}

try:
    from gemini_service import gemini_service
    reply = gemini_service.chat_about_album(payload["artist"], payload["albumTitle"], payload["message"])
    print("AI Reply:")
    print(reply)
except Exception as e:
    print("Error:", e)
