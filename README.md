# zenn-5min-foundry-tools

Zenn シリーズ「5分でわかる Foundry Tools」のサンプルコード集です。
各記事で使う即デプロイ用 Bicep と最小サンプルを、記事ごとのフォルダに置いています。

## 収録

| フォルダ | 内容 | 対象サービス |
| --- | --- | --- |
| [language-sentiment](language-sentiment) | 感情分析 / オピニオンマイニングの Bicep と最小コード | Azure AI Language |

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
