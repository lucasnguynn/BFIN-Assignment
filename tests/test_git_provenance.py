from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
import m2_github_orchestrator as workflow

class TestGithubPinnedControls(unittest.TestCase):
    def test_repo_pinned_and_workflow_present(self):
        requirements=(ROOT/'requirements_github.txt').read_text()
        assert 'ranaroussi/yfinance.git@5cae563642b59f49adf6a04a5ad6744f8b0e084d' in requirements
        workflow_text=(ROOT/'.github/workflows/bfin_member2_yfinance.yml').read_text()
        assert 'actions/upload-artifact@v4' in workflow_text
        assert 'python src/m2_data_pipeline.py fetch --partition estimation' in workflow_text
        assert '2023-2025' not in workflow_text

    def test_no_data_gate_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=workflow.gate(Path(tmp))
            assert result['status']=='BLOCKED'
            assert len(result['remaining_blockers'])>=3

    def test_upstream_historical_endpoint_and_repo_version(self):
        assert workflow.GITHUB_SHA == '5cae563642b59f49adf6a04a5ad6744f8b0e084d'
        assert workflow.GITHUB_REPO.endswith('ranaroussi/yfinance')
