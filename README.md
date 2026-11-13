# FollowBack

## Integrantes
- (nomes completos do grupo)

## Sobre o sistema
Aplicação web que recebe os arquivos `followers.json` e `following.json` exportados do Instagram e mostra quem você segue e não te segue de volta. Nenhum dado é armazenado.

## Tecnologias
Python (lógica e API serverless no Vercel), HTML/CSS/JS, pytest, coverage.py, Playwright, GitHub Actions.

## Uso de IA
(preencher: ferramentas usadas e como contribuíram)

## Execução dos testes
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest tests/unit --cov=followback --cov-report=term-missing
```
