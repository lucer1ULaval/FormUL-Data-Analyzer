import dash
from dash import Input, Output, State, html, dcc
import base64, tempfile, os, json
import asammdf
import pandas as pd

from constants import MONO, SANS, DIM, TEXT, BORDER, BG, COULEURS, ROUGE, ORANGE
from ui import msg, layout_principal, layout_vue_libre
from utils.mdf_loader import charger_config, charger_mdf, signal_vers_dataframe
from fault_detection import detecter_flags_erreur, calculer_zones_faute, identifier_declencheurs
from math_channels import calculer_tous as calculer_math_channels
from views.graphes import construire_graphes
from views.resume import calculer_stats, construire_resume
from views.erreurs import construire_erreurs
from views.math_view import construire_math_view
from views.heatmap import construire_heatmap
from views.comparaison import construire_comparaison_upload, construire_overlay

config = charger_config()
CACHE_FILE  = 'cache_session.json'
LAYOUTS_DIR = 'layouts'
os.makedirs(LAYOUTS_DIR, exist_ok=True)


def _zones_et_decl(mdf, flags_erreur, fault_codes):
    zones = calculer_zones_faute(mdf, flags_erreur or [])
    decl  = identifier_declencheurs(mdf, flags_erreur or [], zones, fault_codes)
    return zones, decl

def _t_max(mdf, flags_erreur, default=300):
    t = default
    for f in (flags_erreur or []):
        try: t = max(t, float(mdf.get(f).timestamps[-1]))
        except: pass
    return t

