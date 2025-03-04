Overview
========
All of AutoRegistry's functionality comes from the ``Registry`` class.

.. code-block:: python

   from autoregistry import Registry

To use the ``Registry`` class, we can either inherit it, or directly invoke
it to create a ``Registry`` object.


Inheritance
^^^^^^^^^^^
Generally, when inheriting ``Registry``, we are defining an interface, and thusly
an `abstract base class`_. The ``Registry`` class is an instance of ``ABCMeta``,
so the ``abc`` decorator ``@abstractmethod`` will work with subclasses of ``Registry``.

.. code-block:: python

   from abc import abstractmethod
   from autoregistry import Registry


   class Pokemon(Registry):
       @abstractmethod
       def attack(self, target) -> int:
           pass


   class Pikachu(Pokemon):
       def attack(self, target):
           return 5

The interface ``Pokemon`` is defined and currently has one subclass, ``Pikachu``.
The ``Pokemon`` **class** can be treated like a dictionary, mapping strings to
class-constructors. The keys are derived from the subclasses' names.

.. code-block:: pycon

   >>> len(Pokemon)
   1
   >>> Pokemon
   <Pokemon: ['pikachu']>
   >>> list(Pokemon)
   ['pikachu']
   >>> pikachu = Pokemon["pikachu"]()
   >>> pikachu
   <__main__.Pikachu object at 0x10689fb20>

Unlike a dictionary, the queries are, by default, case-insensitive:

.. code-block:: pycon

   >>> pikachu = Pokemon["pIkAcHU"]()  # Case insensitive works, too.
   >>> "pikachu" in Pokemon
   True
   >>> "PIKACHU" in Pokemon
   True

If an unregistered string is queried, a ``KeyError`` will be raised.
You can also use the ``get`` method to handle missing-key queries.
If the provided ``default`` argument is a string, a lookup will be performed.

.. code-block:: pycon

   >>> Pokemon["ash"]
   KeyError: 'ash'
   >>> pikachu = Pokemon.get("ash", "pikachu")()
   >>> pikachu = Pokemon.get("ash", Pikachu)()  # The default could also be the constructor.
   >>> pikachu = Pokemon.get("ash")()  # If default is not specified, its None.
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   TypeError: 'NoneType' object is not callable

The ruleset for deriving keys and valid classnames is configurable. See :ref:`Configuration`.

Decorator
^^^^^^^^^

Instead of using classes, you can also use ``Registry`` to explicitly create a dictionary-like
object and use it to decorate functions.

.. code-block:: python

   from autoregistry import Registry

   my_registry = Registry()


   @my_registry
   def foo(x):
       return x


   @my_registry()  # This also works.
   def bar(x):
       return 2 * x


   # You can also register classes this way.
   @my_registry
   class Baz:
       pass

The ``my_registry`` **object** can be treated like a dictionary, mapping strings to
registered functions. The keys are derived from the function names.

.. code-block:: pycon

   >>> len(my_registry)
   3
   >>> my_registry
   <Registry: ['foo', 'bar', "baz"]>
   >>> list(my_registry)
   ['foo', 'bar', 'baz']
   >>> my_registry["foo"](7)
   7

You can also pass in an object or a list of objects at registry creation:

.. code-block:: python

   def foo():
       pass


   def bar():
       pass


   my_registry = Registry([foo, bar])


   @my_registry
   def baz():
       pass


Module
^^^^^^
Another use of AutoRegistry is to automatically create a registry of an external module.
For example, in pytorch, the ``torch.optim`` submodule contains many optimizers that
we may want to configure via a yaml file.

.. code-block:: python

   import torch
   from autoregistry import Registry

   optims = Registry(torch.optim)

   assert list(optims) == [
       "asgd",
       "adadelta",
       "adagrad",
       "adam",
       "adamw",
       "adamax",
       "lbfgs",
       "nadam",
       "optimizer",
       "radam",
       "rmsprop",
       "rprop",
       "sgd",
       "sparseadam",
       "lr_scheduler",
       "swa_utils",
   ]


.. _abstract base class: https://docs.python.org/3/library/abc.html
