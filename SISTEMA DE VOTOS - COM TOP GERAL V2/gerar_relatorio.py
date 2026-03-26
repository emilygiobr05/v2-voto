"""
Gerador de Relatório HTML Estático
Sistema de Análise Eleitoral - Rondônia

Gera um arquivo HTML completo e interativo que pode ser aberto em qualquer navegador.
"""

import os
import sys
import html as html_lib
from pathlib import Path
from datetime import datetime

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.data_processor import DataProcessor
from src.analytics import ElectoralAnalytics
from src.visualizations import ElectoralVisualizations

import plotly.graph_objects as go
import plotly.io as pio


def generate_html_report(data_dir: str = ".", output_file: str = "relatorio_eleitoral.html", ano: int = None):
    """
    Gera um relatório HTML completo e interativo.
    
    Args:
        data_dir: Diretório com os arquivos de dados
        output_file: Nome do arquivo HTML de saída
        ano: Ano específico para análise (ou None para todos)
    """
    print("🚀 Gerando Relatório HTML Interativo...")
    print("=" * 60)
    
    # Carregar dados
    processor = DataProcessor(data_dir)
    processor.load_data()
    df = processor.get_combined_data()
    
    analytics = ElectoralAnalytics(df)
    viz = ElectoralVisualizations(df)
    stats = processor.get_summary_stats()
    
    # Ano padrão: mais recente
    if ano is None:
        ano = max(stats['anos'])
    
    print(f"📊 Gerando análises para {ano}...")
    
    # Gerar gráficos
    print("  📈 Criando visualizações...")
    
    fig_partidos = viz.plot_votes_by_party(ano)
    fig_partidos.update_layout(height=500, title=f"Votos por Partido - {ano}")
    
    fig_municipios = viz.plot_geographic_heatmap(ano)
    fig_municipios.update_layout(height=500, title=f"Distribuição por Município - {ano}")
    
    fig_eleitos = viz.plot_elected_by_party(ano)
    fig_eleitos.update_layout(height=500, title=f"Eleitos por Partido e Cargo - {ano}")
    
    fig_treemap = viz.plot_treemap_municipalities(ano)
    fig_treemap.update_layout(height=600, title=f"Mapa de Votos por Município - {ano}")
    
    fig_sunburst = viz.plot_sunburst_results(ano)
    fig_sunburst.update_layout(height=600, title=f"Hierarquia de Votos - {ano}")
    
    fig_panorama = viz.plot_temporal_overview()
    fig_panorama.update_layout(height=700, title="Panorama Eleitoral - Rondônia (2016-2024)")
    
    # Converter gráficos para HTML
    def fig_to_html(fig):
        return pio.to_html(fig, full_html=False, include_plotlyjs=False)
    
    # Gerar relatório de dados
    print("  📋 Processando estatísticas...")
    report = analytics.generate_electoral_report(ano)
    
    # Top candidatos
    top_candidatos = processor.get_votes_by_candidate(ano).head(20)
    
    # Análise partidária
    party_analysis = analytics.analyze_party_strength(ano)
    
    # Municípios
    municipios = processor.get_votes_by_municipality(ano)
    
    # Gerar HTML
    print("  🎨 Construindo HTML...")
    
    # Alias para escape de HTML (protege contra dados com caracteres especiais)
    esc = html_lib.escape
    
    html_content = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🗳️ Análise Eleitoral - Rondônia {ano}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }}
        
        body {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
            color: white;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }}
        
        .stat-icon {{
            font-size: 2.5rem;
            margin-bottom: 15px;
        }}
        
        .stat-value {{
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .section {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        
        .section-title {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #2C3E50;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .section-title i {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }}
        
        .chart-container {{
            margin: 20px 0;
        }}
        
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        th {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            font-weight: 600;
            color: #2C3E50;
            position: sticky;
            top: 0;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-primary {{
            background: #cce5ff;
            color: #004085;
        }}
        
        .top-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .top-item {{
            display: flex;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 12px;
            transition: all 0.3s ease;
        }}
        
        .top-item:hover {{
            background: #e9ecef;
            transform: translateX(5px);
        }}
        
        .top-rank {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            margin-right: 15px;
        }}
        
        .top-info {{
            flex: 1;
        }}
        
        .top-name {{
            font-weight: 600;
            color: #2C3E50;
        }}
        
        .top-detail {{
            font-size: 0.85rem;
            color: #7f8c8d;
        }}
        
        .top-value {{
            font-weight: 700;
            color: #667eea;
            font-size: 1.1rem;
        }}
        
        .nav-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        
        .nav-tab {{
            padding: 12px 24px;
            background: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 500;
            color: #7f8c8d;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .nav-tab:hover {{
            background: #f0f0ff;
            color: #667eea;
        }}
        
        .nav-tab.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #7f8c8d;
            margin-top: 30px;
        }}
        
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        /* Animações */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .animate {{
            animation: fadeIn 0.5s ease-out;
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header animate">
            <h1><i class="fas fa-vote-yea"></i> Sistema de Análise Eleitoral</h1>
            <p><i class="fas fa-map-marker-alt"></i> Estado de Rondônia • Eleições {ano}</p>
            <p style="margin-top: 15px; font-size: 0.9rem; opacity: 0.8;">
                Gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}
            </p>
        </header>
        
        <!-- Estatísticas Principais -->
        <div class="stats-grid animate">
            <div class="stat-card">
                <div class="stat-icon" style="color: #3498DB;">🗳️</div>
                <div class="stat-value" style="color: #3498DB;">{report['resumo']['total_votos']:,}</div>
                <div class="stat-label">Total de Votos</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #27AE60;">👥</div>
                <div class="stat-value" style="color: #27AE60;">{report['resumo']['total_candidatos']:,}</div>
                <div class="stat-label">Candidatos</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #F39C12;">🏛️</div>
                <div class="stat-value" style="color: #F39C12;">{report['resumo']['total_partidos']}</div>
                <div class="stat-label">Partidos</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #E74C3C;">🏆</div>
                <div class="stat-value" style="color: #E74C3C;">{sum(report['eleitos_por_partido'].values())}</div>
                <div class="stat-label">Eleitos</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #9B59B6;">🏙️</div>
                <div class="stat-value" style="color: #9B59B6;">{report['resumo']['total_municipios']}</div>
                <div class="stat-label">Municípios</div>
            </div>
        </div>
        
        <!-- Navegação por Abas -->
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('overview')">📊 Visão Geral</button>
            <button class="nav-tab" onclick="showTab('candidates')">👤 Candidatos</button>
            <button class="nav-tab" onclick="showTab('parties')">🏛️ Partidos</button>
            <button class="nav-tab" onclick="showTab('geography')">🗺️ Geografia</button>
            <button class="nav-tab" onclick="showTab('history')">📈 Histórico</button>
        </div>
        
        <!-- Aba: Visão Geral -->
        <div id="overview" class="tab-content active">
            <div class="grid-2">
                <div class="section">
                    <h2 class="section-title"><i class="fas fa-chart-bar"></i> Votos por Partido</h2>
                    <div class="chart-container">
                        {fig_to_html(fig_partidos)}
                    </div>
                </div>
                <div class="section">
                    <h2 class="section-title"><i class="fas fa-map"></i> Distribuição por Município</h2>
                    <div class="chart-container">
                        {fig_to_html(fig_municipios)}
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title"><i class="fas fa-trophy"></i> Eleitos por Partido e Cargo</h2>
                <div class="chart-container">
                    {fig_to_html(fig_eleitos)}
                </div>
            </div>
        </div>
        
        <!-- Aba: Candidatos -->
        <div id="candidates" class="tab-content">
            <div class="section">
                <h2 class="section-title"><i class="fas fa-medal"></i> Top 20 Candidatos Mais Votados</h2>
                <div class="top-list">
                    {''.join([f'''
                    <div class="top-item">
                        <div class="top-rank">{i+1}</div>
                        <div class="top-info">
                            <div class="top-name">{esc(str(row['CANDIDATO']))}</div>
                            <div class="top-detail">{esc(str(row['PARTIDO']))} • {esc(str(row['CARGO']))}</div>
                        </div>
                        <div class="top-value">{int(row['TOTAL_VOTOS']):,}</div>
                    </div>
                    ''' for i, row in top_candidatos.head(20).iterrows()])}
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title"><i class="fas fa-table"></i> Tabela Completa de Candidatos</h2>
                <div style="overflow-x: auto; max-height: 500px;">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Candidato</th>
                                <th>Partido</th>
                                <th>Cargo</th>
                                <th>Status</th>
                                <th>Votos</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([f'''
                            <tr>
                                <td>{i+1}</td>
                                <td><strong>{esc(str(row['CANDIDATO']))}</strong></td>
                                <td><span class="badge badge-primary">{esc(str(row['PARTIDO']))}</span></td>
                                <td>{esc(str(row['CARGO']))}</td>
                                <td><span class="badge {'badge-success' if 'ELEITO' in str(row['STATUS']) else ''}">{esc(str(row['STATUS']))}</span></td>
                                <td><strong>{int(row['TOTAL_VOTOS']):,}</strong></td>
                            </tr>
                            ''' for i, row in top_candidatos.head(50).iterrows()])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Aba: Partidos -->
        <div id="parties" class="tab-content">
            <div class="section">
                <h2 class="section-title"><i class="fas fa-landmark"></i> Análise Partidária Completa</h2>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Partido</th>
                                <th>Total Votos</th>
                                <th>Candidatos</th>
                                <th>Eleitos</th>
                                <th>% Votos</th>
                                <th>Taxa Eleição</th>
                                <th>Capilaridade</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([f'''
                            <tr>
                                <td>{i+1}</td>
                                <td><strong>{esc(str(row['PARTIDO']))}</strong></td>
                                <td><strong>{int(row['TOTAL_VOTOS']):,}</strong></td>
                                <td>{int(row['CANDIDATOS'])}</td>
                                <td><span class="badge badge-success">{int(row['ELEITOS'])}</span></td>
                                <td>{row['PERCENTUAL_VOTOS']:.2f}%</td>
                                <td>{row['TAXA_ELEICAO']:.1f}%</td>
                                <td>{row['CAPILARIDADE']:.1f}%</td>
                            </tr>
                            ''' for i, row in party_analysis.head(25).iterrows()])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title"><i class="fas fa-chart-pie"></i> Eleitos por Partido</h2>
                <div class="top-list">
                    {''.join([f'''
                    <div class="top-item">
                        <div class="top-rank">{i+1}</div>
                        <div class="top-info">
                            <div class="top-name">{esc(str(partido))}</div>
                            <div class="top-detail">Candidatos eleitos</div>
                        </div>
                        <div class="top-value">{eleitos}</div>
                    </div>
                    ''' for i, (partido, eleitos) in enumerate(list(report['eleitos_por_partido'].items())[:15])])}
                </div>
            </div>
        </div>
        
        <!-- Aba: Geografia -->
        <div id="geography" class="tab-content">
            <div class="section">
                <h2 class="section-title"><i class="fas fa-map-marked-alt"></i> Mapa de Votos por Município</h2>
                <div class="chart-container">
                    {fig_to_html(fig_treemap)}
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title"><i class="fas fa-city"></i> Estatísticas por Município</h2>
                <div style="overflow-x: auto; max-height: 500px;">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Município</th>
                                <th>Total Votos</th>
                                <th>Eleitorado</th>
                                <th>Candidatos</th>
                                <th>Partidos</th>
                                <th>Participação</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([f'''
                            <tr>
                                <td>{i+1}</td>
                                <td><strong>{esc(str(row['MUNICÍPIO']))}</strong></td>
                                <td><strong>{int(row['TOTAL_VOTOS']):,}</strong></td>
                                <td>{int(row['ELEITORADO']):,}</td>
                                <td>{int(row['NUM_CANDIDATOS'])}</td>
                                <td>{int(row['NUM_PARTIDOS'])}</td>
                                <td><span class="badge {'badge-success' if row['PARTICIPACAO'] > 80 else 'badge-primary'}">{row['PARTICIPACAO']:.1f}%</span></td>
                            </tr>
                            ''' for i, row in municipios.iterrows()])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Aba: Histórico -->
        <div id="history" class="tab-content">
            <div class="section">
                <h2 class="section-title"><i class="fas fa-chart-line"></i> Panorama Eleitoral (2016-2024)</h2>
                <div class="chart-container">
                    {fig_to_html(fig_panorama)}
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title"><i class="fas fa-sitemap"></i> Hierarquia de Votos - {ano}</h2>
                <div class="chart-container">
                    {fig_to_html(fig_sunburst)}
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <footer class="footer">
            <p>
                <i class="fas fa-code"></i> Sistema de Análise Eleitoral • Rondônia<br>
                <small>Dados: Tribunal Superior Eleitoral (TSE)</small><br>
                <small>Desenvolvido com ❤️ • <a href="https://github.com/mankse311/PROJETO-FINAL" target="_blank" rel="noopener noreferrer">GitHub</a></small>
            </p>
        </footer>
    </div>
    
    <script>
        // Navegação por abas
        function showTab(tabId) {{
            // Esconder todas as abas
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Remover classe active de todos os botões
            document.querySelectorAll('.nav-tab').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Mostrar aba selecionada
            document.getElementById(tabId).classList.add('active');
            
            // Ativar botão correspondente
            event.target.classList.add('active');
            
            // Redimensionar gráficos Plotly
            window.dispatchEvent(new Event('resize'));
        }}
        
        // Animação ao scroll
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('animate');
                }}
            }});
        }});
        
        document.querySelectorAll('.section').forEach(el => observer.observe(el));
    </script>
