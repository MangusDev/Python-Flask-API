from flask import Flask, request, jsonify
import sqlite3

# Criar uma instância da classe Flask
app = Flask(__name__)

# Configuração do banco de dados SQLite
DATABASE = 'database.db'

# Função para conectar ao banco de dados
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

# Função para criar a tabela de dados, se ela não existir
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Rota inicial para explicar o uso da API
@app.route('/')
def home():
    return """
    <h1>Bem-vindo à API CRUD com Flask</h1>
    <p>Esta API permite que você execute operações CRUD (Create, Read, Update, Delete) em uma base de dados SQLite.</p>
    <p>Rotas disponíveis:</p>
    <ul>
        <li>POST /dados - Adiciona um novo dado. Envie um JSON com os campos 'nome' e 'idade'.</li>
        <li>GET /dados - Retorna todos os dados na base de dados.</li>
        <li>GET /dados/{id} - Retorna um dado específico por ID.</li>
        <li>PUT /dados/{id} - Atualiza um dado existente por ID. Envie um JSON com os campos 'nome' e 'idade'.</li>
        <li>DELETE /dados/{id} - Deleta um dado existente por ID.</li>
    </ul>
    """

# Rota para criar a tabela de dados
@app.route('/initdb')
def initialize_database():
    init_db()
    return 'Database initialized'

# Rota para adicionar um novo dado
@app.route('/dados', methods=['POST', 'GET'])
def manage_dados():
    if request.method == 'POST':
        nome = request.json.get('nome')
        idade = request.json.get('idade')

        if not nome or not idade:
            return jsonify({'error': 'Nome e idade são obrigatórios'}), 400

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('INSERT INTO dados (nome, idade) VALUES (?, ?)', (nome, idade))
            db.commit()
            return jsonify({'message': 'Dado gravado com sucesso!'}), 201
        except sqlite3.Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            db.close()
    elif request.method == 'GET':
        return home()

# Rota para obter todos os dados
@app.route('/dados', methods=['GET'])
def get_dados():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM dados')
        dados = cursor.fetchall()
        return jsonify([dict(row) for row in dados])
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# Rota para obter um dado por ID
@app.route('/dados/<int:dado_id>', methods=['GET'])
def get_dado(dado_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM dados WHERE id = ?', (dado_id,))
        dado = cursor.fetchone()
        if dado:
            return jsonify(dict(dado))
        else:
            return jsonify({'error': 'Dado não encontrado'}), 404
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# Rota para atualizar um dado por ID
@app.route('/dados/<int:dado_id>', methods=['PUT'])
def update_dado(dado_id):
    nome = request.json.get('nome')
    idade = request.json.get('idade')

    if not nome or not idade:
        return jsonify({'error': 'Nome e idade são obrigatórios'}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE dados SET nome = ?, idade = ? WHERE id = ?', (nome, idade, dado_id))
        db.commit()
        return jsonify({'message': 'Dado atualizado com sucesso!'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# Rota para deletar um dado por ID
@app.route('/dados/<int:dado_id>', methods=['DELETE'])
def delete_dado(dado_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM dados WHERE id = ?', (dado_id,))
        db.commit()
        return jsonify({'message': 'Dado deletado com sucesso!'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# Iniciar a aplicação Flask
if __name__ == '__main__':
    app.run(debug=True)