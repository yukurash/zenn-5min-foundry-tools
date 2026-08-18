# zenn-5min-foundry-tools

Zenn シリーズ「5分でわかる Foundry Tools」のサンプルコード集です。
各記事で使う即デプロイ用 Bicep と最小サンプルを、記事ごとのフォルダに置いています。

記事一覧: [Zenn @yukurash 「5分でわかる Foundry Tools」シリーズ](https://zenn.dev/yukurash)

## 収録

| フォルダ | 内容 | 対象サービス | 記事 |
| --- | --- | --- | --- |
| [language-sentiment](language-sentiment) | 感情分析 / オピニオンマイニングの Bicep と最小コード | Azure Language | [【5分でわかる Foundry Tools シリーズ】Azure Language の感情分析](https://zenn.dev/yukurash/articles/13d11e063d0f99) |
| [docintel-invoice](docintel-invoice) | 請求書（prebuilt-invoice）の Bicep・最小コード・サンプル PDF | Azure AI Document Intelligence | 【5分でわかる Foundry Tools シリーズ】Azure AI Document Intelligence で請求書を読み取る |
| [contentsafety-text](contentsafety-text) | テキストモデレーション（Analyze Text）の Bicep と最小コード | Azure AI Content Safety | 【5分でわかる Foundry Tools シリーズ】Azure AI Content Safety で有害テキストを検出する |
| [vision-image-analysis](vision-image-analysis) | 画像分析（Image Analysis）の Bicep と最小コード。1コールでタグと OCR を取得 | Azure Vision | 【5分でわかる Foundry Tools シリーズ】Azure Vision で画像のタグとテキスト(OCR)を一度に取り出す |
| [speech-pronunciation-assessment](speech-pronunciation-assessment) | 発音評価の4指標と単語別エラーを取得する Bicep と最小コード | Azure Speech | 【5分でわかる Foundry Tools】Azure Speech の発音評価 |

## 使い方（共通）

各フォルダに移動して、Bicep をデプロイしてから Python サンプルを実行します。

```bash
cd language-sentiment

az group create -n rg-foundry-language -l japaneast
az deployment group create -g rg-foundry-language -f main.bicep

pip install azure-ai-textanalytics azure-identity
az login
python quickstart.py
```

認証はキーを持たない Entra ID 方式です。デプロイしたアカウントに「Cognitive Services User」ロールを割り当て、`.env` にエンドポイントだけ書いて実行します。詳細は各記事を参照してください。
