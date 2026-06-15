import streamlit as st
import pandas as pd
import hashlib
import secrets
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import firebase_admin
from firebase_admin import credentials, firestore

# ===================== CONFIG =====================
TZ = ZoneInfo("America/Maceio")
LOCK_HOURS_BEFORE = 1
ADMIN_USER = "ADMIN"
SENHA_PADRAO = "123"

USUARIOS_INICIAIS = [
    "CHEVETTE67",
    "SAPAS",
    "ANAO PIKENO",
    "CHARQUINHO",
    "GAGUINHO",
    "FILHO PREFERIDO",
    "MACACO",
    "REALAL",
]

# ===================== JOGOS =====================
# Formato: id, data_hora, grupo, mandante, visitante
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

    h1, h2, h3 { letter-spacing: -0.4px; }

    div[data-testid="stInfo"] { border-radius: 10px; }

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
        display: flex;
        justify-content: center;
        align-items: center;
        height: 55px;
        color: #60a5fa;
        font-weight: 900;
        text-align: center;
        font-size: 22px;
        line-height: 1;
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
        max-width: 70px;
        margin: auto;
    }

    div[data-testid="stNumberInput"] input {
        text-align: center !important;
        font-weight: 800;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)


# ===================== FIREBASE =====================
@st.cache_resource
def get_db():
    """
    Para funcionar no Streamlit Cloud, coloque o JSON da conta de serviço em:
    Settings > Secrets, com o nome [firebase_service_account]
    """
    if not firebase_admin._apps:
        if "firebase_service_account" not in st.secrets:
            st.error("Configuração do Firebase não encontrada em st.secrets['firebase_service_account'].")
            st.stop()

        cred = credentials.Certificate(dict(st.secrets["firebase_service_account"]))
        firebase_admin.initialize_app(cred)

    # IMPORTANTE:
    # O banco que você criou no Firebase está com ID "default".
    # Se não informar isso, o SDK tenta abrir o banco antigo "(default)"
    # e pode gerar erro NotFound.
    try:
        return firestore.client(database_id="default")
    except TypeError:
        # Compatibilidade com versões antigas do firebase-admin.
        # Se cair aqui, atualize o requirements.txt para firebase-admin>=6.5.0
        return firestore.client()


def now_iso():
    return datetime.now(TZ).isoformat()


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    senha_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, senha_hash


def check_password(password, salt, senha_hash):
    return hashlib.sha256((salt + password).encode()).hexdigest() == senha_hash


def normalize_user(usuario):
    return (usuario or "").strip().upper()


def doc_to_dict(doc):
    dados = doc.to_dict() or {}
    dados["id"] = doc.id
    return dados


def get_all_users():
    db = get_db()
    docs = db.collection("usuarios").stream()
    return {doc.id: doc.to_dict() or {} for doc in docs}


def get_user(usuario):
    db = get_db()
    usuario = normalize_user(usuario)
    snap = db.collection("usuarios").document(usuario).get()
    if snap.exists:
        return snap.to_dict() or {}
    return None


def save_user(usuario, dados, merge=True):
    db = get_db()
    usuario = normalize_user(usuario)
    db.collection("usuarios").document(usuario).set(dados, merge=merge)


def delete_user(usuario):
    db = get_db()
    usuario = normalize_user(usuario)
    db.collection("usuarios").document(usuario).delete()


def create_user(usuario, senha=SENHA_PADRAO, master=False, trocar_senha=False):
    usuario = normalize_user(usuario)
    salt, senha_hash = hash_password(senha)
    save_user(usuario, {
        "salt": salt,
        "senha_hash": senha_hash,
        "master": bool(master),
        "trocar_senha": bool(trocar_senha),
        "ativo": True,
        "criado_em": now_iso(),
        "atualizado_em": now_iso(),
    }, merge=False)


def reset_password(usuario):
    usuario = normalize_user(usuario)
    salt, senha_hash = hash_password(SENHA_PADRAO)
    save_user(usuario, {
        "salt": salt,
        "senha_hash": senha_hash,
        "trocar_senha": True,
        "atualizado_em": now_iso(),
        "senha_redefinida_em": now_iso(),
    }, merge=True)


