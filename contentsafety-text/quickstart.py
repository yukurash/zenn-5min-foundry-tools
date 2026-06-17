"""Azure AI Content Safety - テキストモデレーション（Analyze Text）最小サンプル.

キーレス（Entra ID）認証で接続します。.env から CONTENTSAFETY_ENDPOINT を読み込み、`az login` 済みの ID で認証します
（事前に「Cognitive Services User」ロールが必要）。キーをコードに持たずに済みます。

Analyze Text は入力テキストを Hate / SelfHarm / Sexual / Violence の4カテゴリで評価し、
各カテゴリの severity（既定は 0/2/4/6 の4段階）を返します。
"""
import os

from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

# 検証用の入力（PIIなし）。無害な文と、各カテゴリを軽度に刺激する一般的なテスト文。
SAMPLES = [
    "本日はお招きいただきありがとうございます。とても楽しい時間でした。",
    "おまえみたいな奴は消えてしまえ。二度と顔を見せるな。",
    "全部もう嫌だ。自分なんて生きている価値がない。",
]


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
    endpoint = os.environ["CONTENTSAFETY_ENDPOINT"]
    client = ContentSafetyClient(endpoint, DefaultAzureCredential())

    lines = []
    for i, text in enumerate(SAMPLES):
        try:
            res = client.analyze_text(AnalyzeTextOptions(text=text))
        except HttpResponseError as e:
            lines.append(f"[{i}] 呼び出し失敗: {e.message}")
            continue

        # category -> severity の対応表にする
        sev = {a.category: a.severity for a in res.categories_analysis}
        lines.append(f"[{i}] 入力: {text}")
        lines.append(
            "    Hate={Hate}  SelfHarm={SelfHarm}  "
            "Sexual={Sexual}  Violence={Violence}".format(
                Hate=sev.get("Hate"),
                SelfHarm=sev.get("SelfHarm"),
                Sexual=sev.get("Sexual"),
                Violence=sev.get("Violence"),
            )
        )

    out = "\n".join(lines)
    print(out)

    # ターミナル出力がラグる場合に備え、ファイルにも残す（キー・PIIなし）
    with open("result.txt", "w", encoding="utf-8") as fp:
        fp.write(out + "\n")
    print("\n（結果は result.txt にも保存しました）")


if __name__ == "__main__":
    main()
