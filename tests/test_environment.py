from src.environment import get_environment_report

def test_environment_report_structure():
    report = get_environment_report()

    assert isinstance(report, dict)
    assert "python_version" in report
    assert "os_name" in report
    assert "platform" in report
    assert "python_version_info" in report

    version_info = report["python_version_info"]
    assert isinstance(version_info, dict)
    assert "major" in version_info
    assert "minor" in version_info

def test_environment_python_version():
    report = get_environment_report()
    version_info = report["python_version_info"]

    # We expect Python 3
    assert version_info["major"] >= 3
