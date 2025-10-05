import gzip
import tarfile
import io
from pathlib import Path

import pytest

from show_translations import ShowTranslation


def _write_gzip(path: Path, content: bytes):
    with gzip.open(path, 'wb') as gz:
        gz.write(content)


def _write_tar_gz(path: Path, files: dict[str, bytes]):
    bio = io.BytesIO()
    with tarfile.open(fileobj=bio, mode='w') as tf:
        for name, data in files.items():
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    bio.seek(0)
    with gzip.open(path, 'wb') as gz:
        gz.write(bio.read())


@pytest.fixture()
def isolated(tmp_path):
    """Retorna instância ShowTranslation e diretório doc_sources isolado."""
    # base isolada
    st = ShowTranslation(base_dir=tmp_path)
    doc_sources = tmp_path / 'doc_sources'
    doc_sources.mkdir(exist_ok=True)
    return st, doc_sources


def test_extract_text_single_file(isolated):
    st, doc_sources = isolated
    path = doc_sources / 'TR123.gz'
    _write_gzip(path, b'conteudo exemplo')
    txt = st.extract_text(123)
    assert 'conteudo exemplo' in txt


def test_extract_archive_single_file(isolated):
    st, doc_sources = isolated
    path = doc_sources / 'TR001.gz'
    _write_gzip(path, b'unico arquivo')
    out_dir = st.extract_archive(1)
    created = out_dir / 'TR001.txt'
    assert created.exists()
    assert created.read_text() == 'unico arquivo'


def test_extract_archive_tar(isolated):
    st, doc_sources = isolated
    path = doc_sources / 'TR010.gz'
    _write_tar_gz(path, {'a.txt': b'A', 'b/b.txt': b'Bdata'})
    out_dir = st.extract_archive(10)
    assert (out_dir / 'a.txt').exists()
    assert (out_dir / 'b' / 'b.txt').read_text() == 'Bdata'


def test_verify_user_translations_choice(isolated):
    st, doc_sources = isolated
    # número 2 não existe inicialmente
    res_missing = st.verify_user_translations_choice([2])
    assert res_missing[2] == 'missing-archive'

    # cria o gzip e verifica extração automática
    path = doc_sources / 'TR002.gz'
    _write_gzip(path, b'dados')
    res = st.verify_user_translations_choice([2])
    assert res[2] in {'extracted', 'ok'}
    # segunda chamada deve ser ok
    res2 = st.verify_user_translations_choice([2])
    assert res2[2] == 'ok'
