import uuid
from app import create_app
from database import db
from database.models import (
    Usuario,
    Produto,
    Endereco,
    Pedido,
    ItemPedido,
    TransacaoPagamento,
)
from database.enums.status_pedido_enum import StatusPedidoEnum
from database.enums.status_pagamento_enum import StatusPagamentoEnum
from utils.crypto_utils import criptografar_cpf
from decimal import Decimal


# rode python -m seeders.seed para popular o banco de dados (SOMENTE PARA DESENVOLVIMENTO)
def seed():
    app = create_app()
    with app.app_context():
        # APAGA TUDO
        db.drop_all()
        db.create_all()

        # ADMIN
        admin = Usuario(
            nome="Admin",
            sobrenome="Sistema",
            email="admin@loja.com",
            telefone="51999990001",
            cpf=criptografar_cpf("38909166002"),
            is_admin=True,
        )
        admin.set_senha("admin123")
        db.session.add(admin)

        # ========== USUÁRIO 2: TESTE ==========
        usuario_teste = Usuario(
            nome="João",
            sobrenome="Silva",
            email="teste@teste.com",
            telefone="51999990002",
            cpf=criptografar_cpf("12337797023"),
            is_admin=False,
        )
        usuario_teste.set_senha("teste")
        db.session.add(usuario_teste)

        # ========== USUÁRIO 3: MARIA ==========
        usuario_maria = Usuario(
            nome="Maria",
            sobrenome="Santos",
            email="maria.santos@email.com",
            telefone="11987654321",
            cpf=criptografar_cpf("98765432100"),
            is_admin=False,
        )
        usuario_maria.set_senha("maria123")
        db.session.add(usuario_maria)

        # ========== USUÁRIO 4: PEDRO ==========
        usuario_pedro = Usuario(
            nome="Pedro",
            sobrenome="Oliveira",
            email="pedro.oliveira@email.com",
            telefone="21976543210",
            cpf=criptografar_cpf("45678912300"),
            is_admin=False,
        )
        usuario_pedro.set_senha("pedro123")
        db.session.add(usuario_pedro)

        db.session.commit()

        # ENDEREÇOS

        # Endereço do usuário teste (Porto Alegre/RS)
        endereco_teste = Endereco(
            usuario_id=usuario_teste.id,
            cep="90010000",
            logradouro="Rua dos Andradas",
            numero="1234",
            complemento="Apto 501",
            bairro="Centro Histórico",
            cidade="Porto Alegre",
            estado="RS",
        )
        db.session.add(endereco_teste)

        # Endereço da Maria (São Paulo/SP)
        endereco_maria = Endereco(
            usuario_id=usuario_maria.id,
            cep="01310100",
            logradouro="Avenida Paulista",
            numero="1578",
            complemento="",
            bairro="Bela Vista",
            cidade="São Paulo",
            estado="SP",
        )
        db.session.add(endereco_maria)

        # Endereço do Pedro (Rio de Janeiro/RJ)
        endereco_pedro = Endereco(
            usuario_id=usuario_pedro.id,
            cep="20040020",
            logradouro="Avenida Rio Branco",
            numero="156",
            complemento="Sala 1203",
            bairro="Centro",
            cidade="Rio de Janeiro",
            estado="RJ",
        )
        db.session.add(endereco_pedro)

        db.session.commit()

        #  PRODUTOS

        produtos_data = [
            # FACAS
            {
                "nome": "Faca Chef 8''",
                "descricao": "Faca de aço inoxidável ideal para cortes precisos.",
                "categoria": "facas",
                "preco": 199.90,
                "img": "https://cdn.leroymerlin.com.br/products/faca_artesanal_damasco_6_28_cm_aderente_acabamento_martelado_1571649376_f5ab_600x600.png",
                "estoque": 15,
                "peso": 250.0,
                "altura": 3,
                "largura": 5,
                "comprimento": 25,
            },
            {
                "nome": "Faca Desossadora 6''",
                "descricao": "Perfeita para separar carne do osso com facilidade.",
                "categoria": "facas",
                "preco": 149.90,
                "img": "https://cdn.leroymerlin.com.br/products/faca_artesanal_damasco_6_28_cm_aderente_acabamento_martelado_1571649376_f5ab_600x600.png",
                "estoque": 10,
                "peso": 200.0,
                "altura": 3,
                "largura": 5,
                "comprimento": 20,
            },
            {
                "nome": "Faca Santoku",
                "descricao": "Faca japonesa versátil para legumes, peixe e carne.",
                "categoria": "facas",
                "preco": 179.90,
                "img": "https://cdn.leroymerlin.com.br/products/faca_artesanal_damasco_6_28_cm_aderente_acabamento_martelado_1571649376_f5ab_600x600.png",
                "estoque": 8,
                "peso": 220.0,
                "altura": 3,
                "largura": 5,
                "comprimento": 22,
            },
            # AVENTAIS
            {
                "nome": "Avental Profissional de Couro",
                "descricao": "Proteção premium com bolsos para utensílios.",
                "categoria": "aventais",
                "preco": 159.90,
                "img": "https://images.tcdn.com.br/img/img_prod/698067/avental_para_churrasco_todo_em_couro_legitimo_preto_245_1_20200717175842.jpeg",
                "estoque": 6,
                "peso": 800.0,
                "altura": 5,
                "largura": 40,
                "comprimento": 60,
            },
            {
                "nome": "Avental Jeans Gourmet",
                "descricao": "Estilo e proteção para cozinheiros modernos.",
                "categoria": "aventais",
                "preco": 99.90,
                "img": "https://images.tcdn.com.br/img/img_prod/698067/avental_para_churrasco_todo_em_couro_legitimo_preto_245_1_20200717175842.jpeg",
                "estoque": 12,
                "peso": 500.0,
                "altura": 5,
                "largura": 35,
                "comprimento": 55,
            },
            {
                "nome": "Avental Preto Básico",
                "descricao": "Simples e eficaz para o dia a dia na cozinha.",
                "categoria": "aventais",
                "preco": 49.90,
                "img": "https://images.tcdn.com.br/img/img_prod/698067/avental_para_churrasco_todo_em_couro_legitimo_preto_245_1_20200717175842.jpeg",
                "estoque": 20,
                "peso": 300.0,
                "altura": 5,
                "largura": 30,
                "comprimento": 50,
            },
            # ESTOJOS
            {
                "nome": "Estojo de Facas em Couro",
                "descricao": "Estojo premium para transportar até 8 facas.",
                "categoria": "estojos",
                "preco": 189.90,
                "img": "https://images.tcdn.com.br/img/img_prod/655270/estojo_para_facas_ate_43_cm_com_7_espacos_cor_preta_129_1_b19ce0f008a85c3fbeffe478ee4962e6.jpg",
                "estoque": 5,
                "peso": 600.0,
                "altura": 8,
                "largura": 15,
                "comprimento": 45,
            },
            {
                "nome": "Estojo Rígido Profissional",
                "descricao": "Proteção reforçada para chefs em movimento.",
                "categoria": "estojos",
                "preco": 129.90,
                "img": "https://images.tcdn.com.br/img/img_prod/655270/estojo_para_facas_ate_43_cm_com_7_espacos_cor_preta_129_1_b19ce0f008a85c3fbeffe478ee4962e6.jpg",
                "estoque": 7,
                "peso": 700.0,
                "altura": 8,
                "largura": 12,
                "comprimento": 40,
            },
            {
                "nome": "Estojo Compacto com Alça",
                "descricao": "Leve e prático para uso diário.",
                "categoria": "estojos",
                "preco": 79.90,
                "img": "https://images.tcdn.com.br/img/img_prod/655270/estojo_para_facas_ate_43_cm_com_7_espacos_cor_preta_129_1_b19ce0f008a85c3fbeffe478ee4962e6.jpg",
                "estoque": 9,
                "peso": 400.0,
                "altura": 6,
                "largura": 10,
                "comprimento": 35,
            },
            # CHURRASCOS
            {
                "nome": "Kit Churrasco 5 Peças",
                "descricao": "Faca, garfo, chaira e estojo de couro.",
                "categoria": "churrascos",
                "preco": 249.90,
                "img": "https://images.tcdn.com.br/img/img_prod/1337522/kit_churrasco_faca_7_e_acessorios_para_presente_cod_635_373_1_ac21bebac7ba9272a47ddf1089654816.jpg",
                "estoque": 10,
                "peso": 1200.0,
                "altura": 10,
                "largura": 20,
                "comprimento": 40,
            },
            {
                "nome": "Tabua de Churrasco Rústica",
                "descricao": "Estilo artesanal com excelente acabamento.",
                "categoria": "churrascos",
                "preco": 179.90,
                "img": "https://images.tcdn.com.br/img/img_prod/1337522/kit_churrasco_faca_7_e_acessorios_para_presente_cod_635_373_1_ac21bebac7ba9272a47ddf1089654816.jpg",
                "estoque": 14,
                "peso": 2000.0,
                "altura": 3,
                "largura": 30,
                "comprimento": 50,
            },
            {
                "nome": "Espeto Duplo de Aço Inox",
                "descricao": "Ideal para grelhar carnes com firmeza.",
                "categoria": "churrascos",
                "preco": 69.90,
                "img": "https://images.tcdn.com.br/img/img_prod/1337522/kit_churrasco_faca_7_e_acessorios_para_presente_cod_635_373_1_ac21bebac7ba9272a47ddf1089654816.jpg",
                "estoque": 18,
                "peso": 300.0,
                "altura": 2,
                "largura": 3,
                "comprimento": 60,
            },
        ]

        produtos = {}
        for p in produtos_data:
            novo_produto = Produto(
                id=str(uuid.uuid4()),
                nome=p["nome"],
                descricao=p["descricao"],
                categoria=p["categoria"],
                preco=p["preco"],
                img=p["img"],
                estoque=p["estoque"],
                peso=p["peso"],
                altura=p["altura"],
                largura=p["largura"],
                comprimento=p["comprimento"],
            )
            db.session.add(novo_produto)
            produtos[p["nome"]] = novo_produto

        db.session.commit()

        # PEDIDOS

        # PEDIDO 1: João (teste@teste.com) - ENTREGUE
        pedido1 = Pedido(
            usuario_id=usuario_teste.id,
            endereco_id=endereco_teste.id,
            valor_total=Decimal("0"),
            status=StatusPedidoEnum.ENTREGUE,
            frete_valor=Decimal("25.50"),
            frete_tipo="PAC",
        )
        db.session.add(pedido1)
        db.session.flush()

        # Itens do pedido 1
        item1_1 = ItemPedido(
            pedido_id=pedido1.id,
            produto_id=produtos["Faca Chef 8''"].id,
            quantidade=1,
            preco_unitario=produtos["Faca Chef 8''"].preco,
            peso=produtos["Faca Chef 8''"].peso,
            altura=produtos["Faca Chef 8''"].altura,
            largura=produtos["Faca Chef 8''"].largura,
            comprimento=produtos["Faca Chef 8''"].comprimento,
        )
        item1_2 = ItemPedido(
            pedido_id=pedido1.id,
            produto_id=produtos["Avental Jeans Gourmet"].id,
            quantidade=1,
            preco_unitario=produtos["Avental Jeans Gourmet"].preco,
            peso=produtos["Avental Jeans Gourmet"].peso,
            altura=produtos["Avental Jeans Gourmet"].altura,
            largura=produtos["Avental Jeans Gourmet"].largura,
            comprimento=produtos["Avental Jeans Gourmet"].comprimento,
        )
        db.session.add_all([item1_1, item1_2])

        pedido1.valor_total = Decimal("199.90") + Decimal("99.90") + Decimal("25.50")

        # Transação do pedido 1
        transacao1 = TransacaoPagamento(
            pedido_id=pedido1.id,
            valor=pedido1.valor_total,
            metodo_pagamento="mercadopago",
            status=StatusPagamentoEnum.APROVADO,
            mp_payment_id="1234567890",
        )
        db.session.add(transacao1)

        # PEDIDO 2: Maria - EM_SEPARACAO
        pedido2 = Pedido(
            usuario_id=usuario_maria.id,
            endereco_id=endereco_maria.id,
            valor_total=Decimal("0"),
            status=StatusPedidoEnum.EM_SEPARACAO,
            frete_valor=Decimal("35.00"),
            frete_tipo="SEDEX",
        )
        db.session.add(pedido2)
        db.session.flush()

        item2_1 = ItemPedido(
            pedido_id=pedido2.id,
            produto_id=produtos["Kit Churrasco 5 Peças"].id,
            quantidade=1,
            preco_unitario=produtos["Kit Churrasco 5 Peças"].preco,
            peso=produtos["Kit Churrasco 5 Peças"].peso,
            altura=produtos["Kit Churrasco 5 Peças"].altura,
            largura=produtos["Kit Churrasco 5 Peças"].largura,
            comprimento=produtos["Kit Churrasco 5 Peças"].comprimento,
        )
        item2_2 = ItemPedido(
            pedido_id=pedido2.id,
            produto_id=produtos["Tabua de Churrasco Rústica"].id,
            quantidade=1,
            preco_unitario=produtos["Tabua de Churrasco Rústica"].preco,
            peso=produtos["Tabua de Churrasco Rústica"].peso,
            altura=produtos["Tabua de Churrasco Rústica"].altura,
            largura=produtos["Tabua de Churrasco Rústica"].largura,
            comprimento=produtos["Tabua de Churrasco Rústica"].comprimento,
        )
        db.session.add_all([item2_1, item2_2])

        pedido2.valor_total = Decimal("249.90") + Decimal("179.90") + Decimal("35.00")

        transacao2 = TransacaoPagamento(
            pedido_id=pedido2.id,
            valor=pedido2.valor_total,
            metodo_pagamento="mercadopago",
            status=StatusPagamentoEnum.APROVADO,
            mp_payment_id="0987654321",
        )
        db.session.add(transacao2)

        # PEDIDO 3: Pedro - PAGO
        pedido3 = Pedido(
            usuario_id=usuario_pedro.id,
            endereco_id=endereco_pedro.id,
            valor_total=Decimal("0"),
            status=StatusPedidoEnum.PAGO,
            frete_valor=Decimal("28.00"),
            frete_tipo="PAC",
        )
        db.session.add(pedido3)
        db.session.flush()

        item3_1 = ItemPedido(
            pedido_id=pedido3.id,
            produto_id=produtos["Faca Santoku"].id,
            quantidade=2,
            preco_unitario=produtos["Faca Santoku"].preco,
            peso=produtos["Faca Santoku"].peso,
            altura=produtos["Faca Santoku"].altura,
            largura=produtos["Faca Santoku"].largura,
            comprimento=produtos["Faca Santoku"].comprimento,
        )
        item3_2 = ItemPedido(
            pedido_id=pedido3.id,
            produto_id=produtos["Estojo de Facas em Couro"].id,
            quantidade=1,
            preco_unitario=produtos["Estojo de Facas em Couro"].preco,
            peso=produtos["Estojo de Facas em Couro"].peso,
            altura=produtos["Estojo de Facas em Couro"].altura,
            largura=produtos["Estojo de Facas em Couro"].largura,
            comprimento=produtos["Estojo de Facas em Couro"].comprimento,
        )
        db.session.add_all([item3_1, item3_2])

        pedido3.valor_total = (
            (Decimal("179.90") * 2) + Decimal("189.90") + Decimal("28.00")
        )

        transacao3 = TransacaoPagamento(
            pedido_id=pedido3.id,
            valor=pedido3.valor_total,
            metodo_pagamento="mercadopago",
            status=StatusPagamentoEnum.APROVADO,
            mp_payment_id="1122334455",
        )
        db.session.add(transacao3)

        db.session.commit()


if __name__ == "__main__":
    seed()
