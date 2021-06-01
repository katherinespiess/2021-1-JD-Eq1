from tracery import Grammar

from random import choice, sample, randint
from abc import ABC, abstractproperty

from typing import NamedTuple, Mapping, Union, Dict, List, Callable, Any, Tuple
from typing import Optional, Set, Iterable

from functools import partial, lru_cache
from itertools import chain
from collections import defaultdict

from .. import datamodels


class GrammerMakebla(ABC):
    RAW_GRAMMAR_TYPE = Dict[str, Union[str, List[str]]]

    @abstractproperty
    def base_description(self) -> str:
        return super().base_description

    @abstractproperty
    def context(self) -> 'Context':
        return super().context

    @abstractproperty
    def raw_grammar(self) -> RAW_GRAMMAR_TYPE:
        pass

    @property
    @lru_cache
    def grammar(self) -> Grammar:
        g = Grammar(self.raw_grammar)
        g.add_modifiers(self.context.make_modifires(g))
        return g

    
    def describe(self) -> str:
        desc = self.grammar.flatten(self.base_description)
        return desc.replace('\n', ' ').replace('  ', ' ').replace(' .', '.').strip()


_MONSTER_NAME = {
        'main' : ['#part#'*i for i in range(2,5)],
        'part': ['#sub_a#', '#sub_b##sub_a#'],
        'sub_a': '#a_vog##a_con#',
        'a_vog': ['a', 'e', 'i', 'o', 'u'],
        'a_con': ['l', 'z', 'k', 'w', 'm', 'n'],
        'sub_b': ['ch', 'x', 'k', 'd', 'm', 't', 'tr', 'th'],
        }


def monster_names() -> str:
    g = Grammar(_MONSTER_NAME)
    while True:
        yield g.flatten('#main#')


_INTRO_LETTER = {
            'main': ['#l1#. #l2#.', '#l2#. #l1#.'],
            'l1': [
                '#peço_desculpas# #pedindo#, #interlocutor#, #final#',
                '#interlocutor#, #peço_desculpas# #pedindo#, #final#',
                '#peço_desculpas# #pedindo#, #final#, #interlocutor#'],
            'interlocutor': ['meu #velho# #amigo#', '#velho# #amigo#', 'meu #amigo#'],
            'peço_desculpas': ['eu #peço_desculpas_multi#', 'eu #peço_desculpas_multi#, #peço_desculpas_multi#'],
            'peço_desculpas_multi': ['peço perdão', 'sinto muito', 'peço desculpas'],
            'pedindo': ['por estar te pedindo tanto', 'por ter que te pedir tanto', 'por deixar em teus ombros tal tarefa'],
            'amigo': ['amigo', 'companheiro'],
            'velho': ['velho', 'bom', 'saudoso', 'grande'],
            'há': ['há', 'tenho', 'sei'],
            'pedir': ['pedir', 'recorrer'],
            'final': ['mas não #há# mais a quem #pedir#', 'mas tenho de fazê-lo'],
            'l2': [
                'um #grade_erro# #foi_cometido#, e eu #não_posso# de #resolvê-lo#',
                '#foi_cometido# um #grade_erro#, e eu #não_posso# de #resolvê-lo#'
                ],
            'não_posso': ['não sou mais capaz', 'não posso mais', 'sou incapaz'],
            'resolvê-lo': ['resolvê-lo', 'corrigi-lo', 'fazê-lo correto', 'resolver ele', 'corrigir ele', 'desfazer ele', 'desfazê-lo'],
            'grade_erro': ['#grande# #erro#', '#erro# #grande#'],
            'grande': ['grande', 'terrível', 'fatal', 'horroroso'],
            'erro': ['erro', 'pecado', 'desacerto'],
            'foi_cometido': ['foi cometido', 'aconteceu', 'cometeu-se', 'veio a ser'],
        }


def intro_letter() -> str:
    g = Grammar(_INTRO_LETTER)
    while True:
        yield g.flatten('#main#')


_LOCATION_NAMES = {
            'main': ['#name#', '#prefix# #name#', '#name# #sufix#', '#prefix# #name# #sufix#'],
            'prefix': ['new', 'van'],
            'sufix': ['#direction#', '#altura#'],
            'direction': ['do sul', 'do norte', 'ocidental', 'oriental'],
            'altura': ['baixo', 'alto'],
            'name': '#start##silaba##end#',
            'start': ['h#vogal#', 'k#vogal#', '#vogal#', '#silaba#'],
            'end': ['', 'm', 'n', 'd', 'h'],
            'silaba': ['#silaba##silaba#', '#consoante##vogal#', '#consoante##end##vogal#', '#consoante##vogal#', '#consoante##vogal#'],
            'vogal': ['a', 'e', 'i', 'o', 'u'],
            'consoante': ['ff', 't', 'd', 'rr', 'c', 't', 'j', 'l', 'b', 'c', 'd', 'f', 'j', 'l', 'p', 'q', 'r', 's', 'v']
        }


def location_names() -> str:
    g = Grammar(_LOCATION_NAMES)
    while True:
        yield g.flatten('#main#')

