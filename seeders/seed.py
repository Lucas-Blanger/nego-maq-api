import uuid
from app import create_app
from database import db
from database.models import Usuario, Produto


# rode python -m seeders.seed para popular o banco de dados (SOMENTE PARA DESENVOLVIMENTO)
def seed():
    app = create_app()
    with app.app_context():
        # APAGA TUDO
        db.drop_all()
        db.create_all()

        # Criar usuário admin
        if not Usuario.query.filter_by(email="admin@loja.com").first():
            admin = Usuario(
                nome="Admin", sobrenome="admin", email="admin@loja.com", is_admin=True
            )
            admin.set_senha("admin123")
            db.session.add(admin)

        # Lista de produtos (3 por categoria)
        produtos = [
            # FACAS
            {
                "nome": "Faca Chef 8''",
                "descricao": "Faca de aço inoxidável ideal para cortes precisos.",
                "categoria": "facas",
                "preco": 199.90,
                "img": "https://cdn.leroymerlin.com.br/products/faca_artesanal_damasco_6_28_cm_aderente_acabamento_martelado_1571649376_f5ab_600x600.png",
                "estoque": 15,
            },
            {
                "nome": "Faca Desossadora 6''",
                "descricao": "Perfeita para separar carne do osso com facilidade.",
                "categoria": "facas",
                "preco": 149.90,
                "img": "https://cdn.leroymerlin.com.br/products/faca_artesanal_damasco_6_28_cm_aderente_acabamento_martelado_1571649376_f5ab_600x600.png",
                "estoque": 10,
            },
            {
                "nome": "Faca Santoku",
                "descricao": "Faca japonesa versátil para legumes, peixe e carne.",
                "categoria": "facas",
                "preco": 179.90,
                "img": "https://cdn.leroymerlin.com.br/products/faca_artesanal_damasco_6_28_cm_aderente_acabamento_martelado_1571649376_f5ab_600x600.png",
                "estoque": 8,
            },
            # AVENTAIS
            {
                "nome": "Avental Profissional de Couro",
                "descricao": "Proteção premium com bolsos para utensílios.",
                "categoria": "aventais",
                "preco": 159.90,
                "img": "https://images.tcdn.com.br/img/img_prod/698067/avental_para_churrasco_todo_em_couro_legitimo_preto_245_1_20200717175842.jpeg",
                "estoque": 6,
            },
            {
                "nome": "Avental Jeans Gourmet",
                "descricao": "Estilo e proteção para cozinheiros modernos.",
                "categoria": "aventais",
                "preco": 99.90,
                "img": "https://images.tcdn.com.br/img/img_prod/698067/avental_para_churrasco_todo_em_couro_legitimo_preto_245_1_20200717175842.jpeg",
                "estoque": 12,
            },
            {
                "nome": "Avental Preto Básico",
                "descricao": "Simples e eficaz para o dia a dia na cozinha.",
                "categoria": "aventais",
                "preco": 49.90,
                "img": "https://images.tcdn.com.br/img/img_prod/698067/avental_para_churrasco_todo_em_couro_legitimo_preto_245_1_20200717175842.jpeg",
                "estoque": 20,
            },
            # ESTOJOS
            {
                "nome": "Estojo de Facas em Couro",
                "descricao": "Estojo premium para transportar até 8 facas.",
                "categoria": "estojos",
                "preco": 189.90,
                "img": "https://images.tcdn.com.br/img/img_prod/655270/estojo_para_facas_ate_43_cm_com_7_espacos_cor_preta_129_1_b19ce0f008a85c3fbeffe478ee4962e6.jpg",
                "estoque": 5,
            },
            {
                "nome": "Estojo Rígido Profissional",
                "descricao": "Proteção reforçada para chefs em movimento.",
                "categoria": "estojos",
                "preco": 129.90,
                "img": "https://images.tcdn.com.br/img/img_prod/655270/estojo_para_facas_ate_43_cm_com_7_espacos_cor_preta_129_1_b19ce0f008a85c3fbeffe478ee4962e6.jpg",
                "estoque": 7,
            },
            {
                "nome": "Estojo Compacto com Alça",
                "descricao": "Leve e prático para uso diário.",
                "categoria": "estojos",
                "preco": 79.90,
                "img": "https://images.tcdn.com.br/img/img_prod/655270/estojo_para_facas_ate_43_cm_com_7_espacos_cor_preta_129_1_b19ce0f008a85c3fbeffe478ee4962e6.jpg",
                "estoque": 9,
            },
            # CHURRASCOS
            {
                "nome": "Kit Churrasco 5 Peças",
                "descricao": "Faca, garfo, chaira e estojo de couro.",
                "categoria": "churrascos",
                "preco": 249.90,
                "img": "https://images.tcdn.com.br/img/img_prod/1337522/kit_churrasco_faca_7_e_acessorios_para_presente_cod_635_373_1_ac21bebac7ba9272a47ddf1089654816.jpg",
                "estoque": 10,
            },
            {
                "nome": "Tabua de Churrasco Rústica",
                "descricao": "Estilo artesanal com excelente.",
                "categoria": "churrascos",
                "preco": 179.90,
                "img": "https://images.tcdn.com.br/img/img_prod/1337522/kit_churrasco_faca_7_e_acessorios_para_presente_cod_635_373_1_ac21bebac7ba9272a47ddf1089654816.jpg",
                "estoque": 14,
            },
            {
                "nome": "Espeto Duplo de Aço Inox",
                "descricao": "Ideal para grelhar carnes com firmeza.",
                "categoria": "churrascos",
                "preco": 69.90,
                "img": "https://images.tcdn.com.br/img/img_prod/1337522/kit_churrasco_faca_7_e_acessorios_para_presente_cod_635_373_1_ac21bebac7ba9272a47ddf1089654816.jpg",
                "estoque": 18,
            },
        ]

        for p in produtos:
            existente = Produto.query.filter_by(nome=p["nome"]).first()
            if not existente:
                novo_produto = Produto(
                    id=str(uuid.uuid4()),
                    nome=p["nome"],
                    descricao=p["descricao"],
                    categoria=p["categoria"],
                    preco=p["preco"],
                    img=p["img"],
                    estoque=p["estoque"],
                )
                db.session.add(novo_produto)

        db.session.commit()
        print("Seed concluída com sucesso!")


if __name__ == "__main__":
    seed()
