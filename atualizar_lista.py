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

# 1. Buscar os IPs diretamente do espelho oficial do Azure (evitando falhas de JSON)
print("Buscando IPs atualizados do Azure...")
azure_url = "https://microsoft.com"

# Como o link da Microsoft muda o número do final, usamos uma URL estável que sempre redireciona para o JSON oficial e completo
azure_url = "https://githubusercontent.com"

try:
    response = requests.get(azure_url, timeout=15)
    response.raise_for_status()
    azure_data = response.json()
except Exception as e:
    print(f"Erro ao baixar os IPs do Azure: {e}")
    exit(1)

# Filtrando o JSON completo para pegar apenas o Brazil South
ips_brazil_south = []
for value in azure_data.get("values", []):
    if value.get("name") == "AzureCloud.brazilsouth":
        for ip in value["properties"]["addressPrefixes"]:
            ips_brazil_south.append({"ip": ip, "comment": "Azure Brazil South Auto-Update"})

print(f"Encontrados {len(ips_brazil_south)} IPs para Brazil South.")

if not ips_brazil_south:
    print("Nenhum IP encontrado. Encerrando.")
    exit(1)

# 2. Enviar em massa para a lista do Cloudflare
cf_url = f"https://cloudflare.com{ACCOUNT_ID}/rules/lists/{LIST_ID}/items"

print("Enviando novos IPs para o Cloudflare...")
try:
    cf_response = requests.put(cf_url, headers=headers, json=ips_brazil_south, timeout=15)
except Exception as e:
    print(f"Erro de conexão ou Timeout com o Cloudflare: {e}")
    exit(1)

if cf_response.status_code == 200:
    print("Sucesso! Lista do Cloudflare atualizada perfeitamente.")
else:
    print(f"Erro retornado pelo Cloudflare (Código {cf_response.status_code}):")
    print(cf_response.text)
    exit(1)
