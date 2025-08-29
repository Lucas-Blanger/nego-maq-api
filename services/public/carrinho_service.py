from database.models import Produto


class CarrinhoService:
    carrinho = []

    # Adiciona um produto ao carrinho
    @classmethod
    def adicionar(cls, produto_id):
        produto = Produto.query.get(produto_id)
        if not produto:
            raise ValueError("Produto não encontrado")
        cls.carrinho.append(produto)
        return cls.carrinho

    # Retorna todos os produtos do carrinho
    @classmethod
    def listar(cls):
        return cls.carrinho

    # Limpa o carrinho
    @classmethod
    def limpar(cls):
        cls.carrinho.clear()

    # Finaliza a compra e retorna link do WhatsApp
    @classmethod
    def finalizar(cls, telefone="555492205166"):
        if not cls.carrinho:
            raise ValueError("Carrinho vazio")

        mensagem = "Olá! Quero comprar:\n"
        for p in cls.carrinho:
            mensagem += f"- {p.nome} (R${p.preco})\n"

        cls.limpar()
        # Retorna link formatado para WhatsApp
        return f"https://wa.me/{telefone}?text={mensagem.replace(' ', '%20')}"
