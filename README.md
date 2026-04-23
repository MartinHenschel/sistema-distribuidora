# 📦 Sistema de Distribuidora

Sistema web completo para gerenciamento de uma distribuidora, desenvolvido com **Python + Flask**. Permite controlar clientes, produtos, estoque, vendas e visualizar dados no dashboard.

---

## 🖥️ Demonstração

> Dashboard com gráfico de faturamento por dia

![Dashboard](https://i.imgur.com/g1uNjqe.png)



---

## ✅ Funcionalidades

- 🔐 **Autenticação** — login, cadastro e logout com senha criptografada
- 👤 **Clientes** — cadastro e listagem com busca
- 📦 **Produtos** — cadastro e controle de estoque
- 🧾 **Vendas** — registro de vendas com baixa automática no estoque
- 📊 **Dashboard** — visão geral com cards e gráfico de faturamento por dia
- 📋 **Histórico** — listagem de vendas com filtro por cliente

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3 | Linguagem principal |
| Flask | Framework web |
| Flask-Login | Autenticação de usuários |
| Werkzeug | Criptografia de senhas |
| SQLite | Banco de dados |
| Chart.js | Gráfico no dashboard |
| HTML/CSS | Interface (sem frameworks externos) |

---

## 🚀 Como rodar localmente

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

**2. Crie e ative um ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install flask flask-login werkzeug
```

**4. Rode o projeto**
```bash
python app.py
```

**5. Acesse no navegador**
```
http://localhost:5000
```

> Na primeira vez, crie uma conta em `/registrar` e faça login.

---

## 📁 Estrutura do Projeto

```
📦 sistema-distribuidora/
├── app.py                  # Rotas e lógica principal
├── banco.db                # Banco de dados SQLite (gerado automaticamente)
├── templates/
│   ├── base.html           # Layout base com sidebar
│   ├── login.html          # Tela de login
│   ├── registrar.html      # Tela de cadastro
│   ├── dashboard.html      # Dashboard com gráfico
│   ├── clientes.html       # Cadastro de clientes
│   ├── clientes_lista.html # Listagem de clientes
│   ├── produtos.html       # Cadastro de produtos
│   ├── estoque.html        # Listagem do estoque
│   ├── vendas.html         # Registro de vendas
│   └── historico.html      # Histórico de vendas
└── static/
    └── style.css           # Estilos globais
```

---