def ensure_initial_users():
    """
    Cria admin e participantes iniciais se ainda não existirem no Firebase.

    Regra atual:
    - Usuário novo entra com senha 123 e NÃO é obrigado a trocar no primeiro login.
    - Só será obrigado a trocar se o admin usar o botão de redefinir senha.

    Também corrige usuários que foram criados pela versão anterior do script
    com trocar_senha=True no primeiro login. Se o campo senha_redefinida_em
    não existir, entendemos que não foi uma redefinição feita pelo admin.
    """
    users = get_all_users()

    if ADMIN_USER not in users:
        create_user(ADMIN_USER, SENHA_PADRAO, master=True, trocar_senha=False)

    for usuario in USUARIOS_INICIAIS:
        usuario = normalize_user(usuario)
        if usuario not in users:
            create_user(usuario, SENHA_PADRAO, master=False, trocar_senha=False)

    # Migração automática: desfaz a obrigação de trocar senha dos usuários
    # criados pela versão antiga, sem atrapalhar uma redefinição feita pelo admin.
    users = get_all_users()
    for usuario, dados in users.items():
        if dados.get("trocar_senha", False) and not dados.get("senha_redefinida_em"):
            save_user(usuario, {
                "trocar_senha": False,
                "atualizado_em": now_iso(),
                "migrado_troca_senha_primeiro_login": True,
            }, merge=True)


def get_palpites_usuario(usuario):
    db = get_db()
    usuario = normalize_user(usuario)
    doc = db.collection("palpites").document(usuario).get()
    return doc.to_dict() or {}


def save_palpites_usuario(usuario, palpites_usuario):
    db = get_db()
    usuario = normalize_user(usuario)
    db.collection("palpites").document(usuario).set(palpites_usuario)


def get_all_palpites():
    db = get_db()
    return {doc.id: doc.to_dict() or {} for doc in db.collection("palpites").stream()}


def delete_palpites_usuario(usuario):
    db = get_db()
    usuario = normalize_user(usuario)
    db.collection("palpites").document(usuario).delete()


def rename_palpites_usuario(usuario_antigo, novo_nome):
    db = get_db()
    usuario_antigo = normalize_user(usuario_antigo)
    novo_nome = normalize_user(novo_nome)
    dados = get_palpites_usuario(usuario_antigo)
    if dados:
        db.collection("palpites").document(novo_nome).set(dados)
    db.collection("palpites").document(usuario_antigo).delete()


def get_resultados():
    db = get_db()
    doc = db.collection("configuracoes").document("resultados_reais").get()
    return doc.to_dict() or {}


def save_resultados(resultados):
    db = get_db()
    db.collection("configuracoes").document("resultados_reais").set(resultados)


# ===================== LOGIN =====================
def tela_trocar_senha(usuario, user_data):
    st.warning("Você precisa criar uma nova senha antes de continuar.")

    nova = st.text_input("Nova senha", type="password", key="nova_senha_obrigatoria")
    confirmar = st.text_input("Confirmar nova senha", type="password", key="confirma_senha_obrigatoria")

    if st.button("Salvar nova senha", use_container_width=True):
        if not nova or not confirmar:
            st.error("Preencha a nova senha e a confirmação.")
        elif nova != confirmar:
            st.error("As senhas não conferem.")
        elif len(nova) < 4:
            st.error("A senha precisa ter pelo menos 4 caracteres.")
        elif nova == SENHA_PADRAO:
            st.error("Escolha uma senha diferente da senha padrão 123.")
        else:
            salt, senha_hash = hash_password(nova)
            save_user(usuario, {
                "salt": salt,
                "senha_hash": senha_hash,
                "trocar_senha": False,
                "atualizado_em": now_iso(),
                "senha_alterada_em": now_iso(),
            }, merge=True)
            st.success("Senha alterada! Faça login novamente.")
            st.session_state.clear()
            st.rerun()

    st.stop()


