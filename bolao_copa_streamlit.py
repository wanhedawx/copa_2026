import streamlit as st
import pandas as pd
import json, hashlib, secrets
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# ===================== CONFIG =====================
TZ = ZoneInfo("America/Maceio")
USERS_FILE = Path("usuarios.json")
PALPITES_FILE = Path("palpites.json")
RESULTADOS_FILE = Path("resultados_reais.json")
LOCK_HOURS_BEFORE = 1
ADMIN_USER = "admin"  # crie esse usuário no primeiro login e use como admin

# ===================== JOGOS =====================
# Ajuste/complete aqui os jogos. Formato: id, data_hora, grupo, mandante, visitante
JOGOS = [

    # GRUPO A
    {"id":"A01","data_hora":"2026-06-11 16:00","grupo":"A","mandante":"México","visitante":"África do Sul"},
    {"id":"A02","data_hora":"2026-06-11 23:00","grupo":"A","mandante":"Coreia do Sul","visitante":"República Tcheca"},
    {"id":"A03","data_hora":"2026-06-18 13:00","grupo":"A","mandante":"República Tcheca","visitante":"África do Sul"},
    {"id":"A04","data_hora":"2026-06-18 22:00","grupo":"A","mandante":"México","visitante":"Coreia do Sul"},
    {"id":"A05","data_hora":"2026-06-24 22:00","grupo":"A","mandante":"República Tcheca","visitante":"México"},
    {"id":"A06","data_hora":"2026-06-24 22:00","grupo":"A","mandante":"África do Sul","visitante":"Coreia do Sul"},

    # GRUPO B
    {"id":"B01","data_hora":"2026-06-12 16:00","grupo":"B","mandante":"Canadá","visitante":"Bósnia e Herzegovina"},
    {"id":"B02","data_hora":"2026-06-13 16:00","grupo":"B","mandante":"Catar","visitante":"Suíça"},
    {"id":"B03","data_hora":"2026-06-18 16:00","grupo":"B","mandante":"Suíça","visitante":"Bósnia e Herzegovina"},
    {"id":"B04","data_hora":"2026-06-18 19:00","grupo":"B","mandante":"Canadá","visitante":"Catar"},
    {"id":"B05","data_hora":"2026-06-24 16:00","grupo":"B","mandante":"Suíça","visitante":"Canadá"},
    {"id":"B06","data_hora":"2026-06-24 16:00","grupo":"B","mandante":"Bósnia e Herzegovina","visitante":"Catar"},

    # GRUPO C
    {"id":"C01","data_hora":"2026-06-13 19:00","grupo":"C","mandante":"Brasil","visitante":"Marrocos"},
    {"id":"C02","data_hora":"2026-06-13 22:00","grupo":"C","mandante":"Haiti","visitante":"Escócia"},
    {"id":"C03","data_hora":"2026-06-19 19:00","grupo":"C","mandante":"Escócia","visitante":"Marrocos"},
    {"id":"C04","data_hora":"2026-06-19 22:00","grupo":"C","mandante":"Brasil","visitante":"Haiti"},
    {"id":"C05","data_hora":"2026-06-24 19:00","grupo":"C","mandante":"Escócia","visitante":"Brasil"},
    {"id":"C06","data_hora":"2026-06-24 19:00","grupo":"C","mandante":"Marrocos","visitante":"Haiti"},

    # GRUPO D
    {"id":"D01","data_hora":"2026-06-12 22:00","grupo":"D","mandante":"Estados Unidos","visitante":"Paraguai"},
    {"id":"D02","data_hora":"2026-06-14 01:00","grupo":"D","mandante":"Austrália","visitante":"Turquia"},
    {"id":"D03","data_hora":"2026-06-19 16:00","grupo":"D","mandante":"Estados Unidos","visitante":"Austrália"},
    {"id":"D04","data_hora":"2026-06-20 01:00","grupo":"D","mandante":"Turquia","visitante":"Paraguai"},
    {"id":"D05","data_hora":"2026-06-25 23:00","grupo":"D","mandante":"Turquia","visitante":"Estados Unidos"},
    {"id":"D06","data_hora":"2026-06-25 23:00","grupo":"D","mandante":"Paraguai","visitante":"Austrália"},

    # GRUPO E
    {"id":"E01","data_hora":"2026-06-14 14:00","grupo":"E","mandante":"Alemanha","visitante":"Curaçao"},
    {"id":"E02","data_hora":"2026-06-14 20:00","grupo":"E","mandante":"Costa do Marfim","visitante":"Equador"},
    {"id":"E03","data_hora":"2026-06-20 17:00","grupo":"E","mandante":"Alemanha","visitante":"Costa do Marfim"},
    {"id":"E04","data_hora":"2026-06-20 17:00","grupo":"E","mandante":"Equador","visitante":"Curaçao"},
    {"id":"E05","data_hora":"2026-06-25 17:00","grupo":"E","mandante":"Equador","visitante":"Alemanha"},
    {"id":"E06","data_hora":"2026-06-25 17:00","grupo":"E","mandante":"Curaçao","visitante":"Costa do Marfim"},

    # GRUPO F
    {"id":"F01","data_hora":"2026-06-14 17:00","grupo":"F","mandante":"Holanda","visitante":"Japão"},
    {"id":"F02","data_hora":"2026-06-14 23:00","grupo":"F","mandante":"Suécia","visitante":"Tunísia"},
    {"id":"F03","data_hora":"2026-06-20 14:00","grupo":"F","mandante":"Holanda","visitante":"Suécia"},
    {"id":"F04","data_hora":"2026-06-21 01:00","grupo":"F","mandante":"Tunísia","visitante":"Japão"},
    {"id":"F05","data_hora":"2026-06-25 20:00","grupo":"F","mandante":"Japão","visitante":"Suécia"},
    {"id":"F06","data_hora":"2026-06-25 20:00","grupo":"F","mandante":"Tunísia","visitante":"Holanda"},

    # GRUPO G
    {"id":"G01","data_hora":"2026-06-15 16:00","grupo":"G","mandante":"Bélgica","visitante":"Egito"},
    {"id":"G02","data_hora":"2026-06-15 22:00","grupo":"G","mandante":"Irã","visitante":"Nova Zelândia"},
    {"id":"G03","data_hora":"2026-06-21 16:00","grupo":"G","mandante":"Bélgica","visitante":"Irã"},
    {"id":"G04","data_hora":"2026-06-21 22:00","grupo":"G","mandante":"Nova Zelândia","visitante":"Egito"},
    {"id":"G05","data_hora":"2026-06-27 00:00","grupo":"G","mandante":"Egito","visitante":"Irã"},
    {"id":"G06","data_hora":"2026-06-27 00:00","grupo":"G","mandante":"Nova Zelândia","visitante":"Bélgica"},

    # GRUPO H
    {"id":"H01","data_hora":"2026-06-15 13:00","grupo":"H","mandante":"Espanha","visitante":"Cabo Verde"},
    {"id":"H02","data_hora":"2026-06-15 19:00","grupo":"H","mandante":"Arábia Saudita","visitante":"Uruguai"},
    {"id":"H03","data_hora":"2026-06-21 13:00","grupo":"H","mandante":"Espanha","visitante":"Arábia Saudita"},
    {"id":"H04","data_hora":"2026-06-21 19:00","grupo":"H","mandante":"Uruguai","visitante":"Cabo Verde"},
    {"id":"H05","data_hora":"2026-06-26 21:00","grupo":"H","mandante":"Cabo Verde","visitante":"Arábia Saudita"},
    {"id":"H06","data_hora":"2026-06-26 21:00","grupo":"H","mandante":"Uruguai","visitante":"Espanha"},

    # GRUPO I
    {"id":"I01","data_hora":"2026-06-16 16:00","grupo":"I","mandante":"França","visitante":"Senegal"},
    {"id":"I02","data_hora":"2026-06-16 19:00","grupo":"I","mandante":"Iraque","visitante":"Noruega"},
    {"id":"I03","data_hora":"2026-06-22 16:00","grupo":"I","mandante":"França","visitante":"Iraque"},
    {"id":"I04","data_hora":"2026-06-22 18:00","grupo":"I","mandante":"Noruega","visitante":"Senegal"},
    {"id":"I05","data_hora":"2026-06-26 16:00","grupo":"I","mandante":"Noruega","visitante":"França"},
    {"id":"I06","data_hora":"2026-06-26 16:00","grupo":"I","mandante":"Senegal","visitante":"Iraque"},

    # GRUPO J
    {"id":"J01","data_hora":"2026-06-16 22:00","grupo":"J","mandante":"Argentina","visitante":"Argélia"},
    {"id":"J02","data_hora":"2026-06-17 01:00","grupo":"J","mandante":"Áustria","visitante":"Jordânia"},
    {"id":"J03","data_hora":"2026-06-22 14:00","grupo":"J","mandante":"Argentina","visitante":"Áustria"},
    {"id":"J04","data_hora":"2026-06-23 00:00","grupo":"J","mandante":"Jordânia","visitante":"Argélia"},
    {"id":"J05","data_hora":"2026-06-27 23:00","grupo":"J","mandante":"Argélia","visitante":"Áustria"},
    {"id":"J06","data_hora":"2026-06-27 23:00","grupo":"J","mandante":"Jordânia","visitante":"Argentina"},

    # GRUPO K
    {"id":"K01","data_hora":"2026-06-17 14:00","grupo":"K","mandante":"Portugal","visitante":"RD do Congo"},
    {"id":"K02","data_hora":"2026-06-17 23:00","grupo":"K","mandante":"Uzbequistão","visitante":"Colômbia"},
    {"id":"K03","data_hora":"2026-06-23 14:00","grupo":"K","mandante":"Portugal","visitante":"Uzbequistão"},
    {"id":"K04","data_hora":"2026-06-23 23:00","grupo":"K","mandante":"Colômbia","visitante":"RD do Congo"},
    {"id":"K05","data_hora":"2026-06-27 20:30","grupo":"K","mandante":"Colômbia","visitante":"Portugal"},
    {"id":"K06","data_hora":"2026-06-27 20:30","grupo":"K","mandante":"RD do Congo","visitante":"Uzbequistão"},

    # GRUPO L
    {"id":"L01","data_hora":"2026-06-17 17:00","grupo":"L","mandante":"Inglaterra","visitante":"Croácia"},
    {"id":"L02","data_hora":"2026-06-17 20:00","grupo":"L","mandante":"Gana","visitante":"Panamá"},
    {"id":"L03","data_hora":"2026-06-23 17:00","grupo":"L","mandante":"Inglaterra","visitante":"Gana"},
    {"id":"L04","data_hora":"2026-06-23 20:00","grupo":"L","mandante":"Panamá","visitante":"Croácia"},
    {"id":"L05","data_hora":"2026-06-27 18:00","grupo":"L","mandante":"Panamá","visitante":"Inglaterra"},
    {"id":"L06","data_hora":"2026-06-27 18:00","grupo":"L","mandante":"Croácia","visitante":"Gana"},
]


