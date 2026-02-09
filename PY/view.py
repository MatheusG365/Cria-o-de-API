from flask import Flask, jsonify, request
from main import app, con

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