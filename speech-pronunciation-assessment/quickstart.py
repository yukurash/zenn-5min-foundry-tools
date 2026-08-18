"""Azure AI Speech - 発音評価の再現可能な検証サンプル."""

import gc
import json
import os
import tempfile
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
from azure.identity import AzureCliCredential


REFERENCE_TEXT = "The quick brown fox jumps over the lazy dog."
SPOKEN_TEXT = "The quick brown fox jumps over the dog."


def load_env(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def synthesize_sample(speech_config: speechsdk.SpeechConfig, audio_path: str) -> None:
    speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = synthesizer.speak_text_async(SPOKEN_TEXT).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        details = speechsdk.SpeechSynthesisCancellationDetails(result)
        raise RuntimeError(f"音声生成に失敗しました: {details.reason} / {details.error_details}")
    Path(audio_path).write_bytes(result.audio_data)


def assess_pronunciation(
    speech_config: speechsdk.SpeechConfig,
    audio_path: str,
) -> tuple[speechsdk.PronunciationAssessmentResult, list[dict[str, object]]]:
    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
    assessment_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=REFERENCE_TEXT,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True,
    )
    assessment_config.enable_prosody_assessment()

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        language="en-US",
        audio_config=audio_config,
    )
    assessment_config.apply_to(recognizer)
    result = recognizer.recognize_once()
    if result.reason != speechsdk.ResultReason.RecognizedSpeech:
        details = speechsdk.CancellationDetails.from_result(result)
        raise RuntimeError(f"発音評価に失敗しました: {result.reason} / {details.error_details}")

    assessment = speechsdk.PronunciationAssessmentResult(result)
    raw_result = result.properties.get(
        speechsdk.PropertyId.SpeechServiceResponse_JsonResult
    )
    words = json.loads(raw_result)["NBest"][0]["Words"]
    del recognizer
    del audio_config
    gc.collect()
    return assessment, words


def format_result(
    assessment: speechsdk.PronunciationAssessmentResult,
    words: list[dict[str, object]],
    spoken_description: str,
) -> str:
    lines = [
        f"Reference:    {REFERENCE_TEXT}",
        f"Spoken:       {spoken_description}",
        "",
        f"Accuracy:     {assessment.accuracy_score:.1f}",
        f"Fluency:      {assessment.fluency_score:.1f}",
        f"Completeness: {assessment.completeness_score:.1f}",
        f"Prosody:      {assessment.prosody_score:.1f}",
        "",
        "Word details:",
    ]
    for word in words:
        pronunciation = word["PronunciationAssessment"]
        accuracy = pronunciation.get("AccuracyScore")
        accuracy_text = f"{accuracy:5.1f}" if accuracy is not None else "  n/a"
        lines.append(
            f"- {word['Word']:<12} "
            f"accuracy={accuracy_text} "
            f"error={pronunciation['ErrorType']}"
        )
    return "\n".join(lines)


def main() -> None:
    load_env()
    speech_config = speechsdk.SpeechConfig(
        token_credential=AzureCliCredential(
            tenant_id=os.environ["AZURE_TENANT_ID"],
        ),
        endpoint=os.environ["SPEECH_ENDPOINT"],
    )

    audio_path = os.environ.get("SPEECH_AUDIO_FILE")
    delete_audio = audio_path is None
    if audio_path is None:
        temporary_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio_path = temporary_audio.name
        temporary_audio.close()
    try:
        if delete_audio:
            synthesize_sample(speech_config, audio_path)
        assessment, words = assess_pronunciation(speech_config, audio_path)
        spoken_description = SPOKEN_TEXT if delete_audio else "External WAV file"
        output = format_result(assessment, words, spoken_description)
        print(output)
        Path("result.txt").write_text(output + "\n", encoding="utf-8")
    finally:
        if delete_audio:
            Path(audio_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()