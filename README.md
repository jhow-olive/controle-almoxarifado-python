# Sistema de Controle de Almoxarifado

Sistema desktop desenvolvido em Python para gerenciamento de almoxarifado, controle de materiais, movimentações e rastreabilidade de equipamentos.

---

# Funcionalidades

- Login com autenticação segura
- Controle de usuários
- Cadastro de materiais
- Controle de saída e retorno
- Histórico de movimentações
- Relatórios
- Logs do sistema
- Backup do banco de dados
- Interface gráfica moderna

---

# Tecnologias Utilizadas

- Python 3
- PySide6
- MySQL
- bcrypt
- PyInstaller

---

# Estrutura do Projeto

```text
app/        -> regras de negócio
ui/         -> telas do sistema
assets/     -> imagens e estilos
logs/       -> logs do sistema
backups/    -> backups automáticos
```

---

# Instalação

## Clonar repositório

```bash
git clone https://github.com/jhow-olive/controle-almoxarifado-python.git
```

---

## Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Configurar banco de dados

Execute o arquivo:

```text
database.sql
```

no MySQL.

---

# Executar projeto

```bash
python main.py
```

---

# Gerar executável

```bash
pyinstaller main.spec
```

---

# Segurança

O sistema utiliza:

- Hash de senhas com bcrypt
- Proteção contra brute force
- Logs de autenticação
- Controle de acesso por usuário

---

# Futuras Melhorias

- Dashboard com gráficos
- Relatórios PDF
- Controle de permissões avançadas
- Sistema multiusuário em rede
- API REST
- Backup automático agendado

---

# Autor

Desenvolvido por Jhow Oliveira.

---

# Licença

Projeto para fins de estudo e uso interno.