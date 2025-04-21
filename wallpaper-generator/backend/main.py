from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import boto3, json, time, requests

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = boto3.client("bedrock-runtime", region_name="us-east-1")

@app.post("/generate")
async def generate_wallpaper(prompt: str = Form(...)):
    body = json.dumps({
        "prompt": prompt,
        "style": "wallpaper",
        "resolution": "4K"
    })

    response = client.invoke_model(
        modelId="amazon.nova-canvas",
        contentType="application/json",
        accept="application/json",
        body=body
    )

    output_path = "output_wallpaper.png"
    with open(output_path, "wb") as f:
        f.write(response["body"].read())

    return FileResponse(output_path, media_type="image/png")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    bucket = "ai-wallpaper-audio"
    filename = f"audio-{int(time.time())}.wav"
    filepath = f"/tmp/{filename}"

    # Save audio locally
    with open(filepath, "wb") as f:
        f.write(await file.read())

    # Upload to S3
    s3 = boto3.client("s3")
    s3.upload_file(filepath, bucket, filename)

    job_name = f"Transcription-{int(time.time())}"
    file_uri = f"s3://{bucket}/{filename}"

    transcribe = boto3.client("transcribe")
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": file_uri},
        MediaFormat="wav",
        LanguageCode="en-US",
        OutputBucketName=bucket
    )

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status["TranscriptionJob"]["TranscriptionJobStatus"] in ["COMPLETED", "FAILED"]:
            break
        time.sleep(2)

    output_uri = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
    transcript = requests.get(output_uri).json()
    prompt = transcript["results"]["transcripts"][0]["transcript"]

    return JSONResponse(content={"prompt": prompt})
