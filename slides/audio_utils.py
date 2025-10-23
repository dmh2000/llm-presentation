#!/usr/bin/env python3
"""
Audio utilities for text-to-speech and audio playback.

This module provides functions for:
- Generating speech from text using Google Gemini and ElevenLabs TTS APIs
- Converting between audio formats (PCM to WAV/MP3)
- Playing audio files using ffplay
"""
import sys
import os
import subprocess
import wave
import traceback
from google import genai
from google.genai import types
from pydub import AudioSegment

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play



def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    """
    Save PCM audio data to a WAV file.

    Args:
        filename: Path where the WAV file will be saved
        pcm: Raw PCM audio data (bytes)
        channels: Number of audio channels (1=mono, 2=stereo, default: 1)
        rate: Sample rate in Hz (default: 24000)
        sample_width: Sample width in bytes (2=16-bit, default: 2)
    """
    with wave.open(filename, "wb") as wf:
        # Configure WAV file parameters
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        # Write the PCM audio data to the file
        wf.writeframes(pcm)


def speak(voice, text, filename):
    """
    Generate speech from text using Google Gemini TTS API and save as MP3.

    Args:
        voice: Voice name from Gemini's prebuilt voice options
        text: Text to convert to speech
        filename: Base filename for the output MP3 file (without extension)

    Returns:
        str: Path to the generated MP3 file

    Raises:
        SystemExit: If all 3 retry attempts fail
    """
    # Retry up to 3 times in case of transient errors
    text = f'"{text}", wait 2 seconds after speaking'
    for i in range(3):
        try:
            # Initialize Google Gemini client with API key from environment
            client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

            # Generate audio content using Gemini's TTS model
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],  # Request audio output
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice,
                            )
                        ),
                    ),
                ),
            )

            # Extract PCM audio data from the response
            data = response.candidates[0].content.parts[0].inline_data.data

            # Convert PCM data to MP3 format and save
            file_name = f"{filename}.mp3"
            pcm_to_mp3(data, file_name)

            return file_name

        except Exception as e:
            # Log detailed error information for debugging
            print(f"Error in speak: {e}", file=sys.stderr)
            tb = traceback.extract_tb(e.__traceback__)
            filename, lineno, funcname, text = tb[-1]
            print(f"Exception type: {type(e).__name__}")
            print(f"File: {filename}")
            print(f"Line number: {lineno}")
            print(f"Error message: {e}")
            print(f"Line of code: {text}")

    # Exit if all retry attempts failed
    sys.exit(1)


def play_wave(wav_file):
    """
    Play WAV audio file using ffplay.

    Args:
        wav_file: Path to the WAV file to play

    Raises:
        SystemExit: If ffplay fails to execute
    """
    try:
        # Run ffplay with:
        # -nodisp: Don't show video display window
        # -autoexit: Exit when playback finishes
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", wav_file],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running ffplay: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def play_mp3(mp3_file):
    """
    Play MP3 audio file using ffplay.

    Args:
        mp3_file: Path to the MP3 file to play

    Raises:
        SystemExit: If ffplay fails to execute
    """
    try:
        # Run ffplay with:
        # -nodisp: Don't show video display window
        # -autoexit: Exit when playback finishes
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", mp3_file],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running ffplay: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def pcm_to_mp3(pcm_data, output_filename, channels=1, sample_width=2, frame_rate=24000):
    """
    Convert PCM audio data to MP3 format and save to file.

    Args:
        pcm_data: Raw PCM audio data (bytes)
        output_filename: Path to save the MP3 file
        channels: Number of audio channels (default: 1 for mono)
        sample_width: Sample width in bytes (default: 2 for 16-bit)
        frame_rate: Sample rate in Hz (default: 24000)

    Returns:
        str: Path to the created MP3 file
    """
    try:
        # Create AudioSegment object from raw PCM data with specified audio parameters
        audio_segment = AudioSegment(
            data=pcm_data,
            sample_width=sample_width,  # Bytes per sample (2 = 16-bit)
            frame_rate=frame_rate,      # Sample rate in Hz
            channels=channels,           # Number of audio channels
        )

        # Export the audio segment to MP3 format
        audio_segment.export(output_filename, format="mp3")

        return output_filename

    except Exception as e:
        print(f"Error converting PCM to MP3: {e}", file=sys.stderr)
        sys.exit(1)

def speak11(voice, text, filename):
    """
    Generate speech from text using ElevenLabs TTS API and save as MP3.

    Args:
        voice: ElevenLabs voice ID
        text: Text to convert to speech
        filename: Path where the MP3 file will be saved

    Returns:
        None: Returns None on error (check stderr for error messages)
    """
    try:
        # Load environment variables for API key
        load_dotenv()

        # Initialize ElevenLabs client with API key
        elevenlabs = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        )

        # Convert text to speech using specified voice
        # Output format: MP3 at 44.1kHz sample rate with 128kbps bitrate
        audio = elevenlabs.text_to_speech.convert(
            text=text,
            voice_id=voice,
            output_format="mp3_44100_128",
        )

        # Write the audio stream to file
        with open(f"{filename}.mp3", "wb") as f:
            # Combine all audio chunks into a single byte string
            b = b"".join(audio)
            f.write(b)

    except Exception as e:
        # Log error details and return None to indicate failure
        print(f"Error in speak11: {e}", file=sys.stderr)
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test the ElevenLabs TTS function with a simple "hello world" message
    # Note: Requires valid ELEVENLABS_API_KEY in environment and a valid voice ID
    speak11("", "hello world", "hello.mp3")
