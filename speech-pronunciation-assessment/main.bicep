// Azure AI Speech（発音評価）即デプロイ用テンプレ
// kind を変えれば他の Foundry Tools にも流用できます。
// ローカルキー認証は無効化し、デプロイ実行者へ最小権限を付与します。

@description('Cognitive Services の kind。Speech は SpeechServices。')
param kind string = 'SpeechServices'

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
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
  tags: {
    project: 'foundry-tools-series'
  }
}

var speechUserRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'f2dc8367-1007-4938-bd23-fe263f013447'
)

resource speechUserRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(account.id, deployer().objectId, speechUserRoleDefinitionId)
  scope: account
  properties: {
    roleDefinitionId: speechUserRoleDefinitionId
    principalId: deployer().objectId
  }
}

@description('確認コマンドで使うアカウント名')
output accountName string = account.name

@description('SDK で使うエンドポイント')
output endpoint string = account.properties.endpoint