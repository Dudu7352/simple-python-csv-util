from inspect import getargs, isroutine, signature
import re
from uuid import uuid4 as uuid


def Singletone(decorated_class):
    inst = decorated_class()
    return lambda: inst


def to_snake(camel_case: str) -> str:
    def callback(pat): return f'{pat.group(1)[0]}_{pat.group(1)[1]}'
    return re.sub(r'([a-z][A-Z])', callback, camel_case.replace(' ', '_').replace('ID', 'id_')).lower()


@Singletone
class TableRepo:
    def __init__(self):
        self.__registry: dict[dict] = {}

    def register_table(self, entity):
        self.__registry[entity] = entity.table

    # TODO: create connections after all objects have been loaded
    def request_obj(self, type, id):
        return self.__registry[type][id]


class Table:
    def __init__(self, file: str, primary="_id", head_map: dict[str, str] = {}, ref_map: dict[str, 'Ref'] = {}):
        self.__file = file
        self.__primary = primary
        self.__head_map = head_map
        self.__ref_map = ref_map

    def __call__(self, decorated_class):
        decorated_class.primary = self.__primary
        class_sig = signature(decorated_class)

        with open(self.__file) as f:
            file = [i.strip() for i in f]

        # print(self.__ref_map.keys())
        head = []
        for i in filter(lambda x: x != '', file[0].split(';')):
            if i in self.__head_map.keys():
                head.append(self.__head_map[i])
            elif i in self.__ref_map.keys():
                head.append(self.__ref_map[i].field)
            else:
                head.append(to_snake(i))

        # print(file[0].split(';'), head)

        head_p = [class_sig.parameters[i].annotation for i in head]
        head_zip = list(zip(head, head_p))
        ref_cols = {i.field: k for k, i in self.__ref_map.items()}

        # print(ref_cols)

        decorated_class.table = {}

        for row in file[1:]:
            # print("-" * 20, *list(zip(head_zip, row.strip().split(';'))), sep='\n')
            params = {elem_name: TableRepo().request_obj(class_sig
                                                   .parameters[elem_name]
                                                   .annotation,
                                                   csv_p)
                      if elem_name in ref_cols
                      else elem_type(csv_p)
                      for (elem_name, elem_type), csv_p in zip(head_zip, row.strip().split(';'))}

            obj = decorated_class(**params)

            decorated_class.table[str(params[self.__primary])
                                  if self.__primary in params
                                  else str(uuid())] = obj

        TableRepo().register_table(decorated_class)
        print(f"Loaded and registered {decorated_class}")
        print(self.__primary)
        print(*decorated_class.table, sep='\n')
        return decorated_class


class Ref:
    def __init__(self, field: str, referenced_table):
        self.field = field
        self.referenced_table = referenced_table

    def __repr__(self) -> str:
        return f"Ref(field: {self.field}, referenced_table:{self.referenced_table})"


@Table("uczniowie.txt", primary="id_ucznia")
class Uczen:
    def __init__(self,
                 id_ucznia: int,
                 nazwisko: str,
                 imie: str,
                 ulica: str,
                 dom: int,
                 id_klasy: str
                 ):
        self.id_ucznia = id_ucznia
        self.nazwisko = nazwisko
        self.imie = imie
        self.ulica = ulica
        self.dom = dom
        self.id_klasy = id_klasy


@Table("przedmioty.txt", primary="id_przedmiotu")
class Przedmiot:
    def __init__(self,
                 id_przedmiotu: int,
                 nazwa_przedmiotu: str,
                 nazwisko_naucz: str,
                 imie_naucz: str
                 ):
        self.id_przedmiotu = id_przedmiotu
        self.nazwa_przedmiotu = nazwa_przedmiotu
        self.nazwisko_naucz = nazwisko_naucz
        self.imie_naucz = imie_naucz


@Table("oceny.txt",
       ref_map={"IDprzedmiotu": Ref('przedmiot', Przedmiot),
                "IDucznia": Ref('uczen', Uczen)})
class Ocena:
    def __init__(self,
                 uczen: Uczen,
                 przedmiot: Przedmiot,
                 ocena: int,
                 data: str
                 ):
        self.uczen = uczen
        self.przedmiot = przedmiot
        self.ocena = ocena
        self.data = data
