"""Real Artcraft round trips and workspace isolation, using disposable stores."""
import io
import zipfile

import pytest
from PIL import Image, ImageChops

from medillustrate import core, exports, graphics
from medillustrate.workspace import Conflict, Store, get_frame


@pytest.fixture(params=['photo', 'vector'])
def engine(request):
    name = request.param
    try:
        graphics.binary(name)
    except core.IllustrationError:
        pytest.skip(name + ' engine binary is not installed')
    return name


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / 'workspace.sqlite3')


def artwork(engine):
    if engine == 'vector':
        return 'drawing.svg', b'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="48" viewBox="0 0 64 48"><rect x="2" y="2" width="20" height="20" fill="#204060"/></svg>'
    out = io.BytesIO()
    Image.new('RGB', (64, 48), (20, 40, 60)).save(out, 'PNG')
    return 'photo.png', out.getvalue()


def imported(store, engine):
    p = store.create()['project']['id']
    name, raw = artwork(engine)
    result = graphics.import_artwork(store, p, 1, engine, name, raw)
    assert result['version'] == 2
    return p


def edit_steps(engine):
    return [{'command': 'image.adjustments.invert', 'params': {}}] if engine == 'photo' else [
        {'command': 'shape.rectangle', 'params': {'x': 35, 'y': 5, 'width': 20, 'height': 25}}
    ]


def image(store, pid, document):
    return Image.open(io.BytesIO(store.get_media(pid, document['preview_media_id'])['data'])).convert('RGB')


def ids(info, engine):
    def walk(rows):
        return [(row['id'], row.get('kind'), row.get('name')) for row in rows] + [
            entry for row in rows for entry in walk(row.get('children', []))
        ]
    return walk(info['layers'])


def test_real_engine_changes_pixels_and_reopens_native(store, engine):
    pid = imported(store, engine)
    original = store.get(pid)
    first = get_frame(original['project'])['document']
    original_native = store.get_media(pid, first['native_media_id'])['data']
    before = image(store, pid, first)
    proposal = graphics.propose(store, pid, 2, engine, edit_steps(engine), 'Edit artwork')

    # A preview is a real render, but leaves both the accepted project and native source intact.
    assert store.get(pid) == original
    assert store.get_media(pid, first['native_media_id'])['data'] == original_native
    candidate = proposal['operations'][0]['document']
    after = image(store, pid, candidate)
    assert before.size == after.size == (64, 48)
    assert ImageChops.difference(before, after).getbbox() is not None
    if engine == 'photo':
        assert before.getpixel((10, 10)) == (20, 40, 60)
        assert after.getpixel((10, 10)) == (235, 215, 195)
    else:
        assert len(ids(candidate['inspection'], engine)) == len(ids(first['inspection'], engine)) + 1
        assert '<svg' in store.get_media(pid, candidate['svg_media_id'])['data'].decode()

    accepted = store.decide(pid, proposal['id'], True)
    assert accepted['version'] == 3
    doc = get_frame(accepted['project'])['document']
    assert doc['native_media_id'] == candidate['native_media_id']
    assert doc['native_media_id'] != first['native_media_id']
    # Inspection is obtained by reopening the actual accepted native bytes in another process.
    reopened = graphics.inspect(store, pid, engine)
    assert ids(reopened, engine) == ids(candidate['inspection'], engine)
    assert store.get_media(pid, first['native_media_id'])['data'] == original_native
    with pytest.raises(Conflict):
        store.decide(pid, proposal['id'], True)