class Substantive(NamedTuple):
    word: str
    o: str
    um: str

    def raw(self, prefix, context=None):
        rw = {
                f'{prefix}': self.word,
                f'{prefix}_o': self.o,
                f'{prefix}_um': self.um,
                }
        if context:
            context._register_norepeat_map(set(rw.values()))
        return rw

    @classmethod
    def make_male(cls, word):
        return cls(word, 'o', 'um')

    @classmethod
    def make_female(cls, word):
        return cls(word, 'a', 'uma')


class Adjective(NamedTuple):
    m: str
    ms: str
    f: str
    fs: str

    @classmethod
    def make(cls, rad=None, m=None, ms=None, f=None, fs=None):
        return Adjective(
                m = f'{rad}o' if m is None else m,
                ms = f'{rad}os' if ms is None else ms,
                f = f'{rad}a' if f is None else f,
                fs = f'{rad}as' if fs is None else fs
                )

    @classmethod
    def make_agender(cls, rad, rad_s=None, same=False):
        if same:
            rad_s = rad
        elif rad_s is None:
            rad_s = f'{rad}s'
        return Adjective(rad, rad_s, rad, rad_s)
    

    @classmethod
    def make_format(cls, _format, m='o', ms='os', f='a', fs='as'):
        return Adjective(_format(m), _format(ms), _format(f), _format(fs))


class _Flavor(NamedTuple):
    adjectives: Tuple['Adjective'] = tuple()

    def raw(self, adj = 'adjetivo', context=None):
        m  = []
        ms = []
        f  = []
        fs = []

        for a in self.adjectives:
            m.append(a.m)
            ms.append(a.ms)
            f.append(a.f)
            fs.append(a.fs)
            if context:
                context._register_norepeat_map(set(a))
                
        rw = {
                f'{adj}_o':  m,
                f'{adj}_os': ms,
                f'{adj}_a':  f,
                f'{adj}_as': fs
                }
        return rw

    @classmethod
    @lru_cache
    def join(cls, a, b, *c):
        new = cls(a.adjectives + b.adjectives)
        if c:
            return cls.join(new, *c)
        else:
            return new


_MAP_FLAVOR_LIST = (
        _Flavor((
            Adjective.make('decrépit'),
            Adjective.make('decaíd'),
            Adjective.make('abandonad'),
            Adjective.make('descuidad'),
            Adjective.make('maltratad'),
            Adjective.make('castigad'))),
        _Flavor((
            Adjective.make('sombri'),
            Adjective.make('escur'),
            Adjective.make('mal iluminad'),
            Adjective.make('obscur'),
            Adjective.make_agender('fúnebre'))),
        _Flavor((
            Adjective.make('gótic'),
            Adjective.make('melancólic'),
            Adjective.make_agender('triste'),
            Adjective.make_agender('sufocante'))),
        _Flavor((
            Adjective.make('isolad'),
            Adjective.make('solitári'),
            Adjective.make_agender('só'))),
        _Flavor((
            Adjective.make('mal falad'),
            Adjective.make('maldit'),
            Adjective.make('amaldiçoad'),
            Adjective.make('assombrad'),
            Adjective.make('malign'),
            )),
    )


_PLACE_FLAVOR_LIST = (
        _Flavor((
            Adjective.make('empoeirad'),
            Adjective.make('suj'),
            Adjective.make('imund'),
            )),
        _Flavor((
            Adjective.make('fri'),
            Adjective.make('gélid'),
            Adjective.make('gelad'),
            )),
        _Flavor((
            Adjective.make('húmid'),
            Adjective.make('mofad'),
            )),
        _Flavor((
            Adjective.make('pequen'),
            Adjective.make('claustrofóbic'),
            Adjective.make('apertad'),
            )),
        )


_SECONDATY_PLACE_FLAVOR_LIST = [
        _Flavor((
            Adjective.make_agender('com pó se acumulando nas superfícies', same=True),
            Adjective.make_agender('com teias de aranha', same=True),
            )),
        _Flavor((
            Adjective.make_agender('com goteiras', same=True),
            Adjective.make_agender('com poças d\'água', same=True),
            )),
        _Flavor((
            Adjective.make_agender('com mofo', same=True),
            Adjective.make_agender('com cheiro de mofo', same=True),
            )),
        _Flavor((
            Adjective.make_agender('com poças de sangue seco', same=True),
            Adjective.make_agender('com cheiro de sangue', same=True),
            )),
        _Flavor((
            Adjective.make_agender('com um vento macabro', same=True),
            Adjective.make_agender('com uma brisa desagradável', same=True),
            )),
        _Flavor((
            Adjective.make_agender('com cheiro de podre', same=True),
            Adjective.make_agender('com um cheiro desagradável', same=True),
            )),
        ]


class _MapType(NamedTuple):
    desc: Tuple['Substantive']
    place_types: Tuple['_PlaceType']
    passage_types: Tuple['_PassageType']

    def raw(self, prefix='', context=None):
        return {
                 **choice(self.desc).raw(prefix, context=context)
                }


