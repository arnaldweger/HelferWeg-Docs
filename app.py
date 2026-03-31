import dash
from dash import dcc, html, Input, Output, State, no_update, ALL, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
import os
import base64
import flask
import json

# =============================================================================
# CONFIGURAÇÕES DE DIRETÓRIOS
# =============================================================================
NOTAS_DIR = Path("notas")
IMAGES_DIR = NOTAS_DIR / "images"

NOTAS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

CAT_CORES = {
    "Latte": {"bg": "#eff1f5", "fg": "#4c4f69", "side": "#dce0e8", "acc": "#1e66f5", "brd": "#ccd0da"},
    "Macchiato": {"bg": "#24273a", "fg": "#cad3f5", "side": "#181926", "acc": "#8aadf4", "brd": "#36394f"},
    "Frappé": {"bg": "#303446", "fg": "#c6d0f5", "side": "#232634", "acc": "#8caaee", "brd": "#414559"},
    "Mocha": {"bg": "#1e1e2e", "fg": "#cdd6f4", "side": "#11111b", "acc": "#89b4fa", "brd": "#313244"}
}

def listar_notas():
    arquivos = list(NOTAS_DIR.glob("**/*.md"))
    if not arquivos: return pd.DataFrame(columns=["nome", "caminho", "categoria"])
    return pd.DataFrame([{"nome": a.stem, "caminho": str(a), "categoria": a.parent.name if a.parent != NOTAS_DIR else "Geral"} for a in arquivos])


# =============================================================================
# APP E SERVIDOR
# =============================================================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "HelferWeg Docs"
app._favicon = "favicon.ico"

# Rota para servir as imagens (Precisa estar DEPOIS de app = dash.Dash)
@app.server.route('/images/<path:filename>')
def serve_image(filename):
    return flask.send_from_directory(IMAGES_DIR, filename)


