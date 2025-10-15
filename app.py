"""
Eclipse System - Flask E-commerce Application
A complete e-commerce solution with admin panel and dynamic theming

by @__iguyy7
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'thunder-store-secret-key-2025')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_eclipse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# ========================
# Database Models
# ========================

class User(db.Model):
    """User model for admin authentication"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Product(db.Model):
    """Product model for store items"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(300))
    active = db.Column(db.Boolean, default=True)

class FAQ(db.Model):
    """FAQ model for frequently asked questions"""
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)

class Config(db.Model):
    """Configuration model for site settings"""
    id = db.Column(db.Integer, primary_key=True)
    primary_color = db.Column(db.String(7), default='#808080')

# ========================
# Authentication Decorator
# ========================

def admin_required(f):
    """Decorator to protect admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Por favor, faça login para acessar o painel administrativo.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ========================
# Database Initialization
# ========================

def init_db():
    """Initialize database with default data if needed"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if default admin exists
        admin = User.query.filter_by(email='admin@thunder.com').first()
        if not admin:
            # Create default admin user
            admin = User(
                name='Administrator',
                email='admin@thunder.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            print("✓ Default admin created (admin@thunder.com / admin123)")
        
        # Check if default config exists
        config = Config.query.first()
        if not config:
            # Create default configuration
            config = Config(primary_color='#808080')
            db.session.add(config)
            print("✓ Default configuration created")
        
        # Commit changes
        db.session.commit()
        print("✓ Database initialized successfully")

# ========================
# Customer Routes
# ========================

@app.route('/')
def index():
    """Home page with featured products and FAQs"""
    products = Product.query.filter_by(active=True).limit(6).all()
    faqs = FAQ.query.all()
    config = Config.query.first()
    return render_template('index.html', products=products, faqs=faqs, config=config)

@app.route('/loja')
def loja():
    """Store page with all active products"""
    products = Product.query.filter_by(active=True).all()
    config = Config.query.first()
    return render_template('loja.html', products=products, config=config)

@app.route('/adicionar-carrinho/<int:product_id>')
def add_to_cart(product_id):
    """Add product to session-based cart"""
    product = Product.query.get_or_404(product_id)
    
    # Initialize cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if product already in cart
    cart = session['cart']
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += 1
            session.modified = True
            flash(f'{product.name} quantidade atualizada no carrinho!', 'success')
            return redirect(url_for('loja'))
    
    # Add new product to cart
    cart.append({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'quantity': 1
    })
    session.modified = True
    flash(f'{product.name} adicionado ao carrinho!', 'success')
    return redirect(url_for('loja'))

@app.route('/carrinho')
def carrinho():
    """Shopping cart page"""
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    config = Config.query.first()
    return render_template('carrinho.html', cart=cart, total=total, config=config)

@app.route('/atualizar-carrinho/<int:product_id>/<action>')
def update_cart(product_id, action):
    """Update cart item quantity"""
    if 'cart' in session:
        cart = session['cart']
        for item in cart:
            if item['id'] == product_id:
                if action == 'increase':
                    item['quantity'] += 1
                elif action == 'decrease':
                    item['quantity'] -= 1
                    if item['quantity'] <= 0:
                        cart.remove(item)
                session.modified = True
                break
    return redirect(url_for('carrinho'))

@app.route('/remover-carrinho/<int:product_id>')
def remove_from_cart(product_id):
    """Remove product from cart"""
    if 'cart' in session:
        cart = session['cart']
        session['cart'] = [item for item in cart if item['id'] != product_id]
        session.modified = True
        flash('Produto removido do carrinho!', 'success')
    return redirect(url_for('carrinho'))

@app.route('/checkout')
def checkout():
    """Checkout page"""
    cart = session.get('cart', [])
    if not cart:
        flash('Seu carrinho está vazio!', 'error')
        return redirect(url_for('loja'))
    
    total = sum(item['price'] * item['quantity'] for item in cart)
    config = Config.query.first()
    return render_template('checkout.html', cart=cart, total=total, config=config)

@app.route('/finalizar-compra', methods=['POST'])
def finalizar_compra():
    """Process checkout and clear cart"""
    # Clear the cart
    session.pop('cart', None)
    flash('Pedido realizado com sucesso! Obrigado pela sua compra.', 'success')
    return redirect(url_for('index'))

# ========================
# Admin Authentication Routes
# ========================

@app.route('/painel/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email, is_admin=True).first()
        
        if user and password and check_password_hash(user.password, password):
            session['admin_id'] = user.id
            session['admin_name'] = user.name
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Email ou senha inválidos!', 'error')
    
    config = Config.query.first()
    return render_template('painel/login.html', config=config)

@app.route('/painel/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('admin_login'))

# ========================
# Admin Dashboard Routes
# ========================

@app.route('/painel')
@admin_required
def admin_dashboard():
    """Admin dashboard overview"""
    total_products = Product.query.count()
    active_products = Product.query.filter_by(active=True).count()
    total_faqs = FAQ.query.count()
    config = Config.query.first()
    return render_template('painel/dashboard.html', 
                         total_products=total_products,
                         active_products=active_products,
                         total_faqs=total_faqs,
                         config=config)

# ========================
# Admin Product Routes (CRUD)
# ========================

@app.route('/painel/produtos')
@admin_required
def admin_produtos():
    """List all products"""
    products = Product.query.all()
    config = Config.query.first()
    return render_template('painel/produtos.html', products=products, config=config)

@app.route('/painel/produto/novo', methods=['GET', 'POST'])
@admin_required
def admin_produto_novo():
    """Create new product"""
    if request.method == 'POST':
        product = Product(
            name=request.form.get('name', ''),
            price=float(request.form.get('price', 0)),
            description=request.form.get('description', ''),
            image=request.form.get('image', ''),
            active=request.form.get('active') == 'on'
        )
        db.session.add(product)
        db.session.commit()
        flash('Produto criado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))
    
    config = Config.query.first()
    return render_template('painel/produto_form.html', product=None, config=config)

@app.route('/painel/produto/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_produto_editar(id):
    """Edit existing product"""
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name', '')
        product.price = float(request.form.get('price', 0))
        product.description = request.form.get('description', '')
        product.image = request.form.get('image', '')
        product.active = request.form.get('active') == 'on'
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))
    
    config = Config.query.first()
    return render_template('painel/produto_form.html', product=product, config=config)

@app.route('/painel/produto/deletar/<int:id>')
@admin_required
def admin_produto_deletar(id):
    """Delete product"""
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produto deletado com sucesso!', 'success')
    return redirect(url_for('admin_produtos'))

# ========================
# Admin FAQ Routes (CRUD)
# ========================

@app.route('/painel/perguntas')
@admin_required
def admin_perguntas():
    """List all FAQs"""
    faqs = FAQ.query.all()
    config = Config.query.first()
    return render_template('painel/perguntas.html', faqs=faqs, config=config)

@app.route('/painel/pergunta/nova', methods=['GET', 'POST'])
@admin_required
def admin_pergunta_nova():
    """Create new FAQ"""
    if request.method == 'POST':
        faq = FAQ(
            question=request.form.get('question', ''),
            answer=request.form.get('answer', '')
        )
        db.session.add(faq)
        db.session.commit()
        flash('Pergunta criada com sucesso!', 'success')
        return redirect(url_for('admin_perguntas'))
    
    config = Config.query.first()
    return render_template('painel/pergunta_form.html', faq=None, config=config)

@app.route('/painel/pergunta/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_pergunta_editar(id):
    """Edit existing FAQ"""
    faq = FAQ.query.get_or_404(id)
    
    if request.method == 'POST':
        faq.question = request.form.get('question')
        faq.answer = request.form.get('answer')
        db.session.commit()
        flash('Pergunta atualizada com sucesso!', 'success')
        return redirect(url_for('admin_perguntas'))
    
    config = Config.query.first()
    return render_template('painel/pergunta_form.html', faq=faq, config=config)

@app.route('/painel/pergunta/deletar/<int:id>')
@admin_required
def admin_pergunta_deletar(id):
    """Delete FAQ"""
    faq = FAQ.query.get_or_404(id)
    db.session.delete(faq)
    db.session.commit()
    flash('Pergunta deletada com sucesso!', 'success')
    return redirect(url_for('admin_perguntas'))

# ========================
# Admin Configuration Routes
# ========================

@app.route('/painel/config', methods=['GET', 'POST'])
@admin_required
def admin_config():
    """Configuration page for theme customization"""
    config = Config.query.first()
    
    if request.method == 'POST':
        config.primary_color = request.form.get('primary_color')
        db.session.commit()
        flash('Configuração atualizada com sucesso!', 'success')
        return redirect(url_for('admin_config'))
    
    return render_template('painel/config.html', config=config)

# ========================
# Application Entry Point
# ========================

if __name__ == '__main__':
    # Initialize database on first run
    init_db()
    
    # Run Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)
