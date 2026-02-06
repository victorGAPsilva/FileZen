# FileZen - Seu Organizador Digital

O **FileZen** é um sistema leve e seguro que organiza seus arquivos digitais automaticamente, movendo-os para pastas categorizadas para manter seu computador limpo e produtivo.

## ✨ Funcionalidades

- **Monitoramento Automático**: Vigia pastas como Downloads e Documentos.
- **Categorização Inteligente**: Separa arquivos por tipo (Imagens, Vídeos, Documentos, etc.).
- **Segurança**: Nunca exclui seus arquivos. Se houver conflito de nomes, ele renomeia automaticamente.
- **Log de Atividades**: Mantém um histórico do que foi organizado na pasta `logs`.
- **Modo Silencioso**: Pode rodar em segundo plano sem atrapalhar seu trabalho.

## 🚀 Como Usar

### Instalação e Execução (Windows)

1. **Configuração (Opcional)**:
   - Abra o arquivo `config.json` com o Bloco de Notas se desejar alterar as pastas monitoradas ou adicionar novos tipos de arquivo.

2. **Iniciar**:
   - Dê um duplo clique no arquivo `Iniciar FileZen.bat` (será criado na instalação).
   - Uma janela preta pode aparecer rapidamente e fechar. Isso é normal, o programa está rodando em segundo plano.

3. **Verificar Funcionamento**:
   - Vá até sua pasta de `Downloads`. Crie ou baixe um arquivo de teste.
   - Aguarde alguns segundos (padrão: 60 segundos).
   - Verifique se apareceu uma pasta chamada `Organizados` com seu arquivo dentro da subpasta correta.

4. **Parar**:
   - Para parar, você pode fechar a janela do terminal (se estiver aberta) ou finalizar o processo Python no Gerenciador de Tarefas.

## ⚙️ Configuração (config.json)

Você pode personalizar o comportamento editando o arquivo `config.json`:

```json
{
    "monitored_folders": ["Downloads", "Documents"], 
    "destination_folder": "Organizados",
    "scan_interval_seconds": 60,
    "organize_by_date": false,
    "extensions": {
        "Imagens": [".jpg", ".png", ...],
        ...
    }
}
```

- **monitored_folders**: Lista de nomes de pastas padrão ou caminhos completos (ex: `"C:\\MeusArquivos"`).
- **organize_by_date**: Mude para `true` se quiser subpastas por ano/mês dentro das categorias.

## 🛠️ Requisitos Técnicos

- **Python 3**: Necessário estar instalado no computador.
- **Bibliotecas**: Utiliza apenas bibliotecas padrão do Python (leve e compatível).

## 💡 Sugestões para o Futuro (Versão Pro)

- Interface Gráfica (GUI) para configuração fácil.
- IA para categorizar documentos pelo conteúdo (Faturas, Contratos).
- Compressão automática de arquivos antigos.
- Backup em nuvem integrado.

---
**FileZen** - Organização sem esforço.

**SOBRE!!!!** -filezen ainda esta em desenvolvimeto futuras versões teram melhor funcionamento
