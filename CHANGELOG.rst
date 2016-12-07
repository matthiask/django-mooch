==========
Change log
==========

`Next version`_
~~~~~~~~~~~~~~~

- Fixed the Stripe JavaScript to work again after the CSS class change
  in 0.4.
- Moved the Stripe handler code into an IIFE (Immediately Invoked Function
  Expression)
- Imported ``reverse`` from ``django.urls`` to avoid a deprecation warning.


`0.4`_ (2016-11-28)
~~~~~~~~~~~~~~~~~~~

- Fixed the CSS class on the stripe moochers' wrapping element.
- Made the PostFinance moocher accept payment parameters on the success
  page as well.


`0.3`_ (2016-11-11)
~~~~~~~~~~~~~~~~~~~

- Made the mooch app namespace configurable so that it's easier to add
  the same moocher several times to a single site.
- Changed the ``post_charge`` signal emission to use moocher instances
  instead of the moocher class.


`0.2`_ (2016-11-09)
~~~~~~~~~~~~~~~~~~~

- Keys and secrets are now arguments when instantiating moochers.
- Added the moocher name as prefix to all URL fragments so that moochers
  themselves do not have to be namespaced.
- Fixed the base payments' ``verbose_name_plural`` setting.


`0.1`_ (2016-10-05)
~~~~~~~~~~~~~~~~~~~

- Initial release.


.. _django-ckeditor: https://pypi.python.org/pypi/django-ckeditor
.. _django-content-editor: http://django-content-editor.readthedocs.org/en/latest/
.. _django-mptt: http://django-mptt.github.io/django-mptt/
.. _django-mptt-nomagic: https://github.com/django-mptt/django-mptt/pull/486
.. _django-versatileimagefield: https://github.com/respondcreate/django-versatileimagefield/
.. _feincms-cleanse: https://pypi.python.org/pypi/feincms-cleanse
.. _django-cte-forest: https://github.com/matthiask/django-cte-forest
.. _PostgreSQL: https://www.postgresql.org/
.. _flake8: https://pypi.python.org/pypi/flake8
.. _isort: https://pypi.python.org/pypi/isort
.. _requests: http://docs.python-requests.org/

.. _0.1: https://github.com/matthiask/django-mooch/commit/f5821bbed7
.. _0.2: https://github.com/matthiask/django-mooch/compare/0.1...0.2
.. _0.3: https://github.com/matthiask/django-mooch/compare/0.2...0.3
.. _0.4: https://github.com/matthiask/django-mooch/compare/0.3...0.4
.. _Next version: https://github.com/matthiask/django-mooch/compare/0.4...master