</body>
</html>
'''
    
    # Salvar arquivo
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
    
    print(f"\n✅ Relatório HTML gerado com sucesso!")
    print(f"=" * 60)
    print(f"📄 Arquivo: {output_path.absolute()}")
    print(f"📊 Tamanho: {file_size:.2f} MB")
    print(f"🌐 Abra o arquivo em qualquer navegador!")
    print(f"\n💡 Dica: O relatório é totalmente interativo!")
    print(f"   - Gráficos com zoom, pan e hover")
    print(f"   - Tabelas com ordenação")
    print(f"   - Navegação por abas")
    
    return str(output_path.absolute())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerador de Relatório HTML')
    parser.add_argument('--data-dir', type=str, default='.', 
                       help='Diretório com os arquivos de dados')
    parser.add_argument('--output', '-o', type=str, default='relatorio_eleitoral.html',
                       help='Nome do arquivo HTML de saída')
    parser.add_argument('--year', '-y', type=int, default=None,
                       help='Ano específico (padrão: mais recente)')
    
    args = parser.parse_args()
    
    try:
        generate_html_report(args.data_dir, args.output, args.year)
    except FileNotFoundError as e:
        print(f"\n❌ Erro: arquivo não encontrado — {e}")
        sys.exit(1)
    except ImportError as e:
        print(f"\n❌ Dependência não encontrada: {e}")
        print("   Execute: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