class _PlaceType(NamedTuple):
    desc: 'Substantive'
    decorations: Tuple[Tuple[Optional['_DecorationItemType']]]
    repeat: bool = False


class _ItemType(NamedTuple):
    desc: 'Substantive'
    flavor_list: Tuple['_Flavor']


class _PassageType(NamedTuple):
    a_side: 'Substantive'
    b_side: 'Substantive'
    flavor_list: Tuple['_Flavor']
    lockable: bool = False
    exclusive_lockable: bool = False

    @classmethod
    def make_unsided(cls,
            desc: 'Substantive',
            flavor_list: Tuple['_Flavor'],
            lockable: bool = False,
            exclusive_lockable: bool = False):
        return cls(desc, desc, flavor_list, lockable, exclusive_lockable)


class _DecorationItemType(_ItemType):
    pass


################################################################################


_NULL_ITEM_FLAVOR = _Flavor((Adjective('', '', '', ''),))

_BASE_ITEM_FLAVOR = _Flavor((
        Adjective.make('suj'),
        Adjective.make('muito suj'),
        Adjective.make('imund'),
        Adjective.make('velh'),
        Adjective.make('muito velh'),
        Adjective.make('empoeirad'),
        Adjective.make('muito empoeirad'),
        Adjective.make('maltratad'),
        Adjective.make('esquecid'),
        Adjective.make('abadonad'),
        Adjective.make('nojent'),
        Adjective.make_agender('deplorável', rad_s='deploráveis'),
        Adjective.make_format(lambda g: f'que parece{g[0]} que est{g[1]} suj{g[2]} a muito tempo',
            m=('', 'á', 'o'), ms=('m', 'ão', 'o'), f=('', 'á', 'a'), fs=('m', 'ão', 'as')),
        Adjective.make_format(lambda g: f'que parece{g[0]} que não {g[1]} limp{g[2]} a muito tempo',
            m=('', 'é', 'o'), ms=('m', 'são', 'o'), f=('', 'é', 'a'), fs=('m', 'são', 'as')),
    ))


_WOODEN_ITEM_FLAVOR = _Flavor((
        Adjective.make_agender('de madeira', same=True),
        Adjective.make_agender('de madeira podre', same=True),
        Adjective.make_agender('de madeira maciça', same=True),
        Adjective.make_format(lambda g: f'feit{g} de madeira'),
        Adjective.make_format(lambda g: f' que é feit{g} de madeira podre'),
        Adjective.make_agender('com lascas faltando', same=True),
        Adjective.make_agender('que está com lascas faltando', same=True),
        Adjective.make('lascad'),
        Adjective.make_agender('frágil', 'frágeis'),
    ))


_FABRIC_ITEM_FLAVOR = _Flavor((
        Adjective.make_agender('de tecido', same=True),
        Adjective.make_format(lambda g: f'feit{g} de tecido'),
        Adjective.make_format(lambda g: f'de tecido e chei{g} de rasgos'),
        Adjective.make_format(lambda g: f'chei{g} de rasgos'),
        Adjective.make_format(lambda g: f'chei{g} de manchas'),
        Adjective.make_agender('com manchas', same=True),
        Adjective.make_agender('com rasgos', same=True),
        Adjective.make_agender('com furos', same=True),
        Adjective.make('mofad'),
    ))


_USEBLAE_ITEM_FLAVOR = _Flavor((
        Adjective.make_agender('com marcas de uso', same=True),
        Adjective.make_agender('com muitas marcas de uso', same=True),
        Adjective.make_agender('que parece estar sem uso a anos', same=True),
        Adjective.make_agender('que parece que ninguém usa a muito tempo', same=True),
        Adjective.make_format(lambda g: f'que parece{g[0]} que {g[1]} muito usad{g[2]}',
            m=('', 'foi', 'o'), ms=('m', 'foram', 'o'), f=('', 'foi', 'a'), fs=('m', 'foram', 'as')),
        Adjective.make_format(lambda g: f'que parece{g[0]} que não {g[1]} usad{g[2]} a muito tempo',
            m=('', 'é', 'o'), ms=('m', 'são', 'o'), f=('', 'é', 'a'), fs=('m', 'são', 'as')),
        Adjective.make_format(lambda g: f'abandonad{g} a muito tempo'),
        Adjective.make_format(lambda g: f'que foi abandonad{g} a muito tempo'),
        Adjective.make_format(lambda g: f'replet{g} de marcas de uso'),
        Adjective.make_agender(f'que ninguém usa a muito tempo', same=True),
    ))


_ART_ITEM_FLAVOR = _Flavor((
        Adjective.make_agender('de péssimo gosto', same=True),
        Adjective.make('macabr'),
        Adjective.make('horroros'),
        Adjective.make('sinistr'),
        Adjective.make('macabr'),
        Adjective.make('horroros'),
        Adjective.make('sinistr'),
        Adjective.make('bastante macabr'),
        Adjective.make('bastante sinistr'),
        Adjective.make_format(lambda g: f'atormentador{g}', m='', ms='es'),
        Adjective.make_format(lambda g: f'atormentador{g}', m='', ms='es'),
        Adjective.make_format(lambda g: f'bastante atormentador{g}', m='', ms='es'),
        Adjective.make_format(lambda g: f'muito atormentador{g}', m='', ms='es'),
    ))