# ===================== ESTILO =====================
def aplicar_estilo():
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        letter-spacing: -0.4px;
    }

    div[data-testid="stInfo"] {
        border-radius: 10px;
    }

    .grupo-box {
        margin-top: 26px;
        margin-bottom: 8px;
        padding: 10px 14px;
        border-radius: 10px;
        background: #173b66;
        border-left: 6px solid #f97316;
        color: white;
        font-size: 24px;
        font-weight: 800;
    }

    .cabecalho-jogo {
        padding: 8px 10px;
        margin-top: 8px;
        margin-bottom: 4px;
        border-radius: 8px;
        background: #0f2747;
        color: #dbeafe;
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
    }

    .linha-jogo {
        padding: 8px 10px;
        margin-bottom: 4px;
        border-radius: 10px;
        background: #111827;
        border: 1px solid #243244;
    }

    .texto-data {
        color: #e5e7eb;
        font-weight: 700;
        font-size: 14px;
        white-space: nowrap;
    }

    .texto-time {
        color: #ffffff;
        font-weight: 700;
        font-size: 15px;
    }

    .texto-x {
        color: #60a5fa;
        font-weight: 900;
        text-align: center;
        font-size: 18px;
        padding-top: 7px;
    }

    .status-aberto {
        color: #22c55e;
        font-weight: 800;
        font-size: 14px;
        white-space: nowrap;
    }

    .status-fechado {
        color: #ef4444;
        font-weight: 800;
        font-size: 14px;
        white-space: nowrap;
    }

    div[data-testid="stNumberInput"] {
        max-width: 82px;
    }

    div[data-testid="stNumberInput"] input {
        text-align: center;
        font-weight: 800;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)