# =============================================================================
# LAYOUT
# =============================================================================
app.layout = html.Div(id="main-container", children=[
    dcc.Store(id='store-arquivo-selecionado'),

    dcc.Store(id='store-imagem-para-deletar'),
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Excluir Imagem")),
        dbc.ModalBody(id="corpo-modal-del-img"),
        dbc.ModalFooter([
            dbc.Button("Cancelar", id="btn-cancelar-del-img", color="secondary", className="ms-auto"),
            dbc.Button("Confirmar Exclusão", id="btn-confirmar-del-img-real", color="danger"),
        ]),
    ], id="modal-confirm-del-img", is_open=False),

    dbc.Row([
        # SIDEBAR
        dbc.Col(id="col-sidebar", children=[
            html.Div([
                html.Img(src="/assets/logo.png", style={"height": "60px", "marginBottom": "10px"}),
                html.H4("HelferWeg Docs", id="txt-logo", className="fw-bold"),
            ], className="text-center mb-4"),
            
            html.Hr(),
            html.Label("📁 Pasta:", className="fw-bold small"),
            dcc.Dropdown(id='filtro-categoria', placeholder="Selecione...", className="mb-3"),
            
            html.Label("📄 Documento:", className="fw-bold small"),
            dcc.Dropdown(id='selecao-arquivo-dropdown', placeholder="Selecione...", className="mb-4"),
            
            html.Hr(),
            html.Label("🎨 Tema Catppuccin:", className="fw-bold small"),
            dcc.Dropdown(id="seletor-tema-cat", options=[{"label": k, "value": k} for k in CAT_CORES.keys()], value="Latte", clearable=False, className="mb-4"),

            html.Hr(),
            html.Label("🛠️ Ações:", className="fw-bold small mb-3 d-block", style={"opacity": "0.6"}),
            html.Div([
                dbc.Button("➕ Nova Nota", id="btn-abrir-modal", color="link", className="w-100 text-start p-0 mb-3 fw-bold", style={"color": "#89b4fa", "textDecoration": "none"}),
                dbc.Button("💾 Salvar Alterações", id="btn-salvar", color="link", className="w-100 text-start p-0 mb-3 fw-bold", style={"color": "#95cc90", "textDecoration": "none"}),
                dbc.Button("✏️ Renomear Arquivo", id="btn-abrir-renomear", color="link", className="w-100 text-start p-0 mb-3 fw-bold", style={"color": "#e0cb9d", "textDecoration": "none"}),
                dbc.Button("🗑️ Deletar Nota", id="btn-abrir-deletar", color="link", className="w-100 text-start p-0 mb-3 fw-bold", style={"color": "#f38ba8", "textDecoration": "none"}),
            ], className="px-2"),
            html.Div(id="status-geral", className="mt-2")
        ], width=3),

        # ÁREA PRINCIPAL
        dbc.Col(id="col-main", children=[
            dbc.Tabs([
                dbc.Tab(label="🔍 Visualizar", tab_id="aba-leitura"),
                dbc.Tab(label="📝 Editar", tab_id="aba-edicao"),
                dbc.Tab(label="🖼️ Imagens", tab_id="aba-imagens"),
            ], id="abas-doc", active_tab="aba-leitura", className="mt-2"),
            
            html.Div(id="painel-leitura", children=[dcc.Markdown(id="md-viewer", className="p-4")]),
            
            html.Div(id="painel-edicao", children=[
                dcc.Textarea(id="area-editor", style={'width': '100%', 'height': '75vh', 'padding': '20px', 'fontFamily': 'monospace'})
            ], style={'display': 'none'}),

            html.Div(id="painel-imagens", children=[
                dcc.Upload(
                    id='upload-imagem',
                    children=html.Div(['Arraste ou ', html.A('Selecione uma Imagem')]),
                    style={
                        'width': '100%', 'height': '60px', 'lineHeight': '60px',
                        'borderWidth': '1px', 'borderStyle': 'dashed',
                        'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px 0'
                    },
                    multiple=False
                ),
                html.Div(id='lista-imagens-galeria', className="d-flex flex-wrap p-3")
            ], style={'display': 'none'}),
        ], width=9),
    ], className="g-0"),

    # MODAIS
    dbc.Modal([
        dbc.ModalHeader("Nova Nota"),
        dbc.ModalBody([
            dbc.Label("Nome da Nota:"),
            dbc.Input(id="novo-nome", placeholder="Ex: Relatorio_Compras"),
            html.Hr(),
            dbc.Label("Selecionar Pasta Existente:"),
            dcc.Dropdown(id="dropdown-pastas-modal", placeholder="Selecione uma pasta..."),
            html.P("OU", className="text-center my-2 small fw-bold"),
            dbc.Label("Criar Nova Pasta:"),
            dbc.Input(id="nova-categoria", placeholder="Ex: 🐍Python"),
        ]),
        dbc.ModalFooter(dbc.Button("Criar", id="btn-confirmar-criacao", color="primary"))
    ], id="modal-criar", is_open=False),
    dbc.Modal([dbc.ModalHeader("Renomear"), dbc.ModalBody([dbc.Label("Novo nome:"), dbc.Input(id="input-renomear")]), dbc.ModalFooter(dbc.Button("Confirmar", id="btn-confirmar-renomear", color="warning"))], id="modal-renomear", is_open=False),
    dbc.Modal([dbc.ModalHeader("Excluir"), dbc.ModalBody("Apagar permanentemente?"), dbc.ModalFooter(dbc.Button("Sim", id="btn-confirmar-excluir", color="danger"))], id="modal-deletar", is_open=False),
])

# =============================================================================
# CALLBACKS
# =============================================================================

@app.callback(
    [Output("main-container", "style"), Output("col-sidebar", "style"), Output("txt-logo", "style"),
     Output("painel-leitura", "style"), Output("painel-edicao", "style"), Output("painel-imagens", "style"), 
     Output("area-editor", "style")],
    [Input("seletor-tema-cat", "value"), Input("abas-doc", "active_tab")]
)
def atualizar_layout(tema, aba):
    c = CAT_CORES[tema if tema else "Mocha"]
    style_main = {"backgroundColor": c['bg'], "color": c['fg'], "minHeight": "100vh"}
    style_side = {"backgroundColor": c['side'], "borderRight": f"1px solid {c['brd']}", "padding": "25px", "minHeight": "100vh"}
    style_logo = {"color": c['acc']}
    
    show_read = {'display': 'block'} if aba == 'aba-leitura' else {'display': 'none'}
    show_edit = {'display': 'block'} if aba == 'aba-edicao' else {'display': 'none'}
    show_img = {'display': 'block'} if aba == 'aba-imagens' else {'display': 'none'}
    
    style_editor = {'width': '100%', 'height': '75vh', 'backgroundColor': c['side'], 'color': c['fg'], 
                    'border': f"1px solid {c['brd']}", 'padding': '20px', 'fontFamily': 'monospace'}
    
    return style_main, style_side, style_logo, show_read, show_edit, show_img, style_editor

