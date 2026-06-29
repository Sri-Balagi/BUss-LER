from app.intelligence.strategy.library.engine import StrategyLibrary

def test_library_catalog():
    library = StrategyLibrary()
    catalog = library.get_catalog()
    assert len(catalog.strategies) == 3

def test_library_retrieve():
    library = StrategyLibrary()
    growth_strats = library.retrieve_by_category("GROWTH")
    
    assert len(growth_strats) == 1
    assert growth_strats[0].strategy_id == "STRAT_002"
    assert growth_strats[0].name == "Market Expansion"
