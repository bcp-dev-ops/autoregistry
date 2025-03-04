import pytest
from common import construct_pokemon_classes

from autoregistry import Registry


def test_defaults_basic_usecase():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes()
    charmander = Pokemon["cHaRmAnDer"](1, 2)
    assert isinstance(charmander, Charmander)

    assert Pokemon.__registry__.name == "pokemon"
    assert Charmander.__registry__.name == "charmander"
    assert Pikachu.__registry__.name == "pikachu"
    assert SurfingPikachu.__registry__.name == "surfingpikachu"


def test_defaults_contains():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes()
    for pokemon in ["charmander", "pikachu", "surfingpikachu"]:
        assert pokemon in Pokemon

    # Test for case insensitivity.
    for pokemon in ["charmander", "pikachu", "surfingpikachu"]:
        assert pokemon.upper() in Pokemon


def test_defaults_len():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes()
    assert len(Pokemon) == 3
    assert len(Charmander) == 0
    assert len(Pikachu) == 1
    assert len(SurfingPikachu) == 0


def test_defaults_keys():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes()
    assert list(Pokemon.keys()) == ["charmander", "pikachu", "surfingpikachu"]
    assert list(Charmander.keys()) == []
    assert list(Pikachu.keys()) == ["surfingpikachu"]
    assert list(SurfingPikachu.keys()) == []


def test_defaults_iter():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes()
    assert list(Pokemon) == ["charmander", "pikachu", "surfingpikachu"]
    assert list(Charmander) == []
    assert list(Pikachu) == ["surfingpikachu"]
    assert list(SurfingPikachu) == []


def test_defaults_values():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes()
    expected_names = ["Charmander", "Pikachu", "SurfingPikachu"]
    f_handles = list(Pokemon.values())
    f_names = [x.__name__ for x in f_handles]
    assert expected_names == f_names


def test_defaults_items():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes()
    f_handles = list(Pokemon.items())

    actual_keys = [x[0] for x in f_handles]
    assert actual_keys == ["charmander", "pikachu", "surfingpikachu"]

    f_names = [x[1].__name__ for x in f_handles]
    expected_names = ["Charmander", "Pikachu", "SurfingPikachu"]
    assert expected_names == f_names

    assert len(list(Charmander.items())) == 0
    assert len(list(Pikachu.items())) == 1
    assert len(list(SurfingPikachu.items())) == 0


def test_defaults_get():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes()
    assert Pokemon.get("charmander") == Charmander
    assert Pokemon.get("foo") is None
    assert Pokemon.get("foo", "charmander") == Charmander
    assert Pokemon.get("foo", Charmander) == Charmander


def test_multiple_inheritence_last():
    class Foo:
        pass

    class Bar:
        pass

    class Baz(Foo, Registry):
        pass

    class Boop(Baz):
        pass

    class Blap(Bar, Baz):
        pass

    assert list(Baz) == ["boop", "blap"]


def test_multiple_inheritence_first():
    class Foo:
        def bar(self):
            return "bar"

    class Baz(Registry, Foo):
        def blah(self):
            return "blah"

    class Boop(Baz):
        pass

    assert list(Baz) == ["boop"]


def test_multiple_inheritence_child_first():
    class Foo:
        def bar(self):
            return "bar"

    class Baz(Registry):
        def blah(self):
            return "blah"

    class Boop(Baz, Foo):
        pass

    assert list(Baz) == ["boop"]


def test_multiple_inheritence_child_last():
    class Foo:
        def bar(self):
            return "bar"

    class Baz(Registry):
        def blah(self):
            return "blah"

    class Boop(Foo, Baz):
        pass

    assert list(Baz) == ["boop"]


def test_base_registry():
    class Foo(Registry):
        pass

    class SubFoo(Foo):
        pass

    class Bar(Registry):
        pass

    class SubBar(Bar):
        pass

    assert list(Registry) == []
    assert list(Foo) == ["subfoo"]
    assert list(Bar) == ["subbar"]


def test_hierarchy_init_subclass():
    class Base(Registry):
        pass

    registry_ids = {id(Base.__registry__)}

    expected_registry_name = None

    class Foo(Base):
        def __init_subclass__(cls, **kwargs):
            assert id(cls) not in registry_ids
            assert cls.__registry__.name == expected_registry_name

    assert id(Foo.__registry__) not in registry_ids
    registry_ids.add(id(Foo.__registry__))

    expected_registry_name = "foobar1"

    class FooBar1(Foo):
        pass

    assert id(FooBar1.__registry__) not in registry_ids
    registry_ids.add(id(FooBar1.__registry__))

    expected_registry_name = "foobar2"

    class FooBar2(Foo):
        pass

    assert id(FooBar2.__registry__) not in registry_ids
    registry_ids.add(id(FooBar2.__registry__))


