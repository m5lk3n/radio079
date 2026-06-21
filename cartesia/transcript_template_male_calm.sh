curl -X POST https://api.cartesia.ai/tts/bytes \
-H "Cartesia-Version: 2026-03-01" \
-H "X-API-Key: ${CARTESIA_API_KEY}" \
-H "Content-Type: application/json" \
-d '{
  "model_id": "sonic-3.5",
  "transcript": "${TEXT}",
  "voice": {
    "mode": "id",
    "id": "b7187e84-fe22-4344-ba4a-bc013fcb533e"
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
    "emotion": "calm"
  }
}' \
--output ${OUTPUT_FILE_WAV}
