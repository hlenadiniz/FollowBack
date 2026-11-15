# FollowBack

Ferramenta web para comparar seus seguidores e a lista de perfis que você segue no Instagram.
Escolha os dois arquivos exportados, veja quem não segue você de volta, suas conexões mútuas
e quem segue você. A aplicação não pede sua senha nem mantém os arquivos armazenados.

## Integrantes
- Helena Diniz Faria
- Nathálly Oliveira

## Sobre o sistema
Envie os CSVs de seguidores e de seguindo exportados do Instagram. Para CSVs, use uma coluna
`username` (também são reconhecidos `user_name`, `handle`, `login` e cabeçalhos equivalentes
em português) ou coloque um nome de usuário por linha. Os arquivos JSON originais do Instagram
também são aceitos. O FollowBack mostra quem não segue você de volta, as conexões mútuas e
quem segue você. Não é necessário informar a senha do Instagram.

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

## Execução dos testes
```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m playwright install chromium
pytest tests --cov=followback --cov-report=term-missing --cov-fail-under=80
```
