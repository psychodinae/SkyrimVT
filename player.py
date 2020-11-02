import json
from math import ceil

from estado import Estado


class Player:
    """Claasse com as acoes possiveis pelo jogador"""

    def __init__(self, orm):
        self.orm = orm

    def respawn(self, nome, local_de_respawn: int):
        """
        jogador renasce.

        :param nome: nome do usuario
        :param local_de_respawn: id do lugar onde ira nascer.
        :return:
        """
        self.orm.update_global(nome, local=local_de_respawn)
        self.orm.update_jogador(nome, vida=100, mana=100)

    def andar(self, nome, comando):
        """
        Metodo principal do Game responsavel por fazer o jogador se movimentar pelas "salas".
        Baseado espiritualmente nisso: https://gamedev.stackexchange.com/a/143536

        :param nome: nome do usuario
        :param str comando: nome abreviado do lugar, para saber quais
         lugares estao disponiveis use o metodo localizar desta Classe.
        :return: A mensagem informando para onde o personagem foi, salva no banco de dados.
        """
        sai = json.loads(self.orm.get_mapa(self.orm.get_global(nome).local).saidas)
        if comando not in sai.keys():
            return 'esse local nao existe! nao o enchergo daqui...'

        self.orm.update_global(nome, local=sai[comando])
        irs = self.orm.get_mapa(self.orm.get_global(nome).local).nome_amigavel.split('|')[0]
        return f'voçê foi para {irs}'

    def localizar(self, nome, comando):
        """
        Mostra a localizacao atual e lugares acessiveis ou informacoes sobre o lugar atual.
        se a o parametro ``info`` mostra a descricao INFO do local.

        :param nome: nome do usuario
        :param str comando: digite "info" para ver informacoes sobre o lugar atual.

        :return: mensagem com a localizacao atual e lugares acessiveis ou info.
        """
        local = self.orm.get_global(nome).local
        if 'info' in comando:
            return f'Descricao do local: {self.orm.get_mapa(local).info}'
        return f'voçê atualmente está {self.orm.get_mapa(local).nome_amigavel.split("|")[1]}. ' + \
               f'Voce pode ir para: {list(json.loads(self.orm.get_mapa(local).saidas).keys())}'

    def inventario(self, nome, comando):
        """
        Mostra o inventario em "paginas".

        Digite  1 ou 2 ou 3 ... para ver o inventario.

        Digite  0 ou -1 ou -2 ... para ver o inventario de tras para  frente ;).
        Se nenhum parametro for passado ira exibir a primeira pagina (caso exista).

        :param nome: nome do usuario
        :param str comando: numero da "pagina" a ser visualizada.

        :return: A "pagina". ex: "inventario: [['tunica_velha', 1, 1], ...] pagina 2 de 2"
                 .Salva no banco de dados.

        :raise IndexError: Se o numero da pagina for maior do que existe.
        :raise ValueError: se for digitado qualquer caractere nao decimal, letras etc...
        """

        bolsa = json.loads(self.orm.get_global(nome).inventario)
        # bolsa = json.loads('[]')
        if not bolsa:
            return 'seu inventario está vazio!'
        size = 5  # ajuste o maximo de items por "pagina" aqui.
        seq = bolsa
        chunk_list = [seq[i * size:(i * size) + size] for i in range(ceil(len(seq) / size))]

        chunk_len = len(chunk_list)

        try:
            if comando:
                com = int(comando) - 1
                try:
                    return f'inventario: {chunk_list[com]} pagina {com + 1} de {len(chunk_list)}'
                except IndexError:
                    return f'seu inventario tem apenas {chunk_len} pagina(s).'
            return f'inventario: {chunk_list[0]} pagina 1 de {chunk_len}'

        except ValueError:
            return 'esse comando nao existe para a opção inventario.'

    def equipar(self, nome, comando):
        """
        Equipa os items do inventario.
        :param nome: nome do usuario
        :param comando: Nome do item a ser equipado ou nome do item a ser equipado mais
        em qual mao (separado por espaco).
        :return: Msg para o jogador. Salva no banco de dados.
        """

        try:
            com, mao = comando.split()
        except ValueError:
            com = comando
            mao = None
        if com:
            usr_glb = self.orm.get_global(nome)
            bolsa = json.loads(usr_glb.inventario)
            slots = json.loads(usr_glb.equipado)
            if any([i[0] == com for i in bolsa]):
                eqp = self.orm.get_item(com).equipa
                if eqp == 'maos':
                    if mao in ['mao_direita', 'mao_esquerda']:
                        slots[mao] = com
                        self.orm.update_global(nome, equipado=json.dumps(slots))
                    else:
                        return f"voce tem que escolher se quer equipar na 'mao_direita' ou 'mao_esquerda'."
                else:
                    if eqp:
                        slots[eqp] = com
                        self.orm.update_global(nome, equipado=json.dumps(slots))
                    else:
                        return 'voce nao pode equipar este item, tente USAR ao inves disso.'
                return f"'{com}' foi equipado"
            return 'esse item não existe. Escreva INVENTARIO para ver o que voce possui.'
        return 'voce nao escreveu qual item do inventario quer equipar.'

    def descartar(self, nome, comando, param=None):
        """
        Descarta os items do inventario.

        :param nome: nome do usuario
        :param param: lista de parametros carregadas do estado_salvo
        :param comando: Nome do item a ser descartado ou nome do item a ser descartado mais
               a quantia.
        :return: Msg para o jogador. Salva no banco de dados.
        """
        if param:
            if comando == 'sim':
                inv = json.dumps(param[0], ensure_ascii=False)
                eqp = json.dumps(param[1], ensure_ascii=False)
                self.orm.update_global(nome, inventario=inv, equipado=eqp)
                Estado(self.orm).limpa_estado(nome)
                return 'item excluido com sucesso!'
            Estado(self.orm).limpa_estado(nome)
            return 'excluir item cancelado'
        try:
            item, quantia = comando.split()
            quantia = int(quantia)
            if int(quantia) < 1:
                return 'zero ou numeros negativos não são aceitos.'
        except ValueError:
            item = comando
            quantia = 1
        if item:
            if self.orm.get_item(item).tipo == 'magia':
                return 'voce nao pode descartar uma magia, o que se aprende nao se esquece...'
            usr_glb = self.orm.get_global(nome)
            bolsa = json.loads(usr_glb.inventario)
            slots = json.loads(usr_glb.equipado)
            if any([i[0] == item for i in bolsa]):
                for k, v in enumerate(bolsa):
                    if v[0] == item:
                        if v[1] > quantia:
                            v[1] -= quantia
                        else:
                            bolsa.pop(k)
                            slots = {key: '' if val == item else val for key, val in slots.items()}
                err_msg = 'voçê estava descartando um item do seu inventario, para cancelar digite: DESCARTAR não'
                Estado(self.orm).seta_estado(nome, 'DESCARTAR', [bolsa, slots], err_msg)
                return 'voçê tem certeza que quer excluir este item, se sim digite: "DESCARTAR sim".'
            return 'esse item não existe no seu inventario. Escreva INVENTARIO para ver o que voce possui'

        return 'voce nao escreveu qual item do inventario quer descartar.'

    def usar(self):
        """TODO: Similar a equipar mas para comsumiveis como pocoes ou para keys/items em missoes.

        ou tarefas ex: em um lugar
        que apos usar o INTERAGIR mostre a opcao "garimpar ouro"

        """

    def interagir(self):
        """
        TODO: similar ao metodo localizar, listara os NPCS
        ou outros players no mesmo local e o comando
        sera o nome do NPC/usuario que ira linkalo por
        exemplo, as classes de comprar/vender nas
        tavernas/ferreiro ou a missoes, exploracoes,
        garimpo etc. A partir desde ponto as coisa comecam
        a ficar complexas e sera necessario salvar o estado,
        para que se possa continuar a interacao atual no
        proximo comando. ja que a ideia e nao ser
        necessario digitar mais de tres comandos para
        interagir com o game.

        E por falar em "salvar o estado" e ai que entra o
        savegame que sera um json salvo no banco de dados
        onde sera configurado cada player: onde sera
        "spawnado" qual missao/interacao/luta/trade/evento
        aleatorio foi salvo no comando anterior, caso nao
        exista o player estara livre paraa andar pelo mapa.
        """

    def atacar(self):
        """
        TODO:
        mesmo esquema de interagir, onde sera inserido o
        sistema de lutas do game. Sera possivel atacar outros
        players ou mobs, no caso do PvP, os player quando
        forem atacados assim que tentarem qualquer  interacao no game serao
        informados e terao a opcao de lutar ou correr dropando um item :) --- ISSO E SO UMA IDEIA.

        Outras formas de interacao PvP seriam em arenas, raca A x raca B seguindo o lore se Skyrim ou coop em dungeons,
        """
        
