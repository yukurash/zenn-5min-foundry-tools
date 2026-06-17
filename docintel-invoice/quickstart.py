"""Azure AI Document Intelligence - prebuilt-invoice（請求書）最小サンプル.

キーレス（Entra ID）認証で接続します。.env から DOCINTEL_ENDPOINT を読み込み、`az login` 済みの ID で認証します
（事前に「Cognitive Services User」ロールが必要）。鍵をコードに持たずに済みます。

サンプル請求書は Azure-Samples の公開 PDF（PII なし）を URL 指定で解析します。
"""
import os

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.identity import DefaultAzureCredential

SAMPLE_URL = (
    "https://raw.githubusercontent.com/Azure-Samples/"
    "cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-invoice.pdf"
)


def load_env(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def field_str(field) -> str:
    """フィールドの代表値を取り出す（型差を吸収して文字列化）。"""
    if field is None:
        return "-"
    for attr in (
        "value_string", "value_number", "value_date", "value_currency",
        "value_address", "value_phone_number", "content",
    ):
        v = getattr(field, attr, None)
        if v is not None:
            if attr == "value_currency":
                amount = getattr(v, "amount", None)
                symbol = getattr(v, "currency_symbol", "") or getattr(v, "currency_code", "") or ""
                return f"{symbol}{amount}".strip()
            return str(v)
    return "-"


def conf(field) -> str:
    if field is None or field.confidence is None:
        return ""
    return f"  (confidence={field.confidence:.3f})"


def main() -> None:
    load_env()
    endpoint = os.environ["DOCINTEL_ENDPOINT"]
    client = DocumentIntelligenceClient(endpoint, DefaultAzureCredential())

    print("=== prebuilt-invoice 解析開始 ===")
    print(f"対象: {SAMPLE_URL}\n")

    poller = client.begin_analyze_document(
        "prebuilt-invoice",
        AnalyzeDocumentRequest(url_source=SAMPLE_URL),
    )
    result = poller.result()

    lines = []
    if not result.documents:
        print("請求書フィールドが抽出できませんでした。")
        return

    for di, doc in enumerate(result.documents):
        f = doc.fields or {}
        labels = [
            ("ベンダー名 (VendorName)", "VendorName"),
            ("請求先 (CustomerName)", "CustomerName"),
            ("請求書番号 (InvoiceId)", "InvoiceId"),
            ("請求日 (InvoiceDate)", "InvoiceDate"),
            ("支払期日 (DueDate)", "DueDate"),
            ("小計 (SubTotal)", "SubTotal"),
            ("合計 (InvoiceTotal)", "InvoiceTotal"),
        ]
        lines.append(f"--- 請求書 #{di + 1}（doc信頼度={doc.confidence:.3f}）---")
        for jp, key in labels:
            fld = f.get(key)
            lines.append(f"{jp}: {field_str(fld)}{conf(fld)}")

        items = f.get("Items")
        item_list = getattr(items, "value_array", None) if items else None
        if item_list:
            lines.append("明細 (Items):")
            for ii, item in enumerate(item_list[:3]):  # 代表3行
                io = item.value_object or {}
                desc = field_str(io.get("Description"))
                qty = field_str(io.get("Quantity"))
                amount = field_str(io.get("Amount"))
                lines.append(f"  [{ii + 1}] {desc} / 数量={qty} / 金額={amount}")

    out = "\n".join(lines)
    print(out)

    # ターミナル出力がラグる場合に備え、ファイルにも残す（キー・PIIなし、公開サンプルのみ）
    with open("result.txt", "w", encoding="utf-8") as fp:
        fp.write(out + "\n")
    print("\n（結果は result.txt にも保存しました）")


if __name__ == "__main__":
    main()
