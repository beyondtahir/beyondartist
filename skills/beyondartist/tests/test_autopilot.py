"""Autopilot helper tests. They use synthetic images and make no network calls."""
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import autopilot  # noqa: E402

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None


class Parsing(unittest.TestCase):
    def test_video_links(self):
        for url in ('https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=3', 'https://youtu.be/dQw4w9WgXcQ?si=x',
                    'https://m.youtube.com/watch?v=dQw4w9WgXcQ', 'https://www.youtube.com/shorts/dQw4w9WgXcQ',
                    'https://www.youtube.com/embed/dQw4w9WgXcQ', 'dQw4w9WgXcQ'):
            self.assertEqual(autopilot.video_id(url), 'dQw4w9WgXcQ', url)

    def test_other_hosts_and_bad_ids_are_refused(self):
        for url in ('https://evil.example/watch?v=dQw4w9WgXcQ', 'https://www.youtube.com/watch?v=short',
                    'https://youtube.com.evil.example/watch?v=dQw4w9WgXcQ', '--exec=whoami', ''):
            with self.assertRaises(autopilot.AutopilotError, msg=url):
                autopilot.video_id(url)

    def test_captions_lose_timing_tags_and_repeats(self):
        raw = 'WEBVTT\nKind: captions\nLanguage: en\n\n00:00.000 --> 00:01.000\n<c>Hello</c> &amp; hi\n\n00:01.000 --> 00:02.000\nHello &amp; hi\nnext line\n'
        self.assertEqual(autopilot.captions_to_text(raw), 'Hello & hi next line')

    def test_copy_check_finds_misspelling_missing_and_extra_words(self):
        found = {'every': {'word': 'EVERY', 'confidence': 95, 'box': [0, 0, 1, 1]},
                 'strr': {'word': 'STRR', 'confidence': 90, 'box': [0, 0, 1, 1]},
                 'lorem': {'word': 'LOREM', 'confidence': 91, 'box': [0, 0, 1, 1]}}
        result = autopilot.check_copy('Every star real', found)
        self.assertEqual(result['exact'], ['every'])
        self.assertEqual(result['near'], [{'expected': 'star', 'read': 'STRR'}])
        self.assertEqual(result['missing'], ['real'])
        self.assertEqual(result['unexpected'], ['LOREM'])


class TypeHtml(unittest.TestCase):
    def spec(self, **block):
        base = {'text': 'Hi', 'x': 1, 'y': 2, 'width': 3, 'size': 4}
        base.update(block)
        return {'width': 100, 'height': 50, 'blocks': [base]}

    def test_text_cannot_inject_markup(self):
        page = autopilot.build_type_html(self.spec(text='<script>alert(1)</script>'), None)
        self.assertNotIn('<script>alert', page)
        self.assertIn('&lt;script&gt;', page)

    def test_style_values_cannot_break_out(self):
        page = autopilot.build_type_html(self.spec(color='red"><img src=x onerror=alert(1)>'), None)
        self.assertNotIn('<img src=x', page)

    def test_urdu_uses_nastaliq_and_right_to_left(self):
        page = autopilot.build_type_html(self.spec(text='اردو', lang='ur'), None)
        self.assertIn('Noto+Nastaliq+Urdu', page)
        self.assertIn('dir="rtl"', page)
        self.assertIn('text-align:right', page)

    def test_font_check_uses_the_block_weight(self):
        # A real run showed that checking only the default weight reports loaded fonts as missing.
        self.assertIn('getComputedStyle(el).fontWeight', autopilot.MEASURE)

    def test_overflow_is_measured_against_the_canvas(self):
        # Headless browsers can report a viewport smaller than the canvas.
        self.assertIn('document.body.offsetHeight', autopilot.MEASURE)
        self.assertNotIn('innerHeight', autopilot.MEASURE)

    def test_line_breaks_survive(self):
        self.assertIn('One<br>Two', autopilot.build_type_html(self.spec(text='One\nTwo'), None))