def login_screen():
    aplicar_estilo()
    ensure_initial_users()

    st.title("🏆 Bolão Copa do Mundo 2026")

    tab_login, tab_criar = st.tabs(["Entrar", "Criar usuário"])

    with tab_login:
        usuario = normalize_user(st.text_input("Usuário", key="login_user"))
        senha = st.text_input("Senha", type="password", key="login_pass")

        if st.button("Entrar", use_container_width=True, key="btn_login"):
            user_data = get_user(usuario)

            if not usuario or not senha:
                st.warning("Informe usuário e senha.")
            elif not user_data:
                st.error("Usuário ou senha inválidos.")
            elif not user_data.get("ativo", True):
                st.error("Usuário inativo. Fale com o admin.")
            elif check_password(senha, user_data.get("salt", ""), user_data.get("senha_hash", "")):
                st.session_state["usuario"] = usuario
                st.session_state["master"] = bool(user_data.get("master", False))
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    with tab_criar:
        novo_usuario = normalize_user(st.text_input("Novo usuário", key="criar_user"))
        nova_senha = st.text_input("Senha", type="password", key="criar_senha")
        confirmar_senha = st.text_input("Confirmar senha", type="password", key="criar_confirma_senha")

        if st.button("Criar usuário", use_container_width=True, key="btn_criar_usuario"):
            users = get_all_users()
            admin_name = ADMIN_USER.upper()

            if not novo_usuario or not nova_senha or not confirmar_senha:
                st.warning("Preencha usuário, senha e confirmação.")
            elif novo_usuario == admin_name:
                st.error("Esse nome é reservado para o admin.")
            elif novo_usuario in users:
                st.error("Esse usuário já existe.")
            elif nova_senha != confirmar_senha:
                st.error("As senhas não conferem.")
            elif len(nova_senha) < 3:
                st.error("A senha precisa ter pelo menos 3 caracteres.")
            else:
                create_user(novo_usuario, nova_senha, master=False, trocar_senha=False)
                st.success("Usuário criado! Agora faça login na aba Entrar.")


# ===================== REGRAS =====================
def resultado_tipo(gols_casa, gols_fora):
    if gols_casa > gols_fora:
        return "W"
    if gols_casa < gols_fora:
        return "L"
    return "D"


def valor_em_branco(valor):
    return valor is None or valor == "" or valor == "-"


def palpite_valido(palpite):
    """
    Regra importante:
    - Palpite novo só vale se tiver preenchido=True.
    - Palpite antigo 0x0 sem preenchido=True é considerado em branco,
      porque nas versões antigas o sistema salvava 0x0 automaticamente.
    - Palpite antigo diferente de 0x0 continua valendo.
    """
    if not isinstance(palpite, dict):
        return False

    if "casa" not in palpite or "fora" not in palpite:
        return False

    casa = palpite.get("casa")
    fora = palpite.get("fora")

    if valor_em_branco(casa) or valor_em_branco(fora):
        return False

    try:
        casa_int = int(casa)
        fora_int = int(fora)
    except Exception:
        return False

    if palpite.get("preenchido") is True:
        return True

    # Compatibilidade com dados antigos:
    # 0x0 sem a marcação preenchido=True não conta como palpite.
    if casa_int == 0 and fora_int == 0:
        return False

    return True


def valor_palpite_para_tela(palpite, campo):
    if not isinstance(palpite, dict):
        return "-"

    if not palpite_valido(palpite):
        return "-"

    valor = palpite.get(campo)
    if valor_em_branco(valor):
        return "-"

    try:
        return int(valor)
    except Exception:
        return "-"


def seletor_gols(label, atual, campo, disabled, key):
    opcoes = ["-"] + list(range(0, 31))
    valor = valor_palpite_para_tela(atual, campo)
    indice = opcoes.index(valor) if valor in opcoes else 0

    return st.selectbox(
        label,
        opcoes,
        index=indice,
        disabled=disabled,
        key=key,
        label_visibility="collapsed",
        format_func=lambda x: "-" if x == "-" else str(x),
    )


def aplicar_palpite_temp(palpites_temp, jogo_id, casa, fora, extras=None):
    if casa == "-" or fora == "-":
        palpites_temp.pop(jogo_id, None)
        return

    dados = {
        "casa": int(casa),
        "fora": int(fora),
        "preenchido": True,
        "salvo_em": now_iso(),
    }

    if extras:
        dados.update(extras)

    palpites_temp[jogo_id] = dados


