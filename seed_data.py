"""
Script para popular o banco de dados com dados de exemplo
Execute: python seed_data.py
"""

from app import app, db, Product, FAQ

def seed_database():
    with app.app_context():
        # Verificar se já existem produtos
        if Product.query.count() == 0:
            # Adicionar produtos de exemplo
            produtos = [
                Product(
                    name="Smartphone Premium X1",
                    price=1299.90,
                    description="O mais novo smartphone com tecnologia 5G, tela AMOLED de 6.7 polegadas e câmera de 108MP",
                    image="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500",
                    active=True
                ),
                Product(
                    name="Notebook Gamer Pro",
                    price=4999.90,
                    description="Notebook gamer com RTX 4060, Intel i7 13ª geração, 16GB RAM e SSD 512GB",
                    image="https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500",
                    active=True
                ),
                Product(
                    name="Headphone Bluetooth Elite",
                    price=599.90,
                    description="Headphone com cancelamento de ruído ativo, bateria de 30 horas e som Hi-Fi",
                    image="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
                    active=True
                ),
                Product(
                    name="Smart TV 55' 4K",
                    price=2299.90,
                    description="Smart TV LED 4K com HDR, sistema operacional Android TV e controle por voz",
                    image="https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=500",
                    active=True
                ),
                Product(
                    name="Console Next Gen",
                    price=3499.90,
                    description="Console de última geração com 1TB de armazenamento e suporte a 8K",
                    image="https://images.unsplash.com/photo-1486401899868-0e435ed85128?w=500",
                    active=True
                ),
                Product(
                    name="Smartwatch Sport Pro",
                    price=899.90,
                    description="Smartwatch com GPS, monitor cardíaco, resistente à água e bateria de 7 dias",
                    image="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
                    active=True
                ),
            ]
            
            for produto in produtos:
                db.session.add(produto)
            
            print(f"✓ {len(produtos)} produtos adicionados com sucesso!")
        
        # Verificar se já existem FAQs
        if FAQ.query.count() == 0:
            # Adicionar FAQs de exemplo
            faqs = [
                FAQ(
                    question="Como faço para rastrear meu pedido?",
                    answer="Após a confirmação do pagamento, você receberá um código de rastreamento por email. Você pode usar esse código para acompanhar sua entrega em tempo real."
                ),
                FAQ(
                    question="Qual é o prazo de entrega?",
                    answer="O prazo de entrega varia de acordo com sua região. Geralmente, entregas são realizadas em 3 a 7 dias úteis para todo o Brasil."
                ),
                FAQ(
                    question="Vocês aceitam pagamento por PIX?",
                    answer="Sim! Aceitamos PIX, cartão de crédito, cartão de débito e boleto bancário. O pagamento via PIX tem aprovação instantânea."
                ),
                FAQ(
                    question="Posso trocar ou devolver um produto?",
                    answer="Sim, você tem 7 dias após o recebimento para solicitar troca ou devolução, conforme o Código de Defesa do Consumidor. O produto deve estar em perfeitas condições."
                ),
                FAQ(
                    question="Os produtos têm garantia?",
                    answer="Todos os nossos produtos contam com garantia do fabricante de no mínimo 1 ano. Produtos eletrônicos podem ter garantia estendida opcional."
                ),
            ]
            
            for faq in faqs:
                db.session.add(faq)
            
            print(f"✓ {len(faqs)} FAQs adicionadas com sucesso!")
        
        # Commit das mudanças
        db.session.commit()
        print("✓ Banco de dados populado com sucesso!")

if __name__ == "__main__":
    seed_database()
