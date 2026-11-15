from scripts.package_release import ROOT, collect_files


def test_release_collection_keeps_runtime_samples_and_excludes_local_or_raw_data():
    names = {f"agrishift-ai/{path.relative_to(ROOT).as_posix()}" for path in collect_files()}
    assert "agrishift-ai/README_FINAL_DEMO.md" in names
    assert "agrishift-ai/data/features/features.example.json" in names
    assert "agrishift-ai/data/api-samples/meteomatics/demo_sample.example.json" in names
    assert "agrishift-ai/data/api-samples/meteomatics/json.json" not in names
    assert "agrishift-ai/data/features/features.json" in names
    for name in ("ndvi", "ndmi", "bsi", "slope"):
        assert f"agrishift-ai/data/layers/{name}.png" in names
    runtime_models = {
        "agrishift-ai/ml/clustering/artifacts/scaler.joblib",
        "agrishift-ai/ml/clustering/artifacts/kmeans.joblib",
    }
    assert runtime_models.issubset(names)
    joblib_files = {name for name in names if name.endswith(".joblib")}
    assert joblib_files == runtime_models
    raw_tree = [name for name in names if name.startswith("agrishift-ai/data/raw/")]
    assert all(name.endswith("/README.md") for name in raw_tree)
    assert all(not name.endswith((".db", ".sqlite", ".tif", ".nc")) for name in names)
