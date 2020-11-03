import json
from multiprocessing.dummy import Pool as ThreadPool

from orm import Orm
from player import Player


class Game:
    """
    Game Skyrim MMORPG "online" baseado em "Rooms" para o VT IGN, estilo Zork.

    """
    opcoes = ['ANDAR', 'LOCALIZAR', 'INVENTARIO', 'EQUIPAR', 'DESCARTAR']

    def __init__(self, nome_do_db):
        self.orm = Orm(nome_do_db)
        self.pool = ThreadPool(4)
        self.player = Player(self.orm)
        self.result = None

    def inicio(self, lista_de_entrada):
        """
        inicia o game.

        O nome de usuario é obrigatorio, a acao e comonado sao opcionais porem dever conter uma string
        vazia <''>

        :param lista_de_entrada: o game requer como entrada uma lista de listas que devem obrigatoriamente
         conter 3 items: o nome do USUARIO, a ACAO e o COMANDO.
        :return:
        """
        self.result = self.pool.map(self.check, lista_de_entrada)
        self.orm.save()
        self.orm.close()
        return self.result

    def formata(self, usuario, texto):
        return f'@{usuario} {texto}'

    def check(self, user):
        nome, acao, comando = user
        em_qust, estado_salvo = self.orm.get_global_estado(nome)
        if acao in self.opcoes:
            if em_qust:
                save = json.loads(estado_salvo)
                if acao == save['quest']:
                    return self.formata(nome, getattr(self.player, acao.lower())(nome, comando, save['parametros']))
                return self.formata(nome, save['msg_de_erro'])
            return self.formata(nome, getattr(self.player, acao.lower())(nome, comando))
        return self.formata(nome, 'esse comando não existe, não entendi...')


if __name__ == '__main__':
    """
    * locais existentes no momento:
    
    1. reino
    2. portao_do_reino
    3. castelo
    4. estabulo
    5. caverna_sombria
    
    
    * comandos existentes no momento:
    
    'ANDAR'      ex: <ANDAR castelo>
                 retorna:
                 >>>'@dalton voçê foi para o Castelo Dragonsreach'
    
    
    'LOCALIZAR'  ex: <LOCALIZAR> ou <LOCALIZAR info>
                 retorna:
                 >>>"@dalton voçê atualmente está no Reino Whiterun. Voce pode ir para: ['portao_do_reino', 'castelo']"
                    
                 ou <LOCALIZAR info>
                 retorna:
                 >>>'@dalton Descricao do local: Whiterun é uma das nove principais cidades da província de Skyrim'
                
       
    'INVENTARIO' ex: <INVENTARIO>
                 retorna:
                 >>>"@dalton inventario: [['ouro', 50, 1], ['poção_fraca', 5, 1], ['espada_de_ferro', 1, 1], 
                        ['poção_magia_simples', 5, 1], ['picareta', 1, 1]] PAGINA 1 de 2"
                        
                ou <INVENTARIO 1> (para navegar pelas paginas)
                retorna:
                >>>"@dalton inventario: [['tunica_velha', 1, 1], ['calça_velha', 1, 1], ['botas_velhas', 1, 1], 
                                         ['capuz_ordinario', 1, 1]] PAGINA 2 de 2"
                 
    
    'EQUIPAR'    ex: <EQUIPAR tunica_velha> ou <EQUIPAR espada_de_ferro mao_direita> (items "seguraveis"  tem que 
                     escolher em qual mao).
                 retorna:
                 >>>"@psyco 'espada_de_ferro' foi equipado"
                    
    'DESCARTAR'  ex:  DESCARTAR picareta ou <DESCARTAR poção_fraca 5> (mais a quantidade de items)
                 retorna:
                 >>>'@fox voçê tem certeza que quer excluir este item, se sim digite: "DESCARTAR sim"
                 
                 se o proximo comando for <DESCARTAR sim> deleta o item do inventario e obviamente se o usuario
                 estiver equipadando e nao tiver outros iguais ira desequipa-lo.
                 Qualquer outro comando ira cancelar a operacao.
    
    """

    try:
        with open('sky.db') as file:
            pass
    except FileNotFoundError:
        Orm('sky.db').criar_db()
        print('DB criado com sucesso!')

    lst = [['dalton', 'LOCALIZAR', '2'], ['fox', 'DESCARTAR', 'picareta'], ['psyco', 'EQUIPAR', 'espada_de_ferro mao_esquerda']]

    print(Game('sky.db').inicio(lst))
    # retorna:
    # >>> ["@dalton voçê atualmente está no Reino Whiterun. Voce pode ir para: ['portao_do_reino', 'castelo']", '@fox voçê tem certeza que quer excluir este item, se sim digite: "DESCARTAR sim".', "@psyco 'espada_de_ferro' foi equipado"]
