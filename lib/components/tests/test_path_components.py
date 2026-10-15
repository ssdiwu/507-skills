import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Components(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def command(self, code, out='receipt', timeout=5, source=()):
        cmd = [sys.executable,str(ROOT/'check_run.py'),'--argv-json',json.dumps([sys.executable,'-c',code]),
               '--cwd',str(self.root),'--log-dir',str(self.root/out),'--timeout',str(timeout)]
        for rel in source: cmd += ['--source',rel]
        run = subprocess.run(cmd,capture_output=True,text=True)
        return run.returncode,json.loads(run.stdout)

    def test_failed_command_retains_actual_failure_and_logs(self):
        code,receipt = self.command('import sys;print("original failure");sys.exit(7)')
        self.assertEqual(code,1)
        self.assertEqual(receipt['exitCode'],7)
        log = self.root/'receipt/stdout.log'
        self.assertEqual(log.read_text(),'original failure\n')
        self.assertEqual(receipt['logs']['stdout.log'],hashlib.sha256(log.read_bytes()).hexdigest())

    def test_command_pass_does_not_conceal_changed_or_deleted_source(self):
        (self.root/'source.txt').write_text('before')
        code,r = self.command('from pathlib import Path;Path("source.txt").unlink()',source=['source.txt'])
        self.assertEqual(code,0)
        self.assertFalse(r['sourceUnchanged'])
        self.assertIsNone(r['sourceAfter']['source.txt'])
        self.assertTrue((self.root/'receipt/receipt.json').exists())

    def test_timeout_reports_failure(self):
        code,r = self.command('import time;time.sleep(30)',timeout=.1)
        self.assertEqual(code,1)
        self.assertTrue(r['timedOut'])

    def test_existing_receipt_not_replaced(self):
        self.command('print("one")')
        before=(self.root/'receipt/receipt.json').read_bytes()
        code,_=self.command('print("two")')
        self.assertEqual(code,2)
        self.assertEqual((self.root/'receipt/receipt.json').read_bytes(),before)

    def artifact(self,data,out='artifact'):
        path=self.root/'input.json';path.write_text(json.dumps(data))
        result=subprocess.run([sys.executable,str(ROOT/'render_artifact.py'),'--input',str(path),'--out-dir',str(self.root/out)],capture_output=True,text=True)
        return result.returncode,json.loads(result.stdout)

    def model(self):
        return {'mode':'cards','title':'<script>bad()</script>','pages':[{'title':'完整标题','body':'真实正文','sourceIds':['s']}],'sources':[{'id':'s','label':'来源','url':'https://example.com/source'}]}

    def test_escaped_content_and_bound_sources(self):
        code,r=self.artifact(self.model())
        self.assertEqual(code,0)
        html=(self.root/'artifact/index.html').read_text()
        self.assertNotIn('<script>',html)
        self.assertIn('&lt;script&gt;',html)
        self.assertIn('href="#s0"',html)
        self.assertEqual(r['htmlSha256'],hashlib.sha256(html.encode()).hexdigest())

    def test_unknown_source_and_script_url_do_not_create_output(self):
        data=self.model();data['pages'][0]['sourceIds']=['missing']
        self.assertEqual(self.artifact(data)[0],2)
        self.assertFalse((self.root/'artifact').exists())
        data=self.model();data['sources'][0]['url']='javascript:alert(1)'
        self.assertEqual(self.artifact(data)[0],2)

    def test_collision_preserves_existing_artifact(self):
        self.artifact(self.model())
        before=(self.root/'artifact/index.html').read_bytes()
        data=self.model();data['title']='replacement'
        self.assertEqual(self.artifact(data)[0],2)
        self.assertEqual((self.root/'artifact/index.html').read_bytes(),before)

if __name__=='__main__':
    unittest.main()