@unittest.skipIf(Image is None, 'Pillow is not installed')
class Pixels(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder)

    def image(self, name, size=(1280, 720), background=(10, 10, 10), rectangle=None, fill=(255, 255, 255)):
        canvas = Image.new('RGB', size, background)
        if rectangle:
            ImageDraw.Draw(canvas).rectangle(rectangle, fill=fill)
        path = self.folder / name
        canvas.save(path)
        return path

    def states(self, report):
        return {row['check']: row['state'] for row in report['checks']}

    def test_wrong_shape_and_small_files_fail(self):
        report = autopilot.gate_report(self.image('a.png', (1000, 1000)), 'youtube-thumbnail')
        self.assertEqual(self.states(report)['format'], 'fail')
        self.assertEqual(report['verdict'], 'FAIL')
        small = autopilot.gate_report(self.image('b.png', (640, 360)), 'youtube-thumbnail')
        self.assertEqual(self.states(small)['format'], 'fail')

    def test_clean_design_can_pass_but_still_requires_visual_review(self):
        path = self.image('c.png', rectangle=(60, 60, 700, 400))
        report = autopilot.gate_report(path, 'youtube-thumbnail', boxes=[[0, 40, 720, 380]])
        self.assertEqual(report['verdict'], 'PASS', report['checks'])
        self.assertIn('Inspect the art', report['still_required'])
        self.assertIn('Clicks', report['not_measured'])

    def test_overlay_collision_fails(self):
        path = self.image('d.png', rectangle=(1000, 600, 1279, 719))
        report = autopilot.gate_report(path, 'youtube-thumbnail', boxes=[[1000, 600, 279, 119]])
        self.assertEqual(self.states(report)['overlay_zone'], 'fail')

    def test_low_contrast_and_tiny_text_fail(self):
        path = self.image('e.png', background=(120, 120, 120), rectangle=(100, 100, 500, 300), fill=(135, 135, 135))
        report = autopilot.gate_report(path, 'youtube-thumbnail', boxes=[[100, 100, 400, 200]])
        self.assertEqual(self.states(report)['phone_contrast'], 'fail')
        tiny = autopilot.gate_report(self.image('f.png', rectangle=(100, 100, 400, 110)), 'youtube-thumbnail', boxes=[[100, 95, 300, 20]])
        self.assertEqual(self.states(tiny)['phone_size'], 'fail')

    def test_flat_image_is_sent_to_review(self):
        report = autopilot.gate_report(self.image('g.png', background=(90, 90, 90)), 'youtube-thumbnail')
        self.assertEqual(self.states(report)['squint_contrast'], 'review')
        self.assertEqual(report['verdict'], 'REVIEW')

    def test_repeating_past_work_fails(self):
        first = self.image('h.png', rectangle=(100, 100, 600, 500))
        second = self.image('i.png', rectangle=(100, 100, 600, 500))
        different = self.image('j.png', background=(200, 30, 30), rectangle=(800, 300, 1200, 700), fill=(10, 10, 200))
        self.assertEqual(self.states(autopilot.gate_report(first, 'youtube-thumbnail', history=[second]))['repetition'], 'fail')
        self.assertEqual(self.states(autopilot.gate_report(first, 'youtube-thumbnail', history=[different]))['repetition'], 'pass')

    def test_an_image_is_not_compared_with_itself(self):
        first = self.image('k.png', rectangle=(100, 100, 600, 500))
        report = autopilot.gate_report(first, 'youtube-thumbnail', history=[first])
        self.assertNotIn('repetition', self.states(report))

    def test_distinctness_is_reported_as_information_only(self):
        same = [self.image('s%d.png' % n, background=(20, 40, 90), rectangle=(100, 100, 500, 400)) for n in range(4)]
        odd = self.image('odd.png', background=(240, 200, 20), rectangle=(700, 200, 1200, 700), fill=(180, 10, 10))
        report = autopilot.gate_report(odd, 'youtube-thumbnail', competitors=same)
        row = [r for r in report['checks'] if r['check'] == 'feed_distinctness'][0]
        self.assertEqual((row['state'], row['rank'], row['of']), ('info', 1, 5))
        self.assertIn('not a click prediction', row['detail'])

    def test_feed_renders_both_themes_without_putting_candidate_first(self):
        candidate = self.image('candidate.png', background=(200, 0, 0))
        competitors = self.folder / 'competitors'
        competitors.mkdir()
        for n in range(4):
            Image.new('RGB', (1280, 720), (0, 0, 200)).save(competitors / ('c%d.png' % n))
        out = self.folder / 'feed'
        code = autopilot.main(['feed', str(candidate), '--competitors', str(competitors), '--title', 'Test', '--out', str(out)])
        self.assertEqual(code, 0)
        for theme in ('dark', 'light'):
            canvas = Image.open(out / ('feed-candidate-%s.png' % theme)).convert('RGB')
            self.assertEqual(canvas.getpixel((60, 80)), (0, 0, 200))
            self.assertEqual(canvas.getpixel((60, 80 + 305)), (200, 0, 0))
        report = json.loads((out / 'feed-report.json').read_text())
        self.assertIn('does not measure real clicks', report['limit'])

    def test_package_exports_within_limit_with_checksums(self):
        path = self.image('m.png', (2560, 1440), rectangle=(100, 100, 900, 900))
        out = self.folder / 'delivery'
        self.assertEqual(autopilot.main(['package', str(path), '--name', 'job', '--out', str(out)]), 0)
        manifest = json.loads((out / 'manifest.json').read_text())
        upload = out / 'job-1280x720.jpg'
        self.assertEqual(Image.open(upload).size, (1280, 720))
        self.assertLessEqual(upload.stat().st_size, 2_000_000)
        self.assertEqual({row['file'] for row in manifest['files']}, {'job-master.png', 'job-1280x720.jpg', 'job-phone-preview.jpg'})

    def test_package_refuses_to_crop_a_different_shape(self):
        path = self.image('n.png', (1080, 1350))
        self.assertEqual(autopilot.main(['package', str(path), '--out', str(self.folder / 'x')]), 1)
        self.assertFalse((self.folder / 'x').exists())

    def test_gate_exit_codes(self):
        self.assertEqual(autopilot.main(['gate', str(self.image('p.png', (800, 800))), '--out', str(self.folder / 'r.json')]), 1)
        self.assertEqual(json.loads((self.folder / 'r.json').read_text())['verdict'], 'FAIL')
        self.assertEqual(autopilot.main(['gate', str(self.image('q.png', background=(90, 90, 90)))]), 3)


