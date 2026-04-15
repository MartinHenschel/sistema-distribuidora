from flask import Flask, render_template, request, redirect, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = '123'

# ================= BANCO =================
def criar_banco():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    # tabela vendas
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

    # tabela clientes
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

    # tabela produtos
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

# ================= HOME =================
@app.route('/')
def home():
    return render_template('index.html')


# ================= CLIENTES =================
@app.route('/clientes')
def clientes():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()

    conn.close()

    return render_template('clientes.html', clientes=dados, modo='simples')


@app.route('/add_cliente', methods=['POST'])
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


# 🔍 CLIENTES COM BUSCA (APENAS UMA ROTA)
@app.route('/clientes_lista')
def clientes_lista():
    busca = request.args.get('busca', '')

    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    if busca:
        cursor.execute(
            "SELECT * FROM clientes WHERE nome LIKE ?",
            ('%' + busca + '%',)
        )
    else:
        cursor.execute("SELECT * FROM clientes")

    dados = cursor.fetchall()
    conn.close()

    return render_template('clientes_lista.html', clientes=dados, busca=busca, modo='simples')


# ================= PRODUTOS =================
@app.route('/produtos')
def produtos():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produtos")
    dados = cursor.fetchall()

    conn.close()

    return render_template('produtos.html', produtos=dados, modo='simples')


@app.route('/add_produto', methods=['POST'])
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
def estoque():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produtos")
    dados = cursor.fetchall()

    conn.close()

    return render_template('estoque.html', produtos=dados, modo='simples')


# ================= VENDAS =================
@app.route('/vendas')
def vendas():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    conn.close()

    return render_template('vendas.html', clientes=clientes, produtos=produtos, modo='simples')


@app.route('/add_venda', methods=['POST'])
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

    cursor.execute(
        "UPDATE produtos SET quantidade = ? WHERE id = ?",
        (novo_estoque, produto_id)
    )

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

    return render_template('historico.html', vendas=vendas, busca=busca, modo='simples')

@app.route('/dashboard')
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
    faturamento = cursor.fetchone()[0] or 0  # ✅ já está correto

    # ✅ Corrigido: converte DD/MM/YYYY para YYYY/MM/DD só para ordenar
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
        faturamento=float(faturamento),  # ✅ garante que é float, nunca None
        datas=datas,
        valores=valores
    )
# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)