from flask import Flask, jsonify, request, send_file
from main import app, con
from functions import *
import fpdf

@app.route('/listar_livro', methods=['GET'])
def listar_livro():
    try:
        cur = con.cursor()
        cur.execute('select id_livro, titulo, autor, ano_publicacao from livros')
        livros = cur.fetchall()

        livros_lista = []
        for livro in livros:
            livros_lista.append({
                'id_livro' : livro[0]
                , 'titulo' : livro[1]
                , 'autor'  : livro[2]
                ,  'ano_publicacao': livro[3]
            })

        return jsonify(mensagem= "lista de livros", livros=livros_lista)

    except Exception as e:
        return jsonify({"message" : f"Erro ao consultar bancos de dados: {e}"}), 500
    finally:
        cur.close()



@app.route('/criar_livro',methods=['POST'])
def criar_livro():
    try:
        dados = request.get_json()
        titulo = dados.get('titulo')
        autor = dados.get('autor')
        ano_publicacao = dados.get('ano_publicacao')

        cur = con.cursor()

        cur.execute('SELECT 1 from livros where titulo = ?', (titulo,))
        if cur.fetchone():
            return jsonify({'livro ja cafastrado'}), 400

        cur.execute(""" INSERT into LIVROS(titulo, autor, ano_publicacao)
                        values(?, ?, ?) """, (titulo, autor, ano_publicacao))

        con.commit()
        return jsonify({"message:": "livro cadastrado com sucesso",
                       'livro': {
                        "titulo" : titulo,
                        "autor" : autor,
                        "ano_publicacao" : ano_publicacao}}), 201

    except Exception as e:
        return jsonify({"message": f"Erro ao consultar bancos de dados: {e}"}), 500
    finally:
        cur.close()


@app.route('/editar_livro/<int:id>', methods=['PUT'])
def editar_livro(id):
    try:
        cur = con.cursor()
        cur.execute('SELECT id_livro, titulo, autor, ano_publicacao FROM livros where id_livro = ?', (id,))
        tem_livro = cur.fetchone()

        if not tem_livro:
            cur.close()
            return jsonify({'ERROR': "Livro não encontrado"}),404

        dados = request.get_json()
        titulo= dados.get('titulo')
        autor = dados.get('autor')
        ano_publicacao = dados.get('ano_publicacao')

        cur.execute("""
            UPDATE LIVROS SET TITULO = ?, AUTOR = ?, ANO_PUBLICACAO = ? WHERE ID_LIVRO = ?
        """, (titulo, autor, ano_publicacao, id))

        con.commit()
        return jsonify({"mensagem": "Livro atualizado",
                        "livro": {"Id_livro " :id,"Titulo": titulo,"Autor": autor,"Ano Publicacao": ano_publicacao}})
    except Exception as e:
        return jsonify({"message": f"Erro ao consultar bancos de dados: {e}"}), 500
    finally:
        cur.close()




@app.route('/deletar_livro/<int:id>', methods=['DELETE'])
def deletar_livro(id):
    try:
        cur = con.cursor()
        cur.execute('SELECT 1 from livros where id_livro = ?', (id,))
        tem_livro = cur.fetchone()

        if not tem_livro:
            cur.close()
            return jsonify({'ERROR': "Livro não encontrado"}),404

        cur.execute('DELETE FROM LIVROS WHERE ID_LIVRO = ?',(id,))

        con.commit()
        return jsonify({"mesagem":'Livro deletado',
                        "id_livro": id })

    except Exception as e:
        return jsonify({"message": f"Erro ao consultar bancos de dados: {e}"}), 500
    finally:
        cur.close()

@app.route("/cadastro", methods=['POST'])
def cadastro():
    try:
        dados = request.get_json()
        nome = dados.get('nome')
        senha = dados.get('senha')
        email = dados.get('email')

        cur = con.cursor()
        cur.execute("SELECT 1 from USUARIO WHERE EMAIL = ? ", (email,))
        if cur.fetchone():
            return jsonify({'Usuario já exitente'}), 400

        senha_c = validar_senha(senha)


        cur.execute("""INSERT into USUARIO(NOME, SENHA, EMAIL) VALUES(?,?,?)""",
                    (nome, senha_c, email))

        con.commit()
        return jsonify({"mensage":"Cadastro feito com sucesso", "nome": nome, "email": email, "senha": senha})

    except Exception as e:
        return jsonify({"message": f"Erro ao cadastrar usuario: {e}"}), 500
    finally:
        cur.close()


@app.route("/login", methods=["POST"])
def login():
    try:
        dados = request.get_json()
        senha = dados.get('senha')
        email = dados.get('email')

        cur = con.cursor()

        cur.execute('select usuario.senha, usuario.email from usuario where email = ?', (email,))
        usuario = cur.fetchone()

        if usuario:
            if check_password_hash(usuario[0], senha):
                return jsonify({"message":"Login feito com suucesso"})
            else:
                return jsonify({"error":"Senha errada, tente outra senha"})
        else:
            return jsonify({"error":"Usuario não encontrado"})

    except Exception as e:
        return jsonify({"message": f"Erro ao logar o usuario: {e}"}), 500
    finally:
        cur.close()

@app.route("/editar_user/<int:id>", methods=["PUT"])
def editar_user(id):
    try:
        dados = request.get_json()
        nome = dados.get('nome')
        senha = dados.get('senha')
        email = dados.get('email')

        cur = con.cursor()

        cur.execute("select u.nome, u.senha, u.email from usuario u where email = ?", (email,))
        tem_user = cur.fetchone()

        if not tem_user:
            return jsonify({"error":"Usuario não encontrado"})



        cur.execute("update usuario set nome = ?, email = ?", (nome, email))
        con.commit()
        return jsonify({"mensage": "Usuario autlizado", "nome": nome, "email":email})
    except Exception as e:
        return jsonify({"message": f"Erro ao editar o usuario: {e}"}), 500
    finally:
        cur.close()


@app.route("/deletar_usuario/<int:id>", methods=["DELETE"])
def deletar_usuario(id):
    try:
        dados= request.get_json()
        email = dados.get('email')

        cur = con.cursor()

        cur.execute("SELECT 1 from USUARIO WHERE EMAIL = ? ", (email,))
        if not cur.fetchone():
            return jsonify({'Usuario não exitente'}), 400

        cur.execute("DELETE FROM USUARIO WHERE EMAIL = ?", (email,))
        con.commit()
        return jsonify({"message": "Usuario excluido com suucesso"})

    except Exception as e:
        return jsonify({"message": f"Erro ao excluir o usuario: {e}"}), 500
    finally:
        cur.close()

@app.route("/enviar_livo_pdf", methods=["GET"])
def enviar_livro_pdf():
    try:
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15, style='B')
        pdf.cell(200, 10, txt="Meus livros", ln=True)

        cur = con.cursor()
        cur.execute("select l.titulo, l.autor, l.ano_publicacao from livros l ")
        livros = cur.fetchall()

        pdf.set_font("Arial", size=12)

        for livros in livros:
            pdf.cell(200, 10, txt=f"Título: {livros[0]}", ln=True)
            pdf.cell(200, 10, txt=f"Autor: {livros[1]}", ln=True)
            pdf.cell(200, 10, txt=f"Ano de Publicação: {livros[2]}", ln=True)

        pdf.output("livros.pdf")

        return jsonify({"Message":"Pdf gerado com suucesso"})
    except Exception as e:
        return jsonify({"message": f"Erro ao gerar o pdf: {e}"}), 500
    finally:
        con.close()
