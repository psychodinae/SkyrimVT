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
    
    'LOCALIZAR'  ex: <LOCALIZAR> ou <LOCALIZAR info>
    
    'INVENTARIO' ex: <INVENTARIO> ou <INVENTARIO 1> (para navegar pelas paginas)
    
    'EQUIPAR'    ex: <EQUIPAR tunica_velha> ou <EQUIPAR espada_de_ferro mao_direita> (items "seguraveis"
                    tem que escolher em qual mao)
                    
    'DESCARTAR'  ex:  DESCARTAR picareta ou <DESCARTAR poção_fraca 5> (mais a quantidade de items)
    
    """

    try:
        with open('sky.db') as file:
            pass
    except FileNotFoundError:
        Orm('sky.db').criar_db()
        print('DB criado com sucesso!')

    lst = [['dalton', 'LOCALIZAR', ''], ['fox', 'DESCARTAR', 'picareta'], ['psyco', 'EQUIPAR', 'espada_de_ferro mao_esquerda']]

    print(Game('sky.db').inicio(lst))
