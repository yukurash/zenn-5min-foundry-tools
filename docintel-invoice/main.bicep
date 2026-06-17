// Azure AI Document Intelligence（請求書 prebuilt-invoice）即デプロイ用テンプレ
// kind=AIServices（統合 Foundry リソース）。Document Intelligence API をそのまま叩けます。
// キーは出力しません（キーレスの Entra ID 認証を推奨）。
// 補足: 単独 kind は FormRecognizer ですが、一部サブスク（内部/FDPO 等）の QuotaId 制限を避けるため、
// より広く通る統合 AIServices を既定にしています。kind を変えれば他の Foundry Tools にも流用可。

@description('Cognitive Services の kind。統合リソースは AIServices（Document Intelligence も利用可）。')
param kind string = 'AIServices'

@description('デプロイ先リージョン。既定は japaneast。')
param location string = 'japaneast'

@description('SKU 名。検証は S0 推奨（F0 は 2 ページ / 4MB 制限が厳しい）。')
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

@description('SDK で使うエンドポイント')
output endpoint string = account.properties.endpoint

@description('ロール割り当て等で使うアカウント名')
output accountName string = account.name
