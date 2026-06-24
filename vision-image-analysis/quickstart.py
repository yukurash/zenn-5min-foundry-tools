"""Azure Vision - Image Analysis 4.0 最小サンプル.

1回の呼び出しで tags（キーワード）/ read（OCR 文字起こし）/ objects（物体と位置）を
confidence つきでまとめて取得します。キーレス（Entra ID）認証で接続します。
.env から VISION_ENDPOINT を読み込み、`az login` 済みの ID で認証します
（事前に「Cognitive Services User」ロールが必要）。鍵をコードに持たずに済みます。

caption / denseCaptions（4.0）は対応リージョンが限られ、japaneast では使えません。
本サンプルは caption を別呼び出しで試し、未対応リージョンでの挙動も実機で確認します。

解析対象は Azure-Samples の公開サンプル画像（人物・PII なし）を URL 指定で読み込みます。
"""
import os

from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

# 文字（OCR 対象）が一面に写る公開サンプル画像（栄養成分表示ラベル・人物/PII なし）。
SAMPLE_URL = (
    "https://raw.githubusercontent.com/Azure-Samples/"
    "cognitive-services-sample-data-files/master/ComputerVision/Images/printed_text.jpg"
)


def load_env(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main() -> None:
    load_env()
    endpoint = os.environ["VISION_ENDPOINT"]
    client = ImageAnalysisClient(endpoint, DefaultAzureCredential())

    print("=== Image Analysis 解析開始 ===")
    print(f"対象: {SAMPLE_URL}\n")

    lines: list[str] = []

    # --- 1コールで tags / read(OCR) / objects をまとめて取得 ---
    result = client.analyze_from_url(
        image_url=SAMPLE_URL,
        visual_features=[
            VisualFeatures.TAGS,
            VisualFeatures.READ,
            VisualFeatures.OBJECTS,
        ],
    )

    if result.tags is not None:
        lines.append("タグ (tags) 上位5件:")
        for tag in result.tags.list[:5]:
            lines.append(f"  - {tag.name}  (confidence={tag.confidence:.3f})")

    if result.read is not None:
        lines.append("読み取り (read / OCR):")
        for block in result.read.blocks:
            for line in block.lines:
                lines.append(f"  \"{line.text}\"")

    if result.objects is not None:
        if result.objects.list:
            lines.append("物体 (objects):")
            for obj in result.objects.list:
                t = obj.tags[0]
                bb = obj.bounding_box
                lines.append(
                    f"  - {t.name}  (confidence={t.confidence:.3f}) "
                    f"box=(x={bb.x}, y={bb.y}, w={bb.width}, h={bb.height})"
                )
        else:
            lines.append("物体 (objects): 検出なし（文字中心の画像のため）")

    lines.append(f"モデルバージョン: {result.model_version}")

    # --- caption / denseCaptions は別呼び出しで試す（対応リージョン限定）---
    lines.append("")
    lines.append("--- caption / denseCaptions（4.0・対応リージョン限定）---")
    try:
        cap = client.analyze_from_url(
            image_url=SAMPLE_URL,
            visual_features=[VisualFeatures.CAPTION, VisualFeatures.DENSE_CAPTIONS],
        )
        if cap.caption is not None:
            lines.append(
                f"caption: \"{cap.caption.text}\"  (confidence={cap.caption.confidence:.3f})"
            )
        if cap.dense_captions is not None:
            lines.append("denseCaptions（領域ごと）:")
            for dc in cap.dense_captions.list:
                lines.append(f"  \"{dc.text}\"  (confidence={dc.confidence:.3f})")
    except HttpResponseError as e:
        lines.append(f"caption は呼び出せませんでした: {e.status_code} {e.reason}")
        msg = getattr(getattr(e, "error", None), "message", None) or str(e)
        lines.append(f"  詳細: {msg}")

    out = "\n".join(lines)
    print(out)

    # ターミナル出力がラグる場合に備え、ファイルにも残す（キー・PIIなし、公開サンプルのみ）
    with open("result.txt", "w", encoding="utf-8") as fp:
        fp.write(out + "\n")
    print("\n（結果は result.txt にも保存しました）")


if __name__ == "__main__":
    main()
