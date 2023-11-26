from inspect import signature
import re
from uuid import uuid4 as uuid


def to_snake(camel_case: str) -> str:
    def callback(pat): return f'{pat.group(1)[0]}_{pat.group(1)[1]}'

    return re.sub(r'([a-z][A-Z])', callback, camel_case.replace(' ', '_').replace('ID', 'id_')).lower()


class TableRepo:
    __registry: dict[dict] = {}
    __prim_types: dict = {}

    @staticmethod
    def register_table(entity, primary_key_type):
        TableRepo.__registry[entity] = entity.table
        TableRepo.__prim_types[entity] = primary_key_type

    @staticmethod
    def request_obj(table, elem_id):
        typed_id = TableRepo.__prim_types[table](elem_id)
        return TableRepo.__registry[table][typed_id]


class Table:
    def __init__(self, file: str, primary="_id", head_map: dict[str, str] = {}, refs: list['Ref'] = []):
        self.__file = file
        self.__primary = primary
        self.__head_map = head_map
        self.__refs = refs

    def __call__(self, decorated_class):
        class_sig = signature(decorated_class)
        try:
            primary_type = class_sig.parameters[self.__primary].annotation
        except KeyError:
            primary_type = str
        csv_to_ref = {i.csv_field: i for i in self.__refs} if self.__refs is not None else {}
        col_to_ref = {i.ref_field: i for i in self.__refs} if self.__refs is not None else {}

        with open(self.__file) as f:
            file = [i.strip() for i in f]

        head = [self.__head_map[i]
                if i in self.__head_map.keys()
                else (csv_to_ref[i].ref_field
                      if i in csv_to_ref.keys()
                      else to_snake(i)) for i in filter(lambda x: x != '', file[0].split(';'))]
        head_p = [class_sig.parameters[i].annotation for i in head]
        head_zip = list(zip(head, head_p))

        decorated_class.table = {}

        for row in file[1:]:
            params = {elem_name: TableRepo.request_obj(class_sig.parameters[elem_name].annotation, csv_p)
                      if elem_name in col_to_ref else
                      elem_type(csv_p)
                      for (elem_name, elem_type), csv_p
                      in zip(head_zip, row.strip().split(';'))}

            obj = decorated_class(**params)

            key = params[self.__primary] if self.__primary in params else str(uuid())

            decorated_class.table[key] = obj

        TableRepo.register_table(decorated_class, primary_type)
        return decorated_class


class Ref[T]:
    def __init__(self, csv_field: str, ref_field: str, referenced_table: T):
        self.csv_field = csv_field
        self.ref_field = ref_field
        self.referenced_table = referenced_table


@Table("uczniowie.txt", primary="id_ucznia")
class Uczen:
    def __init__(self,
                 id_ucznia: int,
                 nazwisko: str,
                 imie: str,
                 ulica: str,
                 dom: int,
                 id_klasy: str):
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
                 imie_naucz: str):
        self.id_przedmiotu = id_przedmiotu
        self.nazwa_przedmiotu = nazwa_przedmiotu
        self.nazwisko_naucz = nazwisko_naucz
        self.imie_naucz = imie_naucz


@Table(
    "oceny.txt",
    refs=[
        Ref('IDprzedmiotu', 'przedmiot', Przedmiot),
        Ref('IDucznia', 'uczen', Uczen)
    ]
)
class Ocena:
    def __init__(self,
                 uczen: Uczen,
                 przedmiot: Przedmiot,
                 ocena: int,
                 data: str):
        self.uczen = uczen
        self.przedmiot = przedmiot
        self.ocena = ocena
        self.data = data


# żeby linter wiedział co się dzieje
oceny: dict[int, Ocena] = Ocena.table
uczniowie: dict[int, Uczen] = Uczen.table
przedmioty: dict[str, Przedmiot] = Przedmiot.table

# zadanie 1
avg_dict: dict[Uczen] = {}
for ocena in oceny.values():
    try:
        curr_avg = avg_dict[ocena.uczen]
        avg_dict[ocena.uczen] = [curr_avg[0] + ocena.ocena, curr_avg[1] + 1]
    except KeyError:
        avg_dict[ocena.uczen] = [ocena.ocena, 1]
uczen = max(avg_dict, key=lambda x: avg_dict[x][0] / avg_dict[x][1])
print("Zadanie 1")
print(uczen.imie, uczen.nazwisko, end='\n\n')

# zadanie 2
oceny_z_przedmiotu: dict[Przedmiot, dict[Uczen]] = {}
for ocena in oceny.values():
    try:
        przedm_ocen = oceny_z_przedmiotu[ocena.przedmiot]
        try:
            x = przedm_ocen[ocena.uczen]
            przedm_ocen[ocena.uczen] = [x[0] + ocena.ocena, x[1] + 1]
        except KeyError:
            przedm_ocen[ocena.uczen] = [ocena.ocena, 1]
    except KeyError:
        oceny_z_przedmiotu[ocena.przedmiot] = {}

print("Zadanie 2")
for przedmiot, avg_dict in oceny_z_przedmiotu.items():
    uczen = max(avg_dict, key=lambda x: avg_dict[x][0] / avg_dict[x][1])
    print(
        f"Przedmiot: {przedmiot.nazwa_przedmiotu}\nNauczyciel: {przedmiot.imie_naucz} {przedmiot.nazwisko_naucz}\nUczen: {uczen.imie} {uczen.nazwisko}",
        end='\n\n')
