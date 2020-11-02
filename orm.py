import sqlite3
import models


class Orm:
    def __init__(self, nome_database):
        self.con = sqlite3.connect(nome_database, check_same_thread=False)
        self.con.execute('begin')  # corrige erro "transaction" https://stackoverflow.com/a/23634805/12651034

    def save(self):
        self.con.commit()

    def close(self):
        self.con.close()

    # global
    def get_global(self, username: str):
        glob = self.con.execute("select * from global where usuario=?", (username,)).fetchone()
        return models.Global(*glob)

    def get_global_estado(self, usuario):
        return self.con.execute("select em_quest, estado_salvo from global where usuario=?", (usuario,)).fetchone()

    def update_global(self, usuario, local=None, inventario=None, equipado=None, em_quest=None, estado_salvo=None,
                      timestamp=None):
        sql = """update global set
                 local=ifnull(?, local),
                 inventario=ifnull(?, inventario),
                 equipado=ifnull(?, equipado),
                 em_quest=ifnull(?, em_quest),
                 estado_salvo=ifnull(?, estado_salvo),
                 timestamp=ifnull(?, timestamp)
                 where usuario= ?"""
        self.con.execute(sql, (local, inventario, equipado, em_quest, estado_salvo, timestamp, usuario))

    # mapa
    def get_mapa(self, idx):
        loc = self.con.execute("select * from mapa where id=?", (idx,)).fetchone()
        return models.Mapa(*loc)

    # items
    def get_item(self, nome):
        items = self.con.execute("select * from items where nome=?", (nome,)).fetchone()
        return models.Items(*items)

    # jogador
    def get_jogador(self, username):
        usr = self.con.execute("select * from jogador where usuario=?", (username,)).fetchone()
        return models.Jogador(*usr)

    def update_jogador(self, usuario, level=None, vida=None, mana=None):
        sql = """update jogador set 
                 level=ifnull(?, level),
                 vida=ifnull(?, vida),
                 mana=ifnull(?, mana)
                 where usuario= ?"""
        self.con.execute(sql, (level, vida, mana, usuario))

    def criar_db(self):
        """cria o db default"""

        self.con.executescript("""
    create table if not exists jogador(
        usuario text primary key,
        level integer not null,
        vida integer not null,
        mana integer not null
    );

    create table if not exists items(
        nome text primary key,
        tipo text not null,
        equipa text not null,
        info text not null,
        valor integer not null,
        peso integer not null,
        restaura_vida integer not null,
        restaura_magia integer not null,
        dano integer not null,
        escudo integer not null

    );

    create table if not exists global(
        usuario text primary key,
        local integer not null,
        inventario text not null,
        equipado text not null,
        em_quest integer not null,
        estado_salvo text not null,
        timestamp integer not null
    );

    create table if not exists mapa(
        id integer primary key,
        nome_do_local text not null,
        nome_amigavel text not null,
        info text not null,
        saidas text not null
    );

    insert into mapa(id, nome_do_local, nome_amigavel, info, saidas)
    values(
        1,
        'Reino Xis',
        'o Reino Xis|no Reino Xis',
        'Grandioso reino de xis, lar dos nordicos belos e morais',
        '{"portao_do_reino": 2, "castelo": 3}'
    );

    insert into mapa(id, nome_do_local, nome_amigavel, info, saidas)
    values(
        2,
        'Portao pricipal do Reino Xis',
        'o Portao pricipal do Reino Xis|no Portao pricipal do Reino Xis',
        'Portao de acesso ao reino Xis, daqui é possivel ver a imponencia das muralhas que cercam o Castelo',
        '{"reino": 1, "estabulo": 4, "caverna_sombria": 5}'
    );

    insert into mapa(id, nome_do_local, nome_amigavel, info, saidas)
    values(
        3,
        'Castelo do rei Xisto',
        'o Castelo do rei Xisto|no Castelo do rei Xisto',
        'Castelo do rei xisto, O quente',
        '{"reino": 1}'

    );

    insert into mapa(id, nome_do_local, nome_amigavel, info, saidas)
    values(
       4,
       'Estabulo',
       'o Estabulo|no estabulo',
       'aqui vc pode comprar seu primeiro cavalo, se tiver 1000 dols ',
       '{"portao_do_reino": 2}'

    );

    insert into mapa(id, nome_do_local, nome_amigavel, info, saidas)
    values(
       5,
       'Caverna Sombria',
       'a Caverna Sombria|na Caverna sombria',
       'Essa é a primeira dungeon, dizem que aqui tem ouro, traga sua piraceta e sua espada...',
       '{"portao_do_reino": 2}'

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
       'ouro',
       'comsumivel',
       '',
       'Dinheiro do jogo, em tempos de instabilidade invista em ouro.',
       1,
       0,
       0,
       0,
       0,
       0

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
       'poção_fraca',
       'comsumivel',
       '',
       'Restaura a vida.',
       3,
       1,
       10,
       0,
       0,
       0

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
       'poção_magia_fraca',
       'comsumivel',
       '',
       'Restaura a magia.',
       3,
       1,
       0,
       10,
       0,
       0

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
        'restaurar_simples',
        'magia',
        'maos',
        'Arte arcana basica de cura. restaura a vida ao custo de magia.',
        0,
        0,
        5,
        0,
        0,
        0

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
        'restaurar_magica_simples',
        'magia',
        'maos',
        'Arte arcana basica para restaurar magia, cuidado! restaura a magia ao custo de vida.',
        0,
        0,
        0,
        5,
        0,
        0

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
        'magia_labareda',
        'magia',
        'maos',
        'Magia de nivel iniciante.',
        0,
        0,
        0,
        0,
        3,
        0

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
       'espada_de_ferro',
       'arma',
       'maos',
       'Uma Espada de ferro, pesada e não muito afiada.',
       5,
       7,
       0,
       0,
       3,
       0

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
        'escudo_de_madeira',
        'equipavel',
        'maos',
        'Fragil mas serve, se fizer muito frio posso usa-lo para fazer uma fogueira.',
        4,
        3,
        0,
        0,
        0,
        3

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
        'tunica_velha',
        'equipavel',
        'torso',
        'Camisa desgastada e com remendos.',
        1,
        2,
        0,
        0,
        0,
        1

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
        'calça_velha',
        'equipavel',
        'pernas',
        'Calça desgastada e com remendos.',
        1,
        2,
        0,
        0,
        0,
        1

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
        'botas_velhas',
        'equipavel',
        'pes',
        'Bastante desgastada mas quebram o galho.',
        3,
        2,
        0,
        0,
        0,
        1

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
        'picareta',
        'equipavel',
        'maos',
        'Usada no garimpo de pedras preciosas.',
        3,
        5,
        0,
        0,
        0,
        0

    );

    insert into items(nome, tipo, equipa, info, valor, peso, restaura_vida, restaura_magia, dano, escudo)
    values(
        'capuz_ordinario',
        'equipavel',
        'cabeca',
        'Proteje do frio apenas.',
        1,
        1,
        0,
        0,
        0,
        1

    );

    insert into jogador(usuario, level, vida, mana)
    values(
        'psyco',
        31,
        85,
        100
    );

    insert into global(usuario, local, inventario, equipado, em_quest, estado_salvo, timestamp)
    values(
        'psyco',
        1,
        '[["ouro", 50, 1], ["poção_fraca", 5, 1], ["espada_de_ferro", 1, 1], ["poção_magia_simples", 5, 1], ["picareta", 1, 1], ["tunica_velha", 1, 1], ["calça_velha", 1, 1], ["botas_velhas", 1, 1], ["capuz_ordinario", 1, 1]]',
        '{"cabeca": "", "torso": "", "mao_direita": "", "mao_esquerda": "", "pernas": "", "pes": ""}',
        0,
        '{}',
        4677654475
    );

    insert into jogador(usuario, level, vida, mana)
    values(
        'fox',
        10,
        20,
        30
    );

    insert into global(usuario, local, inventario, equipado, em_quest, estado_salvo, timestamp)
    values(
        'fox',
        5,
        '[["ouro", 50, 1], ["poção_fraca", 5, 1], ["espada_de_ferro", 1, 1], ["poção_magia_simples", 5, 1], ["picareta", 1, 1], ["tunica_velha", 1, 1], ["calça_velha", 1, 1], ["botas_velhas", 1, 1], ["capuz_ordinario", 1, 1]]',
        '{"cabeca": "", "torso": "", "mao_direita": "", "mao_esquerda": "", "pernas": "", "pes": ""}',
        0,
        '{}',
        1231231231
    );

    insert into jogador(usuario, level, vida, mana)
    values(
        'dalton',
        66,
        6,
        7
    );


    insert into global(usuario, local, inventario, equipado, em_quest, estado_salvo, timestamp)
    values(
        'dalton',
        4,
        '[["ouro", 50, 1], ["poção_fraca", 5, 1], ["espada_de_ferro", 1, 1], ["poção_magia_simples", 5, 1], ["picareta", 1, 1], ["tunica_velha", 1, 1], ["calça_velha", 1, 1], ["botas_velhas", 1, 1], ["capuz_ordinario", 1, 1]]',
        '{"cabeca": "", "torso": "", "mao_direita": "", "mao_esquerda": "", "pernas": "", "pes": ""}',
        0,
        '{}',
        7777777777
    );

    """)


if __name__ == '__main__':
    o = Orm('sky.db')
    o.criar_db()
    print('DB criado com sucesso!')