# ===================== FUNÇÕES JSON =====================
def load_json(path, default):
    if not path.exists():
        path.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# ===================== LOGIN =====================
def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    senha_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, senha_hash

def check_password(password, salt, senha_hash):
    return hashlib.sha256((salt + password).encode()).hexdigest() == senha_hash

def login_screen():
    aplicar_estilo()
    st.title("🏆 Bolão Copa do Mundo 2026")
    users = load_json(USERS_FILE, {})

    tab_login, tab_cadastro = st.tabs(["Entrar", "Primeiro acesso / criar senha"])

    with tab_login:
        usuario = st.text_input("Usuário", key="login_user").strip().upper()
        senha = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Entrar"):
            if usuario in users and check_password(senha, users[usuario]["salt"], users[usuario]["senha_hash"]):
                st.session_state["usuario"] = usuario
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    with tab_cadastro:
        novo = st.text_input("Crie seu usuário", key="new_user").strip().upper()
        senha1 = st.text_input("Crie sua senha", type="password", key="new_pass1")
        senha2 = st.text_input("Confirme sua senha", type="password", key="new_pass2")
        if st.button("Criar acesso"):
            if not novo or not senha1:
                st.warning("Preencha usuário e senha.")
            elif novo in users:
                st.error("Esse usuário já existe.")
            elif senha1 != senha2:
                st.error("As senhas não conferem.")
            else:
                salt, senha_hash = hash_password(senha1)
                users[novo] = {"salt": salt, "senha_hash": senha_hash, "criado_em": datetime.now(TZ).isoformat()}
                save_json(USERS_FILE, users)
                st.success("Usuário criado! Agora faça login.")