@app.callback(
    [Output("md-viewer", "children"), Output("area-editor", "value")],
    [Input("store-arquivo-selecionado", "data")]
)
def carregar_arquivo(path):
    if not path or not os.path.exists(path):
        return "Selecione uma nota no menu lateral.", ""
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    return txt, txt

@app.callback(
    [Output("store-arquivo-selecionado", "data"), Output("status-geral", "children"), 
     Output("modal-criar", "is_open"), Output("modal-deletar", "is_open"), Output("modal-renomear", "is_open")],
    [Input("btn-salvar", "n_clicks"), Input("btn-confirmar-criacao", "n_clicks"), 
     Input("btn-confirmar-excluir", "n_clicks"), Input("btn-confirmar-renomear", "n_clicks"),
     Input("btn-abrir-modal", "n_clicks"), Input("btn-abrir-deletar", "n_clicks"), 
     Input("btn-abrir-renomear", "n_clicks"), Input("selecao-arquivo-dropdown", "value")],
    [State("store-arquivo-selecionado", "data"), State("area-editor", "value"), 
     State("novo-nome", "value"), State("nova-categoria", "value"), State("dropdown-pastas-modal", "value"),
     State("input-renomear", "value"), State("modal-criar", "is_open"), State("modal-deletar", "is_open"), State("modal-renomear", "is_open")],
    prevent_initial_call=True
)
def crud_completo(n_sal, n_cri, n_exc, n_ren_conf, n_m1, n_m2, n_m3, drop_val, path, editor_txt, n_nome, n_cat_input, n_cat_drop, r_nome, m1, m2, m3):
    ctx = callback_context
    trig = ctx.triggered[0]['prop_id']

    if "selecao-arquivo-dropdown" in trig: return drop_val, "", False, False, False
    if "btn-abrir-modal" in trig: return path, "", True, False, False
    if "btn-abrir-deletar" in trig: return path, "", False, True, False
    if "btn-abrir-renomear" in trig: return path, "", False, False, True

    if "btn-salvar" in trig and path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(editor_txt if editor_txt else "")
        return path, dbc.Alert("✅ Salvo!", color="success", duration=1000), False, False, False

    if "btn-confirmar-criacao" in trig and n_nome:
        pasta = n_cat_drop if n_cat_drop else (n_cat_input if n_cat_input else "Geral")
        p = NOTAS_DIR / pasta
        p.mkdir(exist_ok=True)
        arq = p / f"{n_nome}.md"
        with open(arq, "w", encoding="utf-8") as f: f.write(f"# {n_nome}")
        return str(arq), "", False, False, False

    if "btn-confirmar-renomear" in trig and path and r_nome:
        old = Path(path); new = old.parent / f"{r_nome}.md"
        os.rename(old, new)
        return str(new), dbc.Alert("✏️ Renomeado", color="info", duration=1000), False, False, False

    if "btn-confirmar-excluir" in trig and path:
        os.remove(path)
        return None, dbc.Alert("🗑️ Excluído", color="danger", duration=1500), False, False, False

    return no_update, "", False, False, False

@app.callback(
    [Output("filtro-categoria", "options"), 
     Output("selecao-arquivo-dropdown", "options"),
     Output("dropdown-pastas-modal", "options")],
    [Input("filtro-categoria", "value"), Input("status-geral", "children")]
)
def up_menus(cat, _):
    df = listar_notas()
    lista_pastas = sorted(df['categoria'].unique())
    opts_pastas = [{'label': c, 'value': c} for c in lista_pastas]
    
    if cat: df = df[df['categoria'] == cat]
    docs = [{'label': n, 'value': c} for n, c in zip(df['nome'], df['caminho'])]
    
    return opts_pastas, docs, opts_pastas

# =============================================================================
# CALLBACKS DE IMAGENS 
# =============================================================================

