#!/usr/bin/env python3
"""
Script para testar se as rotas da API estão acessíveis.
"""
import requests
import sys

def test_health_endpoint(base_url):
    """Testa o endpoint de health check."""
    url = f"{base_url}/health"
    print(f"\n🔍 Testando endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status code: {response.status_code}")
        print(f"📋 Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            if "routes" in data:
                print("\n📡 Rotas disponíveis na API:")
                for route in data["routes"]:
                    print(f"- {route['path']} ({', '.join(route['methods'])}): {route['description']}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao acessar o endpoint: {e}")
        return False

def test_api_routes(base_url):
    """Testa as principais rotas da API."""
    endpoints = [
        "/api/v1/auth/login",
        "/api/v1/products/",
        "/api/v1/categories/",
        "/api/v1/sales/",
        "/api/v1/customers/",
        "/api/v1/employees/",
        "/api/v1/inventory/",
        "/api/v1/users/"
    ]
    
    print(f"\n🔍 Testando rotas da API em {base_url}")
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Testando: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ Status code: {response.status_code}")
            if response.status_code == 200:
                print(f"📋 Response: {response.text[:200]}...")
            elif response.status_code == 401:
                print("⚠️  Autenticação necessária")
            elif response.status_code == 403:
                print("⛔ Acesso não autorizado")
            elif response.status_code == 404:
                print("🔍 Endpoint não encontrado")
        except Exception as e:
            print(f"❌ Erro: {e}")

def main():
    # URL base da API (padrão: http://localhost:8000)
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🚀 Iniciando testes na API em: {base_url}")
    
    # Testar o endpoint de health check
    if test_health_endpoint(base_url):
        # Se o health check passar, testar as rotas da API
        test_api_routes(base_url)
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()
