curl -X POST https://api.cartesia.ai/tts/bytes \
-H "Cartesia-Version: 2026-03-01" \
-H "X-API-Key: ${CARTESIA_API_KEY}" \
-H "Content-Type: application/json" \
-d '{
  "model_id": "sonic-3.5",
  "transcript": "${TEXT}",
  "voice": {
    "mode": "id",
    "id": "38aabb6a-f52b-4fb0-a3d1-988518f4dc06"
  },
  "output_format": {
    "container": "wav",
    "encoding": "pcm_s16le",
    "sample_rate": 44100
  },
  "language": "de",
  "generation_config": {
    "speed": 1,
    "volume": 1,
    "emotion": "excited"
  }
}' \
--output ${OUTPUT_FILE_WAV}