################################################################################


_ESCADA = _PassageType.make_unsided(
        desc = Substantive.make_female('escada'),
        flavor_list = (
            _USEBLAE_ITEM_FLAVOR,
            _BASE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,
            ),
        lockable=False
        )
_PASSAGEM = _PassageType.make_unsided(
        desc = Substantive.make_female('passagem'),
        flavor_list = (
            _USEBLAE_ITEM_FLAVOR,
            _BASE_ITEM_FLAVOR,
            ),
        lockable=False
        )
_PASSAGEM_ADORNADA = _PassageType.make_unsided(
        desc = Substantive.make_female('passagem adornada'),
        flavor_list = (
            _USEBLAE_ITEM_FLAVOR,
            _BASE_ITEM_FLAVOR,
            _ART_ITEM_FLAVOR,
            ),
        lockable=False
        )
_PORTA = _PassageType.make_unsided(
        desc = Substantive.make_female('porta'),
        flavor_list = (
            _USEBLAE_ITEM_FLAVOR,
            _BASE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR
            ),
        lockable=True
        )
_PORTA_DUPLA = _PassageType.make_unsided(
        desc = Substantive.make_female('porta dupla'),
        flavor_list = (
            _USEBLAE_ITEM_FLAVOR,
            _BASE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR
            ),
        lockable=True
        )
_PORTA_ADORNADA = _PassageType.make_unsided(
        desc = Substantive.make_female('porta adornada'),
        flavor_list = (
            _USEBLAE_ITEM_FLAVOR,
            _BASE_ITEM_FLAVOR,
            _ART_ITEM_FLAVOR
            ),
        lockable=True
        )
_PASSAGEM_SECRETA_LIVROS = _PassageType.make_unsided(
        desc = Substantive.make_female('estante de livros'),
        flavor_list = (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,),
        lockable=True,
        exclusive_lockable=True
        )
_PASSAGEM_SECRETA_QUADRO = _PassageType.make_unsided(#TODO two sides
        desc = Substantive.make_male('quadro'),
        flavor_list = (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _ART_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,),
        lockable=True,
        exclusive_lockable=True
        )
_PORTA_TIJOLADA = _PassageType.make_unsided(
        desc = Substantive.make_female('porta fechada com tijolos'),
        flavor_list = (
            _NULL_ITEM_FLAVOR,
            ),
        lockable=True,
        exclusive_lockable=True
        )
_PORTA_TABOAS = _PassageType.make_unsided(
        desc = Substantive.make_female('porta fechada com tábuas'),
        flavor_list = (
            _NULL_ITEM_FLAVOR,
            ),
        lockable=True,
        exclusive_lockable=True
        )
_PORTA_COM_CADEADO = _PassageType.make_unsided(
        desc = Substantive.make_female('porta com um cadeado'),
        flavor_list = (
            _USEBLAE_ITEM_FLAVOR,
            _BASE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR
            ),
        lockable=True
        )


################################################################################


_POLTRONA = _DecorationItemType(
        Substantive.make_female('poltrona'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _FABRIC_ITEM_FLAVOR,)
        )
_SOFA = _DecorationItemType(
        Substantive.make_male('sofa'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _FABRIC_ITEM_FLAVOR,)
        )
_CADEIRA = _DecorationItemType(
        Substantive.make_female('cadeira'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,)
        )
_MESA = _DecorationItemType(
        Substantive.make_female('mesa'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,)
        )
_MESA_DE_CENTRO = _DecorationItemType(
        Substantive.make_female('mesa de centro'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,)
        )
_MESA_DE_CABECEIRA = _DecorationItemType(
        Substantive.make_female('mesa de cabeceira'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,)
        )
_PIA = _DecorationItemType(
        Substantive.make_female('pia'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,)
        )
_LAREIRA = _DecorationItemType(
        Substantive.make_female('lareira'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,)
        )
_FOGAO = _DecorationItemType(
        Substantive.make_male('fogão'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,)
        )
_CAMA = _DecorationItemType(
        Substantive.make_female('cama'),
        (
            _BASE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _FABRIC_ITEM_FLAVOR,)
        )
_ESTANTE = _DecorationItemType(
        Substantive.make_female('estante'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,)
        )
_ESTANTE_DE_LIVROS = _DecorationItemType(
        Substantive.make_female('estante de livros'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,)
        )
_ARMARIO = _DecorationItemType(
        Substantive.make_male('armário'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,)
        )
_CRISTALEIRA = _DecorationItemType(
        Substantive.make_female('cristaleira'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,)
        )
_ESPELHO = _DecorationItemType(
        Substantive.make_male('espelho'),
        (
            _BASE_ITEM_FLAVOR,)
        )
