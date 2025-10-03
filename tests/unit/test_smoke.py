def test_import_version():
    import anyon_condense

    assert hasattr(anyon_condense, "__version__")
