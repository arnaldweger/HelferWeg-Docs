import dash
from dash import dcc, html, Input, Output, State, no_update, ALL, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
import os

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================
NOTAS_DIR = Path("notas")
NOTAS_DIR.mkdir(exist_ok=True)

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
# APP E LAYOUT
# =============================================================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "HelferWeg Docs"
app._favicon = "favicon.ico"

app.layout = html.Div(id="main-container", children=[
    dcc.Store(id='store-arquivo-selecionado'),
    
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
                dbc.Tab(label="Visualizar", tab_id="aba-leitura"),
                dbc.Tab(label="Editar", tab_id="aba-edicao"),
            ], id="abas-doc", active_tab="aba-leitura", className="mt-2"),
            
            # VISUALIZAÇÃO (MARKDOWN)
            html.Div(id="painel-leitura", children=[dcc.Markdown(id="md-viewer", className="p-4")]),
            
            # EDIÇÃO (TEXTAREA) - Ele fica SEMPRE no layout, apenas mudamos o display
            html.Div(id="painel-edicao", children=[
                dcc.Textarea(id="area-editor", style={'width': '100%', 'height': '75vh', 'padding': '20px', 'fontFamily': 'monospace'})
            ], style={'display': 'none'}) 
        ], width=9),
    ], className="g-0"),

    # MODAIS
    dbc.Modal([dbc.ModalHeader("Nova Nota"), dbc.ModalBody([dbc.Label("Nome:"), dbc.Input(id="novo-nome"), dbc.Label("Pasta:"), dbc.Input(id="nova-categoria")]), dbc.ModalFooter(dbc.Button("Criar", id="btn-confirmar-criacao", color="primary"))], id="modal-criar", is_open=False),
    dbc.Modal([dbc.ModalHeader("Renomear"), dbc.ModalBody([dbc.Label("Novo nome:"), dbc.Input(id="input-renomear")]), dbc.ModalFooter(dbc.Button("Confirmar", id="btn-confirmar-renomear", color="warning"))], id="modal-renomear", is_open=False),
    dbc.Modal([dbc.ModalHeader("Excluir"), dbc.ModalBody("Apagar permanentemente?"), dbc.ModalFooter(dbc.Button("Sim", id="btn-confirmar-excluir", color="danger"))], id="modal-deletar", is_open=False),
])

# =============================================================================
# CALLBACKS
# =============================================================================

# 1. TEMA E ALTERNÂNCIA DE ABAS
@app.callback(
    [Output("main-container", "style"), Output("col-sidebar", "style"), Output("txt-logo", "style"),
     Output("painel-leitura", "style"), Output("painel-edicao", "style"), Output("area-editor", "style")],
    [Input("seletor-tema-cat", "value"), Input("abas-doc", "active_tab")]
)
def atualizar_layout(tema, aba):
    c = CAT_CORES[tema if tema else "Latte"]
    
    style_main = {"backgroundColor": c['bg'], "color": c['fg'], "minHeight": "100vh"}
    style_side = {"backgroundColor": c['side'], "borderRight": f"1px solid {c['brd']}", "padding": "25px", "minHeight": "100vh"}
    style_logo = {"color": c['acc']}
    
    # Alternar visibilidade das Divs
    show_read = {'display': 'block'} if aba == 'aba-leitura' else {'display': 'none'}
    show_edit = {'display': 'block'} if aba == 'aba-edicao' else {'display': 'none'}
    
    # Estilo do Editor
    style_editor = {'width': '100%', 'height': '75vh', 'backgroundColor': c['side'], 'color': c['fg'], 
                    'border': f"1px solid {c['brd']}", 'padding': '20px', 'fontFamily': 'monospace'}
    
    return style_main, style_side, style_logo, show_read, show_edit, style_editor

# 2. CARREGAR CONTEÚDO (PARA O VIEWER E PARA O EDITOR AO MESMO TEMPO)
@app.callback(
    [Output("md-viewer", "children"), Output("area-editor", "value")],
    [Input("store-arquivo-selecionado", "data")]
)
def carregar_arquivo(path):
    if not path or not os.path.exists(path):
        msg = "Selecione uma nota no menu lateral."
        return msg, ""
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    return txt, txt

# 3. CRUD (SALVAR, CRIAR, DELETAR, RENOMEAR)
@app.callback(
    [Output("store-arquivo-selecionado", "data"), Output("status-geral", "children"), 
     Output("modal-criar", "is_open"), Output("modal-deletar", "is_open"), Output("modal-renomear", "is_open")],
    [Input("btn-salvar", "n_clicks"), Input("btn-confirmar-criacao", "n_clicks"), 
     Input("btn-confirmar-excluir", "n_clicks"), Input("btn-confirmar-renomear", "n_clicks"),
     Input("btn-abrir-modal", "n_clicks"), Input("btn-abrir-deletar", "n_clicks"), 
     Input("btn-abrir-renomear", "n_clicks"), Input("selecao-arquivo-dropdown", "value")],
    [State("store-arquivo-selecionado", "data"), State("area-editor", "value"), 
     State("novo-nome", "value"), State("nova-categoria", "value"), State("input-renomear", "value"),
     State("modal-criar", "is_open"), State("modal-deletar", "is_open"), State("modal-renomear", "is_open")],
    prevent_initial_call=True
)
def crud_completo(n_sal, n_cri, n_exc, n_ren_conf, n_m1, n_m2, n_m3, drop_val, path, editor_txt, n_nome, n_cat, r_nome, m1, m2, m3):
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
        p = NOTAS_DIR / (n_cat if n_cat else "Geral")
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

# 4. MENUS
@app.callback([Output("filtro-categoria", "options"), Output("selecao-arquivo-dropdown", "options")], 
              [Input("filtro-categoria", "value"), Input("status-geral", "children")])
def up_menus(cat, _):
    df = listar_notas()
    cats = [{'label': c, 'value': c} for c in sorted(df['categoria'].unique())]
    if cat: df = df[df['categoria'] == cat]
    docs = [{'label': n, 'value': c} for n, c in zip(df['nome'], df['caminho'])]
    return cats, docs

if __name__ == "__main__":
    app.run(debug=True)