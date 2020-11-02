from dataclasses import dataclass


@dataclass
class Global:
    usuario: str
    local: int
    inventario: str
    equipado: str
    em_quest: str
    estado_salvo: str
    timestamp: int


@dataclass
class Mapa:
    id: int
    nome_do_local: str
    nome_amigavel: str
    info: str
    saidas: str


@dataclass
class Items:
    nome: str
    tipo: str
    equipa: str
    info: str
    valor: int
    peso: int
    restaura_vida: int
    restaura_magia: int
    dano: int
    escudo: int


@dataclass
class Jogador:
    usuario: str
    level: int
    vida: int
    mana: int
