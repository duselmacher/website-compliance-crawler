import crawler


def _run_main_with_args(monkeypatch, args):
    monkeypatch.setattr("sys.argv", ["crawler.py", *args])
    return crawler.main()


def test_max_urls_requires_extract_content(monkeypatch, capsys):
    code = _run_main_with_args(monkeypatch, ["--domain", "probiom.com", "--max-urls", "10"])
    captured = capsys.readouterr()

    assert code == 1
    assert "--max-urls requires --extract-content" in captured.out


def test_categories_requires_extract_content(monkeypatch, capsys):
    code = _run_main_with_args(monkeypatch, ["--domain", "probiom.com", "--categories", "products"])
    captured = capsys.readouterr()

    assert code == 1
    assert "--categories requires --extract-content" in captured.out


def test_invalid_category_returns_error(monkeypatch, capsys):
    code = _run_main_with_args(
        monkeypatch,
        ["--domain", "probiom.com", "--extract-content", "--categories", "invalid"],
    )
    captured = capsys.readouterr()

    assert code == 1
    assert "Invalid categories: invalid" in captured.out


def test_categories_and_exclude_are_mutually_exclusive(monkeypatch, capsys):
    code = _run_main_with_args(
        monkeypatch,
        [
            "--domain",
            "probiom.com",
            "--extract-content",
            "--categories",
            "products",
            "--exclude",
            "blogs",
        ],
    )
    captured = capsys.readouterr()

    assert code == 1
    assert "--categories und --exclude können nicht gleichzeitig verwendet werden" in captured.out


def test_invalid_domain_returns_error(monkeypatch, capsys):
    code = _run_main_with_args(monkeypatch, ["--domain", "   "])
    captured = capsys.readouterr()

    assert code == 1
    assert "Domain darf nicht leer sein" in captured.out


def test_valid_url_only_run_calls_crawler(monkeypatch):
    called = {}

    def fake_crawl(domain, output_dir):
        called["domain"] = domain
        called["output_dir"] = str(output_dir)
        return {}

    monkeypatch.setattr(crawler, "crawl_urls_only", fake_crawl)

    code = _run_main_with_args(monkeypatch, ["--domain", "https://Probiom.com"])

    assert code == 0
    assert called["domain"] == "probiom.com"
