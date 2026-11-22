# FollowBack

Ferramenta web para comparar seus seguidores e a lista de perfis que você segue no Instagram.
Escolha os dois arquivos exportados, veja quem não segue você de volta, suas conexões mútuas
e quem segue você. A aplicação não pede sua senha nem mantém os arquivos armazenados.

## Integrantes
- Helena Diniz Faria
- Nathálly Oliveira
- Clara Garcia Tavares

## Sobre o sistema
Envie os arquivos JSON de seguidores e de seguindo exportados do Instagram. Se a exportação
dividir os seguidores em vários arquivos `followers_*.json`, selecione todos eles para que as
listas sejam unificadas antes da comparação. O FollowBack mostra quem não segue você de volta,
as conexões mútuas e quem segue você. Não é necessário informar a senha do Instagram.

## Tecnologias
- Python para a comparação das listas e para a API serverless.
- HTML, CSS e JavaScript para a interface responsiva.
- pytest e coverage.py para testes unitários e medição de cobertura.
- Playwright para testes end-to-end.
- GitHub Actions para executar testes e cobertura em Linux, macOS e Windows.
- Vercel para hospedar a aplicação e a API.

## Uso de IA
O GitHub Copilot foi utilizado como ferramenta de apoio para implementar e revisar a interface,
a leitura dos arquivos e os testes. As sugestões foram verificadas e adaptadas pela equipe.

## Publicação
O repositório está estruturado para deploy na Vercel: a pasta `public/` contém a página estática
e `api/analyze.py` é a função da API. Para publicar, importe o repositório em
[vercel.com](https://vercel.com/), mantenha a raiz do projeto como diretório raiz e use as
configurações padrão de build. A Vercel detecta os arquivos estáticos e a função Python.
O runtime está fixado em Python 3.12 pelo arquivo `.python-version`. Para executar `vercel dev`
localmente, instale Python 3.12 e confirme que `python3 --version` retorna essa versão; o CLI
usa o Python disponível no `PATH` para executar a função local.

## Execução dos testes
O projeto tem três tipos de verificação:

- **Testes unitários** (`tests/unit/`, pytest): 64 casos cobrindo a extração de usernames
  dos JSONs do Instagram e de CSVs, a comparação das listas e a API `api/analyze.py`.
- **Testes end-to-end** (`tests/e2e/`, Playwright): 11 cenários no navegador, com upload
  de arquivos, mensagens de erro, botão "Nova análise" e layout em tela de celular.
- **Cobertura** (coverage.py via pytest-cov): mínimo exigido de 80%.

O workflow `.github/workflows/tests.yml` roda tudo isso automaticamente a cada push e pull
request, em Linux, macOS e Windows.

Para rodar localmente:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m playwright install chromium
pytest tests --cov=followback --cov=api --cov-report=term-missing --cov-fail-under=80
```

Para rodar só uma parte: `pytest tests/unit` (unitários) ou `pytest tests/e2e` (end-to-end).
