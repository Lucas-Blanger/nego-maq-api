import os
import requests
import logging


class MelhorEnvioService:
    def __init__(self):
        self.base_url = os.getenv("MELHOR_ENVIO_BASE_URL", "https://sandbox.melhorenvio.com.br/api/v2")
        self.token = os.getenv("MELHOR_ENVIO_TOKEN")

        # DEBUG
        logging.info(f"[ME] Token carregado: {bool(self.token)}")
        logging.info(f"[ME] Tamanho token: {len(self.token) if self.token else 0}")
        logging.info(f"[ME] Base URL: {self.base_url}")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Nego Maq (contato@negomaq.com.br)"
        }

    def calcular_frete(self, origem_cep, destino_cep, produtos):
        """Calcula o frete para uma lista de produtos"""
        logging.info(f"[ME] === INICIANDO CÁLCULO ===")
        logging.info(f"[ME] Origem: {origem_cep} -> Destino: {destino_cep}")

        try:
            # Preparar produtos para o cálculo
            volumes = []
            peso_total = 0

            for produto in produtos:
                peso_produto = produto.get('peso', 0.3)
                quantidade = produto.get('quantidade', 1)
                peso_total += peso_produto * quantidade

                for _ in range(quantidade):
                    volumes.append({
                        "height": produto.get('altura', 10),
                        "width": produto.get('largura', 15),
                        "length": produto.get('comprimento', 20),
                        "weight": peso_produto
                    })

            if not volumes:
                volumes = [{
                    "height": 10,
                    "width": 15,
                    "length": 20,
                    "weight": max(peso_total, 0.1)
                }]

            payload = {
                "from": {"postal_code": origem_cep.replace('-', '').replace('.', '')},
                "to": {"postal_code": destino_cep.replace('-', '').replace('.', '')},
                "products": volumes
            }

            url_completa = f"{self.base_url}/shipment/calculate"

            logging.info(f"[ME] URL: {url_completa}")
            logging.info(f"[ME] Payload: {payload}")

            response = requests.post(
                url_completa,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logging.info(f"[ME] Status Code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                logging.info(f"[ME] Resposta recebida: {len(result)} serviços")

                servicos_disponiveis = []

                for servico in result:
                    if 'error' not in servico and servico.get('price', 0) > 0:
                        servicos_disponiveis.append({
                            'id': servico.get('id'),
                            'name': servico.get('name'),
                            'price': float(servico.get('price', 0)),
                            'delivery_time': servico.get('delivery_time', 0),
                            'company': servico.get('company', {}).get('name', ''),
                            'currency': servico.get('currency', 'R$')
                        })

                return {"success": True, "servicos": servicos_disponiveis}
            else:
                logging.error(f"[ME] Erro HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"Erro HTTP {response.status_code}"}

        except requests.exceptions.Timeout:
            logging.error("[ME] TIMEOUT na requisição")
            return {"success": False, "error": "Timeout na consulta de frete"}
        except requests.exceptions.RequestException as e:
            logging.error(f"[ME] Erro de conexão: {type(e).__name__}")
            logging.error(f"[ME] Detalhes: {str(e)}")
            return {"success": False, "error": f"Erro de conexão: {type(e).__name__}"}
        except Exception as e:
            logging.error(f"[ME] Erro geral: {str(e)}")
            return {"success": False, "error": str(e)}

    def consultar_conta(self):
        """Verifica dados da conta no Melhor Envio"""
        try:
            response = requests.get(
                f"{self.base_url}/me",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                return {"success": True, "dados": response.json()}
            else:
                return {"success": False, "error": f"Erro HTTP {response.status_code}"}

        except Exception as e:
            logging.error(f"Erro ao consultar conta: {str(e)}")
            return {"success": False, "error": str(e)}