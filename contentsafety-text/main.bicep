// Azure AI Content Safety（テキストモデレーション Analyze Text）即デプロイ用テンプレ
// kind=ContentSafety（単独リソース）。japaneast / S0 で Analyze Text API をそのまま叩けます。
// キーは出力しません（キーレスの Entra ID 認証を推奨）。
// 補足: 統合 Foundry リソースを使いたい場合は kind=AIServices に変えても Content Safety API は利用可。

@description('Cognitive Services の kind。Content Safety 単独は ContentSafety。統合なら AIServices。')
param kind string = 'ContentSafety'

@description('デプロイ先リージョン。既定は japaneast。')
param location string = 'japaneast'

@description('SKU 名。検証は S0 推奨（F0 は呼び出しレート制限が厳しい）。')
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
