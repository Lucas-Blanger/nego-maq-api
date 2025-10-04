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
            # Limpar CEPs
            origem_limpo = origem_cep.replace('-', '').replace('.', '').replace(' ', '')
            destino_limpo = destino_cep.replace('-', '').replace('.', '').replace(' ', '')

            # Headers simplificados (como no curl que funcionou)
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "Teste"
            }

            # Query params
            params = {
                'from[postal_code]': origem_limpo,
                'to[postal_code]': destino_limpo,
            }

            for idx, produto in enumerate(produtos):
                params[f'products[{idx}][id]'] = str(idx + 1)
                params[f'products[{idx}][width]'] = int(produto.get('largura', 15))
                params[f'products[{idx}][height]'] = int(produto.get('altura', 10))
                params[f'products[{idx}][length]'] = int(produto.get('comprimento', 20))
                params[f'products[{idx}][weight]'] = float(produto.get('peso', 0.3))
                params[f'products[{idx}][insurance_value]'] = 50
                params[f'products[{idx}][quantity]'] = 1

            url = f"{self.base_url}/shipment/calculate"

            logging.info(f"[ME] URL: {url}")

            response = requests.get(url, headers=headers, params=params, timeout=30)

            logging.info(f"[ME] Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    logging.info(f"[ME] Sucesso! {len(result)} serviços")

                    servicos = []
                    for s in result:
                        if not s.get('error') and s.get('price', 0) > 0:
                            servicos.append({
                                'id': s.get('id'),
                                'name': s.get('name'),
                                'price': float(s.get('price', 0)),
                                'delivery_time': s.get('delivery_time', 0),
                                'company': s.get('company', {}).get('name', ''),
                                'currency': 'R$'
                            })

                    return {"success": True, "servicos": servicos}
                except:
                    logging.error(f"[ME] Não é JSON: {response.text[:200]}")
                    return {"success": False, "error": "Resposta inválida"}
            else:
                logging.error(f"[ME] Erro {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logging.error(f"[ME] Exception: {str(e)}")
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