# Documentação de Conteúdos (Amadon)

Este guia explica:

1. Esquema lógico de links `doc://`
2. Como criar documentos (HTML ou Markdown)
3. Como funcionam as âncoras e rolagem automática
4. Como montar/atualizar a árvore (`documentos_tree.json`)
5. Como injetar conteúdo Markdown em outros módulos
6. Convenções de nomenclatura (arquivo, âncora, títulos)
7. Boas práticas e futuras extensões

---
## 1. Esquema de Links `doc://`

Formato final adotado:
```
doc://DocNNN.html#pAAA_BBB_CCC
```
Onde:
- `DocNNN.html` é o nome físico do arquivo base (pode ser `.html` ou `.md` na pasta de documentos, a extensão do link usa `.html` como canonical).
- O fragmento após `#` é a âncora lógica (`pAAA_BBB_CCC`).

Você pode omitir a âncora em casos especiais (rolará para o topo), porém recomenda-se manter sempre para consistência.

### Resolução Interna
1. O código extrai o nome de arquivo (ex: `Doc003.html`).
2. Procura fisicamente: primeiro `assets/docs/Doc003.html`, depois `assets/docs/Doc003.md`.
3. Carrega o conteúdo:
   - HTML: usado diretamente.
   - Markdown: convertido via `markdown2`.
4. Injeta JavaScript que tenta localizar o elemento com `id="pAAA_BBB_CCC"` e fazer scroll suave + potencial destaque.

Se a âncora não existir, (futuro) poderá ser exibida uma nota de aviso no topo.

---
## 2. Criando Documentos (HTML ou Markdown)

Coloque os arquivos em:
```
assets/docs/
```
Exemplos de nomes válidos:
- `Doc001.html`
- `Doc002.md`
- `Doc010.html`

### Estrutura Recomendada (HTML)
```html
<h1 id="p001_000_000">Título Geral</h1>
<p>Introdução...</p>
<h2 id="p001_001_000">Seção 1</h2>
<p>Texto...</p>
<h3 id="p001_001_001">Subseção Detalhada</h3>
```

### Estrutura Recomendada (Markdown)
Use cabeçalhos normais e injete IDs manualmente se quiser precisão absoluta:
```markdown
# Título Geral {#p001_000_000}

Introdução.

## Seção 1 {#p001_001_000}

Texto.

### Subdetalhe {#p001_001_001}
```
Nem todos os conversores mantêm `{#id}` – o `markdown2` base ignora essa sintaxe. Alternativas:
- Inserir HTML inline no markdown:
  ```markdown
  <h2 id="p001_001_000">Seção 1</h2>
  ```
- Ou pós-processar (futuro) para injetar IDs.

---
## 3. Convenção de Âncoras `pAAA_BBB_CCC`

Padrão: três blocos numéricos separados por `_`.
- `AAA`: Parte / Macro Agrupador (001, 002 ...)
- `BBB`: Seção / Grupo Médio
- `CCC`: Item / Subnível granular

Exemplo progressivo:
- Raiz do documento: `p001_000_000`
- Seção 1: `p001_001_000`
- Documento/Subitem 1: `p001_001_001`
- Documento/Subitem 2: `p001_001_002`

Isso facilita gerar árvore e manter ordenação lexicográfica estável.

---
## 4. Árvore de Conteúdo (`documentos_tree.json`)

Local: `assets/data/documentos_tree.json`

Formato simplificado:
```json
{
  "nodes": [
    {
      "titulo": "Parte I",
      "link": "doc://Doc001.html#p001_000_000",
      "filhos": [
        {
          "titulo": "Seção 1",
          "link": "doc://Doc002.html#p001_001_000",
          "filhos": [
            {"titulo": "Documento 1", "link": "doc://Doc003.html#p001_001_001"}
          ]
        }
      ]
    }
  ]
}
```

### Recomendações
- Sempre usar `titulo` (string) e `link`.
- `filhos` opcional (array). Se ausente ou vazio, é folha.
- Manter ordenação semântica (não apenas alfabética). Use zero padding para preservar ordem.

### Processo de Atualização
1. Criar/editar arquivos `DocNNN`.
2. Definir/ajustar IDs de âncora dentro do conteúdo.
3. Atualizar o JSON com links coerentes.
4. Testar clicando na árvore (log mostrará eventuais falhas de resolução).

---
## 5. Injetando Markdown em Outros Módulos

Qualquer ação derivada de `ToolBar_Base` pode usar:
```python
self.inject_markdown(markdown_text, target='right', clear=True)
```
Parâmetros importantes:
- `css`: estilização extra.
- `use_bootstrap`: por padrão `True` (pode desligar para carregamento mais leve).
- `extras`: lista de extras do `markdown2`.

---
## 6. Convenções de Nomenclatura

| Elemento            | Regra                                 | Exemplo                |
|---------------------|---------------------------------------|------------------------|
| Arquivo Documento   | `DocNNN.(html|md)`                    | `Doc012.md`            |
| ID Raiz do Doc      | `pAAA_000_000`                        | `p002_000_000`         |
| ID Seção Principal  | `pAAA_BBB_000`                        | `p002_001_000`         |
| ID Item/Subseção    | `pAAA_BBB_CCC`                        | `p002_001_003`         |
| Link JSON           | `doc://DocNNN.html#pAAA_BBB_CCC`      | `doc://Doc012.html#p002_001_003` |

Notas:
- Mesmo para markdown o link mantém `.html` como canonical.
- IDs consistentes facilitam busca, cache futuro e validação.

---
## 7. Boas Práticas e Extensões Futuras

Sugestões:
- Criar um script de validação que leia `documentos_tree.json`, abra cada arquivo e verifique se a âncora existe.
- Adicionar highlight pós-scroll (ex.: adicionar classe CSS por 2–3 segundos).
- Implementar cache de conteúdo convertido de Markdown para reduzir custo em reaberturas.
- Adicionar índice de navegação lateral gerado dinamicamente (scan de `<h1..h3>`).
- Internacionalização: permitir múltiplos conjuntos de docs (ex.: `docs/pt-BR`, `docs/en-US`).

---
## 8. Debugging Rápido

Se um clique não abre conteúdo:
1. Verifique o log: deve mostrar tentativa e caminho real.
2. Confirme que o arquivo existe em `assets/docs/`.
3. Verifique se a extensão `.md` ou `.html` está correta.
4. Confirme que a âncora existe (procure por `id="pXXX_YYY_ZZZ"`).

---
## 9. Exemplo de Fluxo Completo
1. Criar `assets/docs/Doc020.md`.
2. Inserir conteúdo com `<h1 id="p003_000_000">Título</h1>` etc.
3. Acrescentar nó no JSON com `doc://Doc020.html#p003_000_000`.
4. Rodar aplicação e clicar → conteúdo renderizado e rolagem ao topo.

---
## 10. Checklist Rápido de Consistência
- [ ] IDs seguem padrão `pNNN_NNN_NNN`
- [ ] JSON sem vírgulas sobrando
- [ ] Todos os arquivos citados existem
- [ ] Âncoras presentes no HTML/Markdown final
- [ ] Sem duplicação de IDs

---
Dúvidas adicionais ou deseja um script de validação automática? Basta pedir.