def _charger_layout(filename):
    path = os.path.join(LAYOUTS_DIR, filename.replace('/', '_') + '.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def _sauvegarder_layout(filename, canaux, vue):
    path = os.path.join(LAYOUTS_DIR, filename.replace('/', '_') + '.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'canaux': canaux, 'vue': vue}, f)

def _construire_vue(vue, mdf, canaux_disponibles, flags_erreur, fault_codes,
                    canaux_sel, domaines_data, plage):
    if vue == 'graphes':
        if not canaux_sel:
            return msg("Select channels in the sidebar")
        zones, decl = _zones_et_decl(mdf, flags_erreur, fault_codes)
        return construire_graphes(mdf, canaux_sel, zones, decl)
    elif vue == 'resume':
        canaux_cles = [c for d in (domaines_data or {}).values()
                       for c in d.get('canaux_cles', []) if c in canaux_disponibles]
        stats = calculer_stats(mdf, canaux_cles, plage)
        label = f"{plage['debut']:.1f}s → {plage['fin']:.1f}s" if plage else "Full Session"
        return construire_resume(stats, label)
    elif vue == 'erreurs':
        zones, decl = _zones_et_decl(mdf, flags_erreur, fault_codes)
        return construire_erreurs(zones, decl, flags_erreur or [])
    elif vue == 'math':
        zones, decl = _zones_et_decl(mdf, flags_erreur, fault_codes)
        resultats = calculer_math_channels(mdf, canaux_disponibles)
        return construire_math_view(resultats, zones, decl, _t_max(mdf, flags_erreur))
    elif vue == 'heatmap':
        return construire_heatmap(mdf, canaux_disponibles)
    elif vue == 'comparaison':
        return construire_comparaison_upload()
    else:
        return msg(f"{vue} — coming soon")

def _liste_canaux_html(canaux, sel, type_checkbox='canal-checkbox'):
    items = []
    for c in canaux:
        idx = sel.index(c) if c in sel else -1
        couleur = COULEURS[idx % len(COULEURS)] if idx >= 0 else None
        est_sel = c in sel
        items.append(html.Div([
            html.Div(style={
                'width': '3px', 'alignSelf': 'stretch', 'flexShrink': '0',
                'background': couleur if couleur else 'transparent',
            }),
            dcc.Checklist(
                id={'type': type_checkbox, 'index': c},
                options=[{'label': '', 'value': c}],
                value=[c] if est_sel else [],
                inputStyle={
                    'width': '9px', 'height': '9px', 'margin': '0 5px 0 4px',
                    'accentColor': couleur or '#444',
                    'cursor': 'pointer', 'flexShrink': '0',
                },
                style={'display': 'flex', 'alignItems': 'center'}
            ),
            html.Span(c, title=c, style={
                'fontFamily': SANS, 'fontSize': '11px',
                'color': TEXT if est_sel else DIM,
                'overflow': 'hidden', 'textOverflow': 'ellipsis',
                'whiteSpace': 'nowrap', 'cursor': 'pointer',
            })
        ], style={
            'display': 'flex', 'alignItems': 'center',
            'padding': '3px 4px 3px 0',
            'borderBottom': f'1px solid {BORDER}',
            'background': '#1f2a1f' if est_sel else 'transparent',
        }))
    return items


def register_callbacks(app):

    # ── Routing ───────────────────────────────────────────────────────────
    @app.callback(Output('contenu-page', 'children'), Input('url', 'pathname'))
    def router(pathname):
        return layout_vue_libre() if pathname == '/view' else layout_principal()

    # ── Chargement MDF principal ──────────────────────────────────────────
    @app.callback(
        Output('store-mdf-path', 'data'),
        Output('store-domaines', 'data'),
        Output('store-flags-erreur', 'data'),
        Output('label-session', 'children'),
        Input('upload-mdf', 'contents'),
        State('upload-mdf', 'filename'),
        prevent_initial_call=True
    )
    def charger_fichier(contents, filename):
        if not contents:
            return [dash.no_update] * 4
        _, b64 = contents.split(',')
        decoded = base64.b64decode(b64)
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(decoded); chemin_tmp = f.name
        mdf, domaines, _, canaux_disponibles = charger_mdf(chemin_tmp, config)
        flags_erreur = detecter_flags_erreur(mdf, canaux_disponibles)
        mdf.close()
        domaines_data = dict(domaines)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'chemin_mdf': chemin_tmp, 'domaines': domaines_data,
                       'flags_erreur': flags_erreur, 'filename': filename}, f)
        return chemin_tmp, domaines_data, flags_erreur, filename

    # ── Chargement MDF détaché ────────────────────────────────────────────
    @app.callback(
        Output('store-mdf-path-det', 'data'),
        Output('store-domaines-det', 'data'),
        Output('store-flags-erreur-det', 'data'),
        Output('label-session-det', 'children'),
        Input('upload-mdf-det', 'contents'),
        State('upload-mdf-det', 'filename'),
        prevent_initial_call=True
    )
    def charger_fichier_det(contents, filename):
        if not contents:
            return [dash.no_update] * 4
        _, b64 = contents.split(',')
        decoded = base64.b64decode(b64)
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(decoded); chemin_tmp = f.name
        mdf, domaines, _, canaux_disponibles = charger_mdf(chemin_tmp, config)
        flags_erreur = detecter_flags_erreur(mdf, canaux_disponibles)
        mdf.close()
        return chemin_tmp, dict(domaines), flags_erreur, filename

    # ── Canaux principale ─────────────────────────────────────────────────
    @app.callback(
        Output('store-canaux-selectionnes', 'data'),
        Input('store-mdf-path', 'data'),
        Input({'type': 'canal-checkbox', 'index': dash.ALL}, 'value'),
        Input('btn-deselectionner', 'n_clicks'),
        State({'type': 'canal-checkbox', 'index': dash.ALL}, 'id'),
        State('store-canaux-selectionnes', 'data'),
        State('upload-mdf', 'filename'),
        State('store-vue', 'data'),
        prevent_initial_call=True
    )
    def maj_canaux(mdf_path, values_list, btn_desel, ids, sel_actuel, filename, vue):
        ctx = dash.callback_context
        if not ctx.triggered: return dash.no_update
        trigger = ctx.triggered[0]['prop_id']
        if 'store-mdf-path' in trigger:
            layout = _charger_layout(filename) if filename else None
            return layout['canaux'] if layout else []
        if 'btn-deselectionner' in trigger:
            if filename: _sauvegarder_layout(filename, [], vue or 'graphes')
            return []
        sel = list(sel_actuel or [])
        for values, id_item in zip(values_list, ids):
            canal = id_item['index']
            if values and canal not in sel: sel.append(canal)
            elif not values and canal in sel: sel.remove(canal)
        if filename: _sauvegarder_layout(filename, sel, vue or 'graphes')
        return sel

    # ── Vue principale ────────────────────────────────────────────────────
    @app.callback(
        Output('store-vue', 'data'),
        Input('store-mdf-path', 'data'),
        Input({'type': 'btn-vue', 'index': dash.ALL}, 'n_clicks'),
        State({'type': 'btn-vue', 'index': dash.ALL}, 'id'),
        State('upload-mdf', 'filename'),
        State('store-canaux-selectionnes', 'data'),
        prevent_initial_call=True
    )
    def maj_vue(mdf_path, n_clicks_list, ids, filename, canaux_sel):
        ctx = dash.callback_context
        if not ctx.triggered: return dash.no_update
        trigger = ctx.triggered[0]['prop_id']
        if 'store-mdf-path' in trigger:
            layout = _charger_layout(filename) if filename else None
            return layout['vue'] if layout else 'graphes'
        for id_item in ids:
            if id_item['index'] in trigger:
                vue = id_item['index']
                if filename: _sauvegarder_layout(filename, canaux_sel or [], vue)
                return vue
        return dash.no_update

    # ── Canaux détachés ───────────────────────────────────────────────────
    @app.callback(
        Output('store-canaux-selectionnes-det', 'data'),
        Input('store-mdf-path-det', 'data'),
        Input({'type': 'canal-checkbox-det', 'index': dash.ALL}, 'value'),
        Input('btn-deselectionner-det', 'n_clicks'),
        State({'type': 'canal-checkbox-det', 'index': dash.ALL}, 'id'),
        State('store-canaux-selectionnes-det', 'data'),
        State('upload-mdf-det', 'filename'),
        State('store-vue-det', 'data'),
        prevent_initial_call=True
    )
    def maj_canaux_det(mdf_path, values_list, btn_desel, ids, sel_actuel, filename, vue):
        ctx = dash.callback_context
        if not ctx.triggered: return dash.no_update
        trigger = ctx.triggered[0]['prop_id']
        if 'store-mdf-path-det' in trigger:
            layout = _charger_layout(filename) if filename else None
            return layout['canaux'] if layout else []
        if 'btn-deselectionner-det' in trigger:
            if filename: _sauvegarder_layout(filename, [], vue or 'graphes')
            return []
        sel = list(sel_actuel or [])
        for values, id_item in zip(values_list, ids):
            canal = id_item['index']
            if values and canal not in sel: sel.append(canal)
            elif not values and canal in sel: sel.remove(canal)
        if filename: _sauvegarder_layout(filename, sel, vue or 'graphes')
        return sel

    # ── Vue détachée ──────────────────────────────────────────────────────
    @app.callback(
        Output('store-vue-det', 'data'),
        Input('store-mdf-path-det', 'data'),
        Input({'type': 'btn-vue-det', 'index': dash.ALL}, 'n_clicks'),
        State({'type': 'btn-vue-det', 'index': dash.ALL}, 'id'),
        State('upload-mdf-det', 'filename'),
        State('store-canaux-selectionnes-det', 'data'),
        prevent_initial_call=True
    )
    def maj_vue_det(mdf_path, n_clicks_list, ids, filename, canaux_sel):
        ctx = dash.callback_context
        if not ctx.triggered: return dash.no_update
        trigger = ctx.triggered[0]['prop_id']
        if 'store-mdf-path-det' in trigger:
            layout = _charger_layout(filename) if filename else None
            return layout['vue'] if layout else 'graphes'
        for id_item in ids:
            if id_item['index'] in trigger:
                vue = id_item['index']
                if filename: _sauvegarder_layout(filename, canaux_sel or [], vue)
                return vue
        return dash.no_update

    # ── Liste canaux principale ───────────────────────────────────────────
    @app.callback(
        Output('liste-canaux', 'children'),
        Input('input-recherche', 'value'),
        Input('store-canaux-selectionnes', 'data'),
        Input('store-domaines', 'data'),
        prevent_initial_call=True
    )
    def filtrer_canaux(recherche, canaux_sel, domaines_data):
        if not domaines_data: return []
        canaux = sorted(set(c for d in domaines_data.values() for c in d['tous_canaux']))
        if recherche:
            canaux = [c for c in canaux if recherche.lower() in c.lower()]
        return _liste_canaux_html(canaux, canaux_sel or [], 'canal-checkbox')

    # ── Liste canaux détachée ─────────────────────────────────────────────
    @app.callback(
        Output('liste-canaux-det', 'children'),
        Input('input-recherche-det', 'value'),
        Input('store-canaux-selectionnes-det', 'data'),
        Input('store-domaines-det', 'data'),
        prevent_initial_call=True
    )
    def filtrer_canaux_det(recherche, canaux_sel, domaines_data):
        if not domaines_data: return []
        canaux = sorted(set(c for d in domaines_data.values() for c in d['tous_canaux']))
        if recherche:
            canaux = [c for c in canaux if recherche.lower() in c.lower()]
        return _liste_canaux_html(canaux, canaux_sel or [], 'canal-checkbox-det')

    # ── Chargement MDF session 2 ──────────────────────────────────────────
    @app.callback(
        Output('store-mdf-s2', 'data'),
        Output('label-s2', 'children'),
        Input('upload-mdf-s2', 'contents'),
        State('upload-mdf-s2', 'filename'),
        prevent_initial_call=True
    )
    def charger_s2(contents, filename):
        if not contents: return dash.no_update, dash.no_update
        _, b64 = contents.split(',')
        decoded = base64.b64decode(b64)
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(decoded); chemin_tmp = f.name
        return chemin_tmp, filename

    # ── Overlay comparaison ───────────────────────────────────────────────
    @app.callback(
        Output('contenu-comparaison', 'children'),
        Input('store-mdf-s2', 'data'),
        State('store-mdf-path', 'data'),
        State('store-canaux-selectionnes', 'data'),
        State('upload-mdf', 'filename'),
        State('upload-mdf-s2', 'filename'),
        prevent_initial_call=True
    )
    def afficher_overlay(chemin_s2, chemin_s1, canaux_sel, fname1, fname2):
        if not chemin_s2 or not chemin_s1: return msg("Load both sessions first")
        try:
            mdf1 = asammdf.MDF(chemin_s1); mdf2 = asammdf.MDF(chemin_s2)
            c1 = set(mdf1.channels_db.keys()); c2 = set(mdf2.channels_db.keys())
            canaux = [c for c in (canaux_sel or []) if c in c1 and c in c2]
            if not canaux:
                canaux = [c for c in (canaux_sel or []) if c in c1 or c in c2]
            contenu = construire_overlay(mdf1, mdf2, canaux,
                                         label1=fname1 or 'Session 1',
                                         label2=fname2 or 'Session 2')
            mdf1.close(); mdf2.close()
        except Exception as e:
            contenu = msg(f"Error: {e}")
        return contenu

    @app.callback(
        Output('label-s1-display', 'children'),
        Input('label-session', 'children'),
        prevent_initial_call=False
    )
    def maj_label_s1(label):
        return label or 'no file loaded'

    # ── Affichage vue principale ──────────────────────────────────────────
    @app.callback(
        Output('contenu-vue', 'children'),
        Input('store-vue', 'data'),
        Input('store-mdf-path', 'data'),
        Input('store-flags-erreur', 'data'),
        Input('store-canaux-selectionnes', 'data'),
        State('store-domaines', 'data'),
        State('store-plage', 'data'),
        prevent_initial_call=True
    )
    def afficher_vue(vue, chemin_mdf, flags_erreur, canaux_sel, domaines_data, plage):
        if not chemin_mdf: return msg("Open an MDF file to begin")
        ctx = dash.callback_context
        trigger = ctx.triggered[0]['prop_id'] if ctx.triggered else ''
        # Canaux changent → seulement si vue graphes
        if 'store-canaux-selectionnes' in trigger and vue != 'graphes':
            return dash.no_update
        # Heatmap → ne recharger que si changement de vue ou de MDF
        if vue == 'heatmap' and trigger not in ('store-mdf-path.data', 'store-vue.data'):
            return dash.no_update
        mdf = asammdf.MDF(chemin_mdf)
        canaux_disponibles = set(mdf.channels_db.keys())
        fault_codes = config.get('fault_codes', {})
        try:
            contenu = _construire_vue(vue, mdf, canaux_disponibles, flags_erreur,
                                      fault_codes, canaux_sel, domaines_data, plage)
        except Exception as e:
            import traceback; print(traceback.format_exc())
            contenu = msg(f"Error: {e}")
        mdf.close()
        return contenu

    # ── Affichage vue détachée ────────────────────────────────────────────
    @app.callback(
        Output('contenu-vue-det', 'children'),
        Input('store-vue-det', 'data'),
        Input('store-mdf-path-det', 'data'),
        Input('store-flags-erreur-det', 'data'),
        Input('store-canaux-selectionnes-det', 'data'),
        State('store-domaines-det', 'data'),
        State('store-plage-det', 'data'),
        prevent_initial_call=True
    )
    def afficher_vue_det(vue, chemin_mdf, flags_erreur, canaux_sel, domaines_data, plage):
        ctx = dash.callback_context
        trigger = ctx.triggered[0]['prop_id'] if ctx.triggered else ''
        if 'store-canaux-selectionnes-det' in trigger and vue != 'graphes':
            return dash.no_update
        if vue == 'heatmap' and trigger not in ('store-mdf-path-det.data', 'store-vue-det.data'):
            return dash.no_update
        if not chemin_mdf and os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
            chemin_mdf    = cache.get('chemin_mdf')
            domaines_data = cache.get('domaines')
            flags_erreur  = cache.get('flags_erreur', [])
        if not chemin_mdf or not os.path.exists(chemin_mdf):
            return msg("Open an MDF file to begin")
        mdf = asammdf.MDF(chemin_mdf)
        canaux_disponibles = set(mdf.channels_db.keys())
        fault_codes = config.get('fault_codes', {})
        try:
            contenu = _construire_vue(vue, mdf, canaux_disponibles, flags_erreur,
                                      fault_codes, canaux_sel, domaines_data, plage)
        except Exception as e:
            import traceback; print(traceback.format_exc())
            contenu = msg(f"Error: {e}")
        mdf.close()
        return contenu

    # ── Absorber les events zoom/pan de la heatmap ────────────────────────
    @app.callback(
        Output('graphe-heatmap-temps', 'config'),
        Input('graphe-heatmap-temps', 'relayoutData'),
        prevent_initial_call=True
    )
    def absorber_heatmap(relayoutData):
        return dash.no_update

    # ── Sync plage principale ─────────────────────────────────────────────
    @app.callback(
        Output('store-plage', 'data'),
        Input('graphe-principal', 'relayoutData'),
        prevent_initial_call=True
    )
    def sync_plage(relayoutData):
        if not relayoutData: return dash.no_update
        if 'xaxis.range[0]' in relayoutData:
            return {'debut': relayoutData['xaxis.range[0]'],
                    'fin':   relayoutData['xaxis.range[1]']}
        if 'xaxis.autorange' in relayoutData: return None
        return dash.no_update

    # ── Sync plage détachée ───────────────────────────────────────────────
    @app.callback(
        Output('store-plage-det', 'data'),
        Input('graphe-principal', 'relayoutData'),
        prevent_initial_call=True,
        allow_duplicate=True
    )
    def sync_plage_det(relayoutData):
        if not relayoutData: return dash.no_update
        if 'xaxis.range[0]' in relayoutData:
            return {'debut': relayoutData['xaxis.range[0]'],
                    'fin':   relayoutData['xaxis.range[1]']}
        if 'xaxis.autorange' in relayoutData: return None
        return dash.no_update

    # ── Statusbar principale ──────────────────────────────────────────────
    @app.callback(
        Output('statusbar-content', 'children'),
        Input('store-plage', 'data'),
        Input('store-mdf-path', 'data'),
    )
    def update_statusbar(plage, chemin_mdf):
        def s(t): return html.Span(t, style={'fontFamily': SANS, 'fontSize': '10px', 'color': DIM})
        if plage:
            return [s(f"t  {plage['debut']:.2f} → {plage['fin']:.2f} s"),
                    s(f"Δ {plage['fin']-plage['debut']:.2f} s")]
        return [s("Full Session")]

    # ── Statusbar détachée ────────────────────────────────────────────────
    @app.callback(
        Output('statusbar-content-det', 'children'),
        Input('store-plage-det', 'data'),
        Input('store-mdf-path-det', 'data'),
    )
    def update_statusbar_det(plage, chemin_mdf):
        def s(t): return html.Span(t, style={'fontFamily': SANS, 'fontSize': '10px', 'color': DIM})
        if plage:
            return [s(f"t  {plage['debut']:.2f} → {plage['fin']:.2f} s"),
                    s(f"Δ {plage['fin']-plage['debut']:.2f} s")]
        return [s("Full Session")]

    # ── Export CSV ────────────────────────────────────────────────────────
    @app.callback(
        Output('download-csv', 'data'),
        Input('btn-export-csv', 'n_clicks'),
        State('store-mdf-path', 'data'),
        State('store-canaux-selectionnes', 'data'),
        State('store-plage', 'data'),
        State('upload-mdf', 'filename'),
        prevent_initial_call=True
    )
    def exporter_csv(n_clicks, chemin_mdf, canaux_sel, plage, filename):
        if not chemin_mdf or not canaux_sel: return dash.no_update
        try:
            mdf = asammdf.MDF(chemin_mdf)
            dfs = []
            for canal in canaux_sel:
                df, unit = signal_vers_dataframe(mdf, canal)
                if df is not None:
                    if plage:
                        mask = ((df['timestamp'] >= plage['debut']) &
                                (df['timestamp'] <= plage['fin']))
                        df = df[mask]
                    dfs.append(df.set_index('timestamp'))
            mdf.close()
            if not dfs: return dash.no_update
            merged = pd.concat(dfs, axis=1)
            merged.index.name = 't (s)'
            base = (filename or 'export').replace('.mdf', '').replace('.MF4', '')
            if plage:
                csv_name = f"{base}_{plage['debut']:.0f}s-{plage['fin']:.0f}s.csv"
            else:
                csv_name = f"{base}_full.csv"
            return dcc.send_data_frame(merged.to_csv, csv_name)
        except Exception as e:
            print(f"Export CSV error: {e}")
            return dash.no_update

    # ── + View ────────────────────────────────────────────────────────────
    @app.callback(
        Output('store-dummy', 'data'),
        Input('btn-nouvelle-vue', 'n_clicks'),
        prevent_initial_call=True
    )
    def nouvelle_vue(n_clicks):
        if n_clicks and n_clicks > 0:
            try:
                import builtins
                builtins._demander_nouvelle_fenetre()
            except Exception:
                pass
        return dash.no_update