_QUADRO = _DecorationItemType(
        Substantive.make_male('quadro'),
        (
            _BASE_ITEM_FLAVOR,
            _WOODEN_ITEM_FLAVOR,
            _ART_ITEM_FLAVOR,
            _ART_ITEM_FLAVOR,)
        )
_TAPETE = _DecorationItemType(
        Substantive.make_male('tapete'),
        (
            _BASE_ITEM_FLAVOR,
            _USEBLAE_ITEM_FLAVOR,
            _FABRIC_ITEM_FLAVOR,)
        )
_BUSTO = _DecorationItemType(
        Substantive.make_male('busto'),
        (
            _BASE_ITEM_FLAVOR,
            _ART_ITEM_FLAVOR,)
        )
_LUSTRE = _DecorationItemType(
        Substantive.make_male('lustre'),
        (
            _BASE_ITEM_FLAVOR,)
        )


################################################################################



_COZINHA = _PlaceType(
        Substantive.make_female('cozinha'),
        (
            (None, _MESA,),
            (_PIA,),
            (_LAREIRA, _FOGAO,),
            (_ESTANTE, _CRISTALEIRA, _ARMARIO,),
            )
        )
_SALA = _PlaceType(
        Substantive.make_female('sala'),
        (
            (_SOFA,),
            (_LAREIRA,),
            (None, _POLTRONA,),
            (None, _MESA_DE_CENTRO,),
            (None, _CRISTALEIRA, _ESTANTE, _ESTANTE_DE_LIVROS, _ARMARIO,),
            (None, _QUADRO,),
            (None, _TAPETE,),
            (None, None, _BUSTO,),
            (None, None, _LUSTRE,),
            ),
        repeat = True
        )
_SALA_DE_JANTAR = _PlaceType(
        Substantive.make_female('sala de jantar'),
        (
            (_CADEIRA,),
            (_MESA,),
            (None, _ESTANTE, _ARMARIO, _CRISTALEIRA,),
            (None, _LAREIRA,),
            )
        )
_SALA_DE_ESTAR = _PlaceType(
        Substantive.make_female('sala de estar'),
        (
            (_POLTRONA,),
            (_SOFA,),
            (_MESA_DE_CENTRO,),
            (None, _CRISTALEIRA, _ARMARIO, _ESTANTE, _ESTANTE_DE_LIVROS,),
            (None, None, _LUSTRE, _LAREIRA, _LAREIRA,),
            (None, _BUSTO, _QUADRO, _BUSTO, _QUADRO,),
            (None, None, None, _TAPETE,),
            ),
        )
_SALA_DE_LEITURA = _PlaceType(
        Substantive.make_female('sala de Leitura'),
        (
            (_LAREIRA,),
            (_POLTRONA,),
            (None, _SOFA,),
            (None, _MESA_DE_CENTRO,),
            (None, _ARMARIO, _ESTANTE, _ESTANTE_DE_LIVROS,),
            (None, _QUADRO, _QUADRO,),
            (None, _BUSTO, _BUSTO,),
            (None, None, _TAPETE,),
            (None, None, None, _LUSTRE,),
            )
        )
_BIBLIOTECA = _PlaceType(
        Substantive.make_female('biblioteca'),
        (
            (_POLTRONA,),
            (_LAREIRA,),
            (_MESA_DE_CENTRO,),
            (_ESTANTE_DE_LIVROS,),
            (None, _SOFA,),
            (None, _ARMARIO,),
            (None, _CADEIRA,),
            (None, _QUADRO, _QUADRO,),
            (None, _BUSTO, _BUSTO,),
            (None, None, _TAPETE,),
            (None, None, _LUSTRE,),
            (None, None, None, _MESA,),
            )
        )
_CORREDOR = _PlaceType(
        Substantive.make_male('corredor'),
        (
            (_QUADRO,),
            (None, _TAPETE,),
            (None, _BUSTO,),
            (None, _MESA_DE_CENTRO,),
            (None, None, _LUSTRE,),
            ),
        repeat = True
        )
_GALERIA = _PlaceType(
        Substantive.make_female('galeria'),
        (
            (None, _LAREIRA,),
            (None, _TAPETE,),
            (None, _MESA_DE_CENTRO,),
            ),
        repeat = True)
_QUARTO_DE_VISITANTES = _PlaceType(
        Substantive.make_male('quarto de visitantes'),
        (
            (_CAMA,),
            (_MESA_DE_CABECEIRA,),
            (None, _LAREIRA,),
            (None, _ESPELHO, _CADEIRA,),
            (None, _SOFA, _POLTRONA,),
            (None, _ARMARIO, _ESTANTE,),
            (None, _MESA_DE_CENTRO,),
            ),
        repeat = True)
_QUARTO_DE_EMPREGADOS = _PlaceType(
        Substantive.make_male('quarto de empregados'),
        (
            (_CAMA,),
            (None, _MESA_DE_CABECEIRA,),
            (None, _CADEIRA,),
            (None, _ARMARIO, _ESTANTE,),
            ),
        )
