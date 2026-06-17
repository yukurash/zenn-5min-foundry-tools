"""Azure Language - 感情分析 & オピニオンマイニング 最小サンプル.

キーレス（Entra ID）認証で接続します。.env から LANGUAGE_ENDPOINT を読み込み、`az login` 済みの ID で認証します
（事前に「Cognitive Services User」ロールが必要）。鍵をコードに持たずに済みます。
"""
import os

from azure.ai.textanalytics import TextAnalyticsClient
from azure.identity import DefaultAzureCredential


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
    endpoint = os.environ["LANGUAGE_ENDPOINT"]
    client = TextAnalyticsClient(endpoint, DefaultAzureCredential())

    documents = [
        {"id": "1", "language": "ja",
         "text": "料理は最高だったが、接客の態度がひどくて残念でした。"},
    ]

    result = client.analyze_sentiment(documents, show_opinion_mining=True)
    for i, doc in enumerate(result):
        if doc.is_error:
            print(f"[{i}] ERROR: {doc.error}")
            continue
        s = doc.confidence_scores
        print(f"[{i}] 文書全体: {doc.sentiment}  "
              f"(pos={s.positive:.2f}, neu={s.neutral:.2f}, neg={s.negative:.2f})")
        for sent in doc.sentences:
            cs = sent.confidence_scores
            print(f"    - 文: {sent.sentiment} "
                  f"(pos={cs.positive:.2f}, neu={cs.neutral:.2f}, neg={cs.negative:.2f}) "
                  f"\"{sent.text}\"")
            for op in sent.mined_opinions:
                target = op.target
                assess = ", ".join(f"{a.text}({a.sentiment})" for a in op.assessments)
                print(f"        対象: {target.text}({target.sentiment}) <- 評価: {assess}")


if __name__ == "__main__":
    main()
