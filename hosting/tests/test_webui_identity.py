import ast
import unittest
from pathlib import Path
from types import SimpleNamespace


ENV_FILE = Path(__file__).resolve().parents[2] / 'backend/open_webui/env.py'


def configured_name(value=None):
    """Exercise the name-setting block without importing backend dependencies."""
    module = ast.parse(ENV_FILE.read_text())
    for index, node in enumerate(module.body):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == 'WEBUI_NAME'
            for target in node.targets
        ):
            block = [node]
            following = module.body[index + 1]
            if isinstance(following, ast.If) and any(
                isinstance(child, ast.Name) and child.id == 'WEBUI_NAME'
                for child in ast.walk(following.test)
            ):
                block.append(following)
            namespace = {
                'os': SimpleNamespace(
                    getenv=lambda key, default: value if value is not None else default
                )
            }
            exec(compile(ast.Module(body=block, type_ignores=[]), str(ENV_FILE), 'exec'), namespace)
            return namespace['WEBUI_NAME']
    raise AssertionError('WEBUI_NAME assignment not found')


class WebUIIdentityTests(unittest.TestCase):
    def test_posylkaai_has_no_automatic_suffix(self):
        self.assertEqual(configured_name('PosylkaAI'), 'PosylkaAI')

    def test_upstream_default_is_preserved(self):
        self.assertEqual(configured_name(), 'Open WebUI')


if __name__ == '__main__':
    unittest.main()
