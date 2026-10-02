import os
import requests

TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
LIST_ID = os.getenv("CLOUDFLARE_LIST_ID")

if not all([TOKEN, ACCOUNT_ID, LIST_ID]):
    print("ERRO: Variáveis secretas do Cloudflare estão vazias no GitHub Secrets!")
    exit(1)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. API Oficial do Azure para descobrir os blocos de IP atuais da Public Cloud
print("Consultando a API oficial de descoberta do Azure...")
azure_api_url = "https://azure.com"

# Endereço alternativo da API do Azure caso o endpoint regional tenha instabilidade
azure_api_url = "https://githubusercontent.com"

# Para remover COMPLETAMENTE o domínio do GitHub da sua rede do Actions, usamos o espelho direto na CDN da Microsoft:
azure_api_url = "https://microsoft.com"

try:
    # Baixando o arquivo direto da CDN da Microsoft com cabeçalho de navegador comum
    user_agent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(azure_api_url, headers=user_agent, timeout=20)
    response.raise_for_status()
    azure_data = response.json()
except Exception as e:
    print(f"Falha ao conectar na infraestrutura Microsoft: {e}")
    exit(1)

# Filtrando o JSON para a tag específica do Brazil South
ips_brazil_south = []
for value in azure_data.get("values", []):
    if value.get("name") == "AzureCloud.brazilsouth":
        for ip in value["properties"]["addressPrefixes"]:
            ips_brazil_south.append({"ip": ip, "comment": "Azure Brazil South Auto-Update"})

print(f"Encontrados {len(ips_brazil_south)} IPs válidos para Brazil South.")

if not ips_brazil_south:
    print("Erro: Nenhum IP foi encontrado dentro do bloco Brazil South.")
    exit(1)

# 2. Atualizar o Cloudflare via API (Substituição Completa)
cf_url = f"https://cloudflare.com{ACCOUNT_ID}/rules/lists/{LIST_ID}/items"
print("Enviando novos IPs para o Cloudflare...")

try:
    cf_response = requests.put(cf_url, headers=headers, json=ips_brazil_south, timeout=20)
except Exception as e:
    print(f"Erro ao conectar na API do Cloudflare: {e}")
    exit(1)

if cf_response.status_code == 200:
    print("Sucesso absoluto! A sua lista no Cloudflare foi atualizada com os IPs do Azure.")
else:
    print(f"Erro retornado pelo Cloudflare (Código {cf_response.status_code}):")
    print(cf_response.text)
    exit(1)
