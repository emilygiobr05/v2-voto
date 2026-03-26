"""
Aplicação Web - Sistema de Análise Eleitoral
Ponto de entrada para deploy em produção (Heroku, Render, Railway, etc.)
"""

import os
import sys
from pathlib import Path

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.dashboard import create_dashboard
except ImportError as e:
    print(f"❌ Erro ao importar módulo: {e}")
    print("   Verifique se os arquivos em src/ estão presentes.")
    print("   Execute: pip install -r requirements.txt")
    sys.exit(1)

# Criar aplicação
app = create_dashboard('.')

# Servidor para Gunicorn
server = app.server

if __name__ == '__main__':
    # Porta do ambiente ou 8050 como padrão
    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Iniciando servidor na porta {port}...")
    app.run(debug=debug, host='0.0.0.0', port=port)