_QUARTO = _PlaceType(
        Substantive.make_male('quarto'),
        (
            (_CAMA,),
            (_MESA_DE_CABECEIRA,),
            (None, _LAREIRA,),
            (None, _CADEIRA,),
            (None, _SOFA, _POLTRONA,),
            (None, _ARMARIO, _ESTANTE,),
            (None, _MESA_DE_CENTRO,),
            (None, _ESPELHO,),
            (None, _QUADRO,),
            (None, _TAPETE,)
            ),
        repeat = True)
_CLOSET = _PlaceType(
        Substantive.make_male('closet'),
        (
            (None, _ESTANTE,),
            (_ARMARIO,),
            (_ESPELHO,)
            ),
        repeat = True)
_DEPOSITO = _PlaceType(
        Substantive.make_male('Depósito'),
        (
            (None, _ESTANTE,),
            (None, _ARMARIO,)
            ),
        repeat = True)
_SOTAO = _PlaceType(
        Substantive.make_male('sótão'),
        (
            (None, _CAMA,),
            (None, _MESA_DE_CABECEIRA,),
            (None, _CADEIRA,),
            (None, _POLTRONA,),
            (None, _SOFA,),
            (None, _ESTANTE,),
            (None, _ARMARIO,),
            (None, _MESA_DE_CENTRO,),
            (None, _ESPELHO,),
            (None, _QUADRO,),
            (None, _TAPETE,),
            (None, _CRISTALEIRA,)
            ))
_PORAO = _PlaceType(
        Substantive.make_male('Porão'),
        (
            (None, _CAMA,),
            (None, _MESA_DE_CABECEIRA,),
            (None, _CADEIRA,),
            (None, _POLTRONA,),
            (None, _SOFA,),
            (None, _ESTANTE,),
            (None, _ARMARIO,),
            (None, _MESA_DE_CENTRO,),
            (None, _ESPELHO,),
            (None, _QUADRO,),
            (None, _TAPETE,),
            (None, _CRISTALEIRA,)
            ))
_ATELIE = _PlaceType(
        Substantive.make_male('atelie'),
        (
            (None, _QUADRO,),
            (None, _ESPELHO,),
            (None, _ARMARIO,),
            (None, _MESA,),
            (None, _TAPETE,),
            (None, _BUSTO,)
            )
        )


_MAP_TYPE = _MapType(
            (
                Substantive.make_female('mansão'),
                Substantive.make_male('castelo'),
                Substantive.make_male('casarão'),
                ),
            (
                _COZINHA,
                _SALA,
                _SALA_DE_JANTAR,
                _SALA_DE_ESTAR,
                _SALA_DE_LEITURA,
                _BIBLIOTECA,
                _CORREDOR,
                _GALERIA,
                _QUARTO_DE_VISITANTES,
                _QUARTO_DE_EMPREGADOS,
                _QUARTO,
                _CLOSET,
                _DEPOSITO,
                _SOTAO,
                _PORAO,
                _ATELIE
                ),
            (
                _ESCADA,
                _PASSAGEM,
                _PASSAGEM_ADORNADA,
                _PORTA,
                _PORTA_DUPLA,
                _PORTA_ADORNADA,
                _PASSAGEM_SECRETA_LIVROS,
                _PASSAGEM_SECRETA_QUADRO,
                _PORTA_TIJOLADA,
                _PORTA_TABOAS,
                _PORTA_COM_CADEADO,
                ),
        )


_MAP_BASE_DESCRIPTION ='''
#tipo_o# #tipo# #nome# é um lugar #empty.norepeat(adjetivo_o)# com seus muros
#empty.norepeat(adjetivo_os)# e seus portais #empty.norepeat(adjetivo_os)#. As
paredes #empty.norepeat(adjetivo_as)# e #empty.norepeat(adjetivo_as)#, o piso e
as tábuas #empty.norepeat(adjetivo_as)#, os móveis
#empty.norepeat(adjetivo_os)#. Tudo parece causar um medo primitivo, como se a
sua alma estivesse se tornando #empty.norepeat(adjetivo_a)# conforme você olha
para esta silhueta #empty.norepeat(adjetivo_a)#. Este não é o local onde você
queria estar.'''


class __MapBase(NamedTuple):
    context: 'Context'
    base_type: '_MapType'
    flavor: '_Flavor'
    name: str
    base_description: str

class Map(__MapBase, GrammerMakebla):
    _LOCATION_NAMES_GENERATOR = location_names()

    @classmethod
    def _composed_map_flavor(cls):
        return _Flavor.join(*sample(_MAP_FLAVOR_LIST, 3))

    @classmethod
    def make(cls, context):
        base_type: '_MapType' = _MAP_TYPE
        flavor: '_Flavor' = cls._composed_map_flavor()
        name: str = next(cls._LOCATION_NAMES_GENERATOR)

        return cls(
                context = context,
                base_type=base_type,
                flavor=flavor,
                name=name,
                base_description=_MAP_BASE_DESCRIPTION)

    @property
    @lru_cache
    def raw_grammar(self):
        return {
                'empty': '',
                'nome': self.name,
                **self.flavor.raw(context=self.context),
                **self.base_type.raw('tipo', context=self.context)
                }

