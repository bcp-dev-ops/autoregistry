import pytest
from common import construct_functions

import autoregistry
from autoregistry import Registry
from autoregistry.exceptions import ModuleAliasError
from tests.fake_module import fake_submodule_1


def test_defaults_functions_contains():
    registry, _, _ = construct_functions()

    for name in ["foo", "bar"]:
        assert name in registry

    assert "baz" not in registry


def test_defaults_functions_len():
    registry, _, _ = construct_functions()
    assert len(registry) == 2


def test_defaults_functions_keys():
    registry, foo, bar = construct_functions()
    assert list(registry.keys()) == ["foo", "bar"]


def test_defaults_functions_values():
    registry, foo, bar = construct_functions()
    assert list(registry.values()) == [foo, bar]


def test_defaults_functions_items():
    registry, foo, bar = construct_functions()
    assert list(registry.items()) == [("foo", foo), ("bar", bar)]


def test_defaults_functions_call():
    registry, _, _ = construct_functions()
    assert registry["foo"]("test string") == "test string"


def assert_fake_module_registry(registry, fake_module):
    assert registry["bar2"] == fake_module.bar2
    assert registry["fake_module_1"]["foo1"] == fake_module.fake_module_1.foo1
    assert registry["fake_module_1"]["bar1"] == fake_module.fake_module_1.bar1
    assert registry["fake_module_1"]["some_str"] == fake_module.fake_module_1.some_str
    assert registry["fake_module_1"]["some_list"] == fake_module.fake_module_1.some_list
    assert registry["fake_module_2"]["foo2"] == fake_module.fake_module_2.foo2
    assert registry["fake_module_2"]["bar2"] == fake_module.fake_module_2.bar2
    assert registry["foo2"] == fake_module.foo2


def test_defaults_module():
    import fake_module

    registry = Registry()
    registry(fake_module)
    assert list(registry) == [
        "bar2",
        "fake_module_1",
        "fake_module_2",
        "fake_submodule_1",
        "foo2",
    ]
    assert list(registry["fake_submodule_1"]["fake_submodule_1"]) == ["foo"]

    assert_fake_module_registry(registry, fake_module)


def test_defaults_module_dot_query():
    import fake_module

    registry = Registry()
    registry(fake_module)

    assert registry["fake_module_1.foo1"] == fake_module.fake_module_1.foo1
    assert registry["fake_module_1.bar1"] == fake_module.fake_module_1.bar1
    assert registry["fake_module_2.foo2"] == fake_module.fake_module_2.foo2
    assert registry["fake_module_2.bar2"] == fake_module.fake_module_2.bar2

    assert registry["fake_module_1/foo1"] == fake_module.fake_module_1.foo1
    assert registry["fake_module_1/bar1"] == fake_module.fake_module_1.bar1
    assert registry["fake_module_2/foo2"] == fake_module.fake_module_2.foo2
    assert registry["fake_module_2/bar2"] == fake_module.fake_module_2.bar2


def test_defaults_module_dot_contains():
    import fake_module

    registry = Registry()
    registry(fake_module)

    assert "fake_module_1.foo1" in registry
    assert "fake_module_1.bar1" in registry
    assert "fake_module_2.foo2" in registry
    assert "fake_module_2.bar2" in registry

    assert "fake_module_1/foo1" in registry
    assert "fake_module_1/bar1" in registry
    assert "fake_module_2/foo2" in registry
    assert "fake_module_2/bar2" in registry

    # Test case-insensitivity
    assert "FAKE_MODULE_1.FOO1" in registry
    assert "FAKE_MODULE_1.BAR1" in registry
    assert "FAKE_MODULE_2.FOO2" in registry
    assert "FAKE_MODULE_2.BAR2" in registry

    assert "FAKE_MODULE_1/FOO1" in registry
    assert "FAKE_MODULE_1/BAR1" in registry
    assert "FAKE_MODULE_2/FOO2" in registry
    assert "FAKE_MODULE_2/BAR2" in registry


def test_defaults_module_builtin():
    import itertools

    with pytest.raises(autoregistry.CannotRegisterPythonBuiltInError):
        Registry(itertools)


def test_case_sensitive_module():
    """Tests that the registry config is propagated to subregistries."""
    import fake_module

    registry = Registry(case_sensitive=True)
    registry(fake_module)

    assert "fake_module_1" in registry
    assert "fake_module_1.SOME_UPPER" in registry
    assert (
        registry["fake_module_1"]["SOME_UPPER"] == fake_module.fake_module_1.SOME_UPPER
    )
    with pytest.raises(KeyError):
        registry["fake_module_1"]["some_upper"]


def test_registry_overwrite():
    registry = Registry(overwrite=True)

    @registry
    def foo():  # type: ignore[reportGeneralTypeIssues]
        pass

    @registry
    def foo():  # noqa: F811
        pass


def test_registry_overwrite_key_collision():
    registry = Registry(overwrite=False)

    @registry
    def foo():  # type: ignore[reportGeneralTypeIssues]
        pass

    with pytest.raises(autoregistry.KeyCollisionError):

        @registry
        def foo():  # noqa: F811
            pass


def test_registry_register_at_creation():
    import fake_module

    def foo():
        pass

    def bar():
        pass

    registry = Registry([foo, bar, fake_module])

    for name in ["foo", "bar"]:
        assert name in registry

    assert "baz" not in registry

    assert_fake_module_registry(registry, fake_module)


def test_registry_register_at_creation_single():
    def bar():
        pass

    registry = Registry(bar)

    assert list(registry) == ["bar"]


def test_registry_module_alias():
    import fake_module

    registry = Registry(fake_module)
    with pytest.raises(ModuleAliasError):
        registry(fake_module, aliases="module_alias")
