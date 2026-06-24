// Azure Vision（Image Analysis 4.0）即デプロイ用テンプレ
// kind=ComputerVision（リソース種別名。本文の製品表記は「Azure Vision」）。
// キーは出力しません（キーレスの Entra ID 認証を推奨）。
// 注意: caption / denseCaptions（4.0）は対応リージョンが限られます。japaneast は
// tags / read(OCR) / objects は使えますが caption は非対応です（後述の検証で実機確認）。
// customSubDomainName は Entra ID 認証（トークン）に必要なので必ず付けます。

@description('Cognitive Services の kind。Azure Vision の Image Analysis は ComputerVision。')
param kind string = 'ComputerVision'

@description('デプロイ先リージョン。既定は japaneast。')
param location string = 'japaneast'

// 一部サブスク（内部/FDPO 等）は ComputerVision の S0 を QuotaId 制限で弾きます。
// その場合は F0 を使います（本シリーズの検証は F0 で実施）。本番では枠のある S0 を推奨。
@description('SKU 名。制限付きサブスクでは F0、枠があれば S0。')
param skuName string = 'F0'

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
