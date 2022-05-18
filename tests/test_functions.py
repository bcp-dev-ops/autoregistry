from common import construct_functions

from autoregistry import Registry


def test_defaults_functions_contains():
    registry, _, _ = construct_functions()

    for name in ["foo", "bar"]:
        assert name in registry


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


def test_defaults_module():
    import fake_module

    registry = Registry()
    registry(fake_module)
    assert list(registry) == ["bar2", "fake_module_1", "fake_module_2", "foo2"]
    assert registry["bar2"] == fake_module.bar2
    assert registry["fake_module_1"]["foo1"] == fake_module.fake_module_1.foo1
    assert registry["fake_module_1"]["bar1"] == fake_module.fake_module_1.bar1
    assert registry["fake_module_2"]["foo2"] == fake_module.fake_module_2.foo2
    assert registry["fake_module_2"]["bar2"] == fake_module.fake_module_2.bar2
    assert registry["foo2"] == fake_module.foo2


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