def test_restore_and_portable_bundle_keep_native_objects(store, engine):
    pid = imported(store, engine)
    initial = get_frame(store.get(pid)['project'])['document']
    proposal = graphics.propose(store, pid, 2, engine, edit_steps(engine), 'Edit artwork')
    changed = store.decide(pid, proposal['id'], True)
    latest = get_frame(changed['project'])['document']
    restored = store.restore(pid, 3, 2)
    assert restored['version'] == 4
    assert get_frame(restored['project'])['document'] == initial
    assert ids(graphics.inspect(store, pid, engine), engine) == ids(initial['inspection'], engine)
    store.restore(pid, 4, 3)

    raw = exports.bundle(store, pid)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert not any('control' in name for name in z.namelist())
        assert z.read('media/' + latest['native_media_id']) == store.get_media(pid, latest['native_media_id'])['data']
    copy = exports.import_bundle(store, raw)
    copy_pid = copy['project']['id']
    assert copy_pid != pid
    copy_doc = get_frame(copy['project'])['document']
    # Media identities are scoped to the new project; native internal object identities survive.
    for key in ('native_media_id', 'preview_media_id') + (('svg_media_id',) if engine == 'vector' else ()):
        assert copy_doc[key] != latest[key]
        copied_bytes = store.get_media(copy_pid, copy_doc[key])['data']
        source_bytes = store.get_media(pid, latest[key])['data']
        if key == 'preview_media_id':
            # Bundle imports normalize raster encodings; rendered RGBA pixels must survive.
            copied_pixels = Image.open(io.BytesIO(copied_bytes)).convert('RGBA')
            source_pixels = Image.open(io.BytesIO(source_bytes)).convert('RGBA')
            assert copied_pixels.size == source_pixels.size
            assert copied_pixels.tobytes() == source_pixels.tobytes()
        else:
            assert copied_bytes == source_bytes
        with pytest.raises(core.IllustrationError):
            store.get_media(copy_pid, latest[key])
    assert ids(graphics.inspect(store, copy_pid, engine), engine) == ids(latest['inspection'], engine)


def test_stale_and_rejected_graphics_proposals_preserve_work(store, engine):
    pid = imported(store, engine)
    source = store.get(pid)
    proposal = graphics.propose(store, pid, 2, engine, edit_steps(engine), 'Candidate')
    store.decide(pid, proposal['id'], False)
    assert store.get(pid) == source
    proposal = graphics.propose(store, pid, 2, engine, edit_steps(engine), 'Stale candidate')
    manual = store.edit(pid, 2, [{'op': 'project_title', 'value': 'My manual revision'}])
    with pytest.raises(Conflict):
        store.decide(pid, proposal['id'], True)
    assert store.get(pid) == manual
    with pytest.raises(Conflict):
        graphics.propose(store, pid, 2, engine, edit_steps(engine), 'Outdated request')
    assert store.get(pid) == manual


@pytest.mark.parametrize('steps', [
    [{'command': 'file.open', 'params': {'path': '/private/file'}}],
    [{'command': 'document.save', 'params': {'path': 'outside.svg'}}],
    [{'command': 'actions.play', 'params': {'action': 'read files'}}],
    [{'command': 'plugin.execute', 'params': {}}],
    [{'command': 'object.place', 'params': {'nested': {'url': 'https://example.org/image'}}}],
    [{'command': 'object.rename', 'params': {'name': '../../private/file'}}],
    [{'command': 'object.rename', 'params': {'name': '/private/file'}}],
    [{'command': 'object.rename', 'params': {'values': [{'directory': 'elsewhere'}]}}],
])
def test_steps_refuse_external_files_and_indirect_execution(steps):
    with pytest.raises(core.IllustrationError):
        graphics.validate_steps(steps)


@pytest.mark.parametrize('body', [
    '<script>alert(1)</script>',
    '<foreignObject><div>active</div></foreignObject>',
    '<image href="https://example.org/image.png"/>',
    '<image href="file:///private/file"/>',
    '<use href="../outside.svg#shape"/>',
    '<rect onload="alert(1)"/>',
    '<rect style="fill:url(https://example.org/paint.svg#x)"/>',
    '<style>@import url(https://example.org/style.css)</style>',
])
def test_active_or_external_svg_is_rejected(body):
    with pytest.raises(core.IllustrationError):
        graphics.passive_svg('<svg xmlns="http://www.w3.org/2000/svg">' + body + '</svg>')


def test_local_svg_filters_and_editable_ids_survive():
    svg = '<svg xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="paint"><stop offset="0" stop-color="#204060"/></linearGradient></defs><g id="editable-shape"><rect fill="url(#paint)" width="20" height="20"/></g></svg>'
    assert graphics.passive_svg(svg) == svg
