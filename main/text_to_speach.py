import os
from io import BytesIO

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs


async def get_voice(text):

    load_dotenv()
    token = os.getenv("ELEVENLABS")

    elevenlabs = ElevenLabs(
        api_key=token,
    )

    try:
        audio = elevenlabs.text_to_speech.convert(
            text=f"{text}",
            voice_id="hU3rD0Yk7DoiYULTX1pD",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
    except Exception as e:
        print(e)

    au_st=BytesIO()
    for hunk in audio:
        au_st.write(hunk)
    au_st.seek(0)

    return au_st