def test_valid_repr():
    class Base(Registry):
        pass

    class Foo(Base):
        pass

    assert str(Base) == "<Base: ['foo']>"


def test_valid_repr_keys_override():
    class Base(Registry):
        keys = {"hey": ["you", "there"]}  # type:ignore[reportGeneralTypeIssues]

    assert str(Base) == "<Base: []>"


def test_invalid_repr():
    class Base(Registry):
        pass

    Base.__registry__ = None  # type: ignore[reportGeneralTypeIssues]
    assert str(Base) == "<class 'test_classes.test_invalid_repr.<locals>.Base'>"


def test_dict_methods_override():
    class Base(Registry):
        def __init__(self, a, b):
            self.a = a
            self.b = b

        def __getitem__(self, key):
            return 0

        def keys(self):
            return 0

        @classmethod
        def some_classmethod(cls):
            return 1

        @staticmethod
        def some_staticmethod():
            return 2

        def normal_method(self):
            return 3

    class Foo(Base):
        pass

    base = Base(1, 2)

    assert base.a == 1
    assert base.b == 2

    assert Base["foo"] == Foo
    assert base["foo"] == 0

    assert list(Base.keys()) == ["foo"]  # pyright: ignore[reportGeneralTypeIssues]

    assert base.keys() == 0
    assert base.some_classmethod() == 1
    assert base.some_staticmethod() == 2
    assert base.normal_method() == 3

    assert Base.some_classmethod() == 1
    assert Base.some_staticmethod() == 2


def test_dict_methods_override_classmethod():
    class Base(Registry):
        def __init__(self):
            pass

        @classmethod
        def keys(cls):
            return 0

    base = Base()
    assert Base.keys() == 0
    assert base.keys() == 0


def test_dict_methods_override_staticmethod():
    class Base(Registry):
        def __init__(self):
            pass

        @staticmethod
        def keys():
            return 0

    base = Base()
    assert Base.keys() == 0
    assert base.keys() == 0


def test_dict_methods_override_redirect_false():
    class Base(Registry, redirect=False):
        def __init__(self, a, b):
            self.a = a
            self.b = b

        def keys(self):
            return 0

    class Foo(Base):
        pass

    with pytest.raises(TypeError):
        Base.keys()  # pyright: ignore[reportGeneralTypeIssues]

    base = Base(1, 2)
    assert base.keys() == 0


def test_dict_method_override_getitem():
    class Base(Registry):
        def __getitem__(self, key):
            return None

    with pytest.raises(KeyError):
        Base["foo"]

    base = Base()
    assert base["foo"] is None


def test_dict_method_override_iter():
    class Base(Registry):
        def __iter__(self):
            yield 1
            yield 2
            yield 3

    assert list(Base) == []
    base = Base()
    assert list(base) == [1, 2, 3]


def test_dict_method_override_len():
    class Base(Registry):
        def __len__(self):
            return 5

    assert len(Base) == 0
    base = Base()
    assert len(base) == 5


def test_dict_method_override_contains():
    class Base(Registry):
        def __contains__(self, key):
            return True

    assert "foo" not in Base
    base = Base()
    assert "foo" in base


def test_dict_method_override_keys():
    class Base(Registry):
        def keys(self):
            return [1, 2, 3]

    assert not Base.keys()  # pyright: ignore[reportGeneralTypeIssues]
    base = Base()
    assert base.keys() == [1, 2, 3]


def test_dict_method_override_values():
    class Base(Registry):
        def values(self):
            return [1, 2, 3]

    assert not Base.values()  # pyright: ignore[reportGeneralTypeIssues]
    base = Base()
    assert base.values() == [1, 2, 3]


def test_dict_method_override_items():
    class Base(Registry):
        def items(self):
            return [1, 2, 3]

    assert not list(Base.items())  # pyright: ignore[reportGeneralTypeIssues]
    base = Base()
    assert base.items() == [1, 2, 3]


def test_dict_method_override_get():
    class Base(Registry):
        def get(self, key):
            return 5

    assert Base.get("foo") is None  # pyright: ignore[reportGeneralTypeIssues]
    base = Base()
    assert base.get("foo") == 5


def test_dict_method_override_clear():
    class Base(Registry):
        def clear(self):
            return 5

    assert Base.clear() is None  # pyright: ignore[reportGeneralTypeIssues]
    base = Base()
    assert base.clear() == 5