# ===================== REGRAS =====================
def resultado_tipo(gols_casa, gols_fora):
    if gols_casa > gols_fora:
        return "C"
    if gols_casa < gols_fora:
        return "F"
    return "E"

def calcula_pontos(palpite, real):
    if palpite is None or real is None:
        return 0, "Pendente"
    pc, pf = palpite["casa"], palpite["fora"]
    rc, rf = real["casa"], real["fora"]
    if pc == rc and pf == rf:
        return 3, "Placar exato"
    if resultado_tipo(pc, pf) == resultado_tipo(rc, rf):
        return 1, "Resultado certo"
    return 0, "Errou"

def jogo_bloqueado(data_hora_str):
    inicio = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
    return datetime.now(TZ) >= inicio - timedelta(hours=LOCK_HOURS_BEFORE)


# ===================== GERENCIAR USUÁRIOS =====================
def gerenciar_usuarios():
    st.subheader("👥 Gerenciar usuários")
    st.info("Área exclusiva do admin para alterar nomes ou excluir participantes.")

    users = load_json(USERS_FILE, {})
    palpites = load_json(PALPITES_FILE, {})

    admin_name = ADMIN_USER.upper()
    lista_usuarios = sorted([u for u in users.keys() if u != admin_name])

    if not lista_usuarios:
        st.warning("Nenhum usuário cadastrado ainda.")
        return

    st.markdown("### Usuários cadastrados")
    df_users = pd.DataFrame({"Usuário": lista_usuarios})
    st.dataframe(df_users, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Alterar nome do usuário")

    usuario_antigo = st.selectbox(
        "Selecione o usuário",
        lista_usuarios,
        key="admin_usuario_antigo"
    )

    novo_nome = st.text_input(
        "Novo nome",
        value=usuario_antigo,
        key="admin_novo_nome"
    ).strip().upper()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✏️ Alterar nome", use_container_width=True):
            if not novo_nome:
                st.warning("Informe um novo nome válido.")
            elif novo_nome == admin_name:
                st.error("Esse nome é reservado para o admin.")
            elif novo_nome == usuario_antigo:
                st.warning("O novo nome é igual ao nome atual.")
            elif novo_nome in users:
                st.error("Já existe um usuário com esse nome.")
            else:
                # Renomeia no arquivo de usuários
                users[novo_nome] = users.pop(usuario_antigo)
                users[novo_nome]["alterado_em"] = datetime.now(TZ).isoformat()
                users[novo_nome]["nome_anterior"] = usuario_antigo

                # Migra também os palpites para manter a pontuação
                if usuario_antigo in palpites:
                    palpites[novo_nome] = palpites.pop(usuario_antigo)

                save_json(USERS_FILE, users)
                save_json(PALPITES_FILE, palpites)

                st.success(f"Usuário alterado de {usuario_antigo} para {novo_nome}.")
                st.rerun()

    with col2:
        if st.button("🗑️ Excluir usuário", use_container_width=True):
            users.pop(usuario_antigo, None)
            palpites.pop(usuario_antigo, None)

            save_json(USERS_FILE, users)
            save_json(PALPITES_FILE, palpites)

            st.success(f"Usuário {usuario_antigo} excluído.")
            st.rerun()

# ===================== APP =====================
def app():
    aplicar_estilo()
    usuario = st.session_state["usuario"]
    is_admin = usuario == ADMIN_USER.upper()

    st.sidebar.success(f"Logado como: {usuario}")
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    palpites = load_json(PALPITES_FILE, {})
    resultados = load_json(RESULTADOS_FILE, {})
    palpites.setdefault(usuario, {})

    if is_admin:
        menu = st.sidebar.radio(
            "Menu",
            ["Meus palpites", "Classificação", "Resultados reais", "Gerenciar usuários"]
        )
    else:
        menu = st.sidebar.radio(
            "Menu",
            ["Meus palpites", "Classificação", "Ver resultados"]
        )

    st.markdown("<h1 style='text-align:center'>🏆 BOLÃO DA COPA DO MUNDO 2026 🏆</h1>", unsafe_allow_html=True)

    if menu == "Meus palpites":
        st.subheader("Minha aba de palpites")
        st.info("Cada jogo trava automaticamente 1 hora antes do início.")

        for grupo in sorted(set(j["grupo"] for j in JOGOS)):
            st.markdown(f"<div class='grupo-box'>Grupo {grupo}</div>", unsafe_allow_html=True)

            h1, h2, h3, h4, h5, h6, h7 = st.columns([1.35, 2.25, 0.62, 0.22, 0.62, 2.25, 0.95])
            h1.markdown("<div class='cabecalho-jogo'>Data/Hora</div>", unsafe_allow_html=True)
            h2.markdown("<div class='cabecalho-jogo'>Mandante</div>", unsafe_allow_html=True)
            h3.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
            h4.markdown("<div class='cabecalho-jogo' style='text-align:center'>x</div>", unsafe_allow_html=True)
            h5.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
            h6.markdown("<div class='cabecalho-jogo'>Visitante</div>", unsafe_allow_html=True)
            h7.markdown("<div class='cabecalho-jogo'>Status</div>", unsafe_allow_html=True)

            jogos_grupo = [j for j in JOGOS if j["grupo"] == grupo]

            for j in jogos_grupo:
                lock = jogo_bloqueado(j["data_hora"])
                atual = palpites[usuario].get(j["id"], {})
                data_formatada = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y - %H:%M")

                c1, c2, c3, c4, c5, c6, c7 = st.columns([1.35, 2.25, 0.62, 0.22, 0.62, 2.25, 0.95])

                with c1:
                    st.markdown(f"<div class='linha-jogo texto-data'>{data_formatada}</div>", unsafe_allow_html=True)

                with c2:
                    st.markdown(f"<div class='linha-jogo texto-time'>{j['mandante']}</div>", unsafe_allow_html=True)

                with c3:
                    casa = st.number_input(
                        "Gols mandante",
                        min_value=0,
                        max_value=30,
                        value=int(atual.get("casa", 0)),
                        disabled=lock,
                        key=f"{usuario}_{j['id']}_c",
                        label_visibility="collapsed"
                    )

                with c4:
                    st.markdown("<div class='texto-x'>x</div>", unsafe_allow_html=True)

                with c5:
                    fora = st.number_input(
                        "Gols visitante",
                        min_value=0,
                        max_value=30,
                        value=int(atual.get("fora", 0)),
                        disabled=lock,
                        key=f"{usuario}_{j['id']}_f",
                        label_visibility="collapsed"
                    )

                with c6:
                    st.markdown(f"<div class='linha-jogo texto-time'>{j['visitante']}</div>", unsafe_allow_html=True)

                with c7:
                    if lock:
                        st.markdown("<div class='linha-jogo status-fechado'>🔒 Fechado</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='linha-jogo status-aberto'>✅ Aberto</div>", unsafe_allow_html=True)

                if not lock:
                    palpites[usuario][j["id"]] = {
                        "casa": casa,
                        "fora": fora,
                        "salvo_em": datetime.now(TZ).isoformat()
                    }

        if st.button("Salvar meus palpites", use_container_width=True):
            save_json(PALPITES_FILE, palpites)
            st.success("Palpites salvos!")

    elif menu == "Classificação":
        st.subheader("🏅 Classificação")
        linhas = []
        for user, palp_user in palpites.items():
            pontos = exatos = resultados_certos = 0
            for j in JOGOS:
                p = palp_user.get(j["id"])
                r = resultados.get(j["id"])
                pts, desc = calcula_pontos(p, r)
                pontos += pts
                if desc == "Placar exato": exatos += 1
                if desc == "Resultado certo": resultados_certos += 1
            linhas.append({"Participante": user, "Pontos": pontos, "Placares Exatos": exatos, "Resultados Certos": resultados_certos})

        df = pd.DataFrame(linhas)
        if not df.empty:
            df = df.sort_values(["Pontos", "Placares Exatos", "Resultados Certos"], ascending=False).reset_index(drop=True)
            df.insert(0, "Pos", df.index + 1)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("Ainda não há palpites.")

    elif menu == "Gerenciar usuários":
        if is_admin:
            gerenciar_usuarios()
        else:
            st.error("Você não tem permissão para acessar esta área.")

    else:
        if is_admin:
            st.subheader("Lançar resultados reais")

            for grupo in sorted(set(j["grupo"] for j in JOGOS)):
                st.markdown(f"<div class='grupo-box'>Grupo {grupo}</div>", unsafe_allow_html=True)

                h1, h2, h3, h4, h5, h6 = st.columns([1.35, 2.25, 0.62, 0.22, 0.62, 2.25])
                h1.markdown("<div class='cabecalho-jogo'>Data/Hora</div>", unsafe_allow_html=True)
                h2.markdown("<div class='cabecalho-jogo'>Mandante</div>", unsafe_allow_html=True)
                h3.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
                h4.markdown("<div class='cabecalho-jogo' style='text-align:center'>x</div>", unsafe_allow_html=True)
                h5.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
                h6.markdown("<div class='cabecalho-jogo'>Visitante</div>", unsafe_allow_html=True)

                for j in [x for x in JOGOS if x["grupo"] == grupo]:
                    atual = resultados.get(j["id"], {})
                    data_formatada = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y - %H:%M")

                    c1, c2, c3, c4, c5, c6 = st.columns([1.35, 2.25, 0.62, 0.22, 0.62, 2.25])

                    with c1:
                        st.markdown(f"<div class='linha-jogo texto-data'>{data_formatada}</div>", unsafe_allow_html=True)

                    with c2:
                        st.markdown(f"<div class='linha-jogo texto-time'>{j['mandante']}</div>", unsafe_allow_html=True)

                    with c3:
                        casa = st.number_input(
                            "Gols mandante real",
                            min_value=0,
                            max_value=30,
                            value=int(atual.get("casa", 0)),
                            key=f"real_{j['id']}_c",
                            label_visibility="collapsed"
                        )

                    with c4:
                        st.markdown("<div class='texto-x'>x</div>", unsafe_allow_html=True)

                    with c5:
                        fora = st.number_input(
                            "Gols visitante real",
                            min_value=0,
                            max_value=30,
                            value=int(atual.get("fora", 0)),
                            key=f"real_{j['id']}_f",
                            label_visibility="collapsed"
                        )

                    with c6:
                        st.markdown(f"<div class='linha-jogo texto-time'>{j['visitante']}</div>", unsafe_allow_html=True)

                    resultados[j["id"]] = {
                        "casa": casa,
                        "fora": fora,
                        "salvo_em": datetime.now(TZ).isoformat()
                    }

            if st.button("Salvar resultados reais", use_container_width=True):
                save_json(RESULTADOS_FILE, resultados)
                st.success("Resultados reais salvos!")
        else:
            st.subheader("Resultados reais")
            linhas = []
            for j in JOGOS:
                r = resultados.get(j["id"])
                linhas.append({
                    "Data": datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y %H:%M"),
                    "Grupo": j["grupo"],
                    "Jogo": f"{j['mandante']} x {j['visitante']}",
                    "Resultado": "-" if not r else f"{r['casa']} x {r['fora']}"
                })
            st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)

# ===================== MAIN =====================
st.set_page_config(page_title="Bolão Copa 2026", layout="wide")
if "usuario" not in st.session_state:
    login_screen()
else:
    app()