# 1. Salvar Upload e Listar Galeria (Atualizado com Botão Deletar)
@app.callback(
    Output('lista-imagens-galeria', 'children'),
    [Input('upload-imagem', 'contents'), Input("status-geral", "children")],
    [State('upload-imagem', 'filename')]
)
def salvar_e_listar_imagens(conteudo, status_md, nome_arquivo):
    ctx = callback_context
    trig = ctx.triggered[0]['prop_id']

    # Se o trigger foi um novo upload
    if "upload-imagem" in trig and conteudo:
        data = conteudo.encode("utf8").split(b";base64,")[1]
        with open(IMAGES_DIR / nome_arquivo, "wb") as f:
            f.write(base64.decodebytes(data))

    # Listar imagens existentes
    ext_permitidas = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')
    imgs = [f for f in IMAGES_DIR.glob("*") if f.suffix.lower() in ext_permitidas]
    
    if not imgs: return html.P("Nenhuma imagem enviada.", className="text-muted p-3")

    return [
        html.Div([
            # Container relativo para posicionar o botão X no canto
            html.Div([
                # Miniatura
                html.Img(src=f"/images/{img.name}", 
                         style={"height": "100px", "width": "auto", "borderRadius": "5px", "border": "1px solid #444"}),
                
                # Botão Excluir (X Vermelho)
                html.Button("×", id={'type': 'btn-del-img', 'index': img.name}, className="btn btn-sm p-0",
                            style={"position": "absolute", "top": "-10px", "right": "-10px", 
                                   "backgroundColor": "#f38ba8", "color": "white", "borderRadius": "50%", 
                                   "width": "22px", "height": "22px", "lineHeight": "18px", "fontWeight": "bold", "border": "none"}),
            ], style={"position": "relative", "display": "inline-block"}),
            
            # Código Markdown para cópia (UserSelect: all para um clique)
            html.Code(
                f"![{img.stem}](images/{img.name})", 
                className="d-block mt-2 p-1",
                style={
                    "fontSize": "11px", "backgroundColor": "rgba(0,0,0,0.2)", 
                    "border": "1px solid #555", "borderRadius": "3px",
                    "color": "#2986cc", "wordBreak": "break-all", "cursor": "pointer",
                    "userSelect": "all" 
                }
            )
        ], style={"width": "160px", "margin": "15px 10px"}, className="text-center") for img in imgs
    ]

# 1. Gerenciar Modal (Abrir/Fechar)
@app.callback(
    [Output("modal-confirm-del-img", "is_open"), 
     Output("corpo-modal-del-img", "children"),
     Output("store-imagem-para-deletar", "data")],
    [Input({'type': 'btn-del-img', 'index': ALL}, 'n_clicks'),
     Input("btn-cancelar-del-img", "n_clicks")],
    [State("modal-confirm-del-img", "is_open")],
    prevent_initial_call=True
)
def gerenciar_modal_delecao(n_clicks_list, n_cancela, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update
    
    trig_id = ctx.triggered_id

    # Se o que disparou foi o dicionário do botão "X"
    if isinstance(trig_id, dict) and trig_id.get('type') == 'btn-del-img':
        nome_img = trig_id.get('index')
        # Verifica se o clique foi real (não None)
        if any(n_clicks_list):
            return True, f"Deseja realmente apagar a imagem '{nome_img}'?", nome_img

    # Se clicou em cancelar
    if trig_id == "btn-cancelar-del-img":
        return False, no_update, no_update

    return no_update, no_update, no_update

# 2. Executar Exclusão Real
@app.callback(
    [Output("status-geral", "children", allow_duplicate=True),
     Output("modal-confirm-del-img", "is_open", allow_duplicate=True)],
    Input("btn-confirmar-del-img-real", "n_clicks"),
    State("store-imagem-para-deletar", "data"),
    prevent_initial_call=True
)
def executa_exclusao_imagem(n_clicks, nome_imagem):
    if n_clicks and nome_imagem:
        caminho = IMAGES_DIR / nome_imagem
        try:
            if caminho.exists():
                os.remove(caminho)
                # Retorna o alerta e FECHA o modal (False)
                return dbc.Alert(f"🗑️ Imagem '{nome_imagem}' removida!", color="danger", duration=2000), False
        except Exception as e:
            return dbc.Alert(f"❌ Erro: {str(e)}", color="warning"), False
            
    return no_update, False

    
# =============================================================================
# INICIALIZAÇÃO
# =============================================================================
server = app.server

if __name__ == "__main__":
    app.run(debug=True)