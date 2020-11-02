import json


class Estado:
    """
    cria o "savegame".
    """

    def __init__(self, orm):
        self.orm = orm

    def limpa_estado(self, nome):
        self.orm.update_global(nome, em_quest=0, estado_salvo='{}')

    def seta_estado(self, nome, quest, parametros=None, msg=''):
        if parametros is None:
            parametros = []
        dict_to_json = json.dumps({'quest': quest, 'parametros': parametros, 'msg_de_erro': msg}, ensure_ascii=False)
        self.orm.update_global(nome, em_quest=1, estado_salvo=dict_to_json)


if __name__ == '__main__':
    pass
    # o = Orm('sky.db')
    # e = Estado(o)
    # nomex = 'psyco'
    # e.seta_estado(nomex, 'DESCARTAR', ['bota_velha', 1], 'vc estava descartando um item do seu inventario, para cancelar digite: DESCARTAR não')
    # e.limpa_estado(nomex)
    # o.close()