class Commands(unittest.TestCase):
    def test_commands_point_at_files_that_exist(self):
        repository = ROOT.parents[1]
        for name in ('autopilot', 'thumbnail', 'carousel', 'brand-setup'):
            text = (repository / 'commands' / (name + '.md')).read_text()
            self.assertTrue(text.startswith('---\ndescription: '), name)
            self.assertIn('$ARGUMENTS', text)
        self.assertTrue((ROOT / 'references/autopilot.md').is_file())

    def test_routing_hardcodes_no_model(self):
        repository = ROOT.parents[1]
        files = [ROOT / 'SKILL.md', ROOT / 'references/autopilot.md', repository / 'README.md', repository / 'docs/autopilot.md',
                 repository / 'docs/getting-started.md'] + sorted((repository / 'commands').glob('*.md'))
        pattern = re.compile(r'gpt-image|chatgpt-image|dall-?e|claude-(?:opus|sonnet|haiku|fable)|imagen-|gemini-\d', re.I)
        for path in files:
            self.assertIsNone(pattern.search(path.read_text()), path.name)

    def test_autopilot_guide_requires_best_available_and_disclosure(self):
        guide = (ROOT / 'references/autopilot.md').read_text()
        self.assertIn('## Best available model', guide)
        self.assertIn('Which image model or tool made the work', guide)

    def test_autopilot_guide_forbids_publishing_and_click_promises(self):
        guide = (ROOT / 'references/autopilot.md').read_text()
        self.assertIn('does not upload, publish, schedule or message', guide)
        self.assertIn('Never promise clicks', guide)
        self.assertIn('not instructions', guide)
        self.assertIn('Never edit a threshold', guide)


if __name__ == '__main__':
    unittest.main()
