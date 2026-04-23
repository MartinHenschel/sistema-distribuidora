from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# ================= LOGIN MANAGER =================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para acessar o sistema.'

class User(UserMixin):
    def __init__(self, id, nome, email):
        self.id = id
        self.nome = nome
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email FROM usuarios WHERE id = ?", (user_id,))
    u = cursor.fetchone()
    conn.close()
    if u:
        return User(u[0], u[1], u[2])
    return None

# ================= BANCO =================
def criar_banco():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        data TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        total REAL,
        data TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        telefone TEXT,
        cpf TEXT,
        cep TEXT,
        data TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco REAL,
        quantidade INTEGER
    )
    ''')

    conn.commit()
    conn.close()

criar_banco()

# ================= AUTH =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/dashboard')

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, senha FROM usuarios WHERE email = ?", (email,))
        u = cursor.fetchone()
        conn.close()

        if u and check_password_hash(u[3], senha):
            user = User(u[0], u[1], u[2])
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or '/dashboard')
        else:
            flash('Email ou senha incorretos.')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)
        data = datetime.now().strftime('%d/%m/%Y')

        try:
            conn = sqlite3.connect('banco.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha, data) VALUES (?, ?, ?, ?)",
                (nome, email, senha_hash, data)
            )
            conn.commit()
            conn.close()
            flash('✅ Conta criada com sucesso! Faça login.')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('❌ Este email já está cadastrado.')

    return render_template('registrar.html')


# ================= HOME =================
@app.route('/')
@login_required
def home():
    return redirect('/dashboard')


# ================= CLIENTES =================
@app.route('/clientes')
@login_required
def clientes():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=dados)


@app.route('/add_cliente', methods=['POST'])
@login_required
def add_cliente():
    nome = request.form['nome']
    telefone = request.form['telefone']
    cpf = request.form['cpf']
    cep = request.form['cep']
    data = datetime.now().strftime('%d/%m/%Y')

    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nome, telefone, cpf, cep, data) VALUES (?, ?, ?, ?, ?)",
        (nome, telefone, cpf, cep, data)
    )
    conn.commit()
    conn.close()
    return redirect('/clientes')


@app.route('/clientes_lista')
@login_required
def clientes_lista():
    busca = request.args.get('busca', '')
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    if busca:
        cursor.execute("SELECT * FROM clientes WHERE nome LIKE ?", ('%' + busca + '%',))
    else:
        cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()
    conn.close()
    return render_template('clientes_lista.html', clientes=dados, busca=busca)


# ================= PRODUTOS =================
@app.route('/produtos')
@login_required
def produtos():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    dados = cursor.fetchall()
    conn.close()
    return render_template('produtos.html', produtos=dados)


@app.route('/add_produto', methods=['POST'])
@login_required
def add_produto():
    nome = request.form['nome']
    preco = request.form['preco']
    quantidade = request.form['quantidade']

    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
        (nome, preco, quantidade)
    )
    conn.commit()
    conn.close()
    return redirect('/produtos')


@app.route('/estoque')
@login_required
def estoque():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    dados = cursor.fetchall()
    conn.close()
    return render_template('estoque.html', produtos=dados)


# ================= VENDAS =================
@app.route('/vendas')
@login_required
def vendas():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return render_template('vendas.html', clientes=clientes, produtos=produtos)


@app.route('/add_venda', methods=['POST'])
@login_required
def add_venda():
    cliente_id = request.form['cliente']
    produto_id = request.form['produto']
    quantidade = int(request.form['quantidade'])

    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("SELECT preco, quantidade FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()

    preco = produto[0]
    estoque = produto[1]

    if quantidade > estoque:
        conn.close()
        flash("❌ Não tem estoque suficiente!")
        return redirect('/vendas')

    total = preco * quantidade
    novo_estoque = estoque - quantidade
    data = datetime.now().strftime('%d/%m/%Y %H:%M')

    cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (novo_estoque, produto_id))
    cursor.execute(
        "INSERT INTO vendas (cliente_id, produto_id, quantidade, total, data) VALUES (?, ?, ?, ?, ?)",
        (cliente_id, produto_id, quantidade, total, data)
    )
    conn.commit()
    conn.close()

    flash("✅ Venda realizada com sucesso!")
    return redirect('/vendas')


# ================= HISTÓRICO =================
@app.route('/historico')
@login_required
def historico():
    busca = request.args.get('busca', '')
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    if busca:
        cursor.execute('''
            SELECT vendas.id, clientes.nome, produtos.nome, vendas.quantidade, vendas.total, vendas.data
            FROM vendas
            JOIN clientes ON vendas.cliente_id = clientes.id
            JOIN produtos ON vendas.produto_id = produtos.id
            WHERE clientes.nome LIKE ?
        ''', ('%' + busca + '%',))
    else:
        cursor.execute('''
            SELECT vendas.id, clientes.nome, produtos.nome, vendas.quantidade, vendas.total, vendas.data
            FROM vendas
            JOIN clientes ON vendas.cliente_id = clientes.id
            JOIN produtos ON vendas.produto_id = produtos.id
        ''')

    vendas = cursor.fetchall()
    conn.close()
    return render_template('historico.html', vendas=vendas, busca=busca)


# ================= DASHBOARD =================
@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vendas")
    total_vendas = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM vendas")
    faturamento = cursor.fetchone()[0] or 0

    cursor.execute('''
        SELECT SUBSTR(data, 1, 10) as dia, SUM(total)
        FROM vendas
        GROUP BY dia
        ORDER BY SUBSTR(data, 7, 4) || SUBSTR(data, 4, 2) || SUBSTR(data, 1, 2) ASC
    ''')
    dados = cursor.fetchall()
    conn.close()

    datas = [d[0] for d in dados]
    valores = [d[1] for d in dados]

    return render_template(
        'dashboard.html',
        clientes=total_clientes,
        produtos=total_produtos,
        vendas=total_vendas,
        faturamento=float(faturamento),
        datas=datas,
        valores=valores
    )


# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)