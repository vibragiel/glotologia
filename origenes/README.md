origenes.py
===========

Consulta en el Nuevo Tesoro Lexicográfico el año y diccionario en el que se recogió una palabra por primera vez.

```
$ python origenes.py origen año electrónico
origen: 1737 ACADEMIA AUTORIDADES (O-R)
año: 1726 ACADEMIA AUTORIDADES (A-B)
electrónico: 1956 ACADEMIA USUAL
```

```python
>>> from origenes import Ntlle
>>> ntlle = Ntlle()
>>> ntlle.origen("origen")
'1737 ACADEMIA AUTORIDADES (O-R)'
>>> ntlle.origen(u"año")
'1726 ACADEMIA AUTORIDADES (A-B)'
>>> ntlle.origen(u"electrónico")
'1956 ACADEMIA USUAL'
```
