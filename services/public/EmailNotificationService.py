import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import logging
from utils.email import enviar_email

logger = logging.getLogger(__name__)


class EmailNotificationService:
    # Serviço para envio de notificações por email sobre pedidos

    @staticmethod
    def _formatar_moeda(valor):
        # Formata valor para moeda brasileira
        return (
            f"R$ {float(valor):,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    @staticmethod
    def _gerar_lista_itens_html(pedido):
        # Gera HTML com a lista de itens do pedido
        itens_html = ""
        for item in pedido.itens:
            subtotal = item.preco_unitario * item.quantidade
            itens_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">
                    <strong>{item.produto.nome}</strong>
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">
                    {item.quantidade}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                    {EmailNotificationService._formatar_moeda(item.preco_unitario)}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                    {EmailNotificationService._formatar_moeda(subtotal)}
                </td>
            </tr>
            """
        return itens_html

    @staticmethod
    def _gerar_endereco_html(endereco):
        # Gera HTML formatado do endereço
        return f"""
        {endereco.logradouro}, {endereco.numero}
        {f'- {endereco.complemento}' if endereco.complemento else ''}<br>
        {endereco.bairro} - {endereco.cidade}/{endereco.estado}<br>
        CEP: {endereco.cep}
        """

    @staticmethod
    def _gerar_header_html():
        # Gera o header padrão para todos os emails
        return """
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr>
                <td style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 40px 30px; text-align: center; border-radius: 8px 8px 0 0;">
                    <img src="https://res.cloudinary.com/dq4catqou/image/upload/v1761932437/p2jof6awhzpzjiddfk7d.png" alt="Logo NegoMaq" width="120" style="margin-bottom: 15px; border-radius: 8px;">
                    <p style="color: #cccccc; margin: 10px 0 0 0; font-size: 14px; letter-spacing: 1px;">
                        COUROS & FACAS ARTESANAIS
                    </p>
                </td>
            </tr>
        </table>
        """

    @staticmethod
    def _gerar_footer_html():
        # Gera o footer padrão para todos os emails
        return """
        <table style="width: 100%; border-collapse: collapse; margin-top: 30px;">
            <tr>
                <td style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 30px; text-align: center; border-radius: 0 0 8px 8px;">
                    <p style="color: #cccccc; margin: 0; font-size: 12px;">
                        © 2025 NegoMaq - Couros & Facas Artesanais<br>
                        <span style="color: #888888; font-size: 11px;">Este é um email automático, por favor não responda.</span>
                    </p>
                </td>
            </tr>
        </table>
        """

    @staticmethod
    def notificar_pedido_criado(pedido):
        # Envia email quando o pedido é criado
        usuario = pedido.usuario

        assunto = f"Pedido recebido - Aguardando Pagamento"

        itens_html = EmailNotificationService._gerar_lista_itens_html(pedido)
        endereco_html = EmailNotificationService._gerar_endereco_html(pedido.endereco)

        header = EmailNotificationService._gerar_header_html()
        footer = EmailNotificationService._gerar_footer_html()

        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                {header}
                <div style="padding: 30px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 0;">
                        Pedido Recebido! 
                    </h2>
                
                <p>Olá, <strong>{usuario.nome}</strong>!</p>
                
                <p>Recebemos seu pedido com sucesso. Assim que o pagamento for confirmado, começaremos a preparar sua encomenda.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c3e50;">Detalhes do Pedido</h3>
                    <p><strong>Data:</strong> {pedido.criado_em.strftime('%d/%m/%Y às %H:%M')}</p>
                    <p><strong>Status:</strong> Aguardando Pagamento</p>
                </div>
                
                <h3 style="color: #2c3e50;">Itens do Pedido</h3>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Produto</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Qtd</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Preço Unit.</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {itens_html}
                    </tbody>
                </table>
                
                <div style="text-align: right; margin: 20px 0;">
                    <p><strong>Subtotal:</strong> {EmailNotificationService._formatar_moeda(pedido.valor_total - pedido.frete_valor)}</p>
                    <p><strong>Frete ({pedido.frete_servico_nome or pedido.frete_tipo}):</strong> {EmailNotificationService._formatar_moeda(pedido.frete_valor)}</p>
                    <h3 style="color: #27ae60; margin: 10px 0;">Total: {EmailNotificationService._formatar_moeda(pedido.valor_total)}</h3>
                </div>
                
                <h3 style="color: #2c3e50;">Endereço de Entrega</h3>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                    {endereco_html}
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <p style="margin: 0;"><strong> Aguardando Pagamento</strong></p>
                    <p style="margin: 10px 0 0 0;">Complete o pagamento para confirmarmos seu pedido e iniciarmos a preparação.</p>
                </div>
                
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                        Em caso de dúvidas, entre em contato conosco.
                    </p>
                </div>
                {footer}
            </div>
        </body>
        </html>
        """

        return enviar_email(usuario.email, assunto, corpo)

    @staticmethod
    def notificar_pagamento_aprovado(pedido):
        # Envia email quando o pagamento é aprovado
        usuario = pedido.usuario

        assunto = f"Pagamento Confirmado"

        itens_html = EmailNotificationService._gerar_lista_itens_html(pedido)

        header = EmailNotificationService._gerar_header_html()
        footer = EmailNotificationService._gerar_footer_html()

        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                {header}
                <div style="padding: 30px;">
                    <h2 style="color: #27ae60; border-bottom: 2px solid #27ae60; padding-bottom: 10px; margin-top: 0;">
                        Pagamento Confirmado! 
                    </h2>
                
                <p>Olá, <strong>{usuario.nome}</strong>!</p>
                
                <p>Ótimas notícias! Seu pagamento foi confirmado com sucesso.</p>
                
                <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                    <p style="margin: 0;"><strong>Pagamento Aprovado</strong></p>
                    <p style="margin: 10px 0 0 0;">Seu pedido está sendo preparado e em breve será enviado.</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c3e50;">Resumo do Pedido</h3>
                    <p><strong>Valor Total:</strong> {EmailNotificationService._formatar_moeda(pedido.valor_total)}</p>
                    <p><strong>Status:</strong> Pagamento Confirmado</p>
                </div>
                
                <h3 style="color: #2c3e50;">Itens do Pedido</h3>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Produto</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Qtd</th>
                        </tr>
                    </thead>
                    <tbody>
                        {itens_html}
                    </tbody>
                </table>
                
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                        Você receberá outro email assim que seu pedido for enviado.
                    </p>
                </div>
                {footer}
            </div>
        </body>
        </html>
        """

        return enviar_email(usuario.email, assunto, corpo)

    @staticmethod
    def notificar_pedido_em_separacao(pedido):
        # Envia email quando o pedido está em separação
        usuario = pedido.usuario

        assunto = f"Seu pedido está sendo preparado"

        header = EmailNotificationService._gerar_header_html()
        footer = EmailNotificationService._gerar_footer_html()

        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                {header}
                <div style="padding: 30px;">
                    <h2 style="color: #3498db; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 0;">
                        Pedido em Preparação 
                    </h2>
                
                <p>Olá, <strong>{usuario.nome}</strong>!</p>
                
                <p>Seu pedido está sendo preparado com muito cuidado pela nossa equipe.</p>
                
                <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #17a2b8;">
                    <p style="margin: 0;"><strong> Em Separação</strong></p>
                    <p style="margin: 10px 0 0 0;">Estamos separando e embalando seus produtos. Em breve enviaremos para a transportadora.</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c3e50;">Informações do Envio</h3>
                    <p><strong>Transportadora:</strong> {pedido.frete_servico_nome or pedido.frete_tipo}</p>
                    {f'<p><strong>Código de Rastreio:</strong> {pedido.melhor_envio_protocolo}</p>' if pedido.melhor_envio_protocolo else ''}
                </div>
                
                    <p>Assim que o pedido for enviado, você receberá outro email com o código de rastreamento completo.</p>
                    
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                        Obrigado pela sua compra!
                    </p>
                </div>
                {footer}
            </div>
        </body>
        </html>
        """

        return enviar_email(usuario.email, assunto, corpo)

    @staticmethod
    def notificar_pedido_enviado(pedido, codigo_rastreio=None):
        # Envia email quando o pedido é enviado
        usuario = pedido.usuario

        assunto = f"Pedido enviado! "

        codigo_rastreio = (
            codigo_rastreio or pedido.melhor_envio_protocolo or "Aguardando atualização"
        )
        etiqueta_url = pedido.etiqueta_url if hasattr(pedido, "etiqueta_url") else None

        header = EmailNotificationService._gerar_header_html()
        footer = EmailNotificationService._gerar_footer_html()

        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                {header}
                <div style="padding: 30px;">
                    <h2 style="color: #ff9800; border-bottom: 2px solid #ff9800; padding-bottom: 10px; margin-top: 0;">
                        Seu Pedido Foi Enviado! 
                    </h2>
                
                <p>Olá, <strong>{usuario.nome}</strong>!</p>
                
                <p>Ótimas notícias! Seu pedido foi despachado e está a caminho.</p>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <p style="margin: 0;"><strong> Pedido em Trânsito</strong></p>
                    <p style="margin: 10px 0 0 0;">Seu pedido está nas mãos da transportadora e logo chegará até você!</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c3e50;">Informações de Rastreamento</h3>
                    <p><strong>Transportadora:</strong> {pedido.frete_servico_nome or pedido.frete_tipo}</p>
                    <p><strong>Código de Rastreio:</strong> <span style="background-color: #e9ecef; padding: 5px 10px; border-radius: 3px; font-family: monospace;">{codigo_rastreio}</span></p>
                    {f'<p><a href="{etiqueta_url}" style="color: #3498db; text-decoration: none;"> Ver Etiqueta de Envio</a></p>' if etiqueta_url else ''}
                </div>
                
                <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong> Dica:</strong></p>
                    <p style="margin: 10px 0 0 0;">Use o código de rastreio acima no site da transportadora para acompanhar a entrega em tempo real.</p>
                </div>
                
                <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                    Você receberá uma confirmação quando o pedido for entregue.<br>
                    Este é um email automático, por favor não responda.
                </p>
            </div>
        </body>
        </html>
        """

        return enviar_email(usuario.email, assunto, corpo)

    @staticmethod
    def notificar_pedido_entregue(pedido):
        # Envia email quando o pedido é entregue
        usuario = pedido.usuario

        assunto = f"Pedido entregue! "

        header = EmailNotificationService._gerar_header_html()
        footer = EmailNotificationService._gerar_footer_html()

        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                {header}
                <div style="padding: 30px;">
                    <h2 style="color: #28a745; border-bottom: 2px solid #28a745; padding-bottom: 10px; margin-top: 0;">
                        Pedido Entregue! 
                    </h2>
                
                <p>Olá, <strong>{usuario.nome}</strong>!</p>
                
                <p>Seu pedido foi entregue com sucesso!</p>
                
                <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                    <p style="margin: 0;"><strong> Entrega Confirmada</strong></p>
                    <p style="margin: 10px 0 0 0;">Esperamos que você esteja satisfeito com sua compra!</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c3e50;">Detalhes da Entrega</h3>
                    <p><strong>Data da Entrega:</strong> {datetime.now().strftime('%d/%m/%Y')}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0; padding: 20px; background-color: #f8f9fa; border-radius: 5px;">
                    <h3 style="color: #2c3e50; margin-top: 0;">Como foi sua experiência?</h3>
                    <p>Sua opinião é muito importante para nós! Conte-nos o que achou do produto e do atendimento.</p>
                </div>
                
                    <p style="text-align: center; margin-top: 20px;">
                        <strong>Obrigado por comprar conosco!</strong>
                    </p>
                </div>
                {footer}
            </div>
        </body>
        </html>
        """

        return enviar_email(usuario.email, assunto, corpo)
