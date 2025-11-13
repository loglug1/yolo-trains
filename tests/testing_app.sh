#!/bin/bash
# ================================================
# Test Script for Railway Object Detection API
# ================================================

BASE_URL="http://localhost:5000"
MODEL_FILE="sample_model.pt"
VIDEO_FILE="sample_video.mp4"

echo "=== Testing /models (POST upload model) ==="
MODEL_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$BASE_URL/models" \
  -F "model_file=@${MODEL_FILE}")

MODEL_STATUS=$(echo "$MODEL_RESPONSE" | grep HTTP_STATUS | cut -d: -f2)
MODEL_BODY=$(echo "$MODEL_RESPONSE" | sed -e 's/HTTP_STATUS:.*//g')

if [[ "$MODEL_STATUS" != "201" ]]; then
  echo "Failed to upload model (status $MODEL_STATUS)"
  echo "$MODEL_BODY"
  exit 1
fi
echo "Model uploaded successfully."
MODEL_ID=$(echo "$MODEL_BODY" | grep -oP '"model_id":\s*"\K[^"]+')
echo "MODEL_ID=$MODEL_ID"

echo ""
echo "=== Testing /videos (POST upload video) ==="
VIDEO_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$BASE_URL/videos" \
  -F "video_file=@${VIDEO_FILE}")

VIDEO_STATUS=$(echo "$VIDEO_RESPONSE" | grep HTTP_STATUS | cut -d: -f2)
VIDEO_BODY=$(echo "$VIDEO_RESPONSE" | sed -e 's/HTTP_STATUS:.*//g')

if [[ "$VIDEO_STATUS" != "201" ]]; then
  echo "Failed to upload video (status $VIDEO_STATUS)"
  echo "$VIDEO_BODY"
  exit 1
fi
echo "✅ Video uploaded successfully."
VIDEO_ID=$(echo "$VIDEO_BODY" | grep -oP '"video_id":\s*"\K[^"]+')
echo "VIDEO_ID=$VIDEO_ID"

echo ""
echo "=== Testing /videos (GET all videos) ==="
curl -s -X GET "$BASE_URL/videos" | jq

echo ""
echo "=== Testing /models (GET all models) ==="
curl -s -X GET "$BASE_URL/models" | jq

echo ""
echo "=== Testing /objects/$MODEL_ID/$VIDEO_ID (GET object types) ==="
curl -s -X GET "$BASE_URL/objects/$MODEL_ID/$VIDEO_ID" | jq

echo ""
echo "=== Testing /videos/$VIDEO_ID (GET video info + frame list) ==="
curl -s -X GET "$BASE_URL/videos/$VIDEO_ID" | jq

echo ""
echo "=== Testing /videos/$VIDEO_ID/0 (GET first raw frame) ==="
curl -s -X GET "$BASE_URL/videos/$VIDEO_ID/0" | jq | head -n 10

echo ""
echo "=== Testing /models/$MODEL_ID/$VIDEO_ID (GET all processed frames) ==="
curl -s -X GET "$BASE_URL/models/$MODEL_ID/$VIDEO_ID" | jq | head -n 20

echo ""
echo "=== Testing /models/$MODEL_ID/$VIDEO_ID/0 (GET first processed frame) ==="
curl -s -X GET "$BASE_URL/models/$MODEL_ID/$VIDEO_ID/0" | jq | head -n 15

echo ""
echo "=== Testing /models/$MODEL_ID/$VIDEO_ID/0/history (GET processed frame history) ==="
curl -s -X GET "$BASE_URL/models/$MODEL_ID/$VIDEO_ID/0/history" | jq

echo ""
echo "=== All tests completed successfully. ==="