def calcula_pontos(palpite, real):
    if not palpite_valido(palpite) or real is None:
        return 0, "Pendente"

    pc, pf = int(palpite["casa"]), int(palpite["fora"])
    rc, rf = int(real["casa"]), int(real["fora"])

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
    st.info("Área exclusiva do admin para alterar nomes, excluir participantes ou redefinir senha para 123.")

    users = get_all_users()
    admin_name = ADMIN_USER.upper()
    lista_usuarios = sorted([u for u in users.keys() if u != admin_name])

    if not lista_usuarios:
        st.warning("Nenhum usuário cadastrado ainda.")
        return

    st.markdown("### Usuários cadastrados")
    df_users = pd.DataFrame({
        "Usuário": lista_usuarios,
        "Trocar senha?": ["Sim" if users[u].get("trocar_senha", False) else "Não" for u in lista_usuarios],
        "Ativo?": ["Sim" if users[u].get("ativo", True) else "Não" for u in lista_usuarios],
    })
    st.dataframe(df_users, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Alterar, excluir ou redefinir senha")

    usuario_antigo = st.selectbox("Selecione o usuário", lista_usuarios, key="admin_usuario_antigo")
    novo_nome = normalize_user(st.text_input("Novo nome", value=usuario_antigo, key="admin_novo_nome"))

    col1, col2, col3 = st.columns(3)

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
                dados_user = users[usuario_antigo]
                dados_user["alterado_em"] = now_iso()
                dados_user["nome_anterior"] = usuario_antigo

                save_user(novo_nome, dados_user, merge=False)
                delete_user(usuario_antigo)
                rename_palpites_usuario(usuario_antigo, novo_nome)

                st.success(f"Usuário alterado de {usuario_antigo} para {novo_nome}.")
                st.rerun()

    with col2:
        if st.button("🔑 Redefinir senha", use_container_width=True):
            reset_password(usuario_antigo)
            st.success(f"Senha de {usuario_antigo} redefinida para 123. No próximo login ele terá que criar uma nova senha.")
            st.rerun()

    with col3:
        if st.button("🗑️ Excluir usuário", use_container_width=True):
            delete_user(usuario_antigo)
            delete_palpites_usuario(usuario_antigo)
            st.success(f"Usuário {usuario_antigo} excluído.")
            st.rerun()

    st.divider()
    st.markdown("### Criar novo usuário manualmente")
    novo_usuario_manual = normalize_user(st.text_input("Nome do novo usuário", key="novo_usuario_manual"))
    senha_manual = st.text_input("Senha do novo usuário", type="password", key="senha_usuario_manual")
    confirma_senha_manual = st.text_input("Confirmar senha do novo usuário", type="password", key="confirma_senha_usuario_manual")

    if st.button("➕ Criar usuário", use_container_width=True, key="btn_criar_usuario_admin"):
        if not novo_usuario_manual or not senha_manual or not confirma_senha_manual:
            st.warning("Informe o nome do usuário, a senha e a confirmação.")
        elif novo_usuario_manual in users:
            st.error("Esse usuário já existe.")
        elif novo_usuario_manual == admin_name:
            st.error("Esse nome é reservado para o admin.")
        elif senha_manual != confirma_senha_manual:
            st.error("As senhas não conferem.")
        elif len(senha_manual) < 3:
            st.error("A senha precisa ter pelo menos 3 caracteres.")
        else:
            create_user(novo_usuario_manual, senha_manual, master=False, trocar_senha=False)
            st.success(f"Usuário {novo_usuario_manual} criado com a senha informada.")
            st.rerun()


# ===================== EDITAR PALPITES COMO ADMIN =====================
def editar_palpites_admin():
    st.subheader("🛠️ Editar palpites dos usuários")
    st.warning("Modo admin: todos os jogos ficam abertos para edição, mesmo os que já passaram ou travaram.")

    users = get_all_users()
    admin_name = ADMIN_USER.upper()
    lista_usuarios = sorted([u for u, d in users.items() if u != admin_name and d.get("ativo", True)])

    if not lista_usuarios:
        st.warning("Nenhum usuário disponível para editar.")
        return

    usuario_alvo = st.selectbox("Selecione o usuário para editar", lista_usuarios, key="admin_editar_palpites_usuario")
    palpites_temp = dict(get_palpites_usuario(usuario_alvo))

    st.markdown(f"### Editando palpites de: **{usuario_alvo}**")

    for grupo in sorted(set(j["grupo"] for j in JOGOS)):
        st.markdown(f"<div class='grupo-box'>Grupo {grupo}</div>", unsafe_allow_html=True)

        h1, h2, h3, h4, h5, h6, h7 = st.columns([1.4, 2.3, 0.55, 0.35, 0.55, 2.3, 0.9])
        h1.markdown("<div class='cabecalho-jogo'>Data/Hora</div>", unsafe_allow_html=True)
        h2.markdown("<div class='cabecalho-jogo'>Mandante</div>", unsafe_allow_html=True)
        h3.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
        h4.markdown("<div class='cabecalho-jogo' style='text-align:center'>x</div>", unsafe_allow_html=True)
        h5.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
        h6.markdown("<div class='cabecalho-jogo'>Visitante</div>", unsafe_allow_html=True)
        h7.markdown("<div class='cabecalho-jogo'>Status</div>", unsafe_allow_html=True)

        for j in [x for x in JOGOS if x["grupo"] == grupo]:
            atual = palpites_temp.get(j["id"], {})
            data_formatada = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y - %H:%M")

            c1, c2, c3, c4, c5, c6, c7 = st.columns([1.4, 2.3, 0.55, 0.35, 0.55, 2.3, 0.9])

            with c1:
                st.markdown(f"<div class='linha-jogo texto-data'>{data_formatada}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='linha-jogo texto-time'>{j['mandante']}</div>", unsafe_allow_html=True)
            with c3:
                casa = seletor_gols(
                    "Gols mandante",
                    atual,
                    "casa",
                    disabled=False,
                    key=f"admin_edit_{usuario_alvo}_{j['id']}_c",
                )
            with c4:
                st.markdown("<div class='texto-x'>X</div>", unsafe_allow_html=True)
            with c5:
                fora = seletor_gols(
                    "Gols visitante",
                    atual,
                    "fora",
                    disabled=False,
                    key=f"admin_edit_{usuario_alvo}_{j['id']}_f",
                )
            with c6:
                st.markdown(f"<div class='linha-jogo texto-time'>{j['visitante']}</div>", unsafe_allow_html=True)
            with c7:
                st.markdown("<div class='linha-jogo status-aberto'>🔓 Admin</div>", unsafe_allow_html=True)

            aplicar_palpite_temp(
                palpites_temp,
                j["id"],
                casa,
                fora,
                extras={
                    "editado_por_admin": True,
                    "admin": st.session_state.get("usuario", ADMIN_USER),
                },
            )

    if st.button(f"Salvar palpites de {usuario_alvo}", use_container_width=True, key=f"salvar_palpites_admin_{usuario_alvo}"):
        save_palpites_usuario(usuario_alvo, palpites_temp)
        st.success(f"Palpites de {usuario_alvo} salvos no Firebase!")
        st.rerun()


# ===================== APP =====================
def app():
    aplicar_estilo()

    usuario = st.session_state["usuario"]
    user_data = get_user(usuario)

    if not user_data:
        st.session_state.clear()
        st.error("Usuário não encontrado. Faça login novamente.")
        st.stop()

    if user_data.get("trocar_senha", False):
        tela_trocar_senha(usuario, user_data)

    is_admin = bool(user_data.get("master", False)) or usuario == ADMIN_USER.upper()

    st.sidebar.success(f"Logado como: {usuario}")
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    palpites_usuario = get_palpites_usuario(usuario)
    resultados = get_resultados()

    if is_admin:
        menu = st.sidebar.radio("Menu", ["Meus palpites", "Editar palpites", "Classificação", "Resultados reais", "Gerenciar usuários"])
    else:
        menu = st.sidebar.radio("Menu", ["Meus palpites", "Classificação", "Ver resultados"])

    st.markdown("<h1 style='text-align:center'>🏆 BOLÃO DA COPA DO MUNDO 2026 🏆</h1>", unsafe_allow_html=True)

    if menu == "Meus palpites":
        st.subheader("Minha aba de palpites")
        st.info("Cada jogo trava automaticamente 1 hora antes do início.")
        st.markdown("""
        ### 📌 Regras de pontuação
        - **3 pontos**: acertou o placar exato.
        - **1 ponto**: acertou o resultado **W/D/L**: vitória do mandante, empate ou vitória do visitante.
        - **0 pontos**: errou o resultado.
        - **Sem pontuação**: se deixar `-`, fica como palpite não preenchido.
        """)

        palpites_temp = dict(palpites_usuario)

        for grupo in sorted(set(j["grupo"] for j in JOGOS)):
            st.markdown(f"<div class='grupo-box'>Grupo {grupo}</div>", unsafe_allow_html=True)

            h1, h2, h3, h4, h5, h6, h7 = st.columns([1.4, 2.3, 0.55, 0.35, 0.55, 2.3, 0.9])
            h1.markdown("<div class='cabecalho-jogo'>Data/Hora</div>", unsafe_allow_html=True)
            h2.markdown("<div class='cabecalho-jogo'>Mandante</div>", unsafe_allow_html=True)
            h3.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
            h4.markdown("<div class='cabecalho-jogo' style='text-align:center'>x</div>", unsafe_allow_html=True)
            h5.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
            h6.markdown("<div class='cabecalho-jogo'>Visitante</div>", unsafe_allow_html=True)
            h7.markdown("<div class='cabecalho-jogo'>Status</div>", unsafe_allow_html=True)

            for j in [x for x in JOGOS if x["grupo"] == grupo]:
                lock = jogo_bloqueado(j["data_hora"])
                atual = palpites_temp.get(j["id"], {})
                data_formatada = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y - %H:%M")

                c1, c2, c3, c4, c5, c6, c7 = st.columns([1.4, 2.3, 0.55, 0.35, 0.55, 2.3, 0.9])

                with c1:
                    st.markdown(f"<div class='linha-jogo texto-data'>{data_formatada}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div class='linha-jogo texto-time'>{j['mandante']}</div>", unsafe_allow_html=True)
                with c3:
                    casa = seletor_gols("Gols mandante", atual, "casa", disabled=lock, key=f"{usuario}_{j['id']}_c")
                with c4:
                    st.markdown("<div class='texto-x'>X</div>", unsafe_allow_html=True)
                with c5:
                    fora = seletor_gols("Gols visitante", atual, "fora", disabled=lock, key=f"{usuario}_{j['id']}_f")
                with c6:
                    st.markdown(f"<div class='linha-jogo texto-time'>{j['visitante']}</div>", unsafe_allow_html=True)
                with c7:
                    if lock:
                        st.markdown("<div class='linha-jogo status-fechado'>🔒 Fechado</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='linha-jogo status-aberto'>✅ Aberto</div>", unsafe_allow_html=True)

                if not lock:
                    aplicar_palpite_temp(palpites_temp, j["id"], casa, fora)

        if st.button("Salvar meus palpites", use_container_width=True):
            save_palpites_usuario(usuario, palpites_temp)
            st.success("Palpites salvos no Firebase!")
            st.rerun()

    elif menu == "Editar palpites":
        if is_admin:
            editar_palpites_admin()
        else:
            st.error("Você não tem permissão para acessar esta área.")

    elif menu == "Classificação":
        st.subheader("🏅 Classificação")

        users = get_all_users()
        admin_name = ADMIN_USER.upper()
        usuarios_validos = sorted([u for u, d in users.items() if u != admin_name and d.get("ativo", True)])
        todos_palpites = get_all_palpites()

        linhas = []
        for user in usuarios_validos:
            palp_user = todos_palpites.get(user, {})
            pontos = 0
            exatos = 0
            resultados_certos = 0

            for j in JOGOS:
                p = palp_user.get(j["id"])
                r = resultados.get(j["id"])
                pts, desc = calcula_pontos(p, r)
                pontos += pts
                if desc == "Placar exato":
                    exatos += 1
                elif desc == "Resultado certo":
                    resultados_certos += 1

            linhas.append({
                "Participante": user,
                "Pontos": pontos,
                "Placares Exatos": exatos,
                "Resultados Certos": resultados_certos
            })

        df = pd.DataFrame(linhas)
        if not df.empty:
            df = df.sort_values(["Pontos", "Placares Exatos", "Resultados Certos", "Participante"], ascending=[False, False, False, True]).reset_index(drop=True)
            df.insert(0, "Pos", df.index + 1)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("Ainda não há usuários cadastrados para aparecer na classificação.")

    elif menu == "Gerenciar usuários":
        if is_admin:
            gerenciar_usuarios()
        else:
            st.error("Você não tem permissão para acessar esta área.")

    else:
        if is_admin:
            st.subheader("Lançar resultados reais")
            st.warning("Marque **Resultado definido** somente nos jogos que já terminaram. Jogo desmarcado não conta pontos na classificação.")

            if st.button("🧹 Limpar todos os resultados reais", use_container_width=True):
                save_resultados({})
                st.success("Resultados reais limpos. A classificação foi zerada até você lançar novos resultados.")
                st.rerun()

            resultados_temp = dict(resultados)

            for grupo in sorted(set(j["grupo"] for j in JOGOS)):
                st.markdown(f"<div class='grupo-box'>Grupo {grupo}</div>", unsafe_allow_html=True)

                h1, h2, h3, h4, h5, h6, h7 = st.columns([1.4, 2.3, 0.55, 0.35, 0.55, 2.3, 1.2])
                h1.markdown("<div class='cabecalho-jogo'>Data/Hora</div>", unsafe_allow_html=True)
                h2.markdown("<div class='cabecalho-jogo'>Mandante</div>", unsafe_allow_html=True)
                h3.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
                h4.markdown("<div class='cabecalho-jogo' style='text-align:center'>x</div>", unsafe_allow_html=True)
                h5.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
                h6.markdown("<div class='cabecalho-jogo'>Visitante</div>", unsafe_allow_html=True)
                h7.markdown("<div class='cabecalho-jogo'>Definido?</div>", unsafe_allow_html=True)

                for j in [x for x in JOGOS if x["grupo"] == grupo]:
                    atual = resultados.get(j["id"], {})
                    ja_definido = j["id"] in resultados
                    data_formatada = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y - %H:%M")

                    c1, c2, c3, c4, c5, c6, c7 = st.columns([1.4, 2.3, 0.55, 0.35, 0.55, 2.3, 1.2])

                    with c1:
                        st.markdown(f"<div class='linha-jogo texto-data'>{data_formatada}</div>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<div class='linha-jogo texto-time'>{j['mandante']}</div>", unsafe_allow_html=True)
                    with c3:
                        casa = st.number_input("Gols mandante real", min_value=0, max_value=30, value=int(atual.get("casa", 0)), key=f"real_{j['id']}_c", label_visibility="collapsed")
                    with c4:
                        st.markdown("<div class='texto-x'>X</div>", unsafe_allow_html=True)
                    with c5:
                        fora = st.number_input("Gols visitante real", min_value=0, max_value=30, value=int(atual.get("fora", 0)), key=f"real_{j['id']}_f", label_visibility="collapsed")
                    with c6:
                        st.markdown(f"<div class='linha-jogo texto-time'>{j['visitante']}</div>", unsafe_allow_html=True)
                    with c7:
                        marcado = st.checkbox("OK", value=ja_definido, key=f"real_{j['id']}_check", label_visibility="collapsed")

                    if marcado:
                        resultados_temp[j["id"]] = {"casa": casa, "fora": fora, "salvo_em": now_iso()}
                    else:
                        resultados_temp.pop(j["id"], None)

            if st.button("Salvar resultados reais", use_container_width=True):
                save_resultados(resultados_temp)
                st.success("Resultados reais salvos no Firebase!")
                st.rerun()

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