GrammerMakebla.register(Map)


class __DecorationItemBase(NamedTuple):
    decoration_type: '_DecorationItemType'
    context: 'Context'

class DecorationItem(__DecorationItemBase, GrammerMakebla):
    @property
    @lru_cache
    def desc(self):
        return self.decoration_type.desc

    @property
    @lru_cache
    def raw_grammar(self):
        deco = self.decoration_type
        return {
                'empty': '',
                **deco.desc.raw('nome', context=self.context),
                **choice(deco.flavor_list).raw(context=self.context),
                'main': '#nome_um# #nome##_adjetivo#',
                '_adjetivo': '[adj:adjetivo_#nome_o#]#_sub_adj#',
                '_sub_adj': ['', ' #empty.norepeat(adj)#', ' #empty.norepeat(adj)#']
                }

    @property
    @lru_cache
    def base_description(self):
        return '#main#'

GrammerMakebla.register(DecorationItem)


_PLACE_BASE_DESCRIPTION = ['''
        [temp:adjetivo_#tipo_o#] [temp2:adjetivo_comp_#tipo_o#]
        #tipo_um# #tipo# #empty.norepeat(temp)# e #empty.norepeat(temp2)#. ''', 
        '''[temp:adjetivo_#tipo_o#]
        #tipo_um# #tipo# #empty.norepeat(temp)#. ''',
        '''[temp2:adjetivo_comp_#tipo_o#] #tipo_um# #tipo# #empty.norepeat(temp)# #empty.norepeat(temp2)#.''']


class __PlaceBase(NamedTuple):
    context: 'Context'
    place_type: _PlaceType
    flavor_sec: _Flavor
    flavor_ter: _Flavor
    decorations: Tuple['DecorationItem']
    passages: Tuple['Passage']
    base_description: str = '#desc##decorations#'

class Place(GrammerMakebla, __PlaceBase):
    @classmethod
    def make(cls, place_type: _PlaceType, context: 'Context', passages) -> 'Place':
        flavor_sec = choice(_PLACE_FLAVOR_LIST)
        flavor_ter = choice(_SECONDATY_PLACE_FLAVOR_LIST)

        decorations = tuple(DecorationItem(deco, context) for deco in map(choice, place_type.decorations) if deco is not None)

        return cls(
                context = context,
                place_type = place_type,
                flavor_sec = flavor_sec,
                flavor_ter = flavor_ter,
                decorations = decorations,
                passages = passages
                )

    @property
    @lru_cache
    def nome(self) -> Substantive:
        return self.place_type.desc

    @property
    def raw_grammar(self):
        _raw_grammar = {'empty': ''}
        _raw_grammar['desc'] = _PLACE_BASE_DESCRIPTION

        decor_desc_tuple = tuple(d.describe() for d in chain(self.decorations, self.passages))
        listed_decoration = None
        if (len(decor_desc_tuple) > 1):
            decor_desc_tuple = tuple(sorted(decor_desc_tuple, key=len))
            listed_decoration = ', '.join(decor_desc_tuple[:-1]) + f' e {decor_desc_tuple[-1]}'
        elif decor_desc_tuple:
            listed_decoration = decor_desc_tuple[0]

        if (listed_decoration):
            _raw_grammar['decorations'] = ' onde você pode ver ' + listed_decoration
        else:
            _raw_grammar['decorations'] = ''

        _raw_grammar.update(self.nome.raw('tipo'))
        _raw_grammar.update(self.flavor_sec.raw('adjetivo'))
        _raw_grammar.update(self.flavor_ter.raw('adjetivo_comp'))
        return _raw_grammar


_PASSAGE_BASE_DESCRIPTION = '''
[temp:adjetivo_#nome_o#]
        #nome_um# #nome# #empty.norepeat(temp)#
'''


class __PassageBase(NamedTuple):
    context: 'Context'
    nome: Substantive
    passage_type: _PassageType
    flavor: _Flavor
    base_description: str = '#desc#'


class Passage(GrammerMakebla, __PassageBase):

    @classmethod
    def make(cls, passage_type: _PassageType, context: 'Context') -> Tuple['Passage', 'Passage']:
        flavor = choice(passage_type.flavor_list)
        return (cls(context = context, nome = passage_type.a_side, flavor = flavor, passage_type = passage_type,),
                cls(context = context, nome = passage_type.b_side, flavor = flavor, passage_type = passage_type,))

    @property
    def raw_grammar(self):
        _raw_grammar = {'empty': ''}
        _raw_grammar['desc'] = _PASSAGE_BASE_DESCRIPTION
        _raw_grammar.update(self.nome.raw('nome'))
        _raw_grammar.update(self.flavor.raw('adjetivo'))
        return _raw_grammar


