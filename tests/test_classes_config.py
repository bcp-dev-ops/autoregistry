import pytest
from common import construct_pokemon_classes

from autoregistry import InvalidNameError, Registry


def test_case_sensitive():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes(
        case_sensitive=True,
    )

    assert list(Pokemon.keys()) == ["Charmander", "Pikachu", "SurfingPikachu"]
    assert Pokemon["Charmander"] == Charmander
    with pytest.raises(KeyError):
        Pokemon["CHARMANDER"]


def test_prefix_no_strip():
    class Sensor(Registry, prefix="Sensor", strip_prefix=False):
        pass

    class SensorOxygen(Sensor):
        pass

    class SensorTemperature(Sensor):
        pass

    assert list(Sensor.keys()) == ["sensoroxygen", "sensortemperature"]

    with pytest.raises(InvalidNameError):

        class Foo(Sensor):
            pass


def test_prefix_yes_strip():
    class Sensor(Registry, prefix="Sensor"):
        pass

    class SensorOxygen(Sensor):
        pass

    class SensorTemperature(Sensor):
        pass

    assert list(Sensor.keys()) == ["oxygen", "temperature"]


def test_suffix_no_strip():
    class Sensor(Registry, suffix="Sensor", strip_suffix=False):
        pass

    class OxygenSensor(Sensor):
        pass

    class TemperatureSensor(Sensor):
        pass

    assert list(Sensor.keys()) == ["oxygensensor", "temperaturesensor"]

    with pytest.raises(InvalidNameError):

        class Foo(Sensor):
            pass


def test_suffix_yes_strip():
    class Sensor(Registry, suffix="Sensor"):
        pass

    class OxygenSensor(Sensor):
        pass

    class TemperatureSensor(Sensor):
        pass

    assert list(Sensor.keys()) == ["oxygen", "temperature"]


def test_prefix_suffix_yes_strip():
    class Sensor(Registry, prefix="Premium", suffix="Sensor"):
        pass

    class PremiumOxygenSensor(Sensor):
        pass

    class PremiumTemperatureSensor(Sensor):
        pass

    assert list(Sensor.keys()) == ["oxygen", "temperature"]


def test_register_self():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes(
        register_self=True,
    )
    assert list(Pokemon.keys()) == [
        "pokemon",
        "charmander",
        "pikachu",
        "surfingpikachu",
    ]


def test_no_recursive():
    """Tests that children properly inherit and obey ``recursive=False``."""
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes(
        recursive=False,
    )
    assert list(Pokemon.keys()) == ["charmander", "pikachu"]
    assert list(Charmander.keys()) == []
    assert list(Pikachu.keys()) == ["surfingpikachu"]
    assert list(SurfingPikachu.keys()) == []

    assert "pikachu.surfingpikachu" in Pokemon


def test_recursive_hierarchy_1():
    """Test more complex recursive configurations."""

    class Base(Registry, recursive=False):
        pass

    class Foo(Base, recursive=True):
        pass

    class Bar(Foo):
        pass

    class Baz(Bar):
        pass

    assert list(Base) == ["foo"]
    assert list(Foo) == ["bar", "baz"]


def test_recursive_hierarchy_2():
    class ClassA(Registry, prefix="Class", recursive=False):
        pass

    class ClassB(ClassA):
        pass

    class ClassC(ClassB, recursive=True):
        pass

    class ClassD(ClassC):
        pass

    class ClassE(ClassD):
        pass

    assert list(ClassA) == ["b"]
    assert list(ClassB) == ["c"]
    assert list(ClassC) == ["d", "e"]
    assert list(ClassD) == ["e"]
    assert list(ClassE) == []


def test_snake_case():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes(
        snake_case=True,
    )
    assert list(Pokemon.keys()) == [
        "charmander",
        "pikachu",
        "surfing_pikachu",
    ]


def test_snake_case_hyphen():
    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes(
        snake_case=True, hyphen=True
    )
    assert list(Pokemon.keys()) == [
        "charmander",
        "pikachu",
        "surfing-pikachu",
    ]


def test_transform():
    def transform(name):
        return f"shiny_{name}"

    Pokemon, Charmander, Pikachu, SurfingPikachu = construct_pokemon_classes(
        snake_case=True, transform=transform
    )
    assert list(Pokemon.keys()) == [
        "shiny_charmander",
        "shiny_pikachu",
        "shiny_surfing_pikachu",
    ]


def test_config_hierarchy():
    class Pokemon(Registry, suffix="Type", strip_suffix=True, recursive=False):
        pass

    class RockType(Pokemon, suffix=""):
        pass

    class Geodude(RockType):
        pass

    class GrassType(Pokemon):
        pass

    with pytest.raises(InvalidNameError):
        # Because "Oddish" doesn't end in "Type"
        class Oddish(GrassType):
            pass


def test_name_override():
    class Sensor(Registry):
        pass

    class Oxygen(Sensor, name="o2"):
        pass

    class Temperature(Sensor):
        pass

    assert list(Sensor.keys()) == ["o2", "temperature"]


def test_name_override_invalid():
    class Sensor(Registry):
        pass

    with pytest.raises(InvalidNameError):

        class Oxygen1(Sensor, name="o/2"):
            pass

    with pytest.raises(InvalidNameError):

        class Oxygen2(Sensor, name="o.2"):
            pass


def test_aliases_single_str():
    class Sensor(Registry):
        pass

    class Oxygen(Sensor, aliases="o2"):
        pass

    class Temperature(Sensor):
        pass

    assert list(Sensor.keys()) == ["oxygen", "o2", "temperature"]
    assert Sensor["oxygen"] == Sensor["o2"] == Oxygen


def test_aliases_list():
    class Sensor(Registry):
        pass

    class Oxygen(Sensor, aliases=["o2", "air"]):
        pass

    class Temperature(Sensor):
        pass

    assert list(Sensor.keys()) == ["oxygen", "o2", "air", "temperature"]
    assert Sensor["oxygen"] == Sensor["o2"] == Sensor["air"] == Oxygen


def test_aliases_single_str_invalid():
    class Sensor(Registry):
        pass

    with pytest.raises(InvalidNameError):

        class Oxygen1(Sensor, aliases="o/2"):
            pass

    with pytest.raises(InvalidNameError):

        class Oxygen2(Sensor, aliases="o.2"):
            pass


def test_skip():
    class Sensor(Registry):
        pass

    class Oxygen(Sensor, skip=True):
        pass

    class Temperature(Sensor):
        pass

    assert list(Sensor.keys()) == ["temperature"]
