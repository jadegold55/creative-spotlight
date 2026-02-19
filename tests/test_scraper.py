from scraping.randompoem import scrape


def test_scrape_returns_poem():
    poem = scrape()
    assert poem is not None
    assert "title" in poem
    assert "author" in poem
    assert "content" in poem


def test_scrape_by_author():
    poem = scrape(author="Emily Dickinson")
    assert poem is not None
    assert poem["author"] == "Emily Dickinson"


def test_scrape_bad_author_returns_none():
    poem = scrape(author="xyznotanauthor123")
    assert poem is None