class Context():
    class ContextualModifiers(Mapping['str', Callable[[str, Any], str]]):

        def __init__(self, grammar, context):
            self.grammar = grammar
            self.context = context
            self.__mapping = {
                'norepeat': partial(self.norepeat),
                'gender': partial(self.gender)
            }

        def gender(self, gender, text) -> str: 
            return self.grammar.flatten(f'#{text}_{gender}#')

        def norepeat(self, text=None, group=None) -> str:
            symbols = self.grammar.symbols

            if group not in symbols or not isinstance(symbols[group].raw_rules, list):
                return text
            
            options = symbols[group].raw_rules
            if len(options) == 1 and options[0] in symbols and options[0] != group: 
                # Sometimes the text to be not repeated is nested to treat gender
                # I know it is not pretty but I am neither and I'm not complaining
                return self.norepeat(text, options[0])
            return self.context.norepeat(options)


        def reset_norepeat(self) -> None:
            self.context._reset_norepeat_said()

        def __getitem__(self, key) -> Callable[[str, Any], str]:
            return self.__mapping[key]

        def __iter__(self):
            return iter(self.__mapping)

        def __len__(self):
            return len(self.__mapping)


    def __init__(self):
        self.map = Map.make(self)
        self.place_type_set: Set['_PlaceType'] = set()
        self._norepeat_said = set()
        self._norepeat_map = list()

    def make_modifires(self, grammar: Grammar):
        return self.ContextualModifiers(grammar, self)

    def norepeat(self, options):
        option_set = set(options)
        if option_set <= self._norepeat_said:
            self._reset_norepeat_said(option_set)
        text = choice(tuple(set(options) - self._norepeat_said))
        self._update_norepeat_said(text)
        return text

    def _update_norepeat_said(self, text):
        for group in self._norepeat_map:
            if text in group:
                self._norepeat_said |= group;
                break
        else:
            self._norepeat_map.append({text})
            self._norepeat_said |= {text}

    def _register_norepeat_map(self, options):
        for group in self._norepeat_map:
            if any(op in group for op in options):
                group |= options
                break
        else:
            self._norepeat_map.append(options)

    def _reset_norepeat_said(self, option_set=None):
        if option_set is None:
            self._norepeat_said = set()
            return
        self._norepeat_said -= option_set

    @property
    def map_type(self) -> _MapType:
        return self.map.base_type

    def __choose_place_type(self) -> '_PlaceType':
        can_repeat_func = lambda t: t.repeat or not t in self.place_type_set
        possible_place_type_tuple = tuple(filter(can_repeat_func, self.map_type.place_types))
        place_type = choice(possible_place_type_tuple) 
        return place_type

    def make_place(self, passages=tuple()) -> Place:
        place_type = self.__choose_place_type()
        place = Place.make(place_type, self, passages)

        self.place_type_set.add(place.place_type)
        return place
    
    def make_passage(self, locked = False) -> Tuple['Passage', 'Passage']:

        types_available: Iterable[_PassageType] = self.map_type.passage_types
        if (locked):
            types_available = tuple(t for t in types_available if t.lockable)
        else:
            types_available = tuple(t for t in types_available if not t.exclusive_lockable)

        passage_type = choice(types_available)
        return Passage.make(passage_type, self)


class MapBuilder():

    class __PassageMap(defaultdict):
        def __init__(self, *args, **kwargs):
            super().__init__(dict, *args, **kwargs)

        def iter_pairs(self):
            for _from, sub_dict in self.items():
                for _to, instace in sub_dict.items():
                    if _from > _to:
                        yield ((_to, instace,), (_from, self[_to][_from],))

    def __init__(self):
        self.context = Context()
        self.passage_map = self.__PassageMap()
        self.ambient_map = dict()

    @property
    def ambient_list(self):
        return list(self.ambient_map.values())

    def create_passage(self, _from, _to, locked):
        a_side, b_side = self.context.make_passage(locked)
        self.passage_map[_from][_to] = a_side
        self.passage_map[_to][_from] = b_side

    def create_ambient(self, _id):
        passages = tuple(self.passage_map[_id].values())
        ambient = self.context.make_place(passages)
        self.ambient_map[_id] = ambient

    def build(self) -> datamodels.Map:
        passage_list = list()
        for (f_id, f_inst), (t_id, t_inst) in self.passage_map.iter_pairs():
            passage_pair = (
                    datamodels.Passage(f_id, f_inst.describe()),
                    datamodels.Passage(t_id, t_inst.describe()))
            passage_list.append(passage_pair)

        ambient_list = list()
        for _id, _inst in self.ambient_map.items():
            decoration_list = list()
            for deco in _inst.decorations:
                decoration_list.append(deco.describe())

            sub_passage_list = list()
            for passage in _inst.passages:
                sub_passage_list.append(passage.describe())

            ambient = datamodels.Ambient(
                    id=_id,
                    descritption = _inst.describe(),
                    passages = tuple(sub_passage_list),
                    decorations = tuple(decoration_list),
                    )
            ambient_list.append(ambient)
        
        return datamodels.Map(
                    introducion_letter = next(intro_letter()),
                    name = self.context.map.name,
                    descritption = self.context.map.describe(),
                    ambients = tuple(ambient_list),
                    passages = tuple(passage_list),
                )
