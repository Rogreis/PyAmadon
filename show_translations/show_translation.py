from __future__ import annotations

import gzip
import io
import tarfile
from pathlib import Path
from typing import Optional


class ShowTranslation:
    """Fornece métodos para extrair e retornar conteúdo de arquivos de tradução compactados.

    Convenção de nomes: arquivos ficam em `doc_sources/` na raiz do projeto,
    com padrão `TR###.gz` onde ### é número zero‑padded a 3 dígitos.

    Exemplo: para argumento 7 -> TR007.gz

    Uso rápido:
        >>> from show_translations import ShowTranslation
        >>> st = ShowTranslation()
        >>> texto = st.extract_text(44)  # lê TR044.gz e retorna str
        >>> path = st.extract_to_file(44)  # gera TR044.txt
    """

    def __init__(self, base_dir: Optional[Path] = None, sources_subdir: str = "doc_sources") -> None:
        self.project_root = base_dir or Path(__file__).resolve().parent.parent
        self.sources_dir = self.project_root / sources_subdir

    def _file_path(self, number: int) -> Path:
        if number < 0:
            raise ValueError("Número não pode ser negativo")
        name = f"TR{number:03d}.gz"
        return self.sources_dir / name

    def extract_text(self, number: int, encoding: str = "utf-8") -> str:
        """Abre o arquivo TR###.gz e retorna texto descompactado.

        Compatibilidade: este método assume que o .gz contém apenas UM arquivo
        de texto (stream simples). Se futuramente os pacotes passarem a ser
        tarballs (tar.gz) com múltiplos arquivos, use `extract_archive`.
        """
        path = self._file_path(number)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        with gzip.open(path, "rb") as f:
            data = f.read()
        # tentativa de decodificar como texto puro
        return data.decode(encoding)

    # --- Novos métodos multi-arquivo ---
    def extract_archive(self, number: int, overwrite: bool = False) -> Path:
        """Extrai todos os arquivos contidos em TR###.gz para pasta doc_sources/TR###.

        Suporta dois formatos:
          1. gzip de um único arquivo (cria arquivo único dentro da pasta)
          2. tar.gz (gzip contendo um tar) -> extrai árvore inteira

        Args:
            number: número da tradução
            overwrite: se True, substitui arquivos existentes

        Returns:
            Caminho da pasta destino (doc_sources/TR###)
        """
        archive_path = self._file_path(number)
        if not archive_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {archive_path}")
        target_dir = self.sources_dir / f"TR{number:03d}"
        target_dir.mkdir(parents=True, exist_ok=True)

        # Ler bytes do gzip
        with open(archive_path, 'rb') as fh:
            raw = fh.read()
        try:
            decompressed = gzip.decompress(raw)
        except OSError as e:
            raise RuntimeError(f"Falha ao descomprimir gzip: {archive_path}: {e}") from e

        bio = io.BytesIO(decompressed)
        # Tentar abrir como tar diretamente (tarfile.is_tarfile não aceita fileobj)
        try:
            with tarfile.open(fileobj=bio, mode='r:*') as tf:
                # Se conseguir abrir como tar, extraímos membros
                for member in tf.getmembers():
                    if member.isdir():
                        continue
                    out_path = target_dir / member.name
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    if out_path.exists() and not overwrite:
                        continue
                    extracted = tf.extractfile(member)
                    if extracted is None:
                        continue
                    out_path.write_bytes(extracted.read())
        except tarfile.TarError:
            # Não é tar: tratar como um único arquivo
            bio.seek(0)
            single_name = target_dir / f"TR{number:03d}.txt"
            if single_name.exists() and not overwrite:
                return target_dir
            single_name.write_bytes(bio.read())
        return target_dir

    def verify_user_translations_choice(self, chosen: list[int], auto_extract: bool = True) -> dict[int, str]:
        """Verifica se cada tradução escolhida possui pasta expandida.

        Para cada número em `chosen`:
          - Confere existência de TR###.gz
          - Verifica se `doc_sources/TR###/` existe com algum conteúdo
          - Se não existir e `auto_extract=True`, chama `extract_archive`.

        Returns:
            dict {numero: status}
              status pode ser: 'ok', 'missing-archive', 'extracted', 'exists'
        """
        results: dict[int, str] = {}
        for n in chosen:
            try:
                archive = self._file_path(n)
                if not archive.exists():
                    results[n] = 'missing-archive'
                    continue
                folder = self.sources_dir / f"TR{n:03d}"
                if folder.exists() and any(folder.iterdir()):
                    results[n] = 'ok'
                    continue
                if auto_extract:
                    self.extract_archive(n)
                    results[n] = 'extracted'
                else:
                    results[n] = 'exists' if folder.exists() else 'pending'
            except Exception as e:  # coleta falhas isoladas sem interromper
                results[n] = f'error:{e.__class__.__name__}'
        return results

    def extract_to_file(self, number: int, out_dir: Optional[Path] = None, overwrite: bool = False, encoding: str = "utf-8") -> Path:
        """Extrai o conteúdo para um arquivo de texto ao lado ou em `out_dir`.

        O nome de saída será `TR###.txt`.
        Retorna o caminho do arquivo criado.
        """
        text = self.extract_text(number, encoding=encoding)
        target_dir = out_dir or self.sources_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        out_path = target_dir / f"TR{number:03d}.txt"
        if out_path.exists() and not overwrite:
            raise FileExistsError(f"Arquivo de saída já existe: {out_path}")
        out_path.write_text(text, encoding=encoding)
        return out_path

__all__ = ["ShowTranslation"]
