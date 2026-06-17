// Azure AI Language（感情分析）即デプロイ用テンプレ
// kind=AIServices（統合 Foundry リソース）。Language/感情分析 API をそのまま叩けます。
// 鍵は出力しません（検証時に az ... keys list で取得）。
// 補足: 単独 kind=TextAnalytics の S0 は一部サブスク（内部/FDPO 等）で QuotaId 制限により拒否されるため、
// より広く通る AIServices を既定にしています。kind を変えれば他の Foundry Tools にも流用可。

@description('Cognitive Services の kind。統合リソースは AIServices（Language も利用可）。')
param kind string = 'AIServices'

@description('デプロイ先リージョン。既定は japaneast。')
param location string = 'japaneast'

@description('SKU 名。検証は S0 推奨（F0 は TPM 制限が厳しい）。')
param skuName string = 'S0'

@description('アカウント名。既定で一意化。')
param accountName string = 'foundry-${toLower(kind)}-${uniqueString(resourceGroup().id)}'

resource account 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: accountName
  location: location
  kind: kind
  sku: {
    name: skuName
  }
  properties: {
    customSubDomainName: accountName
    publicNetworkAccess: 'Enabled'
  }
  tags: {
    project: 'foundry-tools-series'
  }
}

@description('キー取得コマンドで使うアカウント名')
output accountName string = account.name

@description('SDK で使うエンドポイント')
output endpoint string = account.properties.endpoint
