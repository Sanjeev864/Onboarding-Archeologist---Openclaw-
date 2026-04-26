from backend.app.services.analyzer import RepositoryAnalyzer


def test_bucket_path_groups_nested_paths():
    analyzer = RepositoryAnalyzer()
    assert analyzer._bucket_path("src/app/main.py") == "src/app"


def test_source_path_filters_build_outputs():
    analyzer = RepositoryAnalyzer()
    assert analyzer._is_source_path("src/app/main.py")
    assert not analyzer._is_source_path("node_modules/pkg/index.js")